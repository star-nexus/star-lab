"""Replay a bounded real trace prefix; time native delta encoding and Python decode separately."""
import argparse,gzip,hashlib,json,os,sys,time,subprocess
from pathlib import Path
from native_loop_trace import digest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--trace',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--ticks',type=int,default=2000);a=p.parse_args()
    src=a.source.resolve();trace=a.trace.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);os.chdir(src);sys.path.insert(0,str(src));sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    from p3_local_agents import stats
    from rotk_env.runtime.native import RustRuntime
    from star_native import _native
    raw=json.loads(gzip.decompress(trace.read_bytes()));initial=trace.with_name(raw['initial']['file']);assert hashlib.sha256(initial.read_bytes()).hexdigest()==raw['initial']['sha256']
    rows=[];ticks=0;request_hashes=[]
    with RustRuntime(json.loads(gzip.decompress(initial.read_bytes())),threads=1) as n:
        n.take_presentation_delta()
        for op in raw['entries']:
            if op['kind']=='request':
                r=n.execute_action(op['action'],op['parameters'],agent_id=op['agent_id'],wall_time=op['wall_time'],registration_time=op['registration_time'])
                h=(hashlib.sha256(json.dumps(r,separators=(',',':'),ensure_ascii=False).encode()).hexdigest() if 'response_wire_sha256' in op else digest(r));assert h==op.get('response_wire_sha256',op.get('response_sha256'));request_hashes.append(h)
            elif op['kind']=='step':n.step(op['dt'],wall_time=op['wall_time']);ticks+=1
            else:
                start=time.perf_counter_ns();wire=n._native.take_presentation_delta_json();encoded=time.perf_counter_ns();delta=json.loads(wire);decoded=time.perf_counter_ns()
                assert digest(delta['events'])==op['events_sha256']
                rows.append(dict(tick=ticks,units=len(delta['units']),bytes=len(wire.encode()),native_ms=(encoded-start)/1e6,decode_ms=(decoded-encoded)/1e6,delta_sha256=digest(delta)))
                if ticks>=a.ticks:break
        final=digest(n.export_state())
    source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip();dirty=subprocess.check_output(['git','status','--porcelain'],cwd=src,text=True).strip();assert not dirty
    measured=[r for r in rows if r['tick']>=900]
    assert measured
    artifact=gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0);(out/'rows.json.gz').write_bytes(artifact)
    result=dict(source_sha=source_sha,tool_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=Path(__file__).resolve().parents[2],text=True).strip(),extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),trace_sha256=hashlib.sha256(trace.read_bytes()).hexdigest(),ticks=ticks,requests=len(request_hashes),request_hashes_sha256=digest(request_hashes),final_state_sha256=final,native_ms=stats([r['native_ms'] for r in measured]),decode_ms=stats([r['decode_ms'] for r in measured]),raw_sha256=hashlib.sha256(artifact).hexdigest(),raw_bytes=len(artifact),all_replay_guards_passed=True,capacity_claim=False)
    (out/'compact.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
