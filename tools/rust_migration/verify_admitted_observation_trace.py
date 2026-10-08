"""E8 actual recorded admission: full wire/delta/order plus periodic authority.

Canonical full authority is a separate prerequisite. This input proves the
recorded accepted segment identities, not realtime budgets or capacity. Keeps
one independent-old runtime and two current runtimes, no history of Worlds.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from threading import RLock
import time

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--extension-dir',type=Path,required=True)
    p.add_argument('--baseline-extension',type=Path,required=True)
    p.add_argument('--trace',type=Path,required=True)
    p.add_argument('--admission',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--threads',type=int,choices=[1,4],default=1)
    a=p.parse_args();assert not a.output.exists()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(a.source));sys.path.insert(0,str(a.extension_dir))
    from rotk_env.runtime.native import RustRuntime
    from star_native import _native
    assert sha(_native.__file__)=='9bb2fa4412bc810fbd751c42f525614f8cddb42e8c136612a51495fa0679f0d9'
    assert sha(a.baseline_extension)=='838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544'
    spec=importlib.util.spec_from_file_location('e8_frozen_reference._native',a.baseline_extension)
    old_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(old_module)
    trace=json.loads(gzip.decompress(a.trace.read_bytes()));entries=trace['entries']
    initial_path=a.trace.with_name(trace['initial']['file'])
    assert sha(initial_path)==trace['initial']['sha256']
    initial=json.loads(gzip.decompress(initial_path.read_bytes()))
    admitted=json.loads(a.admission.read_text())
    observations=[r for r in admitted['admission'] if r['entry'][2]=='observe']
    queries=[o for o in entries if o.get('action')=='get_faction_state']
    assert len(observations)==len(queries)
    serial={};groups={}
    for row,op in zip(observations,queries):
        assert row['params']==op['parameters'];serial[row['entry'][1]]=op['seq']
    for segment in admitted['segments']:
        seqs=[serial[s] for s in segment['executed']]
        if len(seqs)>=2:
            assert 2<=len(seqs)<=4 and seqs==list(range(seqs[0],seqs[-1]+1))
            assert seqs[0] not in groups;groups[seqs[0]]=seqs
    old=RustRuntime.__new__(RustRuntime);old._admission_lock=RLock()
    old._native=old_module.NativeRuntime(json.dumps(initial,allow_nan=False),a.threads)
    witness=RustRuntime(initial,threads=a.threads);new=RustRuntime(initial,threads=a.threads)
    started=time.perf_counter();counts=Counter();context=scope=group=None;snapshots=[];failure=None
    stream=hashlib.sha256();raw=a.output.with_suffix('.checks.jsonl');progress=a.output.with_suffix('.progress.json')
    def authority():
        left=old._native.export_state_json();right=new._native.export_state_json()
        assert left==right or json.loads(left)==json.loads(right)
        counts['full_authority_checkpoints']+=1
        return hashlib.sha256(left.encode()).hexdigest()
    try:
        assert old.take_presentation_delta()==witness.take_presentation_delta()==new.take_presentation_delta()
        initial_hash=authority()
        with raw.open('w') as out:
            for op in entries:
                seq=op['seq'];kind=op['kind'];row=dict(seq=seq,kind=kind)
                if seq in groups:
                    assert scope is None;group=groups[seq];snapshots=[]
                    context=new._admitted_observation_segment('segment_encoded',diagnostics=True)
                    scope=context.__enter__();counts['segments']+=1
                if kind=='request':
                    if 'integer_string_limit' in op:sys.set_int_max_str_digits(op['integer_string_limit'])
                    if op['action']=='get_faction_state':
                        kwargs=dict(op['parameters'],agent_id=op['agent_id'],wall_time=op['wall_time'])
                        left=old.get_faction_state_json(**kwargs)
                        if scope:
                            with witness._admitted_observation_segment('segment_no_reuse',max_requests=2,diagnostics=True) as probe:
                                control=probe.get_faction_state_json(**kwargs)
                            snapshot=probe.report['query_diagnostics'][0]['accounting_after_request']
                            if snapshot['registered_faction'] is not None:
                                assert type(snapshot['agent_actions']) is int and type(snapshot['faction_actions']) is int
                            snapshots.append(snapshot)
                        else:control=witness.get_faction_state_json(**kwargs)
                        right=(scope.get_faction_state_json if scope else new.get_faction_state_json)(**kwargs)
                        assert left==control==right and hashlib.sha256(left.encode()).hexdigest()==op['response_wire_sha256']
                        row['response_wire_sha256']=hashlib.sha256(left.encode()).hexdigest();counts['queries']+=1
                        if scope and seq==group[-1]:
                            context.__exit__(None,None,None)
                            assert [x['accounting_after_request'] for x in context.report['query_diagnostics']]==snapshots
                            counts['scoped_query_accounting_snapshots']+=len(snapshots)
                            row['segment_diagnostics']=context.report;context=scope=group=None
                    else:
                        assert scope is None
                        kwargs=dict(agent_id=op['agent_id'],wall_time=op['wall_time'],registration_time=op['registration_time'])
                        left=old.execute_action(op['action'],op['parameters'],**kwargs)
                        control=witness.execute_action(op['action'],op['parameters'],**kwargs)
                        right=new.execute_action(op['action'],op['parameters'],**kwargs)
                        assert left==control==right and digest(left)==op['response_sha256']
                        row['response_sha256']=digest(left)
                    counts['requests']+=1
                elif kind=='step':
                    assert scope is None
                    for runtime in (old,witness,new):runtime.step(op['dt'],wall_time=op['wall_time'])
                    counts['ticks']+=1
                    if counts['ticks']%100==0:row['authority_sha256']=authority()
                elif kind=='presentation':
                    assert scope is None
                    left=old.take_presentation_delta();control=witness.take_presentation_delta();right=new.take_presentation_delta()
                    assert left==control==right and digest(left['events'])==op['events_sha256']
                    row['full_delta_sha256']=digest(left);counts['presentation']+=1
                else:raise AssertionError(kind)
                counts['operations']+=1;encoded=json.dumps(row,separators=(',',':'))
                out.write(encoded+'\n');stream.update(encoded.encode())
                if seq%1000==0:
                    out.flush();progress.write_text(json.dumps(dict(status='running',seq=seq,total=len(entries),counts=counts,elapsed_s=time.perf_counter()-started))+'\n')
            final=digest(old.export_state())
            assert final==digest(witness.export_state())==digest(new.export_state())==trace['final_state_sha256']
            counts['full_authority_checkpoints']+=1
    except BaseException as e:
        failure=dict(seq=op['seq'] if 'op' in locals() else None,error=repr(e));raise
    finally:
        if context:context.__exit__(*sys.exc_info())
        for runtime in (old,witness,new):runtime.close()
        report=dict(passed=failure is None,failure=failure,mode='segment_encoded',threads=a.threads,counts=dict(counts),
            elapsed_s=time.perf_counter()-started,input_sha256=sha(a.trace),admission_sha256=sha(a.admission),
            source_extension_sha256=sha(_native.__file__),baseline_extension_sha256=sha(a.baseline_extension),tool_sha256=sha(__file__),
            raw_sha256=sha(raw) if raw.exists() else None,checks_stream_sha256=stream.hexdigest(),
            final_state_sha256=final if 'final' in locals() else None,
            authority_scope='Initial, every 100 steps, final; canonical exact world-write/step authority is a separate prerequisite',
            accounting_scope='Every actual scoped query: actual candidate metadata/counts versus lightweight current no-reuse witness; singleton authority covered by canonical and final',
            admission_scope='Frozen recorded accepted segment serials; no realtime pump budget or production network capacity claim',
            performance_claim=False,default_adoption=False)
        a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=failure is None,counts=counts,failure=failure)),flush=True)

if __name__=='__main__':main()
