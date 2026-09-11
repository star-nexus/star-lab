"""Record/replay ordered local commands against a selected STAR source checkout.

Lab owns this diagnostic codec. Sets/maps are canonicalized, lists are never
sorted. Unsupported state is an error; presentation objects are excluded by an
explicit list. Wall time is an input, patched before importing STAR dataclasses.
"""
from __future__ import annotations

import argparse
from collections import deque
import contextlib
import dataclasses
import datetime
from enum import Enum
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time

PRESENTATION = frozenset('Renderable AnimationState Selected Camera UIState InputState MiniMap UnitActionPanel ActionConfirmDialog UIButtonCollection UIPanel GameOverButtons DamageNumber AttackAnimation EffectAnimation ProjectileAnimation'.split())
RECOVERY_FIELDS = ('_last_game_elapsed', 'ap_elapsed', 'mp_elapsed', 'skill_elapsed',
                   'mp_last_points', '_ap_due', '_mp_due', '_skill_due', '_mp_pending_detection')


def encode(value):
    if isinstance(value, Enum):
        return {'enum': type(value).__name__, 'value': encode(value.value)}
    if isinstance(value, float) and not math.isfinite(value):
        return {'float': value.hex()}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, random.Random):
        return {'random_state': encode(value.getstate())}
    if dataclasses.is_dataclass(value):
        return {f.name: encode(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, dict):
        pairs = [[encode(k), encode(v)] for k, v in value.items()]
        return {'map': sorted(pairs, key=lambda p: json.dumps(p[0], sort_keys=True))}
    if isinstance(value, (set, frozenset)):
        return {'set': sorted((encode(v) for v in value), key=lambda v: json.dumps(v, sort_keys=True))}
    if isinstance(value, (list, tuple, deque)):
        return [encode(v) for v in value]
    raise TypeError(f'Unspecified replay state: {type(value)}')


def snapshot(world):
    entities = []
    for entity, components in sorted(world.entities.items()):
        kept = {t.__name__: encode(c) for t, c in components.items() if t.__name__ not in PRESENTATION}
        if kept:
            entities.append({'id': entity, 'components': kept})
    singletons = {t.__name__: encode(c) for t, c in world._singleton_components.items()
                  if t.__name__ not in PRESENTATION}
    recovery = getattr(world, '_resource_recovery_scheduler', None)
    return {'entity_counter': world.entity_counter, 'entities': entities,
            'singletons': singletons,
            'recovery': {k: encode(getattr(recovery, k)) for k in RECOVERY_FIELDS} if recovery else None}


def identity(path):
    return {'sha': subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip(),
            'dirty': subprocess.check_output(['git', '-C', str(path), 'status', '--porcelain'], text=True)}


def first_difference(left, right, path='$'):
    if type(left) is not type(right):
        return {'path': path, 'left': left, 'right': right}
    if isinstance(left, dict):
        if left.keys() != right.keys():
            return {'path': path, 'left_keys': sorted(left), 'right_keys': sorted(right)}
        for k in sorted(left):
            diff = first_difference(left[k], right[k], f'{path}.{k}')
            if diff:
                return diff
    elif isinstance(left, list):
        if len(left) != len(right):
            return {'path': path, 'left_length': len(left), 'right_length': len(right)}
        for i, (a, b) in enumerate(zip(left, right)):
            diff = first_difference(a, b, f'{path}[{i}]')
            if diff:
                return diff
    elif left != right:
        return {'path': path, 'left': left, 'right': right}
    return None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--replay', type=Path)
    p.add_argument('--mode', choices=['real_time', 'turn_based'], default='real_time')
    p.add_argument('--display', choices=['none', 'dummy', 'window'], default='dummy')
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--ticks', type=int, default=150)
    args = p.parse_args()
    args.source = args.source.resolve()
    source_identity = identity(args.source)
    previous = json.loads(gzip.decompress(args.replay.read_bytes())) if args.replay else None
    config = previous['config'] if previous else {'mode': args.mode, 'display': args.display,
                                                 'seed': args.seed, 'ticks': args.ticks}
    fixture = previous['fixture'] if previous else {
        'id': 'lab-rust-replay', 'name': 'Migration contact fixture',
        'width': 9, 'height': 9, 'coordinate_system': 'centered', 'unit_mix': [1, 1, 1],
        'terrain': ['.........'] * 9,
        'formations': {'wei': [[-1, 0], [-2, 1], [-2, -1]],
                       'shu': [[1, 0], [2, 1], [2, -1]], 'wu': [[0, 2], [-1, 3], [1, 3]]}}
    os.chdir(args.source)
    sys.path.insert(0, str(args.source))
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    wall = [1720000000.0]
    time.time = lambda: wall[0]
    original_datetime = datetime.datetime
    class ClockDateTime(original_datetime):
        @classmethod
        def now(cls, tz=None):
            return cls.fromtimestamp(wall[0], tz)
    datetime.datetime = ClockDateTime
    # Store the fixture only for this process. It is archived inside the trace.
    fixture_path = args.source / 'rotk_env/maps/lab-rust-replay.json'
    if fixture_path.exists():
        raise RuntimeError(f'Refusing to overwrite {fixture_path}')
    fixture_path.write_text(json.dumps(fixture))
    events = []
    steps = []
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            import pygame
            pygame.init()
            pygame.display.set_mode((1200, 800))
            from framework.engine.events import EBS
            from rotk_env.prefabs.world_builder import build_skirmish_world
            from rotk_env.prefabs.config import Faction, PlayerType
            from rotk_env.components import Unit, GameTime, FogOfWar
            from rotk_env.systems.llm_system import LLMSystem
            publish = EBS.publish
            def record_event(event):
                events.append({'type': type(event).__name__, 'data': encode(vars(event))})
                publish(event)
            EBS.publish = record_event
            world = build_skirmish_world(players={f: PlayerType.AI for f in Faction},
                mode=config['mode'], display=config['display'], scenario='lab-rust-replay',
                seed=config['seed'], seed_source='replay', env_id='replay-env', hub_url=None)
            gate = next(s for s in world.systems if isinstance(s, LLMSystem))
            initial = {'state': snapshot(world), 'events': list(events)}
            events.clear()
            by_faction = {f.value: sorted(e for e, comps in world.entities.items()
                              if Unit in comps and comps[Unit].faction == f) for f in Faction}
            def apply(op):
                wall[0] = op['wall_time']
                response = None
                if op['kind'] == 'step':
                    world.update(op['dt'])
                elif op['kind'] == 'action':
                    response = gate._process_action_request(op['agent_id'], len(steps),
                        op['action'], dict(op['params']), send_response=False)
                elif op['kind'] == 'pause':
                    world.get_singleton_component(GameTime).paused = op['value']
                elif op['kind'] == 'fog':
                    world.get_singleton_component(FogOfWar).enabled = op['value']
                else:
                    raise ValueError(op)
                # Detach the complete decoded response at its return boundary.
                response = json.loads(json.dumps(response, ensure_ascii=False))
                steps.append({'input': op, 'response': response, 'events': list(events), 'state': snapshot(world)})
                events.clear()
                return response
            def command(kind, **kw):
                return apply({'kind': kind, 'wall_time': wall[0], **kw})
            def action(f, name, **params):
                return command('action', agent_id=f'replay-{f}', action=name, params=params)
            if previous:
                for row in previous['steps']:
                    apply(row['input'])
            else:
                for f, ids in by_faction.items():
                    assert action(f, 'register_agent_info', faction=f, provider='synthetic',
                                  model_id='replay', base_url='http://localhost')['success']
                    assert action(f, 'claim_units', unit_ids=list(reversed(ids)))['success']
                for tick in range(config['ticks']):
                    wall[0] += 1/30
                    if tick % 15 == 0:
                        for f in by_faction:
                            obs = action(f, 'get_faction_state', faction=f)
                            for panel in obs.get('units', []):
                                uid = panel['unit_id']
                                if panel['attackable']:
                                    action(f, 'attack', unit_id=uid, target_id=panel['attackable'][0])
                                elif panel['reachable']:
                                    action(f, 'move', unit_id=uid, target_position=panel['reachable'][-1])
                            action(f, 'get_faction_state', faction=f, unit_ids=[])
                            if config['mode'] == 'turn_based':
                                action(f, 'end_turn', faction=f)
                    if tick in (40, 45):
                        command('pause', value=tick == 40)
                    if tick in (60, 90):
                        command('fog', value=tick == 90)
                    command('step', dt=1/30)
                for f, ids in by_faction.items():
                    action(f, 'get_faction_state', faction=f, unit_ids=[True])
                    action(f, 'release_units')
            world.reset()
            pygame.quit()
    finally:
        fixture_path.unlink(missing_ok=True)
    result = {'schema': 'star-replay-v1', 'source': source_identity, 'tool': identity(Path(__file__).parents[2]),
              'config': config, 'fixture': fixture, 'initial': initial, 'steps': steps}
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(gzip.compress(payload, mtime=0))
    diff = first_difference({'initial': previous['initial'], 'steps': previous['steps']},
                            {'initial': initial, 'steps': steps}) if previous else None
    summary = {'schema': result['schema'], 'source': source_identity, 'config': config,
               'operations': len(steps), 'events': sum(len(s['events']) for s in steps),
               'accepted': {verb: sum(s['input'].get('action') == verb and bool((s['response'] or {}).get('success')) for s in steps)
                            for verb in ['move', 'attack', 'get_faction_state', 'end_turn']},
               'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest(),
               'compared': previous is not None, 'difference': diff}
    args.output.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    if diff:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
