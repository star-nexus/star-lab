"""E8 streaming correctness oracle against the independently frozen E7 binary.

Full authority at every non-observation request and every step; per-query small
accounting snapshots; full presentation deltas. No history of Worlds is kept.
Canonical contiguous runs exercise cache semantics, not admission eligibility.
P0 runs use their recorded accepted segment identities instead.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
from threading import RLock
import sys
import time


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--trace',type=Path,required=True)
    p.add_argument('--baseline-extension',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--admission',type=Path)
    p.add_argument('--mode',choices=['single','segment_no_reuse','segment_encoded'],required=True)
    p.add_argument('--threads',type=int,choices=[1,4],default=1)
    a=p.parse_args();assert not a.output.exists()
    sys.path.insert(0,str(a.source))
    from rotk_env.runtime.native import RustRuntime
    from star_native import _native
    assert hashlib.sha256(a.baseline_extension.read_bytes()).hexdigest()=='838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544'
    spec=importlib.util.spec_from_file_location('e8_frozen_reference._native',a.baseline_extension)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    trace=json.loads(gzip.decompress(a.trace.read_bytes()))
    initial_path=a.trace.with_name(trace['initial']['file'])
    assert hashlib.sha256(initial_path.read_bytes()).hexdigest()==trace['initial']['sha256']
    initial=json.loads(gzip.decompress(initial_path.read_bytes()))
    entries=trace['entries']
    groups={}
    if a.admission:
        admitted=json.loads(a.admission.read_text())
        observed=[r for r in admitted['admission'] if r['entry'][2]=='observe']
        queries=[op for op in entries if op['kind']=='request' and op['action']=='get_faction_state']
        assert len(queries)==len(observed)
        serial={}
        for op,row in zip(queries,observed):
            assert op['parameters']==row['params'];serial[row['entry'][1]]=op['seq']
        for segment in admitted['segments']:
            seqs=[serial[s] for s in segment['executed']]
            if len(seqs)>=2:groups[seqs[0]]=seqs
    else:
        seqs=[]
        for op in entries+[dict(kind='end')]:
            if op['kind']=='request' and op['action']=='get_faction_state':
                seqs.append(op['seq'])
            else:
                for start in range(0,len(seqs),4):
                    block=seqs[start:start+4]
                    if len(block)>=2:groups[block[0]]=block
                seqs=[]
    for seqs in groups.values():
        assert 2<=len(seqs)<=4 and seqs==list(range(seqs[0],seqs[-1]+1)), 'No crossing native barriers'
    reference=RustRuntime.__new__(RustRuntime)
    reference._admission_lock=RLock();reference._native=module.NativeRuntime(json.dumps(initial,allow_nan=False),a.threads)
    candidate=RustRuntime(initial,threads=a.threads)
    counts=Counter();state_stream=hashlib.sha256();response_stream=hashlib.sha256()
    started=time.perf_counter();context=None;scope=None;group=None;snapshots=[]
    raw=a.output.with_suffix('.checks.jsonl');raw.parent.mkdir(parents=True,exist_ok=True)
    progress=a.output.with_suffix('.progress.json')
    def authority():
        old=reference._native.export_state_json();new=candidate._native.export_state_json()
        if old!=new:
            assert json.loads(old)==json.loads(new),'Authority differs (not just JSON spelling)'
        h=hashlib.sha256(old.encode()).hexdigest();state_stream.update(h.encode())
        counts['full_authority_checkpoints']+=1
        return h
    failure=None
    try:
        assert reference.take_presentation_delta()==candidate.take_presentation_delta()
        with raw.open('w') as out:
            for op in entries:
                seq=op['seq'];kind=op['kind'];row=dict(seq=seq,kind=kind)
                if seq in groups and a.mode!='single':
                    assert scope is None
                    group=groups[seq];snapshots=[]
                    context=candidate._admitted_observation_segment(a.mode,diagnostics=True)
                    scope=context.__enter__();counts['segments']+=1
                if kind=='request':
                    if 'integer_string_limit' in op:sys.set_int_max_str_digits(op['integer_string_limit'])
                    if op['action']=='get_faction_state':
                        kwargs=dict(op['parameters'],agent_id=op['agent_id'],wall_time=op['wall_time'])
                        old=reference.get_faction_state_json(**kwargs)
                        new=(scope.get_faction_state_json if scope else candidate.get_faction_state_json)(**kwargs)
                        assert old==new,'Complete observation wire differs'
                        assert hashlib.sha256(old.encode()).hexdigest()==op['response_wire_sha256']
                        response_stream.update(old.encode());counts['queries']+=1
                        if scope:
                            stats=reference.export_state()['singletons'].get('GameStats',{})
                            meta=reference.diagnostics();agent=op['agent_id'];faction=stats.get('agent_id_to_faction',{}).get(agent)
                            snapshots.append(dict(wall_time=op['wall_time'],epoch=meta['epoch'],revision=meta['revision'],
                                agent=agent,registered_faction=faction,agent_actions=stats.get('action_count_by_agent',{}).get(agent),
                                faction_actions=stats.get('action_count_by_faction',{}).get(faction)))
                        else:
                            # Singletons cannot exercise a cache; still verify
                            # complete authority, including query accounting.
                            row['authority_sha256']=authority()
                        if scope and seq==group[-1]:
                            context.__exit__(None,None,None)
                            assert context.report is not None
                            assert [r['accounting_after_request'] for r in context.report['query_diagnostics']]==snapshots
                            counts['query_accounting_snapshots']+=len(snapshots)
                            row['segment_diagnostics']=context.report
                            context=None;scope=None;group=None
                            row['authority_sha256']=authority()
                    else:
                        assert scope is None,'Query scope crossed a native barrier'
                        kwargs=dict(agent_id=op['agent_id'],wall_time=op['wall_time'],registration_time=op['registration_time'])
                        old=reference.execute_action(op['action'],op['parameters'],**kwargs)
                        new=candidate.execute_action(op['action'],op['parameters'],**kwargs)
                        assert old==new,'Action response differs'
                        assert digest(old)==op['response_sha256']
                        row['response_sha256']=digest(old);response_stream.update(row['response_sha256'].encode())
                        row['authority_sha256']=authority()
                    counts['requests']+=1
                elif kind=='step':
                    assert scope is None
                    reference.step(op['dt'],wall_time=op['wall_time']);candidate.step(op['dt'],wall_time=op['wall_time'])
                    row['authority_sha256']=authority();counts['ticks']+=1
                elif kind=='presentation':
                    assert scope is None
                    old=reference.take_presentation_delta();new=candidate.take_presentation_delta()
                    assert old==new,'Full presentation delta differs'
                    assert digest(old['events'])==op['events_sha256']
                    row['full_delta_sha256']=digest(old);counts['presentation']+=1
                else:raise AssertionError(kind)
                counts['operations']+=1
                out.write(json.dumps(row,separators=(',',':'))+'\n')
                if seq%500==0:
                    out.flush();progress.write_text(json.dumps(dict(status='running',seq=seq,total=len(entries),counts=counts,elapsed_s=time.perf_counter()-started))+'\n')
            final=digest(reference.export_state());assert final==digest(candidate.export_state())==trace['final_state_sha256']
    except BaseException as e:
        failure=dict(seq=op['seq'] if 'op' in locals() else None,error=repr(e))
        raise
    finally:
        if context:context.__exit__(*sys.exc_info())
        candidate.close();reference.close()
        report=dict(stage='P2 correctness only',passed=failure is None,mode=a.mode,threads=a.threads,
            input_sha256=hashlib.sha256(a.trace.read_bytes()).hexdigest(),counts=dict(counts),failure=failure,
            source_extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),
            baseline_extension_sha256=hashlib.sha256(a.baseline_extension.read_bytes()).hexdigest(),
            full_authority_scope='Every non-query request and step, plus singleton/segment-end queries; per-query small snapshots inside scopes',
            admission_scope='P0 recorded admitted segments' if a.admission else 'Canonical world-sequence runs only; not host admission proof',
            state_checkpoint_stream_sha256=state_stream.hexdigest(),response_stream_sha256=response_stream.hexdigest(),
            raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest() if raw.exists() else None,
            elapsed_s=time.perf_counter()-started,performance_claim=False,default_adoption=False)
        a.output.write_text(json.dumps(report,indent=2)+'\n')
        progress.write_text(json.dumps(dict(status='passed' if not failure else 'failed',counts=counts,failure=failure))+'\n')
        print(json.dumps(dict(passed=not failure,counts=counts,failure=failure)),flush=True)


if __name__=='__main__':main()
