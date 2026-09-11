"""R1 reproducible initialization, lifecycle and RNG differential evidence."""
import argparse
import contextlib
import hashlib
import io
import json
import platform
from pathlib import Path
import random
import subprocess
import sys


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    source = args.source.resolve()
    sys.path.insert(0, str(source))
    import os
    os.chdir(source)
    from rotk_env.runtime.bootstrap import prepare_scene, rng_state
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.components.rng import _derive_domain_seed
    from star_native import _native
    cases = []
    for mode in ('real_time', 'turn_based'):
        with contextlib.redirect_stdout(io.StringIO()):
            initial = prepare_scene(mode=mode, scenario='chibi-small', seed=42)
        for threads in (1, 2, 4):
            with RustRuntime(initial, threads=threads) as runtime:
                imported = runtime.export_state()
                first_delta = runtime.take_presentation_delta()
                runtime.step(1/30, wall_time=1720000001.0)
                runtime.reset(initial)
                reset = runtime.export_state()
                epoch = runtime.diagnostics()['epoch']
                py = random.Random(_derive_domain_seed(42, 'combat'))
                ops = [{'kind': 'randint', 'lo': 1, 'hi': 20}] * 2000
                expected = [py.randint(1,20) for _ in ops]
                actual = json.loads(runtime._native._rng_probe_json('combat', json.dumps(ops)))
                guards = {'initial_equal': initial == imported, 'reset_equal': initial == reset,
                          'new_epoch': epoch == 2 and first_delta['epoch'] == 1,
                          'random_equal': actual['results'] == expected,
                          'random_state_equal': actual['state'] == rng_state(py)}
                cases.append({'mode': mode, 'threads_requested': threads, 'guards': guards,
                              'initial': initial, 'imported': imported, 'reset': reset,
                              'random_expected': expected, 'random_actual': actual,
                              'random_state_expected': rng_state(py), 'epoch': epoch})
    raw = {'schema': 'star-native-r1-v1', 'source_sha': git(source,'rev-parse','HEAD'),
           'source_dirty': git(source,'status','--porcelain'),
           'tool_sha': git(Path(__file__).parents[2],'rev-parse','HEAD'),
           'python': sys.version, 'platform': platform.platform(),
           'extension_sha256': hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),
           'cargo_lock_sha256': hashlib.sha256((source/'Cargo.lock').read_bytes()).hexdigest(),
           'cases': cases}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(',', ':'))+'\n')
    summary = {k:v for k,v in raw.items() if k != 'cases'}
    summary['cases'] = [{k:v for k,v in c.items() if k in ('mode','threads_requested','guards','epoch')} for c in cases]
    summary['all_passed'] = all(all(c['guards'].values()) for c in cases)
    summary['raw_sha256'] = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.output.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    if not summary['all_passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
