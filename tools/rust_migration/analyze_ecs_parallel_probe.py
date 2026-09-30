"""Validate E1 mechanism evidence and derive its compact, explicitly scoped metrics."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import zipfile


P0_SHA = '93b8f7051c0ab8a4fdd67252a88e4ef0db54f531ddd740d00c976a0d18c86c28'
P0_MEMBER = 'results/candidate-t1.timings.json.gz'
SOURCE = 'c058d75c0ad67a7c340c2a6ac74a9d5bc2888adf'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe-results', type=Path, required=True,
                        help='original results directory or E1 raw ZIP')
    parser.add_argument('--p0-raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    archive = zipfile.ZipFile(args.probe_results) if args.probe_results.is_file() else None

    def read(name):
        return archive.read('results/' + name) if archive else (args.probe_results / name).read_bytes()

    metadata = json.loads(read('metadata.json'))
    assert metadata['source_sha'] == SOURCE
    assert metadata['dependency_versions_match_source']
    assert digest(read('probe.Cargo.lock')) == metadata['probe_lock_sha256']
    tool_dir = Path(__file__).parent
    for field, name in [('runner_sha256', 'run_ecs_parallel_probe.py'),
                        ('rust_probe_sha256', 'ecs_parallel_probe.rs')]:
        assert digest((tool_dir / name).read_bytes()) == metadata[field], 'probe tool drift'
    commands = json.loads(read('commands.json'))
    assert [c['name'] for c in commands] == ['lock', 'build', 'schedule-t1', 'schedule-t2',
                                           'schedule-t4', 'scoped-t2', 'scoped-t4']
    assert all(c['exit_status'] == 0 for c in commands)
    input_hashes = {name: digest(read(name)) for name in
                    ['metadata.json', 'commands.json', 'probe.Cargo.lock', 'probe.Cargo.toml']}
    schedule = []
    scoped = []
    for threads in [1, 2, 4]:
        name = f'schedule-t{threads}.json'
        value = json.loads(read(name))
        input_hashes[name] = digest(read(name))
        assert (value['mode'], value['threads'], value['all_passed']) == ('schedule', threads, True)
        checks = value['checks']
        assert [c['case'] for c in checks] == ['disjoint_components', 'same_component',
                                               'same_resource_different_fields', 'exclusive_world']
        for check in checks:
            expected = 2 if threads > 1 and check['case'] == 'disjoint_components' else 1
            assert check['passed'] and check['maximum_simultaneous_bodies'] == expected
        subset = value['active_subset']
        assert subset['passed'] and (subset['resident'], subset['selected'], subset['changed']) == (5000, 100, 100)
        schedule.append(value)
    for threads in [2, 4]:
        name = f'scoped-t{threads}.json'
        value = json.loads(read(name))
        input_hashes[name] = digest(read(name))
        assert (value['mode'], value['threads'], value['all_passed']) == ('scoped', threads, True)
        assert len(value['checks']) == 1
        check = value['checks'][0]
        assert check['passed'] and check['ordered_5000_outputs_equal']
        samples = check['dispatch_samples_ns']
        assert len(samples) == 1000 and all(isinstance(v, int) and v >= 0 for v in samples)
        ordered = sorted(samples)
        assert check['dispatch_median_ns'] == ordered[500]
        assert check['dispatch_p99_ns'] == ordered[990]
        scoped.append({k: v for k, v in check.items() if k != 'dispatch_samples_ns'})
    p0_raw = args.p0_raw.read_bytes()
    assert digest(p0_raw) == P0_SHA, 'P0 canonical input drift'
    with zipfile.ZipFile(args.p0_raw) as p0:
        member = p0.read(P0_MEMBER)
    rows = json.loads(gzip.decompress(member))
    assert len(rows) == 9880
    group = ['recovery', 'lifecycle', 'vision']
    costs = [[r['phases_ns'][phase] for phase in group] for r in rows]
    savings = [sum(c) - max(c) for c in costs]
    ordered = sorted(savings)
    ceiling = dict(input_raw_sha256=P0_SHA, input_member=P0_MEMBER,
                   input_member_sha256=digest(member), ticks=len(rows), group=group,
                   zero_overhead_per_tick_overlap_saving_mean_ns=sum(savings) / len(savings),
                   p99_ns=ordered[int(len(ordered) * 0.99)], maximum_ns=max(savings),
                   scope='ideal per-tick overlap estimate, excludes conversion/scheduling/commit costs; not measured benefit')
    phase_means = {phase: sum(r['phases_ns'][phase] for r in rows) / len(rows)
                   for phase in rows[0]['phases_ns']}
    summary = dict(all_passed=True, source_sha=SOURCE,
                   analyzer_sha256=digest(Path(__file__).read_bytes()), raw_file_sha256=input_hashes,
                   schedule=schedule, scoped=scoped, p0_phase_mean_ns=phase_means,
                   overlap_ceiling=ceiling,
                   scope='locked ECS/ReadPool mechanisms and P0 cost-derived prioritization; no production parallelism, equivalence or capacity claim')
    args.output.mkdir(parents=True, exist_ok=True)
    for name, value in [('comparison.json', summary), ('overlap-ceiling.json', ceiling)]:
        (args.output / name).write_text(json.dumps(value, indent=2) + '\n')
    if archive:
        archive.close()
    print(json.dumps(dict(all_passed=True, overlap_ceiling_mean_ns=ceiling['zero_overhead_per_tick_overlap_saving_mean_ns'],
                          scoped=[dict(threads=c['threads'], median_ns=c['dispatch_median_ns'], p99_ns=c['dispatch_p99_ns']) for c in scoped])))


if __name__ == '__main__':
    main()
