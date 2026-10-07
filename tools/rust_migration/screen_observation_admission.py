"""E8 P1 short same-input service screen, one world per process.

Includes private scope open/drop, owned wire->bytes, complete client decoding
and the frozen LocalAgents consumer. This is a representative static screening
workload, not a formal accepted queue replay or runtime capacity gate.
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

LAB=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(LAB/'tools'))
from p3_local_agents import LocalAgents, Session


def digest(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--p0',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--mode',choices=['single','segment_no_reuse','segment_encoded'],required=True)
    p.add_argument('--cycles',type=int,default=30)
    p.add_argument('--diagnostics',action='store_true')
    p.add_argument('--extension-dir',type=Path)
    a=p.parse_args();assert not a.output.exists()
    sys.path.insert(0,str(a.source))
    if a.extension_dir:sys.path.insert(0,str(a.extension_dir))
    from rotk_env.runtime.native import RustRuntime
    from star_native import _native
    initial=json.loads(gzip.decompress((a.p0/'window.initial.json.gz').read_bytes()))
    trace=json.loads(gzip.decompress((a.p0/'window.trace.json.gz').read_bytes()))
    cost=json.loads((a.p0/'cost-normalized.json').read_text())
    cases={}
    for sample in cost['profiles']:cases.setdefault(sample['kind'],sample['parameters'])
    assert len(cases)==7
    consumer=LocalAgents.__new__(LocalAgents)
    consumer.clock=time.perf_counter;consumer.policy='stochastic';consumer.rng=random.Random(42)
    consumer.cycle_mode='post-action';consumer.observation_hz=None;consumer.counts=Counter()
    consumer.heap=[];consumer.serial=0
    samples=[];diagnostics=[];response_hash=hashlib.sha256();commands_hash=hashlib.sha256()
    ordinal=0
    with RustRuntime(initial,threads=1) as runtime:
        runtime.take_presentation_delta()
        for op in trace['entries']:
            if op['kind']=='request' and op['action']=='get_faction_state':break
            if op['kind']=='request':
                runtime.execute_action(op['action'],op['parameters'],agent_id=op['agent_id'],wall_time=op['wall_time'],registration_time=op['registration_time'])
            elif op['kind']=='step':runtime.step(op['dt'],wall_time=op['wall_time'])
            elif op['kind']=='presentation':runtime.take_presentation_delta()
            else:raise AssertionError(op['kind'])
        prepared=digest(runtime.export_state())
        for cycle in range(a.cycles):
            for kind,params in sorted(cases.items()):
                sessions=[Session(q['agent_id'],q['faction'],q['unit_ids'],30.) for q in params]
                consumer.heap.clear()
                began=time.perf_counter_ns();opened=0;closed=0;context=None;scope=None
                if a.mode!='single' and len(params)>=2:
                    context=runtime._admitted_observation_segment(a.mode,diagnostics=a.diagnostics)
                    scope=context.__enter__()
                opened=time.perf_counter_ns()-began
                per_query=[];wires=[];commands=[]
                try:
                    for q,session in zip(params,sessions):
                        qbegin=time.perf_counter_ns()
                        call=scope.get_faction_state_json if scope else runtime.get_faction_state_json
                        wire=call(q['faction'],unit_ids=q['unit_ids'],agent_id=q['agent_id'],wall_time=1720000000.+ordinal)
                        payload=wire.encode();response=json.loads(payload)
                        assert response['success']
                        row={}
                        consumer._consume_observation(response,row,session,0,0.)
                        elapsed=time.perf_counter_ns()-qbegin
                        per_query.append(elapsed);wires.append(payload);commands.append(session.actions)
                        ordinal+=1
                finally:
                    finish=time.perf_counter_ns()
                    if context:context.__exit__(None,None,None)
                    closed=time.perf_counter_ns()-finish
                work=time.perf_counter_ns()-began
                per_query[0]+=opened;per_query[-1]+=closed
                for wire,actions in zip(wires,commands):
                    response_hash.update(wire);commands_hash.update(digest(actions).encode())
                samples.append(dict(cycle=cycle,kind=kind,query_service_ns=per_query,segment_work_ns=work,open_ns=opened,close_ns=closed,bytes=[len(x) for x in wires]))
                if scope and a.diagnostics:diagnostics.append(dict(cycle=cycle,kind=kind,report=context.report))
        final=digest(runtime.export_state())
    result=dict(stage='P1 representative screen only',mode=a.mode,diagnostic=a.diagnostics,
        source_sha=subprocess.check_output(['git','-C',str(a.source),'rev-parse','HEAD'],text=True).strip(),
        extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),
        prepared_state_sha256=prepared,final_state_sha256=final,
        response_stream_sha256=response_hash.hexdigest(),commands_sha256=commands_hash.hexdigest(),
        requests=ordinal,cycles=a.cycles,samples=samples,diagnostics=diagnostics,
        consumer_counts=dict(consumer.counts),capacity_claim=False,
        excludes='host prefix scan and full moving-world/order/budget replay; not P2/P3 acceptance')
    a.output.write_text(json.dumps(result,separators=(',',':'))+'\n')
    print(json.dumps(dict(mode=a.mode,queries=ordinal,diagnostic=a.diagnostics,completed=True)),flush=True)


if __name__=='__main__':main()
