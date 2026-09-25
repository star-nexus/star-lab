"""Verify old/new and 1/2/4 read-panel results; retain every timing case."""
import argparse
import json
import lzma
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True)
    args = parser.parse_args()
    root = args.results
    scheduling = {'parallel_panel_batches', 'panel_tasks', 'panel_worker_threads'}
    comparisons = []
    for suffix in ('mp0', 'mp6-spaced'):
        names = [f'{name}-{suffix}' for name in ('before', 'after-t1', 'after-t2', 'after-t4')]
        data = [json.loads((root / name / 'compact.json').read_text()) for name in names]
        raw = [json.loads(lzma.decompress((root / name / 'raw.json.xz').read_bytes())) for name in names]
        assert all(len(d['rows']) == 15 and d['all_guards_passed'] for d in data)
        for i in range(15):
            rows = [d['rows'][i] for d in data]
            reference = rows[0]
            for j, row in enumerate(rows):
                assert all(row[k] == reference[k] for k in (
                    'scenario', 'mode', 'requests', 'selected_units', 'initial_sha256',
                    'final_sha256', 'agent_response_sha256', 'reachable_cells'))
                assert raw[j][i]['response']['results'] == raw[0][i]['response']['results']
                assert {k: v for k, v in row['metrics'].items() if k not in scheduling} == reference['metrics']
                assert all({k: v for k, v in m.items() if k not in scheduling} == reference['metrics'] for m in row['sample_metrics'])
                if j and row['metrics']:
                    m = row['metrics']; threads = row['threads']
                    assert m['parallel_panel_batches'] == (0 if threads == 1 else 1)
                    assert m['panel_tasks'] <= threads
                    assert m['panel_worker_threads'] <= threads
                    assert (m['panel_worker_threads'] > 0) == (threads > 1)
            if suffix == 'mp6-spaced' and reference['scenario'] == 'units-5000':
                assert reference['reachable_cells'] > 0
            comparisons.append(dict(workload=suffix, scenario=reference['scenario'],
                mode=reference['mode'], requests=reference['requests'], reachable_cells=reference['reachable_cells'],
                medians_ms={n:r['median_ms'] for n,r in zip(names,rows)},
                t2_over_t1=rows[2]['median_ms']/rows[1]['median_ms'],
                t4_over_t1=rows[3]['median_ms']/rows[1]['median_ms'],
                full_agent_results_equal=True, initial_and_final_equal=True, original_work_counters_equal=True))
    result = dict(all_guards_passed=True, configurations=8, rows=120,
        paired_cases=30, capacity_claim=False, excluded_diagnostics=sorted(scheduling), cases=comparisons)
    (root / 'comparison.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: 30 cases x 4 configurations; full results, states and work counters equal')


if __name__ == '__main__':
    main()
