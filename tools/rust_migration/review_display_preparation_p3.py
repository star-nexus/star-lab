"""Post-measurement P3 integrity and independent statistical review; no reruns.

Run after both supervisors and all timing children exit. Frozen measurement
tools are imported only for their identity/count assertions and cross-checks.
Invalid timings are retained and never passed to the speed analyzer.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
import numpy as np
from run_display_preparation_p3 import job_specs, verify_performance, sha, analyze


def load(p):
    return json.loads(Path(p).read_text())


def resource_valid(g):
    return (g['status'] == 'passed' and g['child_exit'] == 0
            and g['stop_reason'] is None
            and g['policy'] == 'pressure pause only; memory budget telemetry; no automatic termination'
            and g['automatic_termination'] is False and g['budget_enforced'] is False
            and g['paused_seconds'] == 0 and not g['paused'] and not g['events']
            and bool(g['samples']) and all(s['pressure'] == 1 for s in g['samples']))


def independent_metrics(rows):
    result = {}
    for key in ('render_ns', 'chain_ns', 'total_ns', 'display_ns', 'submit_ns', 'apply_ns'):
        sides = np.array([[r[key] for r in side] for side in rows], dtype=np.float64)
        baseline = np.concatenate([sides[0], sides[3]])
        candidate = np.concatenate([sides[1], sides[2]])
        diff = (sides[0] + sides[3] - sides[1] - sides[2]) / 2
        blocks = [diff[start:start + 100] for start in range(0, 9880, 100)]
        sums = np.array([np.sum(b) for b in blocks])
        sizes = np.array([len(b) for b in blocks])
        assert sizes[-1] == 80 and sizes.sum() == 9880
        indices = np.random.default_rng(42).integers(0, 99, (10000, 99))
        bootstrap = np.sum(sums[indices], axis=1) / np.sum(sizes[indices], axis=1)
        interval = np.quantile(bootstrap, [0.025, 0.975]).tolist()
        def stats(v):
            ordered = np.sort(v)
            return dict(samples=len(v), mean_ns=float(np.mean(ordered)),
                        p99_ns=float(ordered[int(len(ordered) * 0.99)]), max_ns=float(ordered[-1]))
        b, c = stats(baseline), stats(candidate)
        improvement = float(np.mean(diff) / np.mean((sides[0] + sides[3]) / 2) * 100)
        passed = c['mean_ns'] < b['mean_ns'] and c['p99_ns'] <= b['p99_ns'] and interval[0] > 0
        if key == 'render_ns':
            passed = passed and improvement >= 5
        result[key] = dict(baseline=b, candidate=c, improvement_percent=improvement,
                           ci95_ns=interval, passed=bool(passed))
    return result


def compare(a, b):
    if isinstance(a, dict):
        assert a.keys() == b.keys()
        for k in a:
            compare(a[k], b[k])
    elif isinstance(a, list):
        assert len(a) == len(b)
        for x, y in zip(a, b):
            compare(x, y)
    elif isinstance(a, float):
        assert np.isclose(a, b, rtol=1e-12, atol=1e-7), (a, b)
    else:
        assert a == b, (a, b)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    lab = Path(__file__).resolve().parents[2]
    exp = lab / 'experiments/2026-10-rust-display-preparation'
    evidence = load(exp / 'results/p3-complete.json')
    specs = job_specs()
    assert evidence['executed'] == [s['name'] for s in specs]
    assert len(evidence['records']) == 24 and evidence['current'] is None
    active = subprocess.run(['pgrep', '-f', 'python.*(continue_display_preparation_p3.py|run_display_preparation_p3.py|display_preparation_performance.py)'], capture_output=True, text=True)
    assert active.returncode == 1, 'Timing supervisor/child still alive; do not compete'
    amendment = load(exp / 'results/p3-continuation-20261007.json')
    tools = lab / 'tools/rust_migration'
    for name, digest in amendment['tool_sha256'].items():
        assert sha(tools / name) == digest, name
    reference = load(exp / 'results/p2-complete.json')['identity']
    records = []
    for spec, recorded in zip(specs, evidence['records']):
        n = spec['name']; path = a.runs / (n + '.json')
        assert all(recorded[k] == v for k, v in spec.items())
        m = verify_performance(a.runs, spec, reference)
        assert sha(path) == recorded['metadata_sha256']
        g = load(a.runs / (n + '.guard.json'))
        assert g['status'] == 'passed' and g['child_exit'] == 0
        assert g['limit_mib'] == 6144 and g['resume_normal_seconds'] == 60
        assert g['tool_sha256'] == amendment['tool_sha256']['guard_display_preparation_pause_only.py']
        valid = resource_valid(g)
        assert valid == recorded['timing_resource_valid']
        zpath = exp / 'artifacts' / recorded['artifact']['file']
        assert sha(zpath) == recorded['artifact']['sha256']
        assert zpath.stat().st_size == recorded['artifact']['bytes']
        with zipfile.ZipFile(zpath) as z:
            files = {p.name: p for p in a.runs.glob(n + '.*') if p.is_file()}
            members = {}
            for line in z.read('SHA256SUMS').decode().splitlines():
                digest, member = line.split('  ', 1)
                assert hashlib.sha256(z.read(member)).hexdigest() == digest
                members[member] = digest
            assert set(members) == {'raw/' + name for name in files}
            assert set(z.namelist()) == set(members) | {'SHA256SUMS'}
            for name, file in files.items():
                assert members['raw/' + name] == sha(file)
        rows = json.loads(gzip.decompress((a.runs / m['raw']['file']).read_bytes()))
        for side in rows:
            for r in side:
                assert r['render_ns'] == r['display_ns'] + r['submit_ns']
                assert r['chain_ns'] == r['decode_ns'] + r['apply_ns'] + r['render_ns'] + r['platform_ns']
                assert r['total_ns'] == r['request_ns'] + r['step_ns'] + r['encode_ns'] + r['chain_ns']
                assert all(v >= 0 for v in r.values())
        metrics = None
        if valid:
            official = analyze(path)
            compare(official, recorded['analysis'])
            metrics = independent_metrics(rows)
            compare(metrics, official['metrics'])
        else:
            assert recorded['analysis'] is None
        records.append(dict(**spec, timing_resource_valid=valid,
            classification='formal' if valid else 'invalid-but-informative; excluded from speed analysis',
            counts=m['counts'], raw=m['raw'], workload_raw=m['workload_raw'],
            artifact=recorded['artifact'], metadata_sha256=sha(path),
            guard=dict(status=g['status'], policy=g['policy'], samples=len(g['samples']),
                       pressure_levels=sorted({s['pressure'] for s in g['samples']}),
                       paused_seconds=g['paused_seconds'], events=g['events'],
                       peak_sampled_rss_bytes=max(s['rss_bytes'] for s in g['samples']),
                       budget_enforced=g['budget_enforced'], automatic_termination=g['automatic_termination']),
            metrics=metrics, passed=None if not valid else all(metrics[k]['passed'] for k in ('render_ns', 'chain_ns', 'total_ns'))))
        print(n, 'verified; timing valid=' + str(valid), flush=True)
    groups = {}
    for label, reported in evidence['analysis'].items():
        consumer, threads, script = label.split('/')
        group = [r for r in records if (r['consumer'], 'native' + str(r['threads']), r['script']) == (consumer, threads, script)]
        valid = [r for r in group if r['timing_resource_valid']]
        complete = len(valid) == 3
        assert reported['executed'] == 3 and reported['valid'] == len(valid) and reported['complete'] == complete
        passed = complete and all(r['passed'] for r in valid)
        assert passed == reported['passed']
        groups[label] = dict(executed=3, valid=len(valid), status='passed' if passed else 'not adopted; gates failed' if complete else 'inconclusive; fewer than 3 valid rounds',
            passed=passed, rounds=[dict(round=r['round'], name=r['name'], passed=r['passed'], metrics=r['metrics']) for r in valid])
    assert [r['name'] for r in records if r['timing_resource_valid']] == evidence['completed']
    assert [r['name'] for r in records if not r['timing_resource_valid']] == evidence['invalid']
    checksum_file = exp / 'artifacts/SHA256SUMS'
    checked = []
    for line in checksum_file.read_text().splitlines():
        digest, relative = line.split('  ', 1)
        assert sha(exp / relative) == digest, relative
        checked.append(relative)
    result = dict(passed=True, review_tool_sha256=sha(__file__), source_sha=evidence['source_sha'],
        identity=reference, executed=24, timing_valid=len(evidence['completed']), timing_invalid=len(evidence['invalid']),
        original_jobs_repeated=False, speed_analyzer_invalid_jobs_called=False,
        source_tools_unchanged=True, inner_zip_and_persistent_bytes_verified=True,
        outer_checksums_verified=len(checked), samples_per_job=dict(sides=4, ticks_per_side=9880),
        method=dict(block_ticks=100, last_block_ticks=80, bootstrap=10000, seed=42,
                    p99_samples_per_arm=19760, all_ticks_retained=True, render_min_improvement_percent=5),
        groups=groups, records=records, production_enabled=False, capacity_claim=False)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:result[k] for k in ('passed', 'executed', 'timing_valid', 'timing_invalid', 'outer_checksums_verified')}), flush=True)


if __name__ == '__main__':
    main()
