"""Finish E7 P2 after a resource interruption, retaining completed canonical jobs."""
import argparse
import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--source-sha', required=True)
    p.add_argument('--trace', type=Path, required=True)
    p.add_argument('--previous-runs', type=Path, required=True)
    p.add_argument('--runs', type=Path, required=True)
    a = p.parse_args()
    assert a.runs.resolve() != a.previous_runs.resolve()
    a.runs.mkdir(exist_ok=False)
    python = a.source / '.venv/bin/python'
    here = Path(__file__).parent
    completed = []
    probe_hash = hashlib.sha256((here / 'display_preparation_probe.py').read_bytes()).hexdigest()

    def status(stage, **extra):
        value = dict(stage=stage, completed=completed, source_sha=a.source_sha,
                     updated_unix=time.time(), capacity_claim=False, **extra)
        (a.runs / 'resume-progress.json').write_text(json.dumps(value, indent=2) + '\n')
        print(json.dumps(value), flush=True)

    def verify(meta):
        assert meta['source_sha'] == a.source_sha and not meta['source_dirty']
        assert meta['task'] == 'correctness' and meta['all_passed'] and meta['formal']
        assert meta['full_authority'] and meta['counts'] == dict(request=40994, step=9880, presentation=9880)
        assert meta['tool_sha256'] == probe_hash and meta['overscan_clock'] == 'items'

    try:
        inherited = []
        for name in ('p2-correctness-t1-static', 'p2-correctness-t4-exercise'):
            path = a.previous_runs / (name + '.json')
            meta = json.loads(path.read_text())
            verify(meta)
            guard = json.loads((a.previous_runs / (name + '.guard.json')).read_text())
            assert guard['status'] == 'passed'
            for key in ('raw', 'authority_raw', 'pixel_raw'):
                item = meta[key]
                assert hashlib.sha256((a.previous_runs / item['file']).read_bytes()).hexdigest() == item['sha256']
            for file in a.previous_runs.glob(name + '.*'):
                if file.is_file():
                    shutil.copy2(file, a.runs / file.name)
            inherited.append(dict(run=name, canonical_directory=str(a.previous_runs),
                                  metadata_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), rerun=False))
            completed.append(name)
        (a.runs / 'inherited-correctness.json').write_text(json.dumps(inherited, indent=2) + '\n')
        for name, threads, script in (('p2-correctness-typed-t1-exercise', 1, 'exercise'),
                                     ('p2-correctness-typed-t4-static', 4, 'static')):
            status('waiting for normal memory pressure', current=name)
            # Stable normal pressure for a full minute; preserve original guard.
            normal = 0
            while normal < 3:
                level = int(subprocess.check_output(['sysctl', '-n', 'kern.memorystatus_vm_pressure_level'], text=True))
                normal = normal + 1 if level == 1 else 0
                status('waiting for normal memory pressure', current=name, pressure=level, normal_samples=normal)
                if normal < 3:
                    time.sleep(30)
            status('P2 full correctness', current=name)
            command = [str(python), str(here / 'guard_display_preparation.py'),
                       '--report', str(a.runs / (name + '.guard.json')), '--',
                       str(python), str(here / 'display_preparation_probe.py'),
                       '--source', str(a.source), '--source-sha', a.source_sha,
                       '--trace', str(a.trace), '--output', str(a.runs / (name + '.json')),
                       '--task', 'correctness', '--threads', str(threads), '--consumer', 'reuse_typed',
                       '--script', script, '--overscan-clock', 'items', '--full-authority']
            with (a.runs / (name + '.supervisor.log')).open('w') as log:
                subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
            meta = json.loads((a.runs / (name + '.json')).read_text())
            verify(meta)
            assert meta['threads'] == threads and meta['consumer'] == 'reuse_typed' and meta['display_script'] == script
            (a.runs / (name + '.log')).write_bytes((a.runs / (name + '.guard.child.log')).read_bytes())
            completed.append(name)
        status('P2 complete; all four full correctness jobs passed')
    except BaseException as error:
        status('stopped or failed', error=repr(error))
        raise


if __name__ == '__main__':
    main()
