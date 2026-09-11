"""Partial R2 Fog/statistics differential trace, not full World.update or capacity."""
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
import time


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()


def run_case(display, mode_name):
    import pytest
    from framework.engine.events import EBS
    from rotk_env.components import (BattleLog, Combat, FogOfWar, GameTime,
                                     UnitCount, UnitStatistics, UnitObservation)
    from rotk_env.prefabs.config import GameMode
    from rotk_env.runtime.bootstrap import export_initial_state, encode
    from rotk_env.systems.statistics_system import StatisticsSystem
    from rotk_env.systems.window_statistics_system import StatisticsSystem as WindowStatistics
    from rotk_env.systems.animation_system import AnimationSystem
    from rotk_env.systems.combat_system import CombatSystem
    from rotk_env.systems.movement_system import MovementSystem
    from rotk_env.systems.resource_recovery_system import ResourceRecoverySystem
    from rotk_env.tests.test_native_vision import make_vision_world
    from star_native import NativeRuntime

    now = [1720000000.]
    patches = pytest.MonkeyPatch()
    patches.setattr(time, 'time', lambda: now[0])
    for cls, field in ((UnitStatistics, 'creation_time'), (UnitObservation, 'last_seen_time')):
        original = cls.__init__
        def initialize(self, *args, _init=original, _field=field, **kwargs):
            _init(self, *args, **kwargs)
            setattr(self, _field, now[0])
        patches.setattr(cls, '__init__', initialize)
    world, (a, b, c), vision = make_vision_world(display)
    clock = world.get_singleton_component(GameTime)
    clock.current_mode = GameMode(mode_name)
    world.add_singleton_component(BattleLog())
    statistics = WindowStatistics(batch_size=1) if display == 'window' else StatisticsSystem()
    world.add_system(statistics)
    recovery = ResourceRecoverySystem(); world.add_system(recovery)
    world.get_component(a, Combat).attack_range = 5
    world.get_component(c, UnitCount).current_count = 1
    move = next(s for s in world.systems if isinstance(s, MovementSystem))
    combat = next(s for s in world.systems if isinstance(s, CombatSystem))
    animation = next((s for s in world.systems if isinstance(s, AnimationSystem)), None)
    initial = export_initial_state(world, display=display)
    native = NativeRuntime(json.dumps(initial))
    records = []; events = []; tick = 0
    original_publish = EBS.publish
    def publish(event):
        events.append({'type': type(event).__name__, 'fields': encode(event)})
        return original_publish(event)
    patches.setattr(EBS, 'publish', publish)

    def record(operation, expected_result=None, actual_result=None):
        expected = export_initial_state(world, display=display)
        expected['clock']['tick'] = tick
        actual = json.loads(native.export_state_json())
        actual_events = json.loads(native.take_presentation_delta_json())['events']
        expected_result = json.loads(json.dumps(expected_result))
        guards = dict(state_equal=expected == actual, response_equal=expected_result == actual_result,
                      events_equal=events == actual_events)
        records.append(dict(operation=operation, guards=guards, expected_state=expected, actual_state=actual,
                            expected_result=expected_result, actual_result=actual_result,
                            expected_events=events.copy(), actual_events=actual_events))
        events.clear()
        return all(guards.values())
    try:
        if record({'kind': 'initial'}):
            for index in range(40):
                now[0] += .25; native._set_wall_metadata(now[0])
                if index == 0:
                    op = dict(kind='move', unit_id=a, goal=(-2, 0))
                    if not record(op, move.move_unit(a, (-2, 0)),
                                  json.loads(native._movement_probe_json(json.dumps([op])))[0]): break
                if index == 4 and display == 'none':
                    op = dict(kind='attack', unit_id=a, target_id=c)
                    if not record(op, combat.execute_attack(a, c),
                                  json.loads(native._combat_probe_json(json.dumps([op])))[0]): break
                if index in (6, 16):
                    op = dict(kind='toggle', enabled=index == 16)
                    world.get_singleton_component(FogOfWar).enabled = op['enabled']
                    native._vision_probe_json(json.dumps([op]))
                    if not record(op): break
                clock.paused = 20 <= index < 24
                native.set_clock(clock.paused, clock.time_scale)
                clock.update(.25)
                statistics.update(.25)
                if animation is not None: animation._update_movement_animations(.25)
                recovery.update(.25); vision.update(.25)
                native.step(.25, clock.last_update_time); tick += 1
                if not record(dict(kind='step', dt=.25, wall_time=now[0], paused=clock.paused)): break
                if index in (2, 8, 27):
                    native.reset(native.export_state_json())
                    # Reset exposes a full presentation refresh, not new game events.
                    if not record(dict(kind='reset')): break
        return dict(display=display, mode=mode_name, initial=initial, operations=records,
                    all_passed=(len(records) == (48 if display == 'none' else 47)
                                and all(all(r['guards'].values()) for r in records)))
    finally:
        patches.undo(); native.close(); world.reset()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); source = args.source.resolve(); output = args.output.resolve()
    sys.path.insert(0, str(source)); os.chdir(source)
    from star_native import _native
    with contextlib.redirect_stdout(io.StringIO()):
        cases = [run_case(d, m) for d in ('none', 'dummy', 'window')
                 for m in ('real_time', 'turn_based')]
    raw = dict(schema='star-native-r2-vision-stats-v1', scope='partial functional gate, no full R2 or capacity',
               source_sha=git(source, 'rev-parse', 'HEAD'), source_dirty=git(source, 'status', '--porcelain'),
               tool_sha=git(Path(__file__).parents[2], 'rev-parse', 'HEAD'),
               python=sys.version, platform=platform.platform(),
               extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),
               cargo_lock_sha256=hashlib.sha256((source / 'Cargo.lock').read_bytes()).hexdigest(), cases=cases)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode() + b'\n'
    output.write_bytes(gzip.compress(payload, mtime=0))
    summary = {k: v for k, v in raw.items() if k != 'cases'}
    summary['cases'] = [dict(display=c['display'], mode=c['mode'], operations=len(c['operations']),
                             all_passed=c['all_passed']) for c in cases]
    summary.update(all_passed=all(c['all_passed'] for c in cases), raw_file=output.name,
                   raw_size=output.stat().st_size, raw_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    output.with_name(output.name.removesuffix('.json.gz') + '.summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    if not summary['all_passed']: raise SystemExit(1)


if __name__ == '__main__': main()
