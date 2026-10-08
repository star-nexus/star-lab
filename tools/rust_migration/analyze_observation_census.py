"""Single-factor fixed-input scan screen; includes all warm/tail samples."""
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np


def analyze(path, monitor_path):
    path = Path(path); meta = json.loads(path.read_text())
    guard = json.loads(Path(monitor_path).read_text())
    assert meta['passed'] and not meta['smoke']
    assert meta['counts'] == dict(requests=12148, queries=3010, ticks=2617, presentation=2617, operations=17382)
    assert meta['modes'] == ['baseline', 'borrowed_census', 'borrowed_census', 'baseline']
    command = guard['command']
    assert str(path) == command[command.index('--output')+1]
    assert meta['extension_sha256'] == command[command.index('--extension-sha256')+1]
    payload = (path.parent/meta['raw']['file']).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == meta['raw']['sha256']
    raw = json.loads(gzip.decompress(payload))
    assert len(raw['queries']) == 3010 and len(raw['ticks']) == 2617
    assert meta['scope_open_count'] == meta['scope_drop_count'] == [750]*4
    for side in range(4):
        assert sum(r['phases'][side]['open_ns'] > 0 for r in raw['queries']) == 750
        assert sum(r['phases'][side]['drop_ns'] > 0 for r in raw['queries']) == 750
        assert all(sum(r['phases'][side].values()) == r['service_ns'][side] for r in raw['queries'])
    metrics = {}; nblocks = (2617+99)//100

    def stats(v):
        ordered = np.sort(v)
        return dict(samples=len(v), mean_ns=float(v.mean()), p99_ns=float(ordered[int(np.ceil(.99*len(v)))-1]), max_ns=float(ordered[-1]))

    for key, rows, field in [('query_service', raw['queries'], 'service_ns'), ('selected_total_work', raw['ticks'], 'total_ns')]:
        values = np.asarray([r[field] for r in rows], dtype=np.float64)
        assert values.shape == (len(rows), 4) and np.isfinite(values).all() and (values >= 0).all()
        base = (values[:,0]+values[:,3])/2; candidate = (values[:,1]+values[:,2])/2
        diff = base-candidate; sums = np.zeros(nblocks); counts = np.zeros(nblocks)
        for row, improvement in zip(rows, diff):
            assert 1 <= row['tick'] <= 2617
            block = (row['tick']-1)//100
            sums[block] += improvement; counts[block] += 1
        chosen = np.random.default_rng(42).integers(0, nblocks, (10000, nblocks))
        denominators = counts[chosen].sum(1)
        assert (denominators > 0).all()  # Each draw must contain queries; zero-query blocks remain in the sample
        ci = np.quantile(sums[chosen].sum(1)/denominators, [.025,.975]).tolist()
        sides = [stats(values[:,i]) for i in range(4)]
        b = stats(np.concatenate([values[:,0], values[:,3]])); c = stats(np.concatenate([values[:,1], values[:,2]]))
        improvement = float(diff.mean()/base.mean()*100)
        p99_gate = c['p99_ns'] <= b['p99_ns'] and max(sides[1]['p99_ns'], sides[2]['p99_ns']) <= max(sides[0]['p99_ns'], sides[3]['p99_ns'])
        passed = improvement > 0 and ci[0] > 0 and p99_gate and (key != 'query_service' or improvement >= 2)
        metrics[key] = dict(baseline=b, candidate=c, sides=sides, improvement_percent=improvement, ci95_improvement_ns=ci,
                            passed=bool(passed), p99_passed=bool(p99_gate), block_counts=counts.tolist())
    descriptions = {}
    for label in ['singleton', 'segment_first', 'segment_later', 'warm', 'steady']:
        rows = [r for r in raw['queries'] if r['role'] == label or label == 'warm' and r['tick'] <= 900 or label == 'steady' and r['tick'] > 900]
        if not rows:
            descriptions[label]=dict(count=0, service_sides=[], mean_phases_ns=[]);continue
        descriptions[label] = dict(count=len(rows), service_sides=[stats(np.asarray([r['service_ns'][i] for r in rows])) for i in range(4)],
                                   mean_phases_ns=[{k:float(np.mean([r['phases'][i][k] for r in rows])) for k in rows[0]['phases'][i]} for i in range(4)])
    valid = guard['status'] == 'passed' and guard['child_exit'] == 0 and not guard['events'] and guard['samples'] and all(v['pressure'] == 1 for v in guard['samples']) and not guard['automatic_pause'] and not guard['automatic_termination']
    positive = bool(valid and all(m['passed'] for m in metrics.values()))
    return dict(timing_resource_valid=bool(valid), metrics=metrics, descriptions=descriptions, screening_positive=positive,
                decision='worth bounded next validation' if positive else 'resource interference; inconclusive' if not valid else 'stop this census ownership factor',
                method=dict(block_ticks=100, bootstrap=10000, seed=42, partial_block_actual_counts=True, query_min_improvement_percent=2,
                            p99='nearest rank, pooled plus worst-side envelope', all_warm_and_tails_retained=True),
                scope=meta['scope'], default_adoption=False, formal_full_host_acceptance=False, automatic_retry=False)
