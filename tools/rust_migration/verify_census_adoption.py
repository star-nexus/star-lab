"""Default census regression against independent recorded input and old binary.

Run once per binary, compare stream/delta/command/final and edge-probe hashes.
This is correctness evidence, not a timed performance screen.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--extension-dir',type=Path,required=True)
    p.add_argument('--extension-sha256',required=True)
    p.add_argument('--trace',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--baseline-binary',action='store_true')
    a = p.parse_args()
    assert not a.output.exists()
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    sys.path.insert(0,str(a.source));sys.path.insert(0,str(a.extension_dir))
    from star_native import _native
    from rotk_env.runtime.native import RustRuntime
    from p3_local_agents import LocalAgents,Session
    from rotk_env.components import ActionPoints,FogOfWar,HexPosition,UnitCount
    from rotk_env.runtime.bootstrap import export_initial_state
    from rotk_env.tests.test_native_observation import setup
    assert sha(_native.__file__) == a.extension_sha256
    trace = json.loads(gzip.decompress(a.trace.read_bytes()))
    initial_file = a.trace.with_name(trace['initial']['file'])
    assert sha(initial_file) == trace['initial']['sha256']
    initial = json.loads(gzip.decompress(initial_file.read_bytes()))
    consumer = LocalAgents.__new__(LocalAgents)
    consumer.clock=lambda:0.;consumer.policy='stochastic';consumer.rng=random.Random(42)
    consumer.cycle_mode='post-action';consumer.observation_hz=None
    consumer.counts=Counter();consumer.heap=[];consumer.serial=0
    streams = {name:hashlib.sha256() for name in ('responses','wires','deltas','commands')}
    rows=[];counts=Counter();began=time.perf_counter();failure=None;final=None
    with RustRuntime(initial,threads=1) as runtime:
        if a.baseline_binary:
            assert runtime._native._observation_scan_research() == 'baseline'
        else:
            assert not hasattr(runtime._native,'_set_observation_scan_research')
        streams['deltas'].update(digest(runtime.take_presentation_delta()).encode())
        try:
            for index,op in enumerate(trace['entries']):
                assert op['seq']==index
                kind=op['kind'];row=dict(seq=index,kind=kind)
                if kind=='request':
                    if 'integer_string_limit' in op:sys.set_int_max_str_digits(op['integer_string_limit'])
                    if op['action']=='get_faction_state':
                        wire=runtime.get_faction_state_json(**op['parameters'],agent_id=op['agent_id'],wall_time=op['wall_time'])
                        wire_hash=hashlib.sha256(wire.encode()).hexdigest()
                        assert wire_hash==op['response_wire_sha256']
                        result=json.loads(wire);streams['wires'].update(wire_hash.encode())
                        session=Session(op['agent_id'],op['parameters']['faction'],op['parameters'].get('unit_ids') or [],30.)
                        consumer.heap.clear();consumer._consume_observation(result,{},session,0,0.)
                        streams['commands'].update(digest(session.actions).encode())
                        counts['queries']+=1
                    else:
                        result=runtime.execute_action(op['action'],op['parameters'],agent_id=op['agent_id'],wall_time=op['wall_time'],registration_time=op['registration_time'])
                    response_hash=digest(result)
                    if op['action']!='get_faction_state':
                        assert response_hash==op['response_sha256']
                    streams['responses'].update(response_hash.encode());row['sha256']=response_hash
                    counts['requests']+=1
                elif kind=='step':
                    runtime.step(op['dt'],wall_time=op['wall_time']);counts['ticks']+=1
                elif kind=='presentation':
                    delta=runtime.take_presentation_delta()
                    assert digest(delta['events'])==op['events_sha256']
                    row['sha256']=digest(delta);streams['deltas'].update(row['sha256'].encode())
                    counts['presentation']+=1
                else:raise AssertionError(kind)
                counts['operations']+=1;rows.append(row)
            final=digest(runtime.export_state());assert final==trace['final_state_sha256']
        except BaseException as error:
            failure=dict(seq=op.get('seq'),error=repr(error));raise
        finally:
            raw=a.output.with_suffix('.rows.json.gz')
            raw.write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0))
            report=dict(passed=failure is None,failure=failure,counts=dict(counts),
                source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=a.source,text=True).strip(),
                source_dirty=subprocess.check_output(['git','status','--porcelain'],cwd=a.source,text=True).strip(),
                extension_sha256=a.extension_sha256,baseline_binary=a.baseline_binary,
                input_sha256=sha(a.trace),initial_sha256=sha(initial_file),tool_sha256=sha(__file__),
                stream_hashes={k:v.hexdigest() for k,v in streams.items()},final_state_sha256=final,
                raw=dict(file=raw.name,sha256=sha(raw)),elapsed_seconds=time.perf_counter()-began,
                scope='Complete recorded short input, ordinary single-query path, full responses/wire/deltas/events/consumer commands/final state; no live-performance claim',
                performance_claim=False)
            a.output.write_text(json.dumps(report,indent=2)+'\n')
    assert dict(counts)==dict(queries=3010,requests=12148,ticks=2617,presentation=2617,operations=17382)
    # Independent old/default probes cover the missing-component boundaries that
    # changed tests exercise, with all work metrics retained in the projection.
    edges=[]
    for threads in (1,4):
        for fog in (False,True):
            for missing in (None,ActionPoints,HexPosition,UnitCount):
                world,(u,v,enemy),_=setup('window')
                try:
                    world.get_singleton_component(FogOfWar).enabled=fog
                    for unit in (u,v,enemy):
                        world.get_component(unit,UnitCount).current_count=1
                        world.get_component(unit,ActionPoints).current_ap=1
                    if missing:world.remove_component(v,missing)
                    state=export_initial_state(world,display='window')
                    queries=[dict(faction='wei',agent_id='alpha',unit_ids=[v,u,v]),dict(faction='shu',agent_id='enemy'),dict(faction='wu',unit_ids=[])]
                    with RustRuntime(state,threads=threads) as runtime:
                        before=runtime.export_state()
                        result=runtime._native._observation_probe_json(json.dumps(queries))
                        assert before==runtime.export_state()
                        edges.append(dict(threads=threads,fog=fog,missing=None if missing is None else missing.__name__,projection_and_metrics_sha256=hashlib.sha256(result.encode()).hexdigest()))
                finally:world.reset()
    report['edge_probes']=edges
    a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,counts=dict(counts),edge_probes=len(edges))))


if __name__=='__main__':main()
