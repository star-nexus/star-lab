"""Archive/recompute the frozen parallel-observation probe; no timing reruns."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from p3_local_agents import stats


def digest(data):
    return hashlib.sha256(data).hexdigest()


def summarize(data):
    rows = data['rows']
    summary = {k:stats([r[k] for r in rows if k in r]) for k in data['summary']}
    assert summary == data['summary'], 'raw/summary mismatch'
    assert len(rows) == data['workload']['queries']
    assert sorted(r['query'] for r in rows) == list(range(len(rows)))
    assert data['all_equal'] and all(r['equal'] for r in rows)
    assert not data['source']['dirty'] and not data['tooling']['dirty']
    assert data['requests_per_second'] == len(rows)/data['wall_seconds']
    if 'guards' in data:
        assert all(data['guards'].values()), data['guards']
        assert data['census_before'] == data['census_after']
    result = {k:v for k,v in data.items() if k != 'rows'}
    result['summary'] = summary
    result['sample_count'] = len(rows)
    result['observed_worker_pids'] = sorted({r['worker_pid'] for r in rows if 'worker_pid' in r})
    return result


def recompute(raw):
    groups = {'guarded':[], 'pre-guard':[]}
    with zipfile.ZipFile(raw) as z:
        for name in sorted(z.namelist()):
            if name == 'validation-summary.json':
                continue
            group = name.split('/')[0]
            payload = z.read(name)
            row = summarize(json.loads(payload))
            row['raw_member'], row['raw_member_sha256'] = name, digest(payload)
            groups[group].append(row)
        validation = json.loads(z.read('validation-summary.json'))
    for group, rows in groups.items():
        assert len(rows) == 8
        assert {r['workload']['workers'] for r in rows} == {0,1,2,4}
        assert len({r['expected_sha256'] for r in rows}) == 1
        assert len({r['fixture_sha256'] for r in rows}) == 1
        assert len({r['source']['sha'] for r in rows}) == 1
    return {'kind':'frozen equivalence and cost; NOT realtime capacity',
        'primary_group':'guarded', 'groups':groups, 'validation':validation,
        'raw':{'path':'artifacts/'+raw.name, 'sha256':digest(raw.read_bytes()), 'size':raw.stat().st_size}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', required=True)
    p.add_argument('--guarded')
    p.add_argument('--pre-guard')
    p.add_argument('--verify', action='store_true')
    a = p.parse_args()
    case = Path(a.case)
    artifacts, results = case/'artifacts', case/'results'
    artifacts.mkdir(parents=True, exist_ok=True)
    results.mkdir(exist_ok=True)
    raw = artifacts/'frozen-raw.zip'
    if not a.verify:
        validation = {'source_sha':'3c4fba1a40fccee7bfc06575ade338c30a4b784e',
            'command':'.venv/bin/python -m pytest -q', 'passed':936,
            'record_type':'summary of observed terminal result',
            'new_parallel_contract_cases':24, 'production_merge':False}
        with zipfile.ZipFile(raw, 'w', zipfile.ZIP_DEFLATED) as z:
            for group, root in (('guarded', a.guarded), ('pre-guard', a.pre_guard)):
                paths = sorted(Path(root).glob('*.json'))
                assert len(paths) == 8
                for path in paths:
                    z.write(path, group+'/'+path.name)
            z.writestr('validation-summary.json', json.dumps(validation,indent=2)+'\n')
    result = recompute(raw)
    compact_json = (json.dumps(result,indent=2)+'\n').encode()
    summary = results/'frozen.json'
    compact = artifacts/'frozen-compact.zip'
    if a.verify:
        assert summary.read_bytes() == compact_json
        with zipfile.ZipFile(compact) as z:
            assert z.read('frozen.json') == compact_json
            assert z.read('SHA256SUMS').decode() == digest(compact_json)+'  frozen.json\n'
    else:
        summary.write_bytes(compact_json)
        with zipfile.ZipFile(compact, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('frozen.json',compact_json)
            z.writestr('SHA256SUMS',digest(compact_json)+'  frozen.json\n')
        (artifacts/'SHA256SUMS').write_text(''.join(
            digest(path.read_bytes())+'  '+str(path.relative_to(case))+'\n'
            for path in (raw, compact)))
    print(json.dumps({'verified':True,'raw_sha256':digest(raw.read_bytes()),
        'raw_bytes':raw.stat().st_size,'compact_sha256':digest(compact.read_bytes()),
        'compact_bytes':compact.stat().st_size},indent=2))


if __name__ == '__main__':
    main()
