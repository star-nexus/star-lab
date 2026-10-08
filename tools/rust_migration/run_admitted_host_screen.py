"""Exactly four serial live host attempts; no retries, default or capacity change."""
import argparse
import fcntl
import json
from pathlib import Path
import subprocess
import sys

from run_observation_admission_p2 import LAB, EXP, SOURCE, sha, write, archive, checksums
from analyze_admitted_host import analyze, verify_point


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--preregister', type=Path, required=True)
    a = p.parse_args()
    reg = json.loads(a.preregister.read_text())
    root = Path(reg['runs']);root.mkdir(parents=True, exist_ok=True)
    lock = (root / 'owner.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert not (root / 'progress.json').exists(), 'No duplicate launch or automatic retry'
    tools = LAB / 'tools/rust_migration'
    progress = root / 'progress.json'
    points = []
    def identity():
        assert subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip() == reg['source_sha']
        assert not subprocess.check_output(['git','-C',str(SOURCE),'status','--porcelain'],text=True)
        for name, digest in reg['frozen_files'].items():
            assert sha(LAB / name) == digest, name
        assert sha(Path(reg['extension_dir']) / 'star_native/_native.cpython-313-darwin.so') == reg['extension_sha256']
    try:
        for i, mode in enumerate(reg['order']):
            identity()
            out = root / f'{i+1}-{mode}.json'
            assert not out.exists()
            write(progress, dict(status='running',attempt=i+1,total=4,mode=mode,completed=len(points),child_report=str(out)))
            command = [str(SOURCE/'.venv/bin/python'),str(tools/'monitor_observation_admission.py'),
                       '--report',str(out.with_suffix('.monitor.json')),'--',
                       str(SOURCE/'.venv/bin/python'),str(tools/'admitted_observation_host.py'),
                       '--host-mode',mode,*reg['runtime_args'],'--output',str(out)]
            with (root / f'{i+1}.supervisor.log').open('w') as log:
                result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
            assert result.returncode == 0, f'Attempt {i+1} exited {result.returncode}; no retry'
            verify_point(out)
            points.append(out)
            write(progress, dict(status='attempt_complete',completed=len(points),total=4,mode=mode))
        identity()
        result = analyze(points)
        write(root/'analysis.json',result)
        files = [('raw/'+p.name,p) for p in sorted(root.iterdir()) if p.is_file() and p.name not in ('owner.lock','parent.log')]
        files += [('tools/'+Path(name).name,LAB/name) for name in reg['frozen_files']]
        files += [('preregister.json',a.preregister)]
        package = archive('e8-full-host-screen-20261008', files)
        write(EXP/'results/full-host-screen.json', dict(analysis=result,raw=package))
        checksums()
        write(progress, dict(status='complete',completed=4,total=4,analysis=result,raw=package))
    except BaseException as error:
        write(progress, dict(status='failed',completed=len(points),failure=repr(error),automatic_retry=False))
        files = [('raw/'+p.name,p) for p in sorted(root.iterdir()) if p.is_file() and p.name not in ('owner.lock','parent.log')]
        files += [('preregister.json',a.preregister)]
        package = archive('e8-full-host-screen-interruption-20261008',files)
        write(EXP/'results/full-host-screen-interruption.json',dict(failure=repr(error),raw=package,automatic_retry=False))
        checksums()
        raise


if __name__ == '__main__':
    main()
