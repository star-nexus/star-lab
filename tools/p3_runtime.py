"""Run the production window loop with a Lab-only local Agent controller.

Normal ENV/animation/Vision/render systems remain installed. The only replaced
boundary is network transport. Frame timing surrounds the full production
_update plus Agent pump, with a 30Hz wall-clock pacing wait outside work timing.
"""
from __future__ import annotations
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import sys
import time

from p3_local_agents import Attribution, LocalAgents, fixture, identity, stats


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True)
    p.add_argument('--units', type=int, default=100)
    p.add_argument('--agents', type=int, default=100)
    p.add_argument('--delay', default='1')
    p.add_argument('--scope', choices=['faction', 'selected'], default='faction')
    p.add_argument('--layout', choices=['canonical', 'interleaved'], default='canonical')
    p.add_argument('--policy', choices=['mixed', 'move', 'observe'], default='mixed')
    p.add_argument('--seconds', type=float, default=15)
    p.add_argument('--warmup', type=float, default=5)
    p.add_argument('--budget-ms', type=float, default=4)
    p.add_argument('--attribute', action='store_true')
    p.add_argument('--no-encode', action='store_true')
    p.add_argument('--synchronized', action='store_true')
    p.add_argument('--movement-overlay', action='store_true')
    p.add_argument('--no-agents', action='store_true')
    p.add_argument('--gc-policy', choices=['auto', 'realtime_defer'], default='auto')
    p.add_argument('--output', required=True)
    args = p.parse_args()
    args.source = str(Path(args.source).resolve())
    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, args.source)
    source_id = identity(args.source)
    tooling_id = identity(Path(__file__).resolve().parents[1])
    scenario, fixture_hash = fixture(args.source, args.units, args.layout)
    os.chdir(args.source)  # Production assets include repository-relative font paths.
    os.environ['STAR_SCALE_MINIMAP_UNITS'] = 'off'
    from rotk_env import main as entry
    from rotk_env.scenes.game_scene import GameScene
    from framework.engine.game_engine import GameEngine
    from rotk_env.components import Unit, UnitCount, MovementAnimation, HexPosition, GameState, FogOfWar
    from rotk_env.prefabs.config import GameConfig
    from performance_profiler import profiler
    GameConfig.FPS = 30
    holder = {}
    original_init = GameScene._initialize_game
    original_update = GameEngine._update
    frames, censuses = [], []

    def initialize(scene):
        original_init(scene)
        holder['scene'] = scene
        holder['world'] = scene.world
        holder['agents'] = LocalAgents(scene.world, args.agents,
            args.delay if args.delay == 'mixed' else float(args.delay), scope=args.scope,
            encode=not args.no_encode, policy=args.policy)
        if args.attribute:
            holder['attribution'] = Attribution(holder['agents'].gate.action_handler)
        if args.movement_overlay:
            if args.policy != 'observe':
                raise ValueError('Movement overlay is observation-only attribution, not an Agent action loop')
            harness = next(s for s in scene.world.systems if s.__class__.__name__=='ScaleHarnessSystem')
            prepared = harness.handle_command({'command':'prepare_routes','density':1.,'seed':42,'route_steps':12})
            started = harness.handle_command({'command':'start_sustained',
                'batch_id':prepared['batch_id'], 'execution_density':1.,
                'duration_seconds':args.seconds+args.warmup+10,'phase':'staggered',
                'phase_seed':42,'gc_policy':args.gc_policy})
            if not prepared.get('ok') or not started.get('ok'):
                raise RuntimeError((prepared, started))
            holder['overlay'] = {'prepared':prepared, 'started':started}
        elif args.gc_policy == 'realtime_defer':
            # Explicit finite experiment epoch; GC maintenance is before warmup.
            gc.collect()
            gc.disable()
        holder['start'] = time.perf_counter()
        holder['last_census'] = -1
        holder['sim_time'] = 0.

    def update(engine):
        start = time.perf_counter()
        engine._p3_start = start
        if 'start' in holder:
            elapsed = start - holder['start']
            if elapsed >= args.warmup+args.seconds:
                engine.running = False
                holder['finished'] = True
                holder['end'] = start
                return
            agents = holder['agents']
            if agents.epoch is None:
                agents.start(holder['start'], args.synchronized)
            if not args.no_agents:
                agents.pump(args.budget_ms)
        agent_end = time.perf_counter()
        original_update(engine)
        if 'start' not in holder or start < holder['start']:
            return
        holder['sim_time'] += engine.delta_time
        elapsed = start - holder['start']
        if int(elapsed) != holder['last_census']:
            holder['last_census'] = int(elapsed)
            world = holder['world']
            ids = world.query().with_component(Unit).entities()
            counts = [world.get_component(i, UnitCount) for i in ids]
            alive = sum(c is not None and c.current_count > 0 for c in counts)
            moving = sum(bool((a:=world.get_component(i, MovementAnimation)) and a.is_moving) for i in ids)
            # Count location changes across bounded one-second samples (not all commits).
            positions = {i:(p.col,p.row) for i in ids if (p:=world.get_component(i, HexPosition))}
            old = holder.get('positions', positions)
            changes = sum(old.get(i) != pos for i,pos in positions.items())
            holder['positions'] = positions
            heap = agents.heap
            oldest = max(0., time.perf_counter()-heap[0][0])*1000 if heap else 0
            censuses.append({'t':elapsed, 'alive':alive, 'moving':moving,
                'position_changes':changes, 'oldest_due_ms':oldest,
                'game_over':world.get_singleton_component(GameState).game_over,
                'fog':world.get_singleton_component(FogOfWar).enabled,
                'gc_enabled':gc.isenabled(), 'sim_time':holder['sim_time'],
                'maxrss':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                'counts':dict(agents.counts)})
        end = time.perf_counter()
        if len(frames) >= 20000:
            raise RuntimeError('frame recorder overflow')
        frames.append({'t':elapsed,'work_ms':(end-start)*1000,
            'agent_ms':(agent_end-start)*1000, 'dt':engine.delta_time})

    def wait(engine, prof):
        now = time.perf_counter()
        deadline = getattr(engine, '_p3_next_tick', engine._p3_start + 1/30)
        # Carry sleep overshoot forward instead of adding it to every period.
        remaining = max(0., deadline-now)
        if remaining:
            with prof.time_system('fps_cap_wait', category='wait'):
                time.sleep(remaining)
        engine._p3_next_tick = max(deadline+1/30, now)

    GameScene._initialize_game = initialize
    GameEngine._update = update
    GameEngine._wait_for_frame_cap = wait
    sys.argv = [str(Path(args.source)/'rotk_env/main.py'), '--skip-start',
        '--mode','real_time','--players','human_vs_two_ai','--scenario',scenario,
        '--seed','42','--no-hub','--uncapped','--scale-harness-socket',
        f'/tmp/star-p3-{os.getpid()}.sock']
    entry.main()
    if not holder.get('finished'):
        raise RuntimeError('Runtime ended before complete measurement; inspect log')
    agents = holder['agents']
    admitted = [f for f in frames if f['t'] >= args.warmup]
    events = [r for r in agents.records if r['t'] >= args.warmup]
    cens = [r for r in censuses if r['t'] >= args.warmup]
    work = stats([f['work_ms'] for f in admitted])
    ob = stats([r['response_ms'] for r in events if r['event']=='observe'])
    ac = stats([r['queue_ms'] for r in events if r['event']=='act'])
    blocks = []
    for i in range(int(args.seconds//30)):
        rows = [r['work_ms'] for r in admitted if args.warmup+i*30 <= r['t'] < args.warmup+(i+1)*30]
        blocks.append(stats(rows))
    worst5 = max([0]+[stats([r['work_ms'] for r in admitted if t <= r['t'] < t+5]).get('p99',0)
        for t in range(math_floor(args.warmup), math_floor(args.warmup+args.seconds-5)+1)])
    streak = longest = 0
    for frame in admitted:
        streak = streak+1 if frame['work_ms'] > 1000/30 else 0
        longest = max(longest, streak)
    guards = {'complete':bool(admitted) and holder['end']-holder['start']>=args.seconds+args.warmup,
        'source_clean':not source_id['dirty'], 'tooling_clean':not tooling_id['dirty'],
        'fog_on':all(r['fog'] for r in cens), 'world_alive':all(not r['game_over'] for r in cens),
        'resident_retained':all(r['alive']==args.units for r in cens),
        'position_progress':sum(r['position_changes'] for r in cens)>0,
        'frame_p99':work.get('p99',float('inf')) <= 1000/30,
        'world_hz':len(admitted)/args.seconds >= 29.7,
        'observation_p99':args.no_agents or ob.get('p99',float('inf')) <=100,
        'action_queue_p99':args.no_agents or ac.get('p99',float('inf')) <=100,
        'queue_bounded':args.no_agents or agents.summary()['oldest_overdue_ms']<=100,
        'duration_formal':args.seconds>=60, 'not_diagnostic':not args.attribute}
    raw = {'frames':frames, 'events':agents.records, 'censuses':censuses}
    raw_path = out.with_suffix('.raw.json')
    raw_path.write_text(json.dumps(raw,separators=(',',':'))+'\n')
    result = {'source':source_id,'tooling':tooling_id,'workload':vars(args),
        'hardware':{'platform':platform.platform(),'python':sys.version,'machine':platform.machine(),
                    'chrome':'kept open; no slow frames removed'},
        'fixture_sha256':fixture_hash, 'guards':guards, 'pass':all(guards.values()),
        'frame_work_ms':work,'frame_count':len(admitted),'world_hz':len(admitted)/args.seconds,
        'observation_response_ms':ob,'action_queue_ms':ac, 'blocks30':blocks,
        'worst_rolling5_p99_ms':worst5,'longest_miss_streak':longest,
        'miss_fraction':sum(f['work_ms']>1000/30 for f in admitted)/max(1,len(admitted)),
        'agents':agents.summary(), 'censuses':censuses,
        'attribution':dict(holder['attribution'].values) if 'attribution' in holder else None,
        'overlay':holder.get('overlay'),
        'raw':{'path':raw_path.name,'size':raw_path.stat().st_size,
               'sha256':hashlib.sha256(raw_path.read_bytes()).hexdigest()}}
    out.write_text(json.dumps(result,indent=2)+'\n')
    return result


def math_floor(value):
    import math
    return math.floor(value)


if __name__ == '__main__':
    main()
