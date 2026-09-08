"""Archive a complete P3 runtime point as compact evidence + raw forensic ZIPs."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from p3_analyze import analyze


def digest(path):
    return {'path':path.name, 'size':path.stat().st_size,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def archive(point_path, case):
    point_path, case = Path(point_path), Path(case)
    original = json.loads(point_path.read_text())
    analysis = analyze(point_path)
    run = point_path.stem
    artifacts, results = case/'artifacts', case/'results'
    artifacts.mkdir(parents=True,exist_ok=True)
    results.mkdir(parents=True,exist_ok=True)
    raw_zip = artifacts/(run+'-raw.zip')
    with zipfile.ZipFile(raw_zip,'w',zipfile.ZIP_DEFLATED) as z:
        for path in (point_path, point_path.with_suffix('.raw.json'), point_path.with_suffix('.log')):
            if path.exists():
                z.write(path,path.name)
        src = Path(original['workload']['source'])
        layout, units = original['workload']['layout'], original['workload']['units']
        fixture = src/'rotk_env/maps'/f'lab-p3-{layout}-{units}.json'
        if fixture.exists():
            if hashlib.sha256(fixture.read_bytes()).hexdigest() != original['fixture_sha256']:
                raise ValueError('fixture differs from recorded source')
            z.write(fixture,fixture.name)
    compact = {k:v for k,v in original.items() if k != 'censuses'}
    compact['raw_package'] = digest(raw_zip)
    compact['raw_package']['path'] = 'artifacts/'+raw_zip.name
    compact['reanalysis'] = analysis
    # Retain the raw member checksum; no path implies the raw is an unpacked file.
    compact['raw']['locator'] = 'artifacts/'+raw_zip.name+'#'+point_path.with_suffix('.raw.json').name
    payload = (json.dumps(compact,indent=2)+'\n').encode()
    (results/(run+'.json')).write_bytes(payload)
    compact_zip = artifacts/(run+'-compact.zip')
    with zipfile.ZipFile(compact_zip,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr(run+'.json',payload)
        z.writestr('SHA256SUMS',hashlib.sha256(payload).hexdigest()+'  '+run+'.json\n')
    return {'run':run,'compact':digest(compact_zip),'raw':digest(raw_zip)}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('point')
    p.add_argument('--case', default='experiments/2026-09-p3-local-agents')
    args = p.parse_args()
    print(json.dumps(archive(args.point,args.case),indent=2))
