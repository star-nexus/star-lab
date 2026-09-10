"""Archive and independently recompute the settled-view text-cache A/B."""
import argparse
import json
from pathlib import Path
import tempfile
import zipfile

from p3_local_agents import stats
from p3_text_archive import analyze, digest


def summarize_run(root, mode):
    result = analyze(root, mode)
    if mode == 'replay':
        raw = json.loads((Path(root)/'replay.raw.json').read_text())
        cold = [r for r in raw['frames'] if r.get('cold_activation')]
        result['cold_activation'] = {
            name: {key: stats([r.get(key, 0) for r in cold if r['condition'] == name])
                   for key in ('frame_ms', 'coordinates_ms', 'damage_render_ms')}
            for name in sorted({r['condition'] for r in cold})}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--case', required=True)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    source, case = Path(args.input).resolve(), Path(args.case).resolve()
    (case/'results').mkdir(parents=True, exist_ok=True)
    (case/'artifacts').mkdir(exist_ok=True)
    for group in ('baseline', 'fixed', 'live'):
        mode = 'live' if group == 'live' else 'replay'
        archive = case/'artifacts'/f'{group}-raw.zip'
        if not args.verify:
            names = [f'{mode}.json', f'{mode}.raw.json', f'{mode}.log']
            if mode == 'live':
                names += ['live.runtime.json', 'live.runtime.raw.json']
            with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
                for name in names:
                    z.write(source/group/name, name)
            with zipfile.ZipFile(archive) as z:
                for name in names:
                    assert z.read(name) == (source/group/name).read_bytes()
        with tempfile.TemporaryDirectory(prefix='star-text-cache-') as tmp:
            with zipfile.ZipFile(archive) as z:
                z.extractall(tmp)
            result = summarize_run(tmp, mode)
        result['raw_archive'] = dict(path=f'artifacts/{archive.name}', size=archive.stat().st_size,
                                      sha256=digest(archive))
        point = case/'results'/f'{group}.json'
        if args.verify:
            assert json.loads(point.read_text()) == result, f'{group} recomputation mismatch'
            with zipfile.ZipFile(case/'artifacts'/f'{group}-compact.zip') as z:
                assert z.read(point.name) == point.read_bytes()
                assert z.read('SHA256SUMS').decode().split()[0] == digest(point)
        else:
            point.write_text(json.dumps(result, indent=2)+'\n')
            with zipfile.ZipFile(case/'artifacts'/f'{group}-compact.zip', 'w', zipfile.ZIP_DEFLATED) as z:
                z.write(point, point.name)
                z.writestr('SHA256SUMS', f'{digest(point)}  {point.name}\n')
        print(group, 'raw unpack/recompute verified', result['raw_archive'])
    if not args.verify:
        paths = sorted([*case.glob('artifacts/*.zip'), *case.glob('results/*.json')])
        (case/'artifacts/SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(case)}\n' for p in paths))


if __name__ == '__main__':
    main()
