"""Verify fixed-stream guards and summarize System cost / read-sharing opportunity."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--trace', type=Path, required=True)
    args = parser.parse_args()
    results = args.root / 'results'
    baseline = json.loads((results / 'frozen-t1.json').read_text())
    trace_hash = hashlib.sha256(args.trace.read_bytes()).hexdigest()
    assert trace_hash == baseline['trace_sha256']
    trace = json.loads(gzip.decompress(args.trace.read_bytes()))
    observations = 0
    repeated_factions = 0
    repeated_panels = 0
    factions, panels, lengths, barriers = Counter(), set(), Counter(), Counter()
    query_count = 0

    def finish(barrier):
        nonlocal repeated_factions, repeated_panels, query_count
        if not query_count:
            return
        lengths[query_count] += 1
        barriers[barrier] += 1
        repeated_factions += query_count - len(factions)
        repeated_panels += panel_references[0] - len(panels)
        factions.clear()
        panels.clear()
        panel_references[0] = 0
        query_count = 0

    panel_references = [0]
    for op in trace['entries']:
        if op['kind'] != 'request' or op['action'] != 'get_faction_state':
            finish(op['kind'] if op['kind'] != 'request' else 'action:'+str(op['action']))
            continue
        query_count += 1
        observations += 1
        params = op['parameters']
        factions[params['faction']] += 1
        ids = params.get('unit_ids')
        assert isinstance(ids, list), 'This workload analyzer requires explicit subsets'
        unique = set(ids)
        panel_references[0] += len(unique)
        panels.update(unique)
    finish('end')
    assert dict(lengths) == {int(k): v for k, v in baseline['read_segment_histogram'].items()}
    candidates = {}
    for threads in (1, 2, 4):
        run = json.loads((results / f'candidate-t{threads}.json').read_text())
        assert run['all_passed'] and baseline['all_passed']
        for key in ('counts', 'stream_sha256', 'final_state_sha256', 'trace_sha256', 'initial_sha256', 'read_segment_histogram'):
            assert run[key] == baseline[key], (threads, key)
        raw = results / run['timing_raw']['file']
        assert hashlib.sha256(raw.read_bytes()).hexdigest() == run['timing_raw']['sha256']
        rows = json.loads(gzip.decompress(raw.read_bytes()))
        assert len(rows) == baseline['counts']['step']
        means = {name: data['mean_ns'] for name, data in run['phase_summary'].items()}
        total_mean = sum(row['native_ns'] for row in rows) / len(rows)
        assert all(row['native_ns'] >= sum(row['phases_ns'].values()) for row in rows)
        candidates[str(threads)] = dict(phase_mean_ms={k: v / 1e6 for k, v in means.items()},
                                        native_mean_ms=total_mean / 1e6,
                                        mean_unattributed_timer_map_ns=total_mean-sum(means.values()),
                                        scope='phase wall time in paired replay; not thread performance A/B')
    result = dict(all_passed=True, trace_sha256=trace_hash, counts=baseline['counts'],
                  stream_sha256=baseline['stream_sha256'], final_state_sha256=baseline['final_state_sha256'],
                  observations=observations, read_segment_histogram=dict(sorted(lengths.items())),
                  queries_in_multi_read_segments=sum(n*c for n, c in lengths.items() if n > 1),
                  multi_read_query_fraction=sum(n*c for n, c in lengths.items() if n > 1)/observations,
                  repeated_faction_requests_within_segment=repeated_factions,
                  repeated_faction_fraction=repeated_factions/observations,
                  repeated_selected_panel_references_within_segment=repeated_panels,
                  segment_end_barriers=dict(barriers), candidates=candidates,
                  interpretation='sharing opportunity only; not predicted latency reduction or scheduler feasibility',
                  analyzer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (results / 'comparison.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
