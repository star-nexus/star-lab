"""Frozen-world observation equivalence/cost probe. NOT realtime capacity.

Runs one mode per invocation so distinct experiments never compete for cores.
Worker startup is warmed outside measurements; source/tool identities and each
raw request are retained. No Agents think or issue actions during this probe.
"""
from __future__ import annotations
import argparse
from concurrent.futures import wait, FIRST_COMPLETED
from contextlib import redirect_stdout
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import sys
import time

from p3_local_agents import LocalAgents, fixture, identity, stats


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True)
    p.add_argument('--units', type=int, default=5000)
    p.add_argument('--agents', type=int, default=1000)
    p.add_argument('--queries', type=int, default=100)
    p.add_argument('--workers', type=int, default=2, help='0 = ordinary local gate')
    p.add_argument('--max-pending', type=int, default=4)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    a.source = str(Path(a.source).resolve())
    sys.path.insert(0, a.source)
    os.chdir(a.source)
    from rotk_env.prefabs.world_builder import build_skirmish_world
    from rotk_env.prefabs.config import Faction, PlayerType
    from rotk_env.utils.unit_spatial_index import rebuild_unit_spatial_index
    from rotk_env.utils.parallel_observation import ParallelObservationService
    from rotk_env.components import Unit, UnitCount, HexPosition, FogOfWar, MovementPoints, ActionPoints
    def census(world):
        ids = sorted(world.query().with_component(Unit).entities())
        values = []
        alive = 0
        for uid in ids:
            unit = world.get_component(uid, Unit)
            count = world.get_component(uid, UnitCount)
            pos = world.get_component(uid, HexPosition)
            ap = world.get_component(uid, ActionPoints)
            mp = world.get_component(uid, MovementPoints)
            alive += bool(count and count.current_count > 0)
            values.append((uid, unit.faction.value, count.current_count if count else None,
                (pos.col, pos.row) if pos else None, ap.current_ap if ap else None,
                mp.current_mp if mp else None))
        fog = world.get_singleton_component(FogOfWar)
        visible = sorted((f.value, sorted(cells)) for f, cells in fog.faction_vision.items()) if fog else None
        return {'units':len(ids), 'alive':alive, 'revision':world.revision,
            'fog_enabled':bool(fog and fog.enabled),
            'state_sha256':hashlib.sha256(json.dumps((values,visible)).encode()).hexdigest()}
    source, tooling = identity(a.source), identity(Path(__file__).resolve().parents[1])
    with open(os.devnull, 'w') as sink, redirect_stdout(sink):
        scenario, fixture_sha = fixture(a.source, a.units)
        world = build_skirmish_world(players={f: PlayerType.AI for f in Faction},
            mode='real_time', scenario=scenario, seed=42, display='none', hub_url=None)
        world.update(1/24)
        rebuild_unit_spatial_index(world)
        agents = LocalAgents(world, a.agents, 30, scope='selected', encode=True)
        # Cycle through all factions, rather than a prefix of one faction.
        groups = {}
        for session in agents.sessions:
            groups.setdefault(session.faction, []).append(session)
        ordered = [group[i] for i in range(max(map(len, groups.values())))
                   for group in groups.values() if i < len(group)]
        requests = [(s, {'faction':s.faction, 'unit_ids':s.units})
                    for s in (ordered[i % len(ordered)] for i in range(a.queries))]
        expected = [agents.call(s, 'get_faction_state', params) for s, params in requests]
        expected_hash = hashlib.sha256(json.dumps(expected, sort_keys=True).encode()).hexdigest()
        before = census(world)
        worker_pids = ()
        service = ParallelObservationService(agents.gate, workers=a.workers,
                    max_pending=a.max_pending) if a.workers else None
        try:
            if service:
                worker_pids = service.warmup()
                assert len(set(worker_pids)) == a.workers
                for i, (s, params) in enumerate(requests[:max(4, a.workers*2)]):
                    service.submit(s.agent_id, -i, params).result(timeout=30)
            rows, pending = [], {}
            started = time.perf_counter()
            def consume(f):
                i, begin, export_ms, admission_ms = pending.pop(f)
                reply = f.result(timeout=30)
                arrived = time.perf_counter()
                response = json.loads(reply.payload)
                end = time.perf_counter()
                assert response == expected[i], f'Query {i} differs'
                rows.append({'query':i, 'export_ms':export_ms, 'admission_ms':admission_ms,
                    'response_ms':(end-begin)*1000, 'decode_ms':(end-arrived)*1000,
                    'bytes':len(reply.payload), 'equal':True, **reply.metrics})
            for i, (s, params) in enumerate(requests):
                begin = time.perf_counter()
                if service:
                    while len(pending) >= a.max_pending:
                        done, _ = wait(pending, timeout=30, return_when=FIRST_COMPLETED)
                        if not done:
                            raise TimeoutError('worker stalled')
                        for f in done:
                            consume(f)
                    begin = time.perf_counter()
                    f = service.submit(s.agent_id, i, params)
                    pending[f] = (i, begin, service.last_export_ms,
                                  (time.perf_counter()-begin)*1000)
                else:
                    response = agents.call(s, 'get_faction_state', params)
                    built = time.perf_counter()
                    payload = json.dumps(response, ensure_ascii=False).encode()
                    encoded = time.perf_counter()
                    assert json.loads(payload) == expected[i]
                    end = time.perf_counter()
                    rows.append({'query':i, 'build_ms':(built-begin)*1000,
                        'encode_ms':(encoded-built)*1000, 'decode_ms':(end-encoded)*1000,
                        'response_ms':(end-begin)*1000, 'bytes':len(payload), 'equal':True})
            for f in list(pending):
                consume(f)
            wall = time.perf_counter()-started
        finally:
            if service:
                service.close()
        after = census(world)
    result = {'kind':'frozen diagnostic, NOT runtime capacity', 'source':source, 'tooling':tooling,
        'workload':vars(a), 'fixture_sha256':fixture_sha, 'expected_sha256':expected_hash,
        'machine':{'platform':platform.platform(), 'python':sys.version, 'cpu_count':os.cpu_count()},
        'census_before':before, 'census_after':after, 'registered_sessions':len(agents.sessions),
        'warmed_worker_pids':worker_pids,
        'guards':{'source_clean':not source['dirty'], 'tooling_clean':not tooling['dirty'],
            'world_unchanged':before == after, 'unit_count':before['units'] == a.units,
            'alive_count':before['alive'] == a.units, 'agents_registered':len(agents.sessions) == a.agents,
            'fog_on':before['fog_enabled'], 'complete':len(rows) == a.queries,
            'workers_warmed':len(set(worker_pids)) == a.workers},
        'wall_seconds':wall, 'requests_per_second':len(rows)/wall, 'rows':rows,
        'rss_self_max':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'rss_children_max':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        'summary':{k:stats([r[k] for r in rows if k in r]) for k in (
            'export_ms','admission_ms','restore_ms','build_ms','encode_ms','decode_ms',
            'worker_queue_ipc_ms','response_ms','snapshot_bytes','bytes')},
        'all_equal':all(r['equal'] for r in rows)}
    path = Path(a.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('all_equal','requests_per_second','summary')}, indent=2))


if __name__ == '__main__':
    main()
