"""Record private team and faction projection parity; not an authenticated Agent test."""
import argparse
import contextlib
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys


def git(path,*args):
    return subprocess.check_output(['git','-C',str(path),*args],text=True).strip()


def run_case(display,fog):
    from rotk_env.components import FogOfWar, TeamCoordination, Combat, UnitCount
    from rotk_env.runtime.bootstrap import export_initial_state
    from rotk_env.systems.llm_action_handler import LLMActionHandler
    from rotk_env.systems.movement_system import MovementSystem
    from rotk_env.tests.test_native_observation import setup
    from star_native import NativeRuntime
    world,(a,b,c),vision=setup(display)
    world.get_singleton_component(FogOfWar).enabled=fog
    coord=world.get_singleton_component(TeamCoordination)
    native=NativeRuntime(json.dumps(export_initial_state(world,display=display)))
    handler=LLMActionHandler(world);records=[]
    def state():return export_initial_state(world,display=display)
    def record(operation,expected,actual,metrics=None):
        expected=json.loads(json.dumps(expected));before=state();after=json.loads(native.export_state_json())
        guards=dict(response_equal=expected==actual,state_equal=before==after)
        records.append(dict(operation=operation,expected=expected,actual=actual,expected_state=before,
                            actual_state=after,guards=guards,metrics=metrics))
        if not all(guards.values()):raise AssertionError('projection parity failed')
    def query():
        requests=[dict(faction='wei',agent_id='alpha'),dict(faction='shu',agent_id='enemy'),
                  dict(faction='wei',agent_id='beta',unit_ids=[b,a,b]),dict(faction='wei',unit_ids=[]),
                  dict(faction='wu'),dict(faction='wei',unit_ids=[c]),dict(faction='wei',unit_ids=[True])]
        expected=[handler.handle_faction_state(p) for p in requests]
        actual=json.loads(native._observation_probe_json(json.dumps(requests)))
        record(dict(kind='observations',requests=requests),expected,actual['results'],actual['metrics'])
        return (actual['metrics']['census_builds']==1 and actual['metrics']['faction_builds']==3
                and actual['metrics']['panel_builds']==3)
    try:
        guards=[query()]
        for kind,params in [('claim',dict(agent_id='beta',unit_ids=[a,b],exclusive=True)),
                            ('claim',dict(agent_id='beta',unit_ids=[a,b],exclusive=False)),
                            ('release',dict(agent_id='beta',unit_ids=None))]:
            expected=coord.claim_units(**params) if kind=='claim' else coord.release_units(**params)
            op=dict(kind=kind,**params)
            actual=json.loads(native._team_probe_json(json.dumps([op])))[0]
            record(op,expected,actual);guards.append(query())
        move=next(s for s in world.systems if isinstance(s,MovementSystem))
        expected=move.move_unit(a,(-2,0));op=dict(kind='move',unit_id=a,goal=(-2,0))
        actual=json.loads(native._movement_probe_json(json.dumps([op])))[0]
        record(op,expected,actual);guards.append(query())
        native.reset(native.export_state_json());guards.append(query())
        return dict(display=display,fog=fog,operations=records,all_passed=all(guards) and len(records)==10)
    finally:native.close();world.reset()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();source=a.source.resolve();output=a.output.resolve()
    os.chdir(source);sys.path.insert(0,str(source))
    from star_native import _native
    with contextlib.redirect_stdout(io.StringIO()):
        cases=[run_case(d,f) for d in ('none','dummy','window') for f in (False,True)]
    raw=dict(schema='star-r2-projection-v1',source_sha=git(source,'rev-parse','HEAD'),
             source_dirty=git(source,'status','--porcelain'),tool_sha=git(Path(__file__).parents[2],'rev-parse','HEAD'),
             python=sys.version,platform=platform.platform(),
             extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),cases=cases)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(gzip.compress(json.dumps(raw,sort_keys=True,separators=(',',':')).encode()+b'\n',mtime=0))
    summary={k:v for k,v in raw.items() if k!='cases'}
    summary['cases']=[dict(display=c['display'],fog=c['fog'],operations=len(c['operations']),all_passed=c['all_passed']) for c in cases]
    summary.update(all_passed=all(c['all_passed'] for c in cases),raw_file=output.name,
                   raw_size=output.stat().st_size,raw_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    output.with_name(output.name.removesuffix('.json.gz')+'.summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    if not summary['all_passed']:raise SystemExit(1)

if __name__=='__main__':main()
