"""Recompute one live ABBA host screen; never claim fixed-input causality."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / 'tools'))
from p3_local_agents import stats


def verify_point(path):
    path = Path(path)
    meta = json.loads(path.read_text())
    raw_path = path.parent / meta['raw']['path']
    assert hashlib.sha256(raw_path.read_bytes()).hexdigest() == meta['raw']['sha256']
    raw = json.loads(raw_path.read_text())
    frames = [r for r in raw['frames'] if r['t'] >= meta['workload']['warmup']]
    events = [r for r in raw['events'] if r['t'] >= meta['workload']['warmup']]
    assert frames and all('work_ms' in f for f in frames)
    assert stats([r['work_ms'] for r in frames]) == meta['frame_work_ms']
    assert stats([r['response_ms'] for r in events if r['event'] == 'observe']) == meta['observation_response_ms']
    assert stats([r['queue_ms'] for r in events if r['event'] == 'act']) == meta['action_queue_ms']
    assert sum(r['event'] == 'observe' for r in events) == meta['completed_observations']
    assert meta['native_recording']['queries'] == meta['native_recording']['payloads']
    assert meta['extension']['sha256'] == '9bb2fa4412bc810fbd751c42f525614f8cddb42e8c136612a51495fa0679f0d9'
    assert meta['host_mode'] in ('single', 'segment_encoded')
    assert meta['workload']['presentation_research_mode'] == 'baseline'
    assert meta['native_recording']['full_world_exports_during_measurement'] == 0
    return meta, raw, frames, events


def analyze(paths):
    points = [verify_point(p) for p in paths]
    assert [p[0]['host_mode'] for p in points] == ['single', 'segment_encoded', 'segment_encoded', 'single']
    assert all(p[0]['surface_size'] == [2480, 1235] and p[0]['hardware']['window'] == [2480, 1235] for p in points)
    for field in ('fixture_sha256', 'dependency_lock_sha256', 'extension', 'surface_size', 'display_driver'):
        assert all(p[0][field] == points[0][0][field] for p in points), field
    resource_valid = []
    for path in paths:
        guard = json.loads(Path(path).with_suffix('.monitor.json').read_text())
        resource_valid.append(bool(guard['status'] == 'passed' and guard['child_exit'] == 0 and guard['samples']
                                   and not guard['events'] and all(s['pressure'] == 1 for s in guard['samples'])
                                   and not guard['automatic_pause'] and not guard['automatic_termination']))
    metrics = {}
    for key, frame_metric in [('frame_work_ms', True), ('observation_service_ms', False)]:
        per_run = []
        blocks = []
        for meta, raw, frames, events in points:
            rows = frames if frame_metric else [r for r in events if r['event'] == 'observe']
            field = 'work_ms' if frame_metric else 'service_ms'
            values = [r[field] for r in rows]
            per_run.append(stats(values))
            # Assign event to the real completed frame that contains it, including
            # events between frames; blocks retain actual event counts.
            frame_t = np.array([f['t'] for f in raw['frames']])
            first = next(i for i, f in enumerate(raw['frames']) if f['t'] >= meta['workload']['warmup'])
            sums = defaultdict(lambda: [0., 0])
            for row, value in zip(rows, values):
                index = int(np.searchsorted(frame_t, row['t'], side='right') - 1)
                block = max(0, index - first) // 100
                sums[block][0] += value
                sums[block][1] += 1
            blocks.append(np.array([sums[i] for i in sorted(sums)]))
        # Independent time-block resampling per live run. These are not paired
        # per-tick differences because queue/deadline/world trajectories differ.
        boot_means = []
        rng = np.random.default_rng(42)
        for b in blocks:
            ix = rng.integers(0, len(b), (10000, len(b)))
            chosen = b[ix]
            boot_means.append(chosen[:, :, 0].sum(1) / chosen[:, :, 1].sum(1))
        baseline = (per_run[0]['avg'] + per_run[3]['avg']) / 2
        candidate = (per_run[1]['avg'] + per_run[2]['avg']) / 2
        ci = np.quantile((boot_means[0] + boot_means[3] - boot_means[1] - boot_means[2]) / 2, [.025, .975]).tolist()
        p99_ok = max(per_run[1]['p99'], per_run[2]['p99']) <= max(per_run[0]['p99'], per_run[3]['p99'])
        improvement = 100 * (baseline - candidate) / baseline
        metrics[key] = dict(per_run=per_run, baseline_mean=baseline, candidate_mean=candidate,
                            improvement_percent=improvement, ci95_live_block_difference_ms=ci,
                            p99_envelope_no_regression=p99_ok,
                            screening_passed=bool(ci[0] > 0 and p99_ok and improvement > 0 and (frame_metric or improvement >= 5)))
    guards = [p[0]['guards'] for p in points]
    operational = all(all(g.values()) for g in guards)
    positive = all(resource_valid) and operational and all(m['screening_passed'] for m in metrics.values())
    return dict(stage='One complete Lab live-host ABBA screen', order=['A', 'B', 'B', 'A'],
                metrics=metrics, resource_valid=resource_valid, runtime_guards=guards,
                operational_guards_passed=operational, screening_positive=positive,
                decision=('promising complete-host evidence; confirmation still needed' if positive else
                          'inconclusive resource interference' if not all(resource_valid) else
                          'host screen did not meet net-benefit/operational gates'),
                method='Unpaired live 100-frame block resampling, 10000 draws, seed42, actual event/tail weights; equal run weights',
                live_trajectories_differ=True, fixed_input_causal_speedup=False,
                formal_full_host_acceptance=False, default_adoption=False,
                scope='Live Lab local request queue through SDL flip; production network excluded',
                automatic_retry=False, automatic_additional_round=False)
