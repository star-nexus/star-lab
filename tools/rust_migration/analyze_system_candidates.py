"""Recompute E3 attribution from canonical raw; never infer a parallel speedup."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def summarize(values, unit='ns'):
    values = list(values)
    if not values:
        return dict(unit=unit, samples=0, total=0, mean=None, p99=None, max=None, nonzero_samples=0)
    ordered = sorted(values)
    return dict(unit=unit, samples=len(values), total=sum(values), mean=sum(values)/len(values),
                p99=ordered[min(len(values)-1, int(len(values)*.99))], max=max(values),
                nonzero_samples=sum(v != 0 for v in values))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    index = json.loads((a.experiment/'results/packages.json').read_text())
    raw = a.experiment/index['raw']['file']
    assert sha(raw.read_bytes()) == index['raw']['sha256']
    assert raw.stat().st_size == index['raw']['bytes']
    points = []
    with zipfile.ZipFile(raw) as z:
        for row in z.read('SHA256SUMS').decode().splitlines():
            expected, member = row.split('  ', 1)
            assert sha(z.read(member)) == expected, member
        stream = final = None
        for name in ['baseline-e2-t1', 'candidate-t1', 'candidate-t2', 'candidate-t4']:
            meta = json.loads(z.read(f'replays/{name}.json'))
            assert meta['source_sha'] == '6d4018cc0c607a51a3783428867ba9259bb43f43'
            assert meta['extension_sha256'] == ('23dc7e4f5425e855a780a802d889f13bd28f300577688e66378ab574b7712d55' if name.startswith('baseline') else 'e0f46cfbffd8542c08cd2b2e6b4a26c000da05ecb9bffd3466d77fa859a9834d')
            assert meta['all_passed'] and meta['counts'] == {'request':40994, 'step':9880, 'presentation':9880}
            assert meta['trace_sha256'] == '1f9b155129de9e43780c8885b40aba805e4c4794755fd2af70747058a7824b77'
            if stream is None:
                stream, final = meta['stream_sha256'], meta['final_state_sha256']
            assert (meta['stream_sha256'], meta['final_state_sha256']) == (stream, final)
            sample = z.read('replays/'+meta['step_raw']['file'])
            assert sha(sample) == meta['step_raw']['sha256']
            assert len(json.loads(gzip.decompress(sample))) == 9880
            if 'timing_raw' not in meta:
                continue
            data = z.read('replays/'+meta['timing_raw']['file'])
            assert sha(data) == meta['timing_raw']['sha256']
            rows = json.loads(gzip.decompress(data))
            assert len(rows) == 9880
            fields = {}
            for row in rows:
                assert row['native_ns'] >= sum(row['phases_ns'].values())
                for system, metrics in row['candidates'].items():
                    for key, value in metrics.items():
                        fields.setdefault(system, {}).setdefault(key, []).append(value)
            computed = {system: {key: summarize(values, 'ns' if key.endswith('_ns') else 'count')
                                 for key, values in metrics.items()} for system, metrics in fields.items()}
            assert computed == meta['candidate_summary'], name
            systems = [row['candidates'] for row in rows]
            def values(system, key):
                return [s[system][key] for s in systems]
            def conditional(system, key, predicate):
                return summarize(s[system][key] for s in systems if predicate(s[system]))
            phases = {key: summarize(row['phases_ns'].get(key, 0) for row in rows)
                      for key in rows[0]['phases_ns']}
            derived = dict(
                vision_geometry_share=computed['vision']['geometry_ns']['total']/phases['vision']['total'],
                vision_commit_share=computed['vision']['commit_ns']['total']/phases['vision']['total'],
                vision_geometry_per_miss_ns=computed['vision']['geometry_ns']['total']/computed['vision']['geometry_misses']['total']
                    if computed['vision']['geometry_misses']['total'] else None,
                vision_miss_tick_histogram=dict(sorted(Counter(values('vision', 'geometry_misses')).items())),
                vision_geometry_nonempty=conditional('vision', 'geometry_ns', lambda s:s['geometry_misses']>0),
                movement_optimistic_row_upper=summarize(max(0, s['movement']['row_ns']-s['movement']['spatial_ns']-s['movement']['dirty_ns']) for s in systems),
                movement_active_histogram=dict(sorted(Counter(values('movement', 'active_rows')).items())),
                visuals_loop_upper=summarize(sum(s['visuals'][key] for key in ['attack_ns','projectile_ns','effect_ns','damage_ns']) for s in systems),
                recovery_due_histogram=dict(sorted(Counter(sum(s['recovery'][key] for key in ['ap_entries','mp_entries','skill_entries']) for s in systems).items())),
                recovery_due_group_upper=summarize(sum(s['recovery'][key] for key in ['ap_ns','mp_ns','skill_ns']) for s in systems),
            )
            for key, count in [('attack_ns','attack_rows'),('projectile_ns','projectile_rows'),('effect_ns','effect_rows'),('damage_ns','damage_rows')]:
                derived['visuals_nonempty_'+key] = conditional('visuals',key,lambda s, count=count:s[count]>0)
            tails = {system: [dict(seq=row['seq'], phase_ns=row['phases_ns'][system], fields=row['candidates'][system])
                             for row in sorted(rows, key=lambda row:row['phases_ns'][system], reverse=True)[:5]]
                     for system in ['vision','movement','visuals','recovery']}
            points.append(dict(name=name,threads=meta['threads'],source_sha=meta['source_sha'],extension_sha256=meta['extension_sha256'],
                               phase_summary=phases,candidate_summary=computed,derived=derived,tail_samples=tails))
        contracts = [json.loads(z.read('contracts/'+name+'.json')) for name in ['baseline-e2-t1','candidate-t1','candidate-t2','candidate-t4']]
        for meta in contracts:
            assert meta['all_passed'] and meta['cases'] == 36 and meta['steps'] == 174
        assert len({meta['raw']['sha256'] for meta in contracts}) == 1
        canonical = index['contracts_raw']
        canonical_path = a.experiment/canonical['archive']
        assert sha(canonical_path.read_bytes()) == canonical['archive_sha256']
        with zipfile.ZipFile(canonical_path) as old:
            assert sha(old.read(canonical['member'])) == canonical['sha256'] == contracts[0]['raw']['sha256']
    result = dict(tool_sha256=sha(Path(__file__).read_bytes()),raw=index['raw'], all_passed=True,
                  stream_sha256=stream,final_state_sha256=final,replays=4,profiled_replays=3,
                  contract_variants=4,contract_cases=36,contract_steps=174,contracts_raw=index['contracts_raw'],points=points,
                  limits='Diagnostic nested timer costs; loop upper bounds include ECS/JSON writes and timing overhead. One fixed canonical trace per thread setting; not causal speedup, new live capacity, or all-Unit activity.')
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'points'}))


if __name__ == '__main__':
    main()
