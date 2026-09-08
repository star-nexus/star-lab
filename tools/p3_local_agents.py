"""Deterministic local Agent workload. Lab-only; imports the selected STAR checkout.

The transport boundary is LLMSystem._process_action_request(send_response=False).
No state edits substitute for registration, ownership or actions. Thinking is a
scheduled deadline, never a sleep in the world loop. An overdue cycle retains
its original deadline so queue delay cannot disappear under overload.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
import hashlib
import heapq
import json
import math
from pathlib import Path
import random
import subprocess
import sys
import time
import zipfile


def identity(root):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()
    return {'path': str(root), 'sha': git('rev-parse', 'HEAD'),
            'dirty': git('status', '--porcelain', '--untracked-files=no')}


def fixture(source, units, layout='canonical'):
    lab = Path(__file__).resolve().parents[1]
    archive = lab / 'experiments/2026-09-10k-e8-volume/artifacts/scenario.zip'
    with zipfile.ZipFile(archive) as z:
        data = json.loads(z.read('chibi-144k-scale-10000.json'))
    names = list(data['formations'])
    if layout == 'canonical':
        for i, name in enumerate(names):
            data['formations'][name] = data['formations'][name][:units // 3 + (i < units % 3)]
    else:
        # A separate actionable fixture: gaps for movement, nearby opposing units.
        from rotk_env.maps.ascii_map import parse_ascii_map
        board = parse_ascii_map('\n'.join(data['terrain']), width=data['width'], height=data['height'])
        cells = [cell for cell in sorted(board) if sum(cell) % 4 != 0]
        random.Random(42).shuffle(cells)
        data['formations'] = {name: [] for name in names}
        for i, cell in enumerate(cells[:units]):
            data['formations'][names[i % 3]].append(cell)
    name = f'lab-p3-{layout}-{units}'
    data['id'] = name
    data['name'] = name
    data.pop('scale_profile', None)
    payload = (json.dumps(data, separators=(',', ':')) + '\n').encode()
    path = Path(source) / 'rotk_env/maps' / (name + '.json')
    path.write_bytes(payload)
    return name, hashlib.sha256(payload).hexdigest()


def stats(values):
    if not values:
        return {'count': 0}
    ordered = sorted(values)
    def p(q):
        return ordered[max(0, math.ceil(q * len(ordered)) - 1)]
    return {'count': len(values), 'avg': sum(values) / len(values),
            'p50': p(.5), 'p95': p(.95), 'p99': p(.99), 'max': ordered[-1]}


class Attribution:
    """Diagnostic-only inclusive helper timings and causal call counts."""
    def __init__(self, handler):
        self.values = defaultdict(lambda: [0, 0.0])
        self.originals = []
        for name in ('_get_faction_units', '_get_faction_status', '_get_detailed_unit_info',
                     '_unit_command_fields', '_visible_enemy_units', '_visible_terrain',
                     '_unit_reachable', '_unit_attackable'):
            original = getattr(handler, name)
            def wrapped(*args, _original=original, _name=name, **kwargs):
                start = time.perf_counter()
                try:
                    return _original(*args, **kwargs)
                finally:
                    row = self.values[_name]
                    row[0] += 1
                    row[1] += (time.perf_counter() - start) * 1000
            self.originals.append((handler, name, original))
            setattr(handler, name, wrapped)


@dataclass
class Session:
    agent_id: str
    faction: str
    units: list[int]
    delay: float
    actions: list = field(default_factory=list)
    observed_at: float = 0.0
    cycle_due: float = 0.0
    completed: int = 0


class LocalAgents:
    def __init__(self, world, count, delay=1.0, *, scope='faction', encode=True,
                 policy='mixed', seed=42, clock=time.perf_counter, max_records=2_000_000):
        from rotk_env.components import Unit, UnitCount
        self.world, self.clock = world, clock
        self.gate = next(s for s in world.systems if s.__class__.__name__ == 'LLMSystem')
        self.scope, self.encode, self.policy = scope, encode, policy
        self.rng = random.Random(seed)
        self.sessions = []
        self.heap = []
        self.serial = 0
        self.request_id = 0
        self.counts = Counter()
        self.records = []
        self.max_records = max_records
        by_faction = defaultdict(list)
        for uid in sorted(world.query().with_component(Unit).entities()):
            unit = world.get_component(uid, Unit)
            amount = world.get_component(uid, UnitCount)
            if amount and amount.current_count > 0:
                by_faction[unit.faction.value].append(uid)
        factions = sorted(by_faction)
        if not len(factions) <= count <= sum(map(len, by_faction.values())):
            raise ValueError('Need at least one Agent per faction and one Unit per Agent')
        allocations = {f: 1 for f in factions}
        for _ in range(count - len(factions)):
            f = max(factions, key=lambda f: len(by_faction[f]) / allocations[f]
                    if allocations[f] < len(by_faction[f]) else -1)
            allocations[f] += 1
        start = clock()
        for f in factions:
            for j in range(allocations[f]):
                aid = f'p3-{f}-{j}'
                owned = by_faction[f][j::allocations[f]]
                think = (1, 5, 15, 60)[len(self.sessions) % 4] if delay == 'mixed' else float(delay)
                session = Session(aid, f, owned, think)
                registration = self.call(session, 'register_agent_info', {
                    'faction': f, 'provider': 'synthetic', 'model_id': 'deterministic',
                    'base_url': 'http://localhost', 'agent_id': aid})
                if not registration.get('success'):
                    raise RuntimeError(f'Registration failed: {registration}')
                claim = self.call(session, 'claim_units', {'unit_ids': owned})
                if not claim.get('success') or claim.get('claimed') != owned:
                    raise RuntimeError(f'Claim failed: {claim}')
                self.sessions.append(session)
        self.setup_ms = (clock() - start) * 1000
        self.epoch = None

    def call(self, session, verb, params):
        self.request_id += 1
        return self.gate._process_action_request(agent_id=session.agent_id,
            action_id=self.request_id, action=verb, params=dict(params), send_response=False)

    def start(self, now=None, synchronized=False):
        self.epoch = self.clock() if now is None else now
        for i, session in enumerate(self.sessions):
            offset = 0 if synchronized else (i / len(self.sessions)) * session.delay
            session.cycle_due = self.epoch + offset
            self._push(session.cycle_due, 'observe', i)

    def _push(self, due, event, index):
        self.serial += 1
        heapq.heappush(self.heap, (due, self.serial, event, index))

    def pump(self, budget_ms=4.0):
        start = self.clock()
        while self.heap and self.heap[0][0] <= self.clock():
            if (self.clock() - start) * 1000 >= budget_ms:
                break
            due, _, event, index = heapq.heappop(self.heap)
            session = self.sessions[index]
            begin = self.clock()
            row = {'t': begin - self.epoch, 'event': event, 'agent': index,
                   'queue_ms': max(0, begin - due) * 1000}
            if event == 'observe':
                params = {'faction': session.faction}
                if self.scope == 'selected':
                    params['unit_ids'] = session.units
                response = self.call(session, 'get_faction_state', params)
                constructed = self.clock()
                if not response.get('success'):
                    raise RuntimeError(f'Observation failed: {response}')
                if self.encode:
                    payload = json.dumps(response, separators=(',', ':'), ensure_ascii=False).encode()
                    row['bytes'] = len(payload)
                row['build_ms'] = (constructed - begin) * 1000
                row['encode_ms'] = (self.clock() - constructed) * 1000
                rows = response.get('units', [])
                row['returned_units'] = len(rows)
                row['reachable'] = sum(len(u.get('reachable', [])) for u in rows)
                row['attackable'] = sum(len(u.get('attackable', [])) for u in rows)
                row['terrain'] = len(response.get('visible_terrain', []))
                row['enemies'] = len(response.get('visible_enemy_units', []))
                owned = set(session.units)
                actions = []
                for unit in rows:
                    uid = unit['unit_id']
                    if uid not in owned or not unit.get('commandable', True):
                        continue
                    targets = unit.get('attackable', [])
                    cells = unit.get('reachable', [])
                    if self.policy == 'mixed' and targets:
                        actions.append(('attack', {'unit_id': uid, 'target_id': self.rng.choice(targets)}))
                    elif self.policy != 'observe' and cells:
                        actions.append(('move', {'unit_id': uid, 'target_position': self.rng.choice(cells)}))
                session.actions = actions
                session.observed_at = self.clock()
                self._push(session.observed_at + session.delay, 'act', index)
                self.counts['observations'] += 1
            else:
                row['snapshot_age_ms'] = (begin - session.observed_at) * 1000
                row['actions'] = []
                # One session event may contain several unit actions; total cost remains measured.
                for verb, params in session.actions:
                    response = self.call(session, verb, params)
                    accepted = bool(response.get('success', response.get('result', False)))
                    self.counts[verb + ('_accepted' if accepted else '_rejected')] += 1
                    row['actions'].append({'verb': verb, 'unit': params['unit_id'],
                                           'accepted': accepted, 'error': response.get('error_code', response.get('error'))})
                if not session.actions:
                    self.counts['wait_cycles'] += 1
                session.actions = []
                session.completed += 1
                session.cycle_due += session.delay
                self._push(session.cycle_due, 'observe', index)
                self.counts['cycles'] += 1
            row['service_ms'] = (self.clock() - begin) * 1000
            row['response_ms'] = row['queue_ms'] + row['service_ms']
            if len(self.records) >= self.max_records:
                raise RuntimeError('event recorder overflow; no capacity claim')
            self.records.append(row)

    def summary(self):
        now = self.clock()
        due = [entry for entry in self.heap if entry[0] <= now]
        return {'counts': dict(self.counts), 'sessions': len(self.sessions),
                'setup_ms': self.setup_ms, 'pending_events': len(self.heap),
                'overdue_events': len(due), 'oldest_overdue_ms': max([0] + [(now-e[0])*1000 for e in due]),
                'cycles_per_session': stats([s.completed for s in self.sessions]),
                'observation_response_ms': stats([r['response_ms'] for r in self.records if r['event']=='observe']),
                'action_queue_ms': stats([r['queue_ms'] for r in self.records if r['event']=='act']),
                'response_bytes': stats([r['bytes'] for r in self.records if 'bytes' in r])}


def probe(args):
    from rotk_env.prefabs.world_builder import build_skirmish_world
    from rotk_env.prefabs.config import Faction, PlayerType
    scenario, sha = fixture(args.source, args.units, args.layout)
    world = build_skirmish_world(players={f: PlayerType.AI for f in Faction},
        mode='real_time', scenario=scenario, seed=42, display='none', hub_url=None)
    world.update(1/30)
    if args.index:
        from rotk_env.utils.unit_spatial_index import rebuild_unit_spatial_index
        rebuild_unit_spatial_index(world)
    agents = LocalAgents(world, args.agents, args.delay, scope=args.scope, encode=True)
    attribution = Attribution(agents.gate.action_handler) if args.attribute else None
    samples = []
    for i in range(args.queries):
        session = agents.sessions[i % len(agents.sessions)]
        params = {'faction': session.faction}
        if args.scope == 'selected':
            params['unit_ids'] = session.units
        start = time.perf_counter()
        response = agents.call(session, 'get_faction_state', params)
        end = time.perf_counter()
        encoded = json.dumps(response, separators=(',', ':'), ensure_ascii=False).encode()
        samples.append({'build_ms': (end-start)*1000,
            'encode_ms': (time.perf_counter()-end)*1000, 'bytes':len(encoded),
            'success': response.get('success'), 'units':len(response.get('units', [])),
            'reachable':sum(len(u.get('reachable', [])) for u in response.get('units', [])),
            'attackable':sum(len(u.get('attackable', [])) for u in response.get('units', []))})
    return {'kind':'static diagnostic, NOT runtime capacity', 'source':identity(args.source),
        'tooling':identity(Path(__file__).resolve().parents[1]),
        'workload':vars(args), 'fixture_sha256':sha, 'setup_ms':agents.setup_ms,
        'samples':samples, 'attribution':dict(attribution.values) if attribution else None}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--units', type=int, default=100)
    parser.add_argument('--agents', type=int, default=100)
    parser.add_argument('--queries', type=int, default=3)
    parser.add_argument('--delay', type=float, default=1)
    parser.add_argument('--scope', choices=['faction', 'selected'], default='faction')
    parser.add_argument('--layout', choices=['canonical', 'interleaved'], default='canonical')
    parser.add_argument('--attribute', action='store_true')
    parser.add_argument('--index', action='store_true', help='Build the production window index for this static diagnostic')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.source)
    result = probe(args)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=2)+'\n')
