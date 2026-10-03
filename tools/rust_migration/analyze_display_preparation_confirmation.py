"""E7 single-instance ABBA confirmation; only accept complete matching runs."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np


def analyze(paths):
    metas = [json.loads(path.read_text()) for path in paths]
    assert len(metas) == 4
    assert [m['modes'] for m in metas] == [
        ['baseline'], ['empty_territory'], ['empty_territory'], ['baseline']]
    identity = ('source_sha', 'extension_sha256', 'trace_sha256', 'initial_sha256',
                'tool_sha256', 'display_script_sha256', 'dependency_lock_sha256',
                'display_clock', 'overscan_clock', 'surface', 'fixture_sha256',
                'consumer', 'threads', 'display_script', 'driver')
    rows = []
    for path, meta in zip(paths, metas):
        assert meta['task'] == 'single' and meta['formal'] and meta['all_passed']
        assert not meta['diagnostic'] and not meta['source_dirty']
        assert meta['consumer'] == 'baseline' and meta['threads'] == 4
        assert meta['overscan_clock'] == 'wall' and meta['driver'] == 'dummy'
        assert meta['counts'] == dict(request=40994, step=9880, presentation=9880)
        assert all(meta[key] == metas[0][key] for key in identity)
        assert meta['stream_sha256'] == metas[0]['stream_sha256']
        assert meta['final_state_sha256'] == metas[0]['final_state_sha256']
        data = (path.parent / meta['raw']['file']).read_bytes()
        assert hashlib.sha256(data).hexdigest() == meta['raw']['sha256']
        side = json.loads(gzip.decompress(data))
        assert len(side) == 1 and len(side[0]) == 9880
        rows.append(side[0])
    metrics = {}
    for key in ('render_ns', 'chain_ns', 'total_ns', 'display_ns', 'submit_ns', 'apply_ns'):
        raw = np.array([[r[key] for r in side] for side in rows], dtype=float)
        assert np.isfinite(raw).all() and (raw >= 0).all()
        baseline_pair = (raw[0] + raw[3]) / 2
        diff = baseline_pair - (raw[1] + raw[2]) / 2
        sums = np.array([diff[i:i+100].sum() for i in range(0, 9880, 100)])
        counts = np.array([len(diff[i:i+100]) for i in range(0, 9880, 100)])
        chosen = np.random.default_rng(42).integers(0, len(sums), (10000, len(sums)))
        ci = np.quantile(sums[chosen].sum(1) / counts[chosen].sum(1), [.025, .975]).tolist()

        def stats(v):
            v = np.sort(v)
            return dict(samples=len(v), mean_ns=float(v.mean()),
                        p99_ns=float(v[int(len(v)*.99)]), max_ns=float(v[-1]))

        baseline = stats(np.concatenate((raw[0], raw[3])))
        candidate = stats(np.concatenate((raw[1], raw[2])))
        improvement = float(diff.mean() / baseline_pair.mean() * 100)
        passed = (candidate['mean_ns'] < baseline['mean_ns']
                  and candidate['p99_ns'] <= baseline['p99_ns'] and ci[0] > 0)
        if key == 'render_ns':
            passed = passed and improvement >= 5
        metrics[key] = dict(baseline=baseline, candidate=candidate,
                            improvement_percent=improvement, ci95_ns=ci, passed=bool(passed))
    return dict(identity={key: metas[0][key] for key in identity},
                runs=[dict(file=str(path), raw_sha256=meta['raw']['sha256'])
                      for path, meta in zip(paths, metas)], metrics=metrics,
                passed=all(metrics[k]['passed'] for k in ('render_ns', 'chain_ns', 'total_ns')))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    results = {script: analyze([a.runs / f'p4-confirm-{script}-{i}-{mode}.json'
                               for i, mode in enumerate(
                                   ('baseline', 'empty_territory', 'empty_territory', 'baseline'), 1)])
               for script in ('static', 'exercise')}
    result = dict(method=dict(order='ABBA, one persistent instance per independent process',
                              ticks=9880, block_ticks=100, bootstrap=10000, seed=42,
                              p99='19760 original samples per side; no averaged P99',
                              tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),
                  results=results, passed=all(r['passed'] for r in results.values()),
                  capacity_claim=False)
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=result['passed'])))


if __name__ == '__main__':
    main()
