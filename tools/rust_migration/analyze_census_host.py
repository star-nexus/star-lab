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
    assert stats([r['queue_ms'] for r in events if r['event']=='observe'])==meta['observation_queue_ms']
    assert sum(r['event'] == 'observe' for r in events) == meta['completed_observations']
    assert meta['native_recording']['queries'] == meta['native_recording']['payloads']
    assert meta['extension']['sha256'] == 'c6a60a42fdafeee481620e89248a1a8604b7e3b3835b7b2a0f43053999977d88'
    assert meta['host_mode']=='single'
    assert meta['census_scan_mode'] in ('baseline','borrowed_census')
    assert meta['native_recording']['scan_mode']==meta['census_scan_mode']
    assert meta['native_recording']['scan_mode_persisted'] and meta['native_recording']['scan_configuration_calls']==1
    assert meta['admitted_segments']['count']==0
    assert meta['workload']['presentation_research_mode'] == 'baseline'
    assert meta['native_recording']['full_world_exports_during_measurement'] == 0
    return meta, raw, frames, events


def analyze(paths):
    points = [verify_point(p) for p in paths]
    assert [p[0]['census_scan_mode'] for p in points] == ['baseline','borrowed_census','borrowed_census','baseline']
    assert all(p[0]['surface_size']==points[0][0]['surface_size'] and p[0]['hardware']['window']==points[0][0]['hardware']['window'] for p in points)
    for field in ('fixture_sha256', 'dependency_lock_sha256', 'extension', 'surface_size', 'display_driver'):
        assert all(p[0][field] == points[0][0][field] for p in points), field
    assert all(p[0]['source']['sha']=='8c2afd7153ebc8ec6c80dd9f3a1406be440405e0' for p in points)
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
            assert np.isfinite(values).all() and min(values)>=0
            per_run.append(stats(values))
            # Frame t is its update-start timestamp; events belong to the most
            # recent frame start. Keep actual event counts and partial tails.
            frame_t = np.array([f['t'] for f in raw['frames']])
            first = next(i for i, f in enumerate(raw['frames']) if f['t'] >= meta['workload']['warmup'])
            nblocks=(len(frames)+99)//100
            sums = defaultdict(lambda: [0., 0])
            for row, value in zip(rows, values):
                index = int(np.searchsorted(frame_t, row['t'], side='right') - 1)
                block = min(nblocks-1,max(0, index - first) // 100)
                sums[block][0] += value
                sums[block][1] += 1
            blocks.append(np.array([sums[i] for i in range(nblocks)]))
        # Independent time-block resampling per live run. These are not paired
        # per-tick differences because queue/deadline/world trajectories differ.
        boot_means = []
        rng = np.random.default_rng(42)
        for b in blocks:
            ix = rng.integers(0, len(b), (10000, len(b)))
            chosen = b[ix]
            assert (chosen[:,:,1].sum(1)>0).all()
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
    queue_envelopes={}
    for field in ['observation_response_ms','observation_queue_ms','action_queue_ms']:
        values=[p[0][field]['p99'] for p in points]
        queue_envelopes[field]=dict(per_run_p99=values,baseline_worst=max(values[0],values[3]),candidate_worst=max(values[1],values[2]),no_regression=max(values[1],values[2])<=max(values[0],values[3]))
    guards = [p[0]['guards'] for p in points]
    operational = all(all(g.values()) for g in guards)
    positive = all(resource_valid) and operational and all(m['screening_passed'] for m in metrics.values()) and all(q['no_regression'] for q in queue_envelopes.values())
    return dict(stage='One census-only ordinary-ingestion live-host ABBA screen', order=['A', 'B', 'B', 'A'],
                metrics=metrics, resource_valid=resource_valid, runtime_guards=guards,
                operational_guards_passed=operational,queue_envelopes=queue_envelopes, screening_positive=positive,
                decision=('supports bounded code cleanup and regression; no automatic adoption' if positive else
                          'inconclusive resource interference' if not all(resource_valid) else
                          'host screen did not meet net-benefit/operational gates'),
                method='Unpaired live 100-frame block resampling, 10000 draws, seed42, actual event/tail weights; equal run weights',
                live_trajectories_differ=True, fixed_input_causal_speedup=False,
                formal_full_host_acceptance=False, default_adoption=False,
                scope='Live Lab local request queue through SDL flip; production network excluded',
                automatic_retry=False, automatic_additional_round=False)
