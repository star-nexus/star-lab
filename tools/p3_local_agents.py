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
    return {'count': len(values), 'min': ordered[0], 'avg': sum(values) / len(values),
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
        # Diagnostic only: distinguish cold construction from cache lookup.
        try:
            from rotk_env.utils.observation_batch import ObservationBatchContext
        except ImportError:
            ObservationBatchContext = None
        if ObservationBatchContext is not None:
            original_memo = ObservationBatchContext.memo
            def timed_memo(context, kind, key, build):
                cached = context._cache.get(kind, {})
                hit = context.reuse and key in cached
                start = time.perf_counter()
                try:
                    return original_memo(context, kind, key, build)
                finally:
                    row = self.values['batch.' + kind + ('.hit' if hit else '.build')]
                    row[0] += 1
                    row[1] += (time.perf_counter()-start)*1000
            self.originals.append((ObservationBatchContext, 'memo', original_memo))
            ObservationBatchContext.memo = timed_memo
        from rotk_env.utils import map_query
        for name in ('unit_cells', 'occupied_cells', 'path_blockers', 'plan_hex_path'):
            original = getattr(map_query, name)
            def wrapped(*args, _original=original, _name=name, **kwargs):
                start = time.perf_counter()
                try:
                    return _original(*args, **kwargs)
                finally:
                    row = self.values['map_query.'+_name]
                    row[0] += 1
                    row[1] += (time.perf_counter()-start)*1000
            self.originals.append((map_query, name, original))
            setattr(map_query, name, wrapped)


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
    thinking: bool = False


class LocalAgents:
    def __init__(self, world, count, delay=1.0, *, scope='faction', encode=True,
                 policy='mixed', seed=42, clock=time.perf_counter, max_records=2_000_000,
                 observation_hz=None, observation_mode="single", cycle_mode="legacy", jitter_seconds=5.0):
        from rotk_env.components import Unit, UnitCount
        self.world, self.clock = world, clock
        self.gate = next(s for s in world.systems if s.__class__.__name__ == 'LLMSystem')
        self.scope, self.encode, self.policy = scope, encode, policy
        if observation_hz is not None and observation_hz <= 0:
            raise ValueError("observation_hz must be positive")
        if observation_mode not in ('single', 'batch-off', 'batch-on'):
            raise ValueError('Unknown observation mode')
        if observation_mode != 'single' and not encode:
            raise ValueError('Batch boundary requires encoding')
        if cycle_mode == 'post-action' and (observation_hz is not None or observation_mode != 'single'):
            raise ValueError('Post-action cycles require single observations and no independent polling')
        self.cycle_mode = cycle_mode
        self.jitter_seconds = jitter_seconds
        self.timing_seed = seed + 100000
        self.initial_offsets = []
        self.delay_rngs = []
        self.observation_mode = observation_mode
        self.batch_metrics = Counter()
        self.observation_hz = observation_hz
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
        self.delay_rngs = [random.Random(self.timing_seed+i) for i in range(len(self.sessions))]

    def call(self, session, verb, params):
        self.request_id += 1
        return self.gate._process_action_request(agent_id=session.agent_id,
            action_id=self.request_id, action=verb, params=dict(params), send_response=False)

    def start(self, now=None, synchronized=False):
        self.epoch = self.clock() if now is None else now
        phase_rng = random.Random(self.timing_seed - 1)
        for i, session in enumerate(self.sessions):
            period = 1/self.observation_hz if self.observation_hz else session.delay
            offset = 0 if synchronized else (i / len(self.sessions)) * period
            if self.cycle_mode == 'post-action' and not synchronized:
                offset = phase_rng.uniform(0, session.delay)
            self.initial_offsets.append(offset)
            session.cycle_due = self.epoch + offset
            self._push(session.cycle_due, 'observe', i)

    def _push(self, due, event, index):
        self.serial += 1
        heapq.heappush(self.heap, (due, self.serial, event, index))

    def _consume_observation(self, response, row, session, index, due):
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
            if self.policy == 'stochastic':
                choice = self.rng.random()
                verb = 'move' if choice < .5 else 'attack' if choice < .75 else 'wait'
                self.counts['chosen_'+verb] += 1
                if verb == 'move' and cells:
                    actions.append(('move', {'unit_id': uid, 'target_position': self.rng.choice(cells)}))
                elif verb == 'attack' and targets:
                    actions.append(('attack', {'unit_id': uid, 'target_id': self.rng.choice(targets)}))
                else:
                    self.counts['idle_units'] += 1
                    if verb != 'wait':
                        self.counts['unavailable_'+verb] += 1
            elif self.policy == 'mixed' and targets:
                actions.append(('attack', {'unit_id': uid, 'target_id': self.rng.choice(targets)}))
            elif self.policy != 'observe' and cells:
                actions.append(('move', {'unit_id': uid, 'target_position': self.rng.choice(cells)}))
        # Telemetry may arrive while a slow decision is in flight. Keep
        # that decision's original snapshot/action set until it completes.
        if not session.thinking:
            session.actions = actions
            session.observed_at = self.clock()
            session.thinking = True
            self._push(session.observed_at + (0 if self.cycle_mode == 'post-action' else session.delay), 'act', index)
        if self.observation_hz:
            # Retain scheduled deadlines under overload; no coalescing,
            # drop, or completion-relative throttling hides offered load.
            self._push(due + 1/self.observation_hz, 'observe', index)
        self.counts['observations'] += 1

    def _pump_observation_batch(self, remaining_ms):
        cutoff = self.clock()
        entries = []
        horizon = cutoff
        # Never look past an action or include a future request. Original heap
        # serials are retained for the unconsumed suffix.
        while (self.heap and len(entries) < 32 and self.heap[0][0] <= horizon
               and self.heap[0][2] == 'observe'):
            entries.append(heapq.heappop(self.heap))
            if self.observation_hz:
                horizon = min(horizon, entries[-1][0] + 1/self.observation_hz)
        requests = []
        for due, serial, event, index in entries:
            session = self.sessions[index]
            params = {'faction': session.faction}
            if self.scope == 'selected':
                params['unit_ids'] = session.units
            self.request_id += 1
            requests.append({'agent_id': session.agent_id,
                             'action_id': self.request_id, 'params': params})
        before = self.clock()
        result = self.gate.process_observation_batch(
            requests, budget_ms=max(0, remaining_ms - (before-cutoff)*1000),
            reuse=self.observation_mode == 'batch-on')
        available = self.clock()
        consumed = result['consumed']
        for entry in entries[consumed:]:
            heapq.heappush(self.heap, entry)
        self.batch_metrics.update(result['cache_metrics'])
        self.batch_metrics['batches'] += 1
        self.batch_metrics['requests'] += consumed
        for entry, item in zip(entries[:consumed], result['responses']):
            due, serial, event, index = entry
            session = self.sessions[index]
            # Every response becomes available at batch return. Individual build
            # completion times must not make queue latency look artificially low.
            row = {'t': before-self.epoch, 'event': event, 'agent': index,
                   'queue_ms': max(0, before-due)*1000,
                   'nominal_cycle_lag_ms': max(0, before-session.cycle_due)*1000,
                   'build_ms': item['build_ms'], 'encode_ms': item['encode_ms'],
                   'bytes': len(item['payload']), 'batch_size': consumed,
                   'batch_return_ms': max(0, available-due)*1000}
            decode_start = self.clock()
            response = json.loads(item['payload'])
            row['decode_ms'] = (self.clock()-decode_start)*1000
            if not response.get('success'):
                raise RuntimeError(f'Observation failed: {response}')
            self._consume_observation(response, row, session, index, due)
            row['service_ms'] = (self.clock()-before)*1000
            row['response_ms'] = row['queue_ms'] + row['service_ms']
            if len(self.records) >= self.max_records:
                raise RuntimeError('event recorder overflow; no capacity claim')
            self.records.append(row)
        return consumed

    def pump(self, budget_ms=4.0):
        start = self.clock()
        while self.heap and self.heap[0][0] <= self.clock():
            if (self.clock() - start) * 1000 >= budget_ms:
                break
            if self.observation_mode != 'single' and self.heap[0][2] == 'observe':
                if not self._pump_observation_batch(budget_ms-(self.clock()-start)*1000):
                    break
                continue
            due, _, event, index = heapq.heappop(self.heap)
            session = self.sessions[index]
            begin = self.clock()
            row = {'t': begin - self.epoch, 'event': event, 'agent': index,
                   'queue_ms': max(0, begin - due) * 1000}
            row['nominal_cycle_lag_ms'] = max(0, begin-session.cycle_due)*1000
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
                # All three modes include the same JSON client boundary.
                if self.encode:
                    decode_start = self.clock()
                    response = json.loads(payload)
                    row['decode_ms'] = (self.clock() - decode_start) * 1000
                self._consume_observation(response, row, session, index, due)
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
                # A real sequential LLM session cannot offer its next pull until
                # its previous response/action completes. Separate this actual
                # ready time from nominal cycle lag; report achieved/ideal load.
                session.thinking = False
                if not self.observation_hz:
                    if self.cycle_mode == 'post-action':
                        think = self._sample_delay(self.delay_rngs[index], session.delay)
                        row['think_seconds'] = think
                        session.cycle_due = self.clock() + think
                        self._push(session.cycle_due, 'observe', index)
                    else:
                        self._push(self.clock(), 'observe', index)
                self.counts['cycles'] += 1
            row['service_ms'] = (self.clock() - begin) * 1000
            row['response_ms'] = row['queue_ms'] + row['service_ms']
            if len(self.records) >= self.max_records:
                raise RuntimeError('event recorder overflow; no capacity claim')
            self.records.append(row)

    def _sample_delay(self, rng, mean):
        # Rejection sampling gives a bounded normal, rather than point masses
        # at the clipping limits. Timing RNG is independent of action choices.
        while True:
            value = rng.gauss(mean, self.jitter_seconds)
            if mean/2 <= value <= mean*1.5:
                return value

    def nominal_closed_loop_observations(self, warmup, duration):
        count = 0
        for i, session in enumerate(self.sessions):
            rng = random.Random(self.timing_seed+i)
            due = self.initial_offsets[i]
            while due < warmup+duration:
                count += due >= warmup
                due += self._sample_delay(rng, session.delay)
        return count

    def summary(self):
        now = self.clock()
        due = [entry for entry in self.heap if entry[0] <= now]
        return {'counts': dict(self.counts), 'sessions': len(self.sessions),
                'batch_metrics': dict(self.batch_metrics), 'observation_mode': self.observation_mode,
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
