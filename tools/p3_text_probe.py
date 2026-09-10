"""Lab-only text rendering attribution; production source stays unchanged.

replay: fixed-dt=0 world, no Agent pumping, randomized repeated overlay ablations.
live: instrument the existing 24Hz 5000U/1000A stochastic runtime.
Neither mode is a new capacity certification. Durations include every slow frame.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import sys
import time

from p3_local_agents import LocalAgents, fixture, identity, stats


def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        if row['admitted']:
            groups[row['condition']].append(row)
    return {name: {key: stats([r.get(key, 0) for r in values]) for key in
            ('frame_ms', 'damage_render_ms', 'damage_update_ms', 'coordinates_ms',
             'flush_ms', 'present_ms', 'effects', 'effects_at_draw', 'onscreen_anchors', 'tiles')}
            for name, values in groups.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--mode', choices=['replay', 'live'], default='replay')
    parser.add_argument('--samples', type=int, default=100)
    parser.add_argument('--repeats', type=int, default=2)
    parser.add_argument('--seconds', type=float, default=60)
    parser.add_argument('--warmup', type=float, default=30)
    args = parser.parse_args()
    source = Path(args.source).resolve()
    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(source))
    provenance = {'source': identity(source), 'tool': identity(Path(__file__).resolve().parents[1]),
                  'args': vars(args), 'argv': sys.argv[:], 'os': platform.platform(),
                  'python': sys.version, 'environment': dict((k, os.environ.get(k)) for k in
                    ('HEADLESS', 'SDL_VIDEODRIVER', 'STAR_SCALE_MINIMAP_UNITS'))}
    os.chdir(source)
    os.environ['STAR_SCALE_MINIMAP_UNITS'] = 'off'
    from rotk_env import main as entry
    from rotk_env.scenes.game_scene import GameScene
    from rotk_env.systems.animation_system import AnimationSystem as BaseAnimation
    from rotk_env.systems.window_animation_system import AnimationSystem
    from rotk_env.systems.map_render_system import MapRenderSystem
    from rotk_env.components import Camera, DamageNumber, UIState, Unit, UnitCount, HexPosition, GameTime, FogOfWar
    from rotk_env.prefabs.config import GameConfig
    from framework.engine.game_engine import GameEngine
    from framework.engine.renders import RenderEngine
    import pygame
    GameConfig.FPS = 24
    current, holder, rows = {}, {}, []
    draw_enabled = True

    def timed(owner, name, metric):
        original = getattr(owner, name)
        def wrapped(*a, **kw):
            start = time.perf_counter()
            try:
                return original(*a, **kw)
            finally:
                current[metric] = current.get(metric, 0) + (time.perf_counter()-start)*1000
        setattr(owner, name, wrapped)
    timed(AnimationSystem, '_update_damage_numbers', 'damage_update_ms')
    timed(RenderEngine, 'update', 'flush_ms')
    timed(pygame.display, 'flip', 'present_ms')
    original_damage = BaseAnimation.render_damage_numbers
    def damage(system):
        current['effects_at_draw'] = len(system.world.query().with_all(DamageNumber).entities())
        start = time.perf_counter()
        if draw_enabled:
            original_damage(system)
        current['damage_render_ms'] = (time.perf_counter()-start)*1000
    BaseAnimation.render_damage_numbers = damage
    original_coordinates = MapRenderSystem._render_coordinates_optimized
    def coordinates(system, tiles, offset, zoom=1.):
        current['tiles'] = len(tiles)
        start = time.perf_counter()
        original_coordinates(system, tiles, offset, zoom)
        current['coordinates_ms'] = (time.perf_counter()-start)*1000
    MapRenderSystem._render_coordinates_optimized = coordinates

    def fingerprint(world):
        data = [(i, vars(world.get_component(i, HexPosition)),
                 vars(world.get_component(i, UnitCount))) for i in world.query().with_all(Unit).entities()]
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    original_init = GameScene._initialize_game
    def initialize(scene):
        original_init(scene)
        holder['world'] = scene.world
        holder['camera'] = scene.world.get_singleton_component(Camera)
        holder['camera_initial'] = vars(holder['camera']).copy()
        holder['coordinates_initial'] = scene.world.get_singleton_component(UIState).show_coordinates
        holder['display'] = list(pygame.display.get_window_size())
        holder['driver'] = pygame.display.get_driver()
        holder['pygame'] = pygame.version.ver
        holder['animation'] = next(s for s in scene.world.systems if isinstance(s, AnimationSystem))
        holder['before'] = fingerprint(scene.world)
        holder['start'] = time.perf_counter()
        if args.mode == 'replay':
            holder['agents'] = LocalAgents(scene.world, 1000, 30., scope='selected', policy='stochastic')
            gc.collect()
            gc.disable()
    GameScene._initialize_game = initialize

    # Fixed synthetic texts isolate rendering, not a synthetic combat workload.
    cases = [dict(name='empty', n=0), dict(name='coordinates', n=0, coords=True),
             *[dict(name=f'damage{n}', n=n) for n in (10, 100, 500, 1000)],
             dict(name='hidden1000', n=1000, draw=False),
             dict(name='offscreen1000', n=1000, offscreen=True),
             dict(name='combined100', n=100, coords=True),
             dict(name='zoom1_empty', n=0, zoom=1.),
             dict(name='zoom1_coordinates', n=0, coords=True, zoom=1.),
             dict(name='zoom05_empty', n=0, zoom=.5),
             dict(name='zoom05_coordinates', n=0, coords=True, zoom=.5)]
    blocks = []
    rng = random.Random(42)
    for repeat in range(args.repeats):
        order = list(cases)
        rng.shuffle(order)
        blocks.extend((repeat, c) for c in order)
    holder['index'] = 0

    def set_case(case):
        nonlocal draw_enabled
        world, camera = holder['world'], holder['camera']
        for i in world.query().with_all(DamageNumber).entities():
            world.destroy_entity(i)
        holder['animation']._floating_world_positions.clear()
        for key, value in holder['camera_initial'].items():
            setattr(camera, key, value)
        camera.zoom = case.get('zoom', holder['camera_initial'].get('zoom', 1.))
        world.get_singleton_component(UIState).show_coordinates = case.get('coords', False)
        draw_enabled = case.get('draw', True)
        for i in range(case['n']):
            sx, sy = 100+(i % 40)*20, 150+(i//40)*14
            if case.get('offscreen'):
                sx += 100000
            entity = holder['animation']._create_floating_text(
                text='CRIT!' if i % 4 == 0 else str(100+i % 900),
                world_pos=((sx-camera.offset_x)/camera.zoom, (sy-camera.offset_y)/camera.zoom),
                lifetime=2.5 if i % 4 == 0 else 2., velocity=(0., 0.),
                color=(255, 255, 0) if i % 4 == 0 else (255, 0, 0),
                font_size=28 if i % 4 == 0 else 24)
            world.get_component(entity, DamageNumber).elapsed_time = .5

    original_update = GameEngine._update
    def update(engine):
        if 'world' not in holder:
            return original_update(engine)
        if args.mode == 'replay':
            block, within = divmod(holder['index']-60, args.samples+10)
            if block >= len(blocks):
                world = holder['world']
                holder['replay_guards'] = {
                    'world_unchanged': fingerprint(world) == holder['frozen_before'],
                    'clock_frozen': world.get_singleton_component(GameTime).game_elapsed_time == holder['frozen_time']}
                holder['finished'] = True
                engine.running = False
                return
            repeat, case = blocks[block] if block >= 0 else (-1, cases[0])
            if within == 0:
                if block == 0:
                    holder['frozen_before'] = fingerprint(holder['world'])
                    holder['frozen_time'] = holder['world'].get_singleton_component(GameTime).game_elapsed_time
                set_case(case)
                print('TEXT_PROBE_BLOCK', repeat, case, flush=True)
            engine.delta_time = 0.
            name, admitted = case['name'], block >= 0 and within >= 10
        else:
            name = 'live'
            admitted = time.perf_counter()-holder['start'] >= args.warmup
            repeat, within = 0, holder['index']
        world, camera = holder['world'], holder['camera']
        effects = [world.get_component(i, DamageNumber) for i in world.query().with_all(DamageNumber).entities()]
        width, height = holder['display']
        onscreen = sum(0 <= d.position[0]+camera.offset_x < width and
                       0 <= d.position[1]+camera.offset_y < height for d in effects)
        current.clear()
        start = time.perf_counter()
        original_update(engine)
        elapsed = (time.perf_counter()-start)*1000
        rows.append(dict(current, frame_ms=elapsed, condition=name, admitted=admitted,
                         repeat=repeat, within=within, effects=len(effects), onscreen_anchors=onscreen,
                         t=time.perf_counter()-holder['start']))
        holder['last_guards'] = {
            '5000_units': len(world.query().with_all(Unit).entities()) == 5000,
            'fog_on': world.get_singleton_component(FogOfWar).enabled}
        holder['index'] += 1
    GameEngine._update = update

    if args.mode == 'live':
        import p3_runtime
        sys.argv = ['p3_runtime.py', '--source', str(source), '--fps', '24', '--clock-mode', 'fixed',
                    '--cycle-mode', 'post-action', '--jitter-seconds', '5', '--units', '5000',
                    '--agents', '1000', '--delay', '30', '--scope', 'selected', '--policy', 'stochastic',
                    '--layout', 'canonical', '--seconds', str(args.seconds), '--warmup', str(args.warmup),
                    '--budget-ms', '18', '--gc-policy', 'realtime_defer', '--output', str(out.with_suffix('.runtime.json'))]
        p3_runtime.main()
        holder['finished'] = True
    else:
        scenario, fixture_hash = fixture(str(source), 5000)
        provenance['fixture_sha256'] = fixture_hash
        sys.argv = [str(source/'rotk_env/main.py'), '--skip-start', '--mode', 'real_time',
                    '--players', 'human_vs_two_ai', '--scenario', scenario, '--seed', '42', '--no-hub',
                    '--scale-harness-socket', f'/tmp/star-text-probe-{os.getpid()}.sock']
        entry.main()
    guards = {'finished': holder.get('finished', False),
              'source_clean': not provenance['source']['dirty'], 'tool_clean': not provenance['tool']['dirty'],
              **holder['last_guards']}
    if args.mode == 'replay':
        guards.update(**holder['replay_guards'],
                      complete_samples=len([r for r in rows if r['admitted']]) == len(cases)*args.samples*args.repeats)
    result = {'provenance': provenance, 'guards': guards, 'cases': cases,
              'camera': holder['camera_initial'], 'display': holder['display'],
              'coordinates_initial': holder['coordinates_initial'],
              'pygame': holder['pygame'], 'driver': holder['driver'], 'summary': summarize(rows)}
    raw = dict(result, frames=rows)
    out.with_suffix('.raw.json').write_text(json.dumps(raw, indent=2)+'\n')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
