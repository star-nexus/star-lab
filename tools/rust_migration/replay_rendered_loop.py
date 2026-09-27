"""Replay actual native request/tick/presentation order; no timing or pixel claim."""
import argparse,gzip,hashlib,json,os,subprocess,sys,time
from pathlib import Path
from native_loop_trace import digest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--trace',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--threads',type=int,choices=[1,2,4]);a=p.parse_args()
    src=a.source.resolve();trace=a.trace.resolve();out=a.output.resolve();os.chdir(src);sys.path.insert(0,str(src))
    from rotk_env.runtime.native import RustRuntime
    from star_native import _native
    raw=json.loads(gzip.decompress(trace.read_bytes()));initial=trace.with_name(raw['initial']['file'])
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip()
    assert source==raw['source']['sha']
    assert hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest()==raw['extension']['sha256']
    assert hashlib.sha256(initial.read_bytes()).hexdigest()==raw['initial']['sha256']
    started=time.perf_counter();counts={};failure=None
    with RustRuntime(json.loads(gzip.decompress(initial.read_bytes())),threads=a.threads or raw['threads']) as n:
        n.take_presentation_delta()  # Recorder starts after the session's initial refresh.
        for index,op in enumerate(raw['entries']):
            assert index==op['seq'];kind=op['kind'];counts[kind]=counts.get(kind,0)+1
            if kind=='request':
                if 'integer_string_limit' in op: sys.set_int_max_str_digits(op['integer_string_limit'])
                r=n.execute_action(op['action'],op['parameters'],agent_id=op['agent_id'],wall_time=op['wall_time'],registration_time=op['registration_time'])
                actual=(hashlib.sha256(json.dumps(r,separators=(',',':'),ensure_ascii=False).encode()).hexdigest() if 'response_wire_sha256' in op else digest(r))
                expected=op.get('response_wire_sha256',op.get('response_sha256'))
            elif kind=='step':n.step(op['dt'],wall_time=op['wall_time']);continue
            elif kind=='presentation':actual=digest(n.take_presentation_delta()['events']);expected=op['events_sha256']
            else:raise ValueError(kind)
            if actual!=expected:failure=dict(seq=index,kind=kind,expected=expected,actual=actual);break
        final=digest(n.export_state())
    result=dict(source_sha=source,tool_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=Path(__file__).resolve().parents[2],text=True).strip(),trace_sha256=hashlib.sha256(trace.read_bytes()).hexdigest(),threads=a.threads or raw['threads'],counts=counts,elapsed_seconds=time.perf_counter()-started,failure=failure,expected_final_sha256=raw['final_state_sha256'],actual_final_sha256=final,all_passed=failure is None and final==raw['final_state_sha256'])
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
    if not result['all_passed']:raise SystemExit(1)

if __name__=='__main__':main()
