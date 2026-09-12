"""Verify archived full states/responses/events and replay each R3 operation in Rust."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();source=args.source.resolve();raw_path=args.input.resolve();output=args.output.resolve()
    data=raw_path.read_bytes();raw=json.loads(gzip.decompress(data))
    sha=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    assert sha==raw['source_sha'],'source mismatch'
    os.chdir(source);sys.path.insert(0,str(source))
    from star_native import _native
    from rotk_env.runtime.native import RustRuntime
    extension=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest()
    assert extension==raw['extension_sha256'],'extension mismatch'
    started=time.perf_counter();nodes=0;groups={}
    for case in raw['cases']:
        assert case['all_passed'],case.get('error')
        canonical=json.dumps(case['operations'],sort_keys=True,separators=(',',':')).encode()
        trace_hash=hashlib.sha256(canonical).hexdigest();assert trace_hash==case['trace_digest']
        groups.setdefault((case['family'],case['display'],case['mode']),set()).add(trace_hash)
        with RustRuntime(case['initial'],threads=case['threads']) as runtime:
            runtime.take_presentation_delta()
            for index,node in enumerate(case['operations']):
                assert all(node['guards'].values())
                assert node['actual']==node['expected']
                assert node['actual_state']==node['expected_state']
                assert node['actual_events']==node['expected_events']
                op=node['operation'];kind=op['kind'];result=None
                if kind=='request':result=runtime.execute_action(op['action'],op['parameters'],agent_id=op['agent_id'],wall_time=op['wall_time'],registration_time=op['registration_time'])
                elif kind=='step':runtime.step(op['dt'],wall_time=op['wall_time'])
                elif kind=='start_capture':result=runtime.start_capture(op['unit_id'],tuple(op['position']),wall_time=op['wall_time'])
                elif kind=='human_end_turn':runtime.finish_human_turn(wall_time=op['wall_time'])
                elif kind=='reset-current':runtime.reset(runtime.export_state())
                else:raise ValueError(kind)
                context=(case['family'],case['display'],case['mode'],case['threads'],index)
                assert result==node['actual'],('response',context)
                assert runtime.export_state()==node['actual_state'],('state',context)
                assert runtime.take_presentation_delta()['events']==node['actual_events'],('events',context)
                nodes+=1
    assert all(len(v)==1 for v in groups.values()),'thread settings differ'
    report=dict(source_sha=sha,extension_sha256=extension,input_file=str(raw_path),input_sha256=hashlib.sha256(data).hexdigest(),
        cases=len(raw['cases']),operations=nodes,thread_settings_equal=True,all_passed=True,replay_seconds=time.perf_counter()-started)
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
