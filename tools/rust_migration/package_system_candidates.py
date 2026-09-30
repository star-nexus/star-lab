"""Package E3 canonical raw, retaining all samples and reusing E2 identical contracts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment', type=Path, required=True)
    p.add_argument('--build-dir', type=Path)
    p.add_argument('--compact-only', action='store_true', help='package decision-grade directory after documents are finalized')
    a = p.parse_args()
    root = a.experiment.resolve()
    results = root/'results'
    if a.compact_only:
        index = json.loads((results/'packages.json').read_text())
        files = {name:(root/name).read_bytes() for name in ['README.md','manifest.yaml','analysis.md','decision.md']}
        for path in sorted(results.glob('*.json')):
            if path.name != 'contract-commands.json' and path.name != 'packages.json':
                files['results/'+path.name] = path.read_bytes()
        snapshot = {key:value for key,value in index.items() if key != 'compact'}
        files['results/packages.json'] = (json.dumps(snapshot,indent=2)+'\n').encode()
        files['SHA256SUMS'] = ''.join(f'{sha(data)}  {name}\n' for name,data in sorted(files.items())).encode()
        compact = root/'artifacts/system-candidates-compact.zip'
        with zipfile.ZipFile(compact,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for name,data in sorted(files.items()):
                item = zipfile.ZipInfo(name,date_time=(2026,10,1,0,0,0))
                item.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(item,data,compresslevel=9)
        index['compact'] = dict(file='artifacts/'+compact.name,sha256=sha(compact.read_bytes()),bytes=compact.stat().st_size,
                                tool_sha256=sha(Path(__file__).read_bytes()),
                                scope='Decision-grade snapshot; own checksum is in the adjacent canonical index to avoid recursive self-hashing.')
        (results/'packages.json').write_text(json.dumps(index,indent=2)+'\n')
        print(json.dumps(index['compact']))
        return
    assert a.build_dir is not None, '--build-dir required for raw packaging'
    build = a.build_dir.resolve()
    files = {}
    for name in ['baseline-e2-t1','candidate-t1','candidate-t2','candidate-t4']:
        path = results/(name+'.json')
        meta = json.loads(path.read_text())
        assert meta['all_passed']
        files['replays/'+path.name] = path.read_bytes()
        for key in ['step_raw','timing_raw']:
            if key in meta:
                item = meta[key]
                data = (results/item['file']).read_bytes()
                assert sha(data) == item['sha256']
                files['replays/'+item['file']] = data
        path = results/('contracts-'+name+'.json')
        meta = json.loads(path.read_text())
        assert meta['all_passed']
        assert sha((results/meta['raw']['file']).read_bytes()) == meta['raw']['sha256'] == '9db82664ad15814eec53a603f0d5148ad4d431ef66a4f36871f21de38847078c'
        files['contracts/'+name+'.json'] = path.read_bytes()
    for name in ['build.log','clippy.log','cargo-test-core.log','pytest.log','targeted.log']:
        files['validation/'+name] = (build/name).read_bytes()
    files['commands/contract-commands.json'] = (results/'contract-commands.json').read_bytes()
    for path in (build/'wheel').glob('*.whl'):
        files['wheel/'+path.name] = path.read_bytes()
    assert b'2315 passed' in files['validation/pytest.log']
    assert b'4 passed; 0 failed' in files['validation/cargo-test-core.log']
    files['SHA256SUMS'] = ''.join(f'{sha(data)}  {name}\n' for name,data in sorted(files.items())).encode()
    raw = root/'artifacts/system-candidates-raw.zip'
    raw.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(raw,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(files.items()):
            item = zipfile.ZipInfo(name,date_time=(2026,10,1,0,0,0))
            item.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(item,data,compresslevel=9)
    index = dict(raw=dict(file='artifacts/'+raw.name,sha256=sha(raw.read_bytes()),bytes=raw.stat().st_size),
                 members={name:dict(sha256=sha(data),bytes=len(data)) for name,data in files.items() if name != 'SHA256SUMS'},
                 contracts_raw=dict(archive='../2026-09-rust-statistics-compute/artifacts/statistics-compute-raw.zip',
                                    archive_sha256='62c5e73a2356334fc0fa85e3b5f4054a46f5f759ad7cb6c9fcef41dcd7b190ba',
                                    member='results/contracts-canonical.raw.json.gz',
                                    sha256='9db82664ad15814eec53a603f0d5148ad4d431ef66a4f36871f21de38847078c',
                                    bytes=1047591,
                                    aliases=[f'contracts-{name}.raw.json.gz' for name in ['baseline-e2-t1','candidate-t1','candidate-t2','candidate-t4']],
                                    reason='All newly executed outputs are byte-identical to E2 canonical raw; retain hash identities and one authoritative artifact.'),
                 tool_sha256=sha(Path(__file__).read_bytes()))
    (results/'packages.json').write_text(json.dumps(index,indent=2)+'\n')
    print(json.dumps(index['raw']))


if __name__ == '__main__':
    main()
