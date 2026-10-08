"""E8 single-factor entity scan screen on complete fixed accepted input.

Both sides use the same encoded scopes. Charged service includes open/drop once;
wire return is separately recorded. No live heap/display/network adoption claim.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import random
import sys
import time

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--extension-dir',type=Path,required=True)
    p.add_argument('--trace',type=Path,required=True)
    p.add_argument('--admission',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--extension-sha256',required=True)
    a=p.parse_args();assert not a.output.exists();a.output.parent.mkdir(parents=True,exist_ok=True)
    lab=Path(__file__).resolve().parents[2];sys.path.insert(0,str(lab/'tools'))
    sys.path.insert(0,str(a.source));sys.path.insert(0,str(a.extension_dir))
    from p3_local_agents import LocalAgents,Session
    from rotk_env.runtime.native import RustRuntime
    from star_native import _native
    assert sha(_native.__file__)==a.extension_sha256
    trace=json.loads(gzip.decompress(a.trace.read_bytes()));entries=trace['entries']
    initial_path=a.trace.with_name(trace['initial']['file']);assert sha(initial_path)==trace['initial']['sha256']
    initial=json.loads(gzip.decompress(initial_path.read_bytes()))
    admitted=json.loads(a.admission.read_text());observations=[r for r in admitted['admission'] if r['entry'][2]=='observe']
    queries=[o for o in entries if o.get('action')=='get_faction_state'];assert len(queries)==len(observations)
    serial={};groups={}
    for row,op in zip(observations,queries):
        assert row['params']==op['parameters'];serial[row['entry'][1]]=op['seq']
    for segment in admitted['segments']:
        seqs=[serial[s] for s in segment['executed']]
        if len(seqs)>=2:
            assert 2<=len(seqs)<=4 and seqs==list(range(seqs[0],seqs[-1]+1));groups[seqs[0]]=seqs
    # All operations before a presentation share that enclosing tick/block.
    enclosing={};pending=[];frame=0
    for op in entries:
        pending.append(op['seq'])
        if op['kind']=='presentation':
            frame+=1
            for seq in pending:enclosing[seq]=frame
            pending=[]
    assert not pending
    runtimes=[RustRuntime(initial,threads=1) for _ in range(4)]
    modes=['baseline','entity_ref','entity_ref','baseline']
    for runtime,mode in zip(runtimes,modes):runtime._set_observation_scan_research(mode)
    contexts=[None]*4;scopes=[None]*4;ends=[None]*4;consumers=[];commands=[hashlib.sha256() for _ in range(4)]
    for _ in range(4):
        consumer=LocalAgents.__new__(LocalAgents)
        consumer.clock=lambda:0.;consumer.policy='stochastic';consumer.rng=random.Random(42)
        consumer.cycle_mode='post-action';consumer.observation_hz=None;consumer.counts=Counter();consumer.heap=[];consumer.serial=0
        consumers.append(consumer)
    totals=[0]*4;service=[[] for _ in range(4)];tick_rows=[];query_rows=[];counts=Counter();failure=None;began=time.perf_counter()
    progress=a.output.with_suffix('.progress.json')
    try:
        initial_deltas=[r.take_presentation_delta() for r in runtimes];assert all(v==initial_deltas[0] for v in initial_deltas)
        for op in entries:
            seq=op['seq'];kind=op['kind'];order=[0,1,2,3] if enclosing[seq]%2==0 else [1,0,3,2]
            responses=[None]*4;elapsed=[0]*4;wire_lengths=[0]*4;phases=[None]*4
            for side in order:
                runtime=runtimes[side];start=time.perf_counter_ns();open_ns=drop_ns=0
                if kind=='request':
                    if 'integer_string_limit' in op:sys.set_int_max_str_digits(op['integer_string_limit'])
                    if op['action']=='get_faction_state':
                        if seq in groups:
                            assert contexts[side] is None
                            contexts[side]=runtime._admitted_observation_segment('segment_encoded',diagnostics=False)
                            scopes[side]=contexts[side].__enter__();ends[side]=groups[seq][-1]
                            open_ns=time.perf_counter_ns()-start
                        call=scopes[side].get_faction_state_json if scopes[side] else runtime.get_faction_state_json
                        native_start=time.perf_counter_ns()
                        wire=call(**op['parameters'],agent_id=op['agent_id'],wall_time=op['wall_time'])
                        native_end=time.perf_counter_ns();payload=wire.encode();bytes_end=time.perf_counter_ns();decoded=json.loads(payload);decode_end=time.perf_counter_ns()
                        session=Session(op['agent_id'],op['parameters']['faction'],op['parameters'].get('unit_ids') or [],30.)
                        consumer=consumers[side];consumer.heap.clear()
                        consumer._consume_observation(decoded,{},session,0,0.);consume_end=time.perf_counter_ns()
                        if contexts[side] is not None and seq==ends[side]:
                            contexts[side].__exit__(None,None,None);contexts[side]=scopes[side]=None;ends[side]=None
                            drop_ns=time.perf_counter_ns()-consume_end
                        elapsed[side]=time.perf_counter_ns()-start
                        service[side].append(elapsed[side]);responses[side]=wire;wire_lengths[side]=len(payload)
                        phases[side]=dict(open_ns=open_ns,wire_interval_ns=native_end-native_start,bytes_ns=bytes_end-native_end,decode_ns=decode_end-bytes_end,consume_ns=consume_end-decode_end,drop_ns=drop_ns)
                        phases[side]['host_overhead_ns']=elapsed[side]-sum(phases[side].values())
                        assert phases[side]['host_overhead_ns']>=0
                        commands[side].update(digest(session.actions).encode())
                    else:
                        assert contexts[side] is None
                        responses[side]=runtime.execute_action(op['action'],op['parameters'],agent_id=op['agent_id'],wall_time=op['wall_time'],registration_time=op['registration_time'])
                        elapsed[side]=time.perf_counter_ns()-start
                elif kind=='step':
                    assert contexts[side] is None
                    runtime.step(op['dt'],wall_time=op['wall_time']);elapsed[side]=time.perf_counter_ns()-start
                elif kind=='presentation':
                    assert contexts[side] is None
                    responses[side]=runtime.take_presentation_delta();elapsed[side]=time.perf_counter_ns()-start
                else:raise AssertionError(kind)
                totals[side]+=elapsed[side]
            assert all(r==responses[0] for r in responses)
            if kind=='request':
                counts['requests']+=1
                if op['action']=='get_faction_state':
                    assert hashlib.sha256(responses[0].encode()).hexdigest()==op['response_wire_sha256']
                    assert wire_lengths.count(wire_lengths[0])==4
                    query_rows.append(dict(seq=seq,tick=enclosing[seq],service_ns=elapsed,phases=phases,bytes=wire_lengths[0],role='segment_first' if seq in groups else 'segment_later' if any(seq in ids[1:] for ids in groups.values()) else 'singleton'));counts['queries']+=1
                else:assert digest(responses[0])==op['response_sha256']
            elif kind=='step':counts['ticks']+=1
            else:
                assert digest(responses[0]['events'])==op['events_sha256'];counts['presentation']+=1
                assert counts['ticks']==enclosing[seq]
                tick_rows.append(dict(tick=enclosing[seq],total_ns=totals));totals=[0]*4
            counts['operations']+=1
            if seq%1000==0:progress.write_text(json.dumps(dict(status='running',seq=seq,total=len(entries),counts=counts,elapsed_s=time.perf_counter()-began))+'\n')
        assert totals==[0]*4 and len(tick_rows)==counts['presentation']
        if not a.smoke:assert counts['presentation']==counts['ticks']
        finals=[digest(r.export_state()) for r in runtimes];assert finals==[trace['final_state_sha256']]*4
        assert len({h.hexdigest() for h in commands})==1
    except BaseException as error:
        failure=repr(error);raise
    finally:
        for context in contexts:
            if context:context.__exit__(*sys.exc_info())
        for runtime in runtimes:runtime.close()
        raw=a.output.with_suffix('.samples.json.gz');raw.write_bytes(gzip.compress(json.dumps(dict(queries=query_rows,ticks=tick_rows),separators=(',',':')).encode(),mtime=0))
        a.output.write_text(json.dumps(dict(passed=failure is None,failure=failure,counts=dict(counts),elapsed_s=time.perf_counter()-began,
            input_sha256=sha(a.trace),admission_sha256=sha(a.admission),extension_sha256=sha(_native.__file__),
            raw=dict(file=raw.name,sha256=sha(raw)),tool_sha256=sha(__file__),consumer_sha256=sha(lab/'tools/p3_local_agents.py'),
            commands_sha256=[h.hexdigest() for h in commands],smoke=a.smoke,
            modes=modes,cache_mode='segment_encoded on both sides',scope_open_count=[len(groups)]*4,scope_drop_count=[len(groups)]*4,source_sha=__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=a.source,text=True).strip(),pairing='Four persistent worlds, per-tick alternating ABBA/BAAB',
            workload='Complete accepted input including warm and all tails; fixed fresh-session deterministic consumer at each query, not original host callback/deadline replay',
            scope='Moving-world scan service screen only (open/drop charged exactly once); excludes live heap admission scan and display apply/render/submit',
            formal_acceptance=False,default_adoption=False),indent=2)+'\n')
        print(json.dumps(dict(passed=failure is None,counts=counts,failure=failure)),flush=True)

if __name__=='__main__':main()
