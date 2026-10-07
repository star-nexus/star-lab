"""Small contracts for E8's passive diagnostic; no production source changes."""
import copy
import heapq
import json
import random
from collections import Counter
from observation_admission_probe import DiagnosticAgents, ready_prefix, original


def make(kind):
    a = kind.__new__(kind)
    a.clock = lambda: 10.0
    a.epoch = 0.0
    a.observation_mode = 'single'
    a.scope = 'selected'
    a.encode = True
    a.policy = 'observe'
    a.cycle_mode = 'post-action'
    a.observation_hz = None
    a.jitter_seconds = 5
    a.rng = random.Random(42)
    a.delay_rngs = [random.Random(100042+i) for i in range(4)]
    a.serial = 4
    a.request_id = 0
    a.counts = Counter()
    a.records = []
    a.max_records = 100
    a.sessions = [original.Session(f'a{i}', 'wei', [i+1], 30) for i in range(4)]
    a.heap = [(5.0+i, i+1, 'observe', i) for i in range(4)]
    a.request_call = lambda session, verb, params: dict(success=True)
    a.payload_callback = None
    a.observation_json_call = lambda session, params: json.dumps(dict(success=True, units=[], visible_terrain=[], enemy_units=[]))
    if kind is DiagnosticAgents:
        a.admission = []
        a.segments = []
        a.pumps = []
        a.segment = None
        a.pump_id = 0
        a._query_original = a.observation_json_call
        a.observation_json_call = a._query
    return a


def main():
    rng = random.Random(42)
    # Compare bounded heap frontier with a full ordering oracle; input immutable.
    for _ in range(300):
        heap = [(rng.randrange(10), i, rng.choice(('observe','observe','act')), i) for i in range(rng.randrange(1,100))]
        heapq.heapify(heap)
        before = copy.deepcopy(heap)
        expected = []
        for e in sorted(heap):
            if e[0] > 5 or e[2] != 'observe' or len(expected) == 4:
                break
            expected.append(e)
        assert ready_prefix(heap, 5)[0] == expected
        assert heap == before
    base, diag = make(original.LocalAgents), make(DiagnosticAgents)
    base.pump(8)
    diag.pump(8)
    assert base.records == diag.records
    assert base.heap == diag.heap and base.request_id == diag.request_id
    assert base.counts == diag.counts and base.sessions == diag.sessions
    assert base.rng.getstate() == diag.rng.getstate()
    assert [x.getstate() for x in base.delay_rngs] == [x.getstate() for x in diag.delay_rngs]
    assert len(diag.segments[0]['executed']) == 4
    # Consume inserts a ready event ahead of the frozen second query: the
    # diagnostic must close the old segment and retain original dequeue order.
    base, diag = make(original.LocalAgents), make(DiagnosticAgents)
    for a in (base, diag):
        consume = a._consume_observation
        def inserted(*args, _a=a, _consume=consume):
            _consume(*args)
            if _a.counts['observations'] == 1:
                _a._push(5.5, 'act', 0)
        a._consume_observation = inserted
    base.pump(8)
    diag.pump(8)
    assert base.records == diag.records and base.heap == diag.heap
    assert len(diag.segments[0]['executed']) == 1
    assert diag.segments[0]['close_reason'] == 'new_head_or_frozen_end'
    print('PASS: 300 heap prefixes; unchanged pump/queue/requests/response consumption/RNG; inserted-head barrier')


if __name__ == '__main__':
    main()
