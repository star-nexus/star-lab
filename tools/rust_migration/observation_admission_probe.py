"""E8 P0 passive admission diagnostic around the frozen single-request pump.

No query is batched, rescheduled or issued for profiling. Diagnostic overhead
changes wall timing: this run establishes eligibility, never a speedup claim.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import heapq
import json
from pathlib import Path
import sys
import time

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / 'tools'))
import p3_local_agents as original
import p3_runtime

FROZEN = {
    'tools/p3_local_agents.py': 'a7f3bb1a7817f487ac748f93f36c902426c104fcffdfef554cade73671eda45b',
    'tools/p3_runtime.py': '2952f4944ee4f3a24740d5013e2e729ed1ac0ebdfea94ea0ef1e17fac43bf4a9',
}


def ready_prefix(heap, cutoff, maximum=4):
    """Read only the first bounded heap prefix; O(maximum log maximum).

    A frontier of heap indices avoids sorting/copying the entire admission heap.
    Stop at the first non-query/future entry; never skip an action.
    """
    if not heap:
        return [], 'empty'
    frontier = [(heap[0], 0)]
    prefix = []
    reason = 'limit'
    while frontier and len(prefix) < maximum:
        entry, i = heapq.heappop(frontier)
        if entry[0] > cutoff:
            reason = 'future'
            break
        if entry[2] != 'observe':
            reason = 'action'
            break
        prefix.append(entry)
        for j in (2*i+1, 2*i+2):
            if j < len(heap):
                heapq.heappush(frontier, (heap[j], j))
    if not frontier and len(prefix) < maximum and reason == 'limit':
        reason = 'empty'
    return prefix, reason


class DiagnosticAgents(original.LocalAgents):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admission = []
        self.segments = []
        self.pumps = []
        self.segment = None
        self.pump_id = 0
        self._query_original = self.observation_json_call
        if self._query_original is not None:
            self.observation_json_call = self._query

    def _query(self, session, params):
        before = time.perf_counter_ns()
        wire = self._query_original(session, params)
        self.admission[-1].update(native_wire_ns=time.perf_counter_ns()-before,
                                  params=dict(params), request_id=self.request_id,
                                  wire_characters=len(wire))
        return wire

    def _close_segment(self, reason):
        if self.segment is not None:
            self.segment['close_reason'] = reason
            self.segments.append(self.segment)
            self.segment = None

    def _before_pop(self, heap):
        cutoff = self.clock()
        head = heap[0]
        if self.segment is not None and (
                self.segment['next'] >= len(self.segment['frozen']) or
                list(head) != self.segment['frozen'][self.segment['next']]):
            self._close_segment('new_head_or_frozen_end')
        prefix, barrier = ready_prefix(heap, cutoff)
        if head[2] == 'observe' and self.segment is None:
            self.segment = dict(id=len(self.segments), pump=self.pump_id,
                                cutoff=cutoff, frozen=[list(e) for e in prefix],
                                next=0, executed=[], prefix_barrier=barrier)
        if head[2] != 'observe':
            self._close_segment('action')
        row = dict(pump=self.pump_id, ordinal=len(self.admission), entry=list(head),
                   cutoff=cutoff, queue_size=len(heap),
                   prefix=[list(e) for e in prefix], prefix_barrier=barrier,
                   record_index=len(self.records))
        if self.segment is not None:
            row['segment_id'] = self.segment['id']
            self.segment['executed'].append(head[1])
            self.segment['next'] += 1
        self.admission.append(row)

    def pump(self, budget_ms=4.0):
        owner = self
        class HeapView:
            def __getattr__(self, name):
                return getattr(heapq, name)
            def heappop(self, heap):
                owner._before_pop(heap)
                return heapq.heappop(heap)
        began = self.clock()
        count = len(self.records)
        saved = original.heapq
        original.heapq = HeapView()
        try:
            # Execute the frozen body. The only replacement is a read-only
            # diagnostic immediately before its existing single heappop.
            super().pump(budget_ms)
        finally:
            original.heapq = saved
            ended = self.clock()
            head = list(self.heap[0]) if self.heap else None
            reason = ('budget' if head and head[0] <= ended and
                      (ended-began)*1000 >= budget_ms else 'pump_end')
            self._close_segment(reason)
            self.pumps.append(dict(id=self.pump_id, start=began, end=ended,
                                   budget_ms=budget_ms, count=len(self.records)-count,
                                   head_after=head, close_reason=reason))
            self.pump_id += 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--diagnostic-output', type=Path, required=True)
    args, runtime_args = p.parse_known_args()
    for file, sha in FROZEN.items():
        assert hashlib.sha256((LAB/file).read_bytes()).hexdigest() == sha, file
    assert not args.diagnostic_output.exists(), 'No overwrite or automatic retry'
    instances = []
    class CapturedAgents(DiagnosticAgents):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            instances.append(self)
    p3_runtime.LocalAgents = CapturedAgents
    sys.argv = [sys.argv[0], *runtime_args]
    meta = p3_runtime.main()
    # Frozen runner contains a historical Chrome note and has no knowledge of
    # this probe. Do not propagate those labels as current environment/proof.
    meta['hardware'].pop('chrome', None)
    meta['hardware']['other_applications'] = 'not controlled; diagnostic only'
    meta['guards']['not_diagnostic'] = False
    meta['pass'] = False
    meta['e8_diagnostic'] = True
    Path(meta['workload']['output']).write_text(json.dumps(meta,indent=2)+'\n')
    assert len(instances) == 1
    agent = instances[0]
    assert len(agent.admission) == len(agent.records)
    for a, r in zip(agent.admission, agent.records):
        assert a['entry'][2:] == [r['event'], r['agent']]
        a['service'] = r
    result = dict(schema='star-e8-admission-p0-v1', frozen_tools=FROZEN,
                  source=meta['source'], extension=meta['extension'],
                  diagnostic_only=True, speedup_claim=False,
                  pump_boundary='each pump ends segment before world update',
                  callback_boundary='NativeLoopTrace.payload only records hash; consume audited LocalAgents',
                  admission=agent.admission, segments=agent.segments, pumps=agent.pumps)
    args.diagnostic_output.write_text(json.dumps(result,separators=(',',':'))+'\n')
    measured = [s for s in agent.segments if s['executed'] and
                s['cutoff']-agent.epoch >= meta['workload']['warmup']]
    lengths = Counter(len(s['executed']) for s in measured)
    print(json.dumps(dict(diagnostic='complete', dequeues=len(agent.admission),
                          measured_segment_lengths=dict(lengths)),sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
