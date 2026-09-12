"""Record core World.update and lifecycle parity, including ordered events."""
import argparse
import contextlib
import datetime
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback


def git(path,*args):return subprocess.check_output(['git','-C',str(path),*args],text=True).strip()


def run_case(display):
    import pytest
    from framework.engine.events import EBS
    from rotk_env.components import Combat,UnitCount,UnitStatistics,UnitObservation
    from rotk_env.runtime.bootstrap import export_initial_state,encode
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.systems.game_time_system import GameTimeSystem
    from rotk_env.systems.realtime_system import RealtimeSystem
    from rotk_env.systems.window_realtime_system import RealtimeSystem as WindowRealtime
    from rotk_env.systems.statistics_system import StatisticsSystem
    from rotk_env.systems.window_statistics_system import StatisticsSystem as WindowStatistics
    from rotk_env.systems.resource_recovery_system import ResourceRecoverySystem
    from rotk_env.systems.llm_system import LLMSystem
    from rotk_env.tests.test_native_vision import make_vision_world
    now=[1720000000.]
    class Frozen(datetime.datetime):
        @classmethod
        def now(cls,tz=None):return cls(2026,9,12,12)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(time,'time',lambda:now[0]);patch.setattr(datetime,'datetime',Frozen)
        for cls,field in ((UnitStatistics,'creation_time'),(UnitObservation,'last_seen_time')):
            original=cls.__init__
            def initialize(self,*args,_init=original,_field=field,**kwargs):
                _init(self,*args,**kwargs);setattr(self,_field,now[0])
            patch.setattr(cls,'__init__',initialize)
        world,(a,b,c),vision=make_vision_world(display)
        world.add_system(GameTimeSystem())
        world.add_system(WindowStatistics(batch_size=1) if display=='window' else StatisticsSystem())
        world.add_system(ResourceRecoverySystem())
        world.add_system(WindowRealtime() if display=='window' else RealtimeSystem())
        llm=LLMSystem();world.add_system(llm)
        world.get_component(a,Combat).attack_range=5;world.get_component(c,UnitCount).current_count=1
        events=[];publish=EBS.publish
        def capture(event):
            events.append(dict(type=type(event).__name__,fields=encode(event)));publish(event)
        patch.setattr(EBS,'publish',capture)
        initial=export_initial_state(world,display=display)
        case=dict(display=display,initial=initial,operations=[],all_passed=False)
        try:
            with RustRuntime(initial) as native:
                native.take_presentation_delta()
                def record(operation,expected,actual):
                    before=export_initial_state(world,display=display);before['clock']['tick']=native.diagnostics()['clock']['tick']
                    after=native.export_state();actual_events=native.take_presentation_delta()['events']
                    expected=json.loads(json.dumps(expected))
                    guards=dict(response_equal=expected==actual,state_equal=before==after,events_equal=events==actual_events)
                    case['operations'].append(dict(operation=operation,expected=expected,actual=actual,
                        expected_state=before,actual_state=after,expected_events=list(events),actual_events=actual_events,guards=guards))
                    events.clear()
                    if not all(guards.values()):raise AssertionError(f'world operation differs: {operation}')
                def request(agent,verb,params):
                    expected=llm._process_action_request(agent_id=agent,action_id=0,action=verb,params=dict(params),send_response=False)
                    actual=native.execute_action(verb,params,agent_id=agent,wall_time=now[0])
                    record(dict(kind='request',agent_id=agent,action=verb,parameters=params,wall_time=now[0]),expected,actual)
                reg=dict(provider='synthetic',model_id='fake',base_url='https://host')
                request('alpha','register_agent_info',{**reg,'faction':'wei'})
                request('enemy','register_agent_info',{**reg,'faction':'shu'})
                request('alpha','claim_units',{'unit_ids':[a,b]})
                for index in range(120):
                    now[0]+=.25
                    if index==0:
                        request('alpha','move',{'unit_id':a,'target_position':{'col':-2,'row':0}})
                        request('alpha','move',{'unit_id':b,'target_position':{'col':-1,'row':1}})
                    if index==40 and display=='none':request('alpha','attack',{'unit_id':a,'target_id':c})
                    if index in (0,20,40,80,119):request('alpha','get_faction_state',{'faction':'wei'})
                    world.update(1/30);native.step(1/30,wall_time=now[0])
                    record(dict(kind='step',dt=1/30,wall_time=now[0]),None,None)
                    if index==60:
                        native.reset(native.export_state());record(dict(kind='reset-current'),None,None)
                case['all_passed']=all(all(op['guards'].values()) for op in case['operations'])
        except Exception:case['error']=traceback.format_exc()
        finally:world.reset()
        return case


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();source=args.source.resolve();output=args.output.resolve();os.chdir(source);sys.path.insert(0,str(source))
    from star_native import _native
    cases=[]
    for display in ('none','dummy','window'):
        console=io.StringIO()
        with contextlib.redirect_stdout(console),contextlib.redirect_stderr(console):case=run_case(display)
        case['console']=console.getvalue();cases.append(case)
    raw=dict(schema='star-r2-lifecycle-v1',source_sha=git(source,'rev-parse','HEAD'),source_dirty=git(source,'status','--porcelain'),
        tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),python=sys.version,platform=platform.platform(),
        extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),cases=cases)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(gzip.compress(json.dumps(raw,sort_keys=True,separators=(',',':')).encode()+b'\n',mtime=0))
    summary={k:v for k,v in raw.items() if k!='cases'}
    summary['cases']=[dict(display=c['display'],operations=len(c['operations']),
        ticks=sum(op['operation']['kind']=='step' for op in c['operations']),
        event_counts={name:sum(e['type']==name for op in c['operations'] for e in op['actual_events']) for name in ('BattleEvent','UnitDeathEvent','GameOverEvent')},
        all_passed=c['all_passed']) for c in cases]
    summary.update(all_passed=all(c['all_passed'] for c in cases) and not raw['source_dirty'],raw_file=output.name,
        raw_size=output.stat().st_size,raw_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    output.with_name(output.name.removesuffix('.json.gz')+'.summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    if not summary['all_passed']:raise SystemExit(1)

if __name__=='__main__':main()
