"""E4 checksum-verified complete ABBA analysis and conservative dispatch screen.

External same-FFI step latencies are measured without diagnostics. E3 timings are
only a zero-overhead bound, not a prediction or a causal latency comparison.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import zipfile
import numpy as np


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verified_zip(path, expected=None):
    if expected:
        assert sha(path.read_bytes()) == expected
    archive = zipfile.ZipFile(path)
    for line in archive.read('SHA256SUMS').decode().splitlines():
        checksum, name = line.split('  ', 1)
        assert sha(archive.read(name)) == checksum, name
    return archive


def stats(values):
    return {'samples':len(values), 'mean_ns':float(np.mean(values)),
            'p99_ns':float(np.sort(values)[int(len(values)*.99)]), 'max_ns':float(np.max(values))}


def interval(values, mask=None):
    # Nonoverlapping 100-tick blocks, including the final 80-tick tail. Weighted
    # mean retains every selected tick. Blocks with no selected ticks are omitted.
    mask = np.ones(len(values), dtype=bool) if mask is None else mask
    sums, counts = [], []
    for offset in range(0, len(values), 100):
        selected = values[offset:offset+100][mask[offset:offset+100]]
        if len(selected):
            sums.append(float(selected.sum()))
            counts.append(len(selected))
    sums, counts = np.array(sums), np.array(counts)
    rng = np.random.default_rng(42)
    draws = rng.integers(0, len(sums), (10000, len(sums)))
    means = sums[draws].sum(axis=1) / counts[draws].sum(axis=1)
    return list(map(float, np.quantile(means, [.025, .975])))


def analyze(replays, e3):
    result = {'method': {'order':'ABBA', 'rounds':3, 'threads':[2,4],
              'samples_per_replay':9880, 'block_ticks':100, 'bootstrap_draws':10000,
              'seed':42, 'confidence':.95, 'tails_removed':False,
              'latency_boundary':'same private Python/FFI complete advancing step, diagnostics off'}, 'configurations':{}}
    identities = []
    def identity(meta):
        assert meta['all_passed'] and meta['counts']['step'] == 9880 and meta['counts']['request'] == 40994 and meta['counts']['presentation'] == 9880
        return (meta['source_sha'],meta['extension_sha256'],meta['stream_sha256'],meta['final_state_sha256'])
    for threads in [2,4]:
        diagnostic = json.loads((replays/f'diagnostic-t{threads}.json').read_text())
        identities.append(identity(diagnostic))
        rows = json.loads(gzip.decompress((replays/diagnostic['timing_raw']['file']).read_bytes()))
        assert sha((replays/diagnostic['timing_raw']['file']).read_bytes()) == diagnostic['timing_raw']['sha256']
        assert len(rows) == 9880
        mask = np.array([bool(row['phases_ns'].get('eligible', 0)) for row in rows])
        assert sum(row['phases_ns'].get('forked', 0) for row in rows) == int(mask.sum())
        old = json.loads(gzip.decompress(e3.read(f'replays/candidate-t{threads}.timings.json.gz')))
        assert [r['seq'] for r in old] == [r['seq'] for r in rows]
        bounds = np.array([min(r['phases_ns']['vision'], r['phases_ns']['recovery']+r['phases_ns']['lifecycle']) for r in old],dtype=float)
        bound = float(bounds[mask].mean())
        residual = np.array([r['phases_ns'].get('fork_region', 0) - r['phases_ns']['recovery'] - r['phases_ns']['lifecycle'] if m else 0 for r, m in zip(rows, mask)], dtype=float)
        config = {'diagnostic_fork_residual_ns':stats(residual[mask]),
                  'diagnostic_residual_minus_bound_ci95_ns':interval(residual-bounds, mask),
                  'eligible_ticks':int(mask.sum()), 'all_ticks':len(mask),
                  'e3_matched_zero_overhead_bound_ns':bound,
                  'e3_all_tick_bound_ns':float(bounds.mean()), 'rounds':[]}
        for round in range(1,4):
            samples = {}
            for label in ['a1','b1','b2','a2']:
                meta = json.loads((replays/f't{threads}-r{round}-{label}.json').read_text())
                raw = (replays/meta['step_raw']['file']).read_bytes()
                assert sha(raw) == meta['step_raw']['sha256']
                assert meta['all_passed'] and meta['counts']['step'] == 9880
                identities.append(identity(meta))
                samples[label] = np.array(json.loads(gzip.decompress(raw)),dtype=float)
            a = (samples['a1']+samples['a2'])/2
            b = (samples['b1']+samples['b2'])/2
            delta = b-a
            matched_ci = interval(delta, mask)
            row = {'round':round, 'baseline':stats(np.concatenate([samples['a1'],samples['a2']])),
                   'empty_fork':stats(np.concatenate([samples['b1'],samples['b2']])),
                   'paired_all_overhead_ns':float(delta.mean()),'paired_all_overhead_ci95_ns':interval(delta),
                   'paired_eligible_overhead_ns':float(delta[mask].mean()),
                   'paired_eligible_overhead_ci95_ns':matched_ci,
                   'paired_ineligible_overhead_ns':float(delta[~mask].mean()),
                   'screen_exhausted':matched_ci[0] >= bound}
            config['rounds'].append(row)
        config['external_screen_exhausted_all_rounds'] = all(row['screen_exhausted'] for row in config['rounds'])
        config['diagnostic_screen_exhausted'] = config['diagnostic_residual_minus_bound_ci95_ns'][0] > 0
        matched_meta = json.loads((replays/f'matched-t{threads}.json').read_text())
        identities.append(identity(matched_meta))
        matched_raw = (replays/matched_meta['timing_raw']['file']).read_bytes()
        assert sha(matched_raw) == matched_meta['timing_raw']['sha256']
        paired = json.loads(gzip.decompress(matched_raw))
        assert len(paired) == 9880
        paired_mask = np.array([bool(r['phases_ns']['eligible']) for r in paired])
        assert np.array_equal(paired_mask, mask)
        assert all(r['baseline_phases_ns']['eligible'] == r['phases_ns']['eligible'] for r in paired)
        current_bounds = np.array([min(r['baseline_phases_ns']['vision'], r['baseline_phases_ns']['recovery']+r['baseline_phases_ns']['lifecycle']) for r in paired],dtype=float)
        current_overhead = np.array([r['phases_ns'].get('fork_region', 0)-r['baseline_phases_ns']['recovery']-r['baseline_phases_ns']['lifecycle'] if m else 0 for r,m in zip(paired,mask)],dtype=float)
        config['contemporary_paired_baseline_bound_ns'] = stats(current_bounds[mask])
        config['contemporary_paired_fork_overhead_ns'] = stats(current_overhead[mask])
        config['contemporary_overhead_minus_bound_ci95_ns'] = interval(current_overhead-current_bounds, mask)
        config['contemporary_screen_exhausted'] = config['contemporary_overhead_minus_bound_ci95_ns'][0] > 0
        config['stop_split'] = config['contemporary_screen_exhausted']
        result['configurations'][str(threads)] = config
    assert len(set(identities)) == 1, identities
    result['identities'] = dict(zip(['source_sha','extension_sha256','stream_sha256','final_state_sha256'],identities[0]))
    result['verified_replay_reports'] = len(identities)
    result['stop_split'] = all(x['stop_split'] for x in result['configurations'].values())
    result['interpretation'] = 'Conservative screen, not proof that every scheduler or larger workload must lose. E3 observer, timed fork residual and paired contemporary baseline diagnostic do not measure a real Vision split. Timed residual includes added diagnostic clocks; external same-FFI results are reported separately without discarding conflicting rounds.'
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replays',type=Path,required=True,help='loose measurement results or verified raw ZIP')
    parser.add_argument('--e3-archive',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    e3=verified_zip(args.e3_archive,'c3e347b145fcc5edfda304bb35030d3d3d9320861f116a5507d2b92cbd9b6abd')
    if args.replays.is_file():
        import tempfile
        raw=verified_zip(args.replays)
        with tempfile.TemporaryDirectory() as work:
            for name in raw.namelist():
                if name.startswith('replays/'):
                    path=Path(work)/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw.read(name))
            result=analyze(Path(work)/'replays',e3)
    else:
        result=analyze(args.replays,e3)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
