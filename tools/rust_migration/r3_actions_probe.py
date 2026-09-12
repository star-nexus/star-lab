"""R3 unit actions, capture lifecycle, and turn handoff: exact Python/native traces."""
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
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def run_case(family,display,mode,threads):
    import pytest
    from framework.engine.events import EBS
    from rotk_env.components import Combat,UnitCount,UnitStatistics,UnitObservation,GameState,UnitStatus,FogOfWar
    from rotk_env.prefabs.config import GameMode,UnitState
    from rotk_env.runtime.bootstrap import export_initial_state,encode
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.tests.test_native_unit_actions import setup as action_setup
    from rotk_env.tests.test_native_turn import setup as turn_setup
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
        if family=='actions':
            world,(a,b,c),territory,llm=action_setup(display,GameMode(mode))
            world.get_component(a,Combat).attack_range=5
            world.get_component(c,UnitCount).current_count=1
            world.get_component(a,UnitStatus).current_status=UnitState.CONFUSION
            world.get_singleton_component(FogOfWar).enabled=False
        else:world,(a,b,c),turn,llm=turn_setup(display)
        events=[];publish=EBS.publish
        def capture(event):
            events.append(dict(type=type(event).__name__,fields=encode(event)));publish(event)
        patch.setattr(EBS,'publish',capture)
        initial=export_initial_state(world,display=display)
        case=dict(family=family,display=display,mode=mode,threads=threads,initial=initial,operations=[],all_passed=False)
        try:
            with RustRuntime(initial,threads=threads) as native:
                native.take_presentation_delta()
                def record(operation,expected,actual):
                    before=export_initial_state(world,display=display);before['clock']['tick']=native.diagnostics()['clock']['tick']
                    after=native.export_state();actual_events=native.take_presentation_delta()['events']
                    expected=json.loads(json.dumps(expected))
                    guards=dict(response_equal=expected==actual,state_equal=before==after,events_equal=events==actual_events)
                    case['operations'].append(dict(operation=operation,expected=expected,actual=actual,
                        expected_state=before,actual_state=after,expected_events=list(events),actual_events=actual_events,guards=guards))
                    events.clear()
                    if not all(guards.values()):raise AssertionError(f'operation differs: {operation}')
                def request(agent,verb,params):
                    expected=llm._process_action_request(agent_id=agent,action_id=0,action=verb,params=dict(params),send_response=False)
                    actual=native.execute_action(verb,params,agent_id=agent,wall_time=now[0])
                    record(dict(kind='request',agent_id=agent,action=verb,parameters=params,wall_time=now[0],registration_time='2026-09-12T12:00:00'),expected,actual)
                def step(dt):
                    world.update(dt);native.step(dt,wall_time=now[0]);record(dict(kind='step',dt=dt,wall_time=now[0]),None,None)
                reg=dict(provider='synthetic',model_id='fake',base_url='https://host')
                for faction in ('wei','shu','wu'):request(faction,'register_agent_info',{**reg,'faction':faction})
                if family=='actions':
                    request('wei','claim_units',{'unit_ids':[a,b]})
                    request('wei','rest',{'unit_id':a});request('wei','rest',{'unit_id':a})
                    request('shu','rest',{'unit_id':a})
                    request('wei','occupy',{'unit_id':a,'position':{'col':-1,'row':0}})
                    request('wei','get_faction_state',{'faction':'wei'})
                    request('wei','fortify',{'unit_id':a,'position':{'col':-1,'row':0}})
                    request('wei','get_faction_state',{'faction':'wei'})
                    request('wei','occupy',{'unit_id':a,'position':{'col':-1,'row':0}})
                    request('wei','fortify',{'unit_id':a,'position':{'col':-1,'row':0}})
                    for name in ('hide','rockslide','arrow_evasion','unknown','unavailable'):
                        request('wei','skill',{'unit_id':a,'skill_name':name})
                    expected=territory.start_capture(b,(0,0));actual=native.start_capture(b,(0,0),wall_time=now[0])
                    record(dict(kind='start_capture',unit_id=b,position=[0,0],wall_time=now[0]),expected,actual)
                    for index in range(24):
                        now[0]+=1000;step(.5)
                        if index==3:
                            native.reset(native.export_state());record(dict(kind='reset-current'),None,None)
                    request('wei','get_faction_state',{'faction':'wei','unit_ids':[b,a]})
                    if display=='none':
                        request('wei','attack',{'unit_id':a,'target_id':c});step(1/30)
                    request('wei','get_faction_state',{'faction':'wei'})
                else:
                    for index in range(36):
                        now[0]+=.125
                        if index%3==0:
                            turn.end_turn();native.finish_human_turn(wall_time=now[0]);record(dict(kind='human_end_turn',wall_time=now[0]),None,None)
                        else:
                            faction=world.get_singleton_component(GameState).current_player.value
                            request(faction,'end_turn',{'faction':faction,'force':None if index%2 else True})
                        step(1/30)
                        if index==8:
                            native.reset(native.export_state());record(dict(kind='reset-current'),None,None)
                case['all_passed']=all(all(op['guards'].values()) for op in case['operations'])
                case['trace_digest']=digest(case['operations'])
        except Exception:case['error']=traceback.format_exc()
        finally:world.reset()
        return case


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();source=args.source.resolve();output=args.output.resolve();os.chdir(source);sys.path.insert(0,str(source))
    from star_native import _native,API_VERSION
    cases=[]
    for family,modes in [('actions',('real_time','turn_based')),('turn',('turn_based',))]:
        for display in ('none','dummy','window'):
            for mode in modes:
                for threads in (1,2,4):
                    console=io.StringIO()
                    with contextlib.redirect_stdout(console),contextlib.redirect_stderr(console):case=run_case(family,display,mode,threads)
                    case['console']=console.getvalue();cases.append(case)
    lab=Path(__file__).resolve().parents[2]
    raw=dict(schema='star-r3-actions-v1',source_sha=git(source,'rev-parse','HEAD'),source_dirty=git(source,'status','--porcelain'),
        tool_sha=git(lab,'rev-parse','HEAD'),tool_dirty=git(lab,'status','--porcelain','--',str(Path(__file__).resolve())),
        python=sys.version,platform=platform.platform(),native_api_version=API_VERSION,
        extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),cases=cases)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(gzip.compress(json.dumps(raw,sort_keys=True,separators=(',',':')).encode()+b'\n',mtime=0))
    summary={k:v for k,v in raw.items() if k!='cases'}
    summary['cases']=[dict(family=c['family'],display=c['display'],mode=c['mode'],threads=c['threads'],operations=len(c['operations']),
        ticks=sum(op['operation']['kind']=='step' for op in c['operations']),trace_digest=c.get('trace_digest'),
        all_passed=c['all_passed']) for c in cases]
    groups={}
    for case in cases:groups.setdefault((case['family'],case['display'],case['mode']),set()).add(case.get('trace_digest'))
    same_threads=all(len(values)==1 and None not in values for values in groups.values())
    summary.update(thread_settings_equal=same_threads,all_passed=all(c['all_passed'] for c in cases) and same_threads and not raw['source_dirty'] and not raw['tool_dirty'],
        raw_file=output.name,raw_size=output.stat().st_size,raw_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    output.with_name(output.name.removesuffix('.json.gz')+'.summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    if not summary['all_passed']:raise SystemExit(1)

if __name__=='__main__':main()
