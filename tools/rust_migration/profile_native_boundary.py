"""Profile the existing native JSON boundary on a fixed recorded request stream.

Diagnostic only: no world pacing/rendering. The direct mode is an experimental
wire forwarding path, not a supported production transport or capacity claim.
"""
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
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--trace',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--mode',choices=['legacy','direct'],required=True)
    p.add_argument('--threads',type=int,choices=[1,2,4],default=1)
    a=p.parse_args();src=a.source.resolve();trace=a.trace.resolve();out=a.output.resolve()
    sys.path.insert(0,str(src));os.chdir(src)
    from rotk_env.runtime.native import RustRuntime,ActionRequest,_complete_result
    from native_loop_trace import digest,artifact
    from p3_local_agents import stats
    from star_native import _native
    raw=json.loads(gzip.decompress(trace.read_bytes()))
    sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip()
    assert sha==raw['source']['sha']
    assert hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest()==raw['extension']['sha256']
    initial=trace.with_name(raw['initial']['file'])
    assert hashlib.sha256(initial.read_bytes()).hexdigest()==raw['initial']['sha256']
    rows=[];counts={};ticks=0;wire_differences=0
    with RustRuntime(json.loads(gzip.decompress(initial.read_bytes())),threads=a.threads) as n:
        n.take_presentation_delta()
        for index,op in enumerate(raw['entries']):
            assert op['seq']==index
            kind=op['kind'];counts[kind]=counts.get(kind,0)+1
            if kind=='step':n.step(op['dt'],wall_time=op['wall_time']);ticks+=1;continue
            if kind=='presentation':
                assert digest(n.take_presentation_delta()['events'])==op['events_sha256'];continue
            assert kind=='request'
            if 'integer_string_limit' in op:sys.set_int_max_str_digits(op['integer_string_limit'])
            kwargs=dict(agent_id=op['agent_id'],wall_time=op['wall_time'],registration_time=op['registration_time'])
            if op['action']!='get_faction_state':
                assert digest(n.execute_action(op['action'],op['parameters'],**kwargs))==op['response_sha256'];continue
            # Keep the same admission lock and trusted envelope. Only omit the
            # redundant server object round trip in the experimental mode.
            with n._admission_lock:
                began=time.perf_counter_ns()
                envelope=json.dumps(ActionRequest(action=op['action'],parameters=op['parameters'],**kwargs).to_wire(),allow_nan=False)
                ready=time.perf_counter_ns()
                native_wire=n._native.execute_action_json(envelope)
                built=time.perf_counter_ns()
                if a.mode=='legacy':
                    result=_complete_result(op['action'],json.loads(native_wire))
                    decoded=time.perf_counter_ns()
                    payload=json.dumps(result,separators=(',',':'),ensure_ascii=False).encode()
                else:
                    decoded=built
                    payload=native_wire.encode()
                encoded=time.perf_counter_ns()
                client=json.loads(payload)
                done=time.perf_counter_ns()
            # Compare the complete decoded reply via the historical canonical
            # Python wire digest; object-key order remains the recorded order.
            canonical=json.dumps(client,separators=(',',':'),ensure_ascii=False).encode()
            assert hashlib.sha256(canonical).hexdigest()==op['response_wire_sha256'],index
            wire_differences+=payload!=canonical
            rows.append(dict(seq=index,tick=ticks,envelope_ms=(ready-began)/1e6,native_ms=(built-ready)/1e6,server_decode_ms=(decoded-built)/1e6,server_encode_ms=(encoded-decoded)/1e6,client_decode_ms=(done-encoded)/1e6,total_ms=(done-began)/1e6,bytes=len(payload),canonical_bytes=len(canonical)))
        final=digest(n.export_state())
        assert final==raw['final_state_sha256']
    admitted=[r for r in rows if r['tick']>=900]
    out.parent.mkdir(parents=True,exist_ok=True)
    saved=artifact(out.with_suffix('.rows.json.gz'),rows)
    result=dict(mode=a.mode,threads=a.threads,source_sha=sha,extension=raw['extension'],trace_sha256=hashlib.sha256(trace.read_bytes()).hexdigest(),all_responses_events_and_final_state_match=True,final_state_sha256=final,counts=counts,observations=len(rows),admitted_observations=len(admitted),warmup_ticks=900,wire_differences=wire_differences,metrics={k:stats([r[k] for r in admitted]) for k in ['envelope_ms','native_ms','server_decode_ms','server_encode_ms','client_decode_ms','total_ms','bytes','canonical_bytes']},raw=saved)
    out.write_text(json.dumps(result,indent=2)+'\n');print(a.mode,a.threads,result['metrics']['total_ms'])

if __name__=='__main__':main()
