"""Native rule-mode integration diagnostic; not a rendered 30Hz capacity gate."""
import argparse
import contextlib
import datetime
import gc
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import resource
import sys
import time
import traceback


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def write_gzip(path,value):
    with path.open('wb') as raw, gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as zipped:
        with io.TextIOWrapper(zipped,encoding='utf-8') as text:
            json.dump(value,text,sort_keys=True,separators=(',',':'),allow_nan=False)
            text.write('\n')
    return dict(file=path.name,size=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--units',type=int,default=5000);p.add_argument('--agents',type=int,default=1000)
    p.add_argument('--seconds',type=float,default=60);p.add_argument('--fps',type=int,default=30)
    p.add_argument('--threads',type=int,choices=(1,2,4),default=1);p.add_argument('--budget-ms',type=float,default=18)
    args=p.parse_args();source=args.source.resolve();output=args.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
    if args.seconds<=0 or args.fps<=0 or args.units<3 or args.agents<3:p.error('positive duration/FPS and at least three Units/Agents required')
    sys.path.insert(0,str(source));sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    from p3_local_agents import LocalAgents,fixture,identity,stats
    from rotk_env.prefabs.world_builder import build_skirmish_world
    from rotk_env.prefabs.config import Faction,PlayerType
    from rotk_env.runtime.bootstrap import export_initial_state
    from rotk_env.runtime.native import RustRuntime
    from star_native import _native
    source_id=identity(source);tool_id=identity(Path(__file__).resolve().parents[2])
    if source_id['dirty']:raise RuntimeError('use a clean source checkout for a recorded run')
    os.chdir(source)
    native=None;world=None;trace=[];frames=[];censuses=[];agents=None;error=None
    scene_file=None;initial_artifact=None;final_digest=None
    def record(kind,**fields):trace.append(dict(seq=len(trace),kind=kind,**fields))
    class NativeAgents(LocalAgents):
        def call(self,session,verb,params):
            self.request_id+=1
            wall=time.time();registration=datetime.datetime.now().isoformat() if verb=='register_agent_info' else None
            response=native.execute_action(verb,params,agent_id=session.agent_id,wall_time=wall,registration_time=registration)
            record('request',agent_id=session.agent_id,action=verb,parameters=params,wall_time=wall,
                   registration_time=registration,response_sha256=digest(response),success=response.get('success'))
            return response
    setup_start=time.perf_counter()
    try:
        scenario,fixture_sha=fixture(source,args.units,'canonical')
        scene_file=source/'rotk_env/maps'/f'{scenario}.json'
        world=build_skirmish_world(players={f:PlayerType.AI for f in Faction},mode='real_time',
            scenario=scenario,seed=42,display='none',hub_url=None,enable_mock_ai=False)
        initial=export_initial_state(world,display='none')
        initial_artifact=write_gzip(output.with_name(output.stem+'.initial.json.gz'),initial)
        native=RustRuntime(initial,threads=args.threads)
        del initial
        agents=NativeAgents(world,args.agents,30.,scope='selected',encode=True,policy='stochastic',
                           observation_mode='single',cycle_mode='post-action',jitter_seconds=5.)
        # LocalAgents uses the Python world only for initial allocation. All later
        # interactions go through the native API; remove every retained ECS handle.
        agents.world=None;agents.gate=None;world.reset();world=None
        scene_file.unlink();scene_file=None
        native.take_presentation_delta();gc.collect()
        setup_seconds=time.perf_counter()-setup_start
        if native.diagnostics()['living_units']!=args.units:raise AssertionError('wrong initial native resident count')
        start=time.perf_counter();deadline=start;agents.start(start)
        cpu_start=time.process_time();last_census=-1
        while time.perf_counter()-start<args.seconds:
            began=time.perf_counter();agents.pump(args.budget_ms);agent_end=time.perf_counter()
            wall=time.time();native.step(1/args.fps,wall_time=wall)
            record('step',dt=1/args.fps,wall_time=wall)
            stepped=time.perf_counter();delta=native.take_presentation_delta();presented=time.perf_counter()
            elapsed=began-start
            if int(elapsed)!=last_census:
                diag=native.diagnostics();last_census=int(elapsed)
                census=dict(t=elapsed,living=diag['living_units'],moving=diag['moving_units'],
                    clock=diag['clock'],counts=dict(agents.counts),maxrss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
                censuses.append(census)
                if last_census%10==0:print(json.dumps(census),flush=True)
            end=time.perf_counter()
            frames.append(dict(t=elapsed,dt=1/args.fps,work_ms=(end-began)*1000,
                agent_ms=(agent_end-began)*1000,step_ms=(stepped-agent_end)*1000,
                delta_ms=(presented-stepped)*1000,delta_units=len(delta['units']),game_events=delta['events']))
            if len(frames)>=20000:raise RuntimeError('bounded frame recorder exhausted')
            deadline=max(deadline+1/args.fps,end)
            remaining=deadline-time.perf_counter()
            if remaining>0:time.sleep(remaining)
        elapsed=time.perf_counter()-start;cpu_seconds=time.process_time()-cpu_start
        agent_summary=agents.summary();diag=native.diagnostics();final_digest=digest(native.export_state())
        guards=dict(completed=elapsed>=args.seconds,initial_residents=censuses[0]['living']==args.units,
            survives=all(c['living']>=args.units*.95 for c in censuses) and diag['living_units']>=args.units*.95,
            all_agents_interacted=min(s.completed for s in agents.sessions)>=1,
            accepted_moves=agents.counts['move_accepted']>0,accepted_attacks=agents.counts['attack_accepted']>0,
            fixed_clock=abs(diag['clock']['elapsed']-len(frames)/args.fps)<1e-6,
            clean_source=not identity(source)['dirty'])
    except Exception:
        error=traceback.format_exc();guards={'complete':False}
    finally:
        if world is not None:world.reset()
        if native is not None:native.close()
        if scene_file is not None and scene_file.exists():scene_file.unlink()
    raw=dict(schema='star-r2-native-rule-loop-v1',source=source_id,tool=tool_id,platform=platform.platform(),python=sys.version,
        extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),initial=initial_artifact,
        fixture_sha256=locals().get('fixture_sha'),configuration=vars(args)|{'source':str(source),'output':str(output)},
        initial_offset='uniform(0,30)',thinking='truncated normal(30,5), range15..45; wall clock, no polling',
        actions='per-unit move/attack/wait=.5/.25/.25, illegal waits, no redraw',
        display='none; instantaneous movement, no render or visual combat',
        timing_scope='client scheduling/JSON + native step + presentation delta + trace digest; no rendering',
        trace=trace,frames=frames,censuses=censuses,agent_records=[] if agents is None else agents.records,
        agent_summary=locals().get('agent_summary'),setup_seconds=locals().get('setup_seconds'),
        elapsed=locals().get('elapsed'),cpu_seconds=locals().get('cpu_seconds'),final_state_sha256=final_digest,
        guards=guards,all_passed=all(guards.values()) and error is None,error=error)
    artifact=write_gzip(output,raw)
    compact={k:v for k,v in raw.items() if k not in ('trace','frames','agent_records','censuses')}
    compact.update(raw=artifact,frames=len(frames),requests=sum(r['kind']=='request' for r in trace),
        loop_work_ms=stats([f['work_ms'] for f in frames]),step_ms=stats([f['step_ms'] for f in frames]),
        alive_min=min((c['living'] for c in censuses),default=None),actual_world_hz=len(frames)/elapsed if frames and error is None else None,
        conclusion='Rule-mode integration diagnostic only. No rendered frame or 30Hz capacity acceptance.')
    output.with_name(output.stem+'.summary.json').write_text(json.dumps(compact,indent=2)+'\n')
    print(json.dumps(compact,indent=2))
    if not raw['all_passed']:raise SystemExit(1)

if __name__=='__main__':main()
