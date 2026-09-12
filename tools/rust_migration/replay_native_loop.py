"""Replay an owned native initial world and the recorded accepted request/tick order."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def git(path,*args):return subprocess.check_output(['git','-C',str(path),*args],text=True).strip()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--trace',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();source=args.source.resolve();trace=args.trace.resolve();output=args.output.resolve()
    os.chdir(source);sys.path.insert(0,str(source))
    from rotk_env.runtime.native import RustRuntime
    from star_native import _native
    raw=json.loads(gzip.decompress(trace.read_bytes()));initial_file=trace.with_name(raw['initial']['file'])
    if sha(initial_file)!=raw['initial']['sha256']:raise ValueError('initial artifact checksum differs')
    if git(source,'rev-parse','HEAD')!=raw['source']['sha']:raise ValueError('use the recorded source SHA')
    if sha(Path(_native.__file__))!=raw['extension_sha256']:raise ValueError('use the recorded extension wheel')
    started=time.perf_counter();requests=ticks=0;failure=None
    initial=json.loads(gzip.decompress(initial_file.read_bytes()))
    with RustRuntime(initial,threads=raw['configuration']['threads']) as runtime:
        runtime.take_presentation_delta()
        for index,op in enumerate(raw['trace']):
            if op['seq']!=index:raise ValueError('noncontiguous trace')
            if op['kind']=='request':
                result=runtime.execute_action(op['action'],op['parameters'],agent_id=op['agent_id'],
                    wall_time=op['wall_time'],registration_time=op['registration_time'])
                actual=digest(result);requests+=1
                if actual!=op['response_sha256']:
                    failure=dict(seq=index,kind='response',expected=op['response_sha256'],actual=actual);break
            elif op['kind']=='step':
                runtime.step(op['dt'],wall_time=op['wall_time'])
                events=runtime.take_presentation_delta()['events']
                expected=raw['frames'][ticks]['game_events'];ticks+=1
                if events!=expected:
                    failure=dict(seq=index,kind='events',expected=expected,actual=events);break
            else:raise ValueError('unknown trace operation')
        final=digest(runtime.export_state())
    result=dict(schema='star-native-loop-replay-v1',source_sha=raw['source']['sha'],
        tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),trace_sha256=sha(trace),
        initial_sha256=sha(initial_file),extension_sha256=raw['extension_sha256'],
        requests_checked=requests,ticks_checked=ticks,expected_final_sha256=raw['final_state_sha256'],
        actual_final_sha256=final,failure=failure,elapsed_seconds=time.perf_counter()-started,
        all_passed=failure is None and final==raw['final_state_sha256'] and ticks==len(raw['frames']))
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    if not result['all_passed']:raise SystemExit(1)

if __name__=='__main__':main()
