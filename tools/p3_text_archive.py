"""Package/recompute text-probe evidence after all performance runs finish."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

from p3_analyze import analyze as analyze_runtime
from p3_local_agents import stats
from p3_text_probe import summarize


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def analyze(root, name):
    root = Path(root)
    point = json.loads((root/f'{name}.json').read_text())
    raw = json.loads((root/f'{name}.raw.json').read_text())
    assert point['summary'] == summarize(raw['frames']), 'probe summary mismatch'
    result = {'verified': True, 'probe': point}
    if name == 'replay':
        result['by_repeat'] = {str(i): summarize([r for r in raw['frames'] if r['repeat'] == i])
                               for i in range(point['provenance']['args']['repeats'])}
    else:
        runtime = json.loads((root/'live.runtime.json').read_text())
        result['runtime_reanalysis'] = analyze_runtime(root/'live.runtime.json')
        runtime_raw = json.loads((root/'live.runtime.raw.json').read_text())
        # Both wrappers record one row per completed update and skip the init
        # and termination updates. Join sequence, then use runtime's warmup
        # boundary, since probe's initialization epoch precedes registration.
        assert len(raw['frames']) == len(runtime_raw['frames']), 'frame alignment mismatch'
        pairs = [(p, r) for p, r in zip(raw['frames'], runtime_raw['frames'])
                 if r['t'] >= runtime['workload']['warmup']]
        offset = [p['t']-r['t']-(p['frame_ms']+r['agent_ms'])/1000 for p, r in pairs]
        result['alignment'] = {'rows': len(pairs), 'epoch_offset_seconds': stats(offset)}
        assert max(offset)-min(offset) < .1, 'frame alignment drift >100ms'
        selected = [dict(p, condition='live', admitted=True) for p, _ in pairs]
        result['runtime_window_probe'] = summarize(selected)['live']
        full = stats([r['work_ms'] for _, r in pairs])
        tail = [(p, r) for p, r in pairs if r['work_ms'] >= full['p99']]
        result['tail'] = {
            'threshold_ms': full['p99'], 'frames': len(tail),
            'damage_render_ms': stats([p.get('damage_render_ms', 0) for p, _ in tail]),
            'effects': stats([p.get('effects_at_draw', 0) for p, _ in tail]),
            'zero_effect_frames': sum(p.get('effects_at_draw', 0) == 0 for p, _ in tail),
            'agent_ms': stats([r['agent_ms'] for _, r in tail]),
            'env_ms': stats([p['frame_ms'] for p, _ in tail]),
            'present_ms': stats([p.get('present_ms', 0) for p, _ in tail]),
            'flush_ms': stats([p.get('flush_ms', 0) for p, _ in tail]),
            'damage_share_of_tail_work': sum(p.get('damage_render_ms', 0) for p, _ in tail)/sum(r['work_ms'] for _, r in tail)}
        result['active_effect_frames'] = sum(p.get('effects_at_draw', 0) > 0 for p, _ in pairs)
        result['runtime'] = {k: v for k, v in runtime.items() if k not in ('censuses', 'agents')}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--case', required=True)
    parser.add_argument('--verify', action='store_true', help='recompute from archived ZIPs only')
    args = parser.parse_args()
    source, case = Path(args.input).resolve(), Path(args.case).resolve()
    (case/'results').mkdir(parents=True, exist_ok=True)
    (case/'artifacts').mkdir(exist_ok=True)
    for name in ('replay', 'live'):
        archive = case/'artifacts'/f'{name}-raw.zip'
        if not args.verify:
            names = [f'{name}.json', f'{name}.raw.json', f'{name}.log']
            if name == 'live':
                names += ['live.runtime.json', 'live.runtime.raw.json']
            with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
                for filename in names:
                    z.write(source/filename, filename)
            with zipfile.ZipFile(archive) as z:
                for filename in names:
                    assert z.read(filename) == (source/filename).read_bytes()
        with tempfile.TemporaryDirectory(prefix='star-text-verify-') as tmp:
            with zipfile.ZipFile(archive) as z:
                z.extractall(tmp)
            result = analyze(tmp, name)
        result['raw_archive'] = {'path': f'artifacts/{archive.name}', 'size': archive.stat().st_size,
                                 'sha256': digest(archive)}
        path = case/'results'/f'{name}.json'
        if args.verify:
            assert json.loads(path.read_text()) == result, f'{name} archived reanalysis mismatch'
        else:
            path.write_text(json.dumps(result, indent=2)+'\n')
            with zipfile.ZipFile(case/'artifacts'/f'{name}-compact.zip', 'w', zipfile.ZIP_DEFLATED) as z:
                z.write(path, path.name)
                z.writestr('SHA256SUMS', f'{digest(path)}  {path.name}\n')
        print(name, 'raw unpack/recompute OK', result['raw_archive'])
    if not args.verify:
        paths = sorted([*case.glob('artifacts/*.zip'), *case.glob('results/*.json')])
        (case/'artifacts/SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(case)}\n' for p in paths))


if __name__ == '__main__':
    main()
