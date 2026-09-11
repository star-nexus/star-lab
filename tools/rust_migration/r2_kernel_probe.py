"""R2 intermediate differential evidence for movement, recovery and rule combat.

This is a functional fixture, NOT an Agent workload or a full World.update replay.
The production contract fixture intentionally has no statistics/Fog subscribers.
"""
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


def git(path, *args):
    return subprocess.check_output(['git','-C',str(path),*args],text=True).strip()


def run_case(display, seed):
    from framework.engine.events import EBS
    from rotk_env.components import Combat, GameTime, RngService
    from rotk_env.runtime.bootstrap import export_initial_state, encode
    from rotk_env.systems.animation_system import AnimationSystem
    from rotk_env.systems.combat_system import CombatSystem
    from rotk_env.systems.movement_system import MovementSystem
    from rotk_env.systems.resource_recovery_system import ResourceRecoverySystem
    from rotk_env.tests.test_native_movement import make_world
    from star_native import NativeRuntime
    world, (a,b,c)=make_world(display)
    world.add_singleton_component(RngService(seed=seed))
    for uid in (a,b,c):
        world.get_component(uid,Combat).attack_range=5
    recovery=ResourceRecoverySystem();world.add_system(recovery)
    move=next(s for s in world.systems if isinstance(s,MovementSystem))
    combat=next(s for s in world.systems if isinstance(s,CombatSystem))
    animation=next((s for s in world.systems if isinstance(s,AnimationSystem)),None)
    clock=world.get_singleton_component(GameTime)
    initial=export_initial_state(world,display=display)
    native=NativeRuntime(json.dumps(initial))
    recorded=[];events=[];tick=0
    original_publish=EBS.publish
    EBS.publish=lambda e:events.append({'type':type(e).__name__,'fields':encode(e)})
    def record(operation,expected_result,actual_result):
        expected=export_initial_state(world,display=display)
        expected['clock']['tick']=tick
        actual=json.loads(native.export_state_json())
        actual_events=json.loads(native.take_presentation_delta_json())['events']
        expected_result=json.loads(json.dumps(expected_result))
        guards={'state_equal':expected==actual,'response_equal':expected_result==actual_result,'events_equal':events==actual_events}
        recorded.append({'operation':operation,'guards':guards,'expected_state':expected,'actual_state':actual,
                         'expected_result':expected_result,'actual_result':actual_result,
                         'expected_events':events.copy(),'actual_events':actual_events})
        events.clear()
        if not all(guards.values()):
            return False
        return True
    try:
        record({'kind':'initial'},None,None)
        for uid,goal in [(a,(-2,0)),(b,(-1,1)),(a,(0,0))]:
            op={'kind':'move','unit_id':uid,'goal':goal}
            expected=move.move_unit(uid,goal)
            actual=json.loads(native._movement_probe_json(json.dumps([op])))[0]
            if not record(op,expected,actual):break
        for index in range(48):
            clock.paused=12<=index<16
            clock.time_scale=.5 if index<24 else 2.
            native.set_clock(clock.paused,clock.time_scale)
            clock.update(.25)
            if animation is not None:animation._update_movement_animations(.25)
            recovery.update(.25)
            native.step(.25,clock.last_update_time);tick+=1
            if not record({'kind':'step','dt':.25,'wall_time':clock.last_update_time},None,None):break
            if display=='none' and index%2==0:
                attacker,target=(a,c) if index%4==0 else (c,a)
                if world.has_entity(attacker) and world.has_entity(target):
                    op={'kind':'attack','unit_id':attacker,'target_id':target}
                    expected=combat.execute_attack(attacker,target)
                    actual=json.loads(native._combat_probe_json(json.dumps([op])))[0]
                    if not record(op,expected,actual):break
        return {'display':display,'seed':seed,'initial':initial,'operations':recorded,
                'all_passed':all(all(r['guards'].values()) for r in recorded)}
    finally:
        EBS.publish=original_publish
        native.close();world.reset()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True,help='Canonical raw .json.gz file')
    args=p.parse_args();source=args.source.resolve();output=args.output.resolve()
    sys.path.insert(0,str(source));os.chdir(source)
    from star_native import _native
    with contextlib.redirect_stdout(io.StringIO()):
        cases=[run_case(display,seed) for display in ('none','dummy','window') for seed in (42,17)]
    raw={'schema':'star-native-r2-kernel-v1','scope':'partial low-level functional gate, not full R2 or performance',
         'source_sha':git(source,'rev-parse','HEAD'),'source_dirty':git(source,'status','--porcelain'),
         'tool_sha':git(Path(__file__).parents[2],'rev-parse','HEAD'),'python':sys.version,
         'platform':platform.platform(),'extension_sha256':hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),
         'cargo_lock_sha256':hashlib.sha256((source/'Cargo.lock').read_bytes()).hexdigest(),'cases':cases}
    output.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(raw,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()+b'\n'
    output.write_bytes(gzip.compress(payload,mtime=0))
    summary={k:v for k,v in raw.items() if k!='cases'}
    summary['cases']=[{'display':c['display'],'seed':c['seed'],'operations':len(c['operations']),
                       'all_passed':c['all_passed']} for c in cases]
    summary.update(all_passed=all(c['all_passed'] for c in cases),
                   raw_file=output.name,raw_size=output.stat().st_size,
                   raw_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    output.with_name(output.name.removesuffix('.json.gz')+'.summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    if not summary['all_passed']:raise SystemExit(1)


if __name__=='__main__':main()
