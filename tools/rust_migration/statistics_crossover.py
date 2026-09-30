"""Synthetic complete-step crossover for current-batch Statistics row dispatch.

Each sample resets outside its timed region. This is a mechanism/crossover control,
not a live workload or capacity test. Original sampling is unchanged in product.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def sha(data):
    return hashlib.sha256(data).hexdigest()


def summary(values):
    ordered = sorted(values)
    return dict(samples=len(values), mean_ns=sum(values)/len(values), median_ns=ordered[len(values)//2],
                p99_ns=ordered[min(len(values)-1, int(len(values)*.99))])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--source-sha', required=True)
    p.add_argument('--extension-sha256', required=True)
    p.add_argument('--cases', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--samples', type=int, default=200)
    p.add_argument('--warmup', type=int, default=20)
    a = p.parse_args()
    assert a.samples > 0 and a.warmup >= 0
    source = a.source.resolve()
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip() == a.source_sha
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=source, text=True).strip()
    sys.path.insert(0, str(source))
    from star_native import NativeRuntime, _native
    assert sha(Path(_native.__file__).read_bytes()) == a.extension_sha256
    cases = json.loads(gzip.decompress(a.cases.read_bytes()))
    template = next(c['initial'] for c in cases if c['name'] == 'window-259-resident-fog-True')
    ids = [e['id'] for e in template['entities'] if 'Unit' in e['components']]
    reports = []
    raw = []
    for size in [0,1,8,16,32,64,128,256]:
        initial = copy.deepcopy(template)
        initial['systems']['AnimationSystem']['enabled'] = False
        initial['systems']['VisionSystem']['enabled'] = False
        stats = initial['systems']['StatisticsSystem']
        stats['batch_size'] = max(size, 1)
        stats['history_limit'] = 10000
        stats['cycle'] = dict(phase='observations', index=0, observation_entities=ids[:size],
                             visibility_entities=[], faction_counts={}, visibility_cleared=False,
                             fog_disabled_visible_to=None)
        initial['singletons']['GameStats']['unit_observation_history'] = [dict(entity=i,
            faction='wei', unit_type='infantry', position=[-1,0], health_percentage=100.,
            movement_remaining=4, terrain_type='plains', timestamp=0.) for i in range(10000)]
        scene = json.dumps(initial)
        for threads in [2,4]:
            instances = {policy:NativeRuntime(scene, threads) for policy in ['inline','forced']}
            samples = {policy:[] for policy in instances}
            try:
                for index in range(a.warmup + a.samples):
                    policies = ['inline','forced'] if index % 2 == 0 else ['forced','inline']
                    for policy in policies:
                        n = instances[policy]
                        n.reset(scene)
                        start = time.perf_counter_ns()
                        n._statistics_step_json(0., 1720000000., 0 if policy == 'forced' else 1 << 60, False)
                        elapsed = time.perf_counter_ns() - start
                        if index >= a.warmup:
                            samples[policy].append(elapsed)
                states = [json.loads(n.export_state_json()) for n in instances.values()]
                deltas = [json.loads(n.take_presentation_delta_json()) for n in instances.values()]
                assert states[0] == states[1] and deltas[0] == deltas[1]
                metrics = {}
                for policy, n in instances.items():
                    n.reset(scene)
                    diagnostic = json.loads(n._statistics_step_json(0., 1720000000., 0 if policy == 'forced' else 1 << 60))
                    metrics[policy] = diagnostic['statistics']
                    assert metrics[policy]['observation_rows'] == size
                    assert metrics[policy]['parallel_batches'] == int(policy == 'forced' and size > 0)
                row = dict(rows=size, resident=259, threads=threads,
                           inline=summary(samples['inline']), forced=summary(samples['forced']),
                           full_state_delta_equal=True, metrics=metrics)
                reports.append(row)
                raw.append(dict(rows=size, threads=threads, samples_ns=samples))
                print(size, threads, row['inline']['mean_ns'], row['forced']['mean_ns'], flush=True)
            finally:
                for n in instances.values():
                    n.close()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    raw_path = a.output.with_suffix('.raw.json.gz')
    raw_path.write_bytes(gzip.compress(json.dumps(raw, separators=(',', ':')).encode(), mtime=0))
    result = dict(source_sha=a.source_sha, extension_sha256=a.extension_sha256,
                  tool_sha256=sha(Path(__file__).read_bytes()), input_sha256=sha(a.cases.read_bytes()),
                  warmup=a.warmup, samples=a.samples, rows=reports, all_passed=True,
                  raw=dict(file=raw_path.name, bytes=raw_path.stat().st_size, sha256=sha(raw_path.read_bytes())),
                  scope='synthetic259resident, selected current batch, steady10000history, alternating policies; reset excluded; disabled animation/vision; not live capacity')
    a.output.write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
