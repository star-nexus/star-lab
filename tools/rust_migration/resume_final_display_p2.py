"""Reuse three verified E7 P2 groups; run only the fourth, then finalize P2."""
import argparse
import json
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path

from finalize_display_correctness import JOBS, SOURCE, EXTENSION, sha, verify_job


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--trace', type=Path, required=True)
    p.add_argument('--previous-runs', type=Path, required=True)
    p.add_argument('--runs', type=Path, required=True)
    p.add_argument('--limit-mib', type=float, default=6144)
    p.add_argument('--run-date', required=True)
    a = p.parse_args()
    assert math.isfinite(a.limit_mib) and a.limit_mib > 0
    assert a.runs.resolve() != a.previous_runs.resolve()
    a.runs.mkdir(exist_ok=False)
    here = Path(__file__).resolve().parent
    completed = []

    def status(stage, **extra):
        v = dict(stage=stage, completed=completed, source_sha=SOURCE,
                 fourth_limit_mib=a.limit_mib, updated_unix=time.time(),
                 capacity_claim=False, **extra)
        (a.runs / 'resume-progress.json').write_text(json.dumps(v, indent=2) + '\n')
        print(json.dumps(v), flush=True)

    try:
        assert subprocess.check_output(['git', '-C', str(a.source), 'rev-parse', 'HEAD'], text=True).strip() == SOURCE
        assert not subprocess.check_output(['git', '-C', str(a.source), 'status', '--porcelain', '--untracked-files=no'], text=True)
        extension = a.source / '.venv/lib/python3.13/site-packages/star_native/_native.cpython-313-darwin.so'
        assert sha(extension) == EXTENSION
        inherited = []
        identity = None
        for index, job in enumerate(JOBS[:3]):
            m, guard = verify_job(a.previous_runs, job, (2500, 2500, 5120)[index])
            assert sha(here / 'display_preparation_probe.py') == m['tool_sha256']
            assert sha(a.trace) == m['trace_sha256']
            keys = ('source_sha', 'tool_sha256', 'extension_sha256', 'trace_sha256',
                    'initial_sha256', 'display_script_sha256', 'fixture_sha256', 'dependency_lock_sha256')
            current = {k: m[k] for k in keys}
            if identity is None:
                identity = current
            assert current == identity
            for file in a.previous_runs.glob(job[0] + '.*'):
                if file.is_file():
                    shutil.copy2(file, a.runs / file.name)
            inherited.append(dict(run=job[0], metadata_sha256=sha(a.previous_runs / (job[0] + '.json')),
                                  guard_limit_mib=guard['limit_mib'], rerun=False))
            completed.append(job[0])
        (a.runs / 'inherited-correctness.json').write_text(json.dumps(inherited, indent=2) + '\n')
        name = JOBS[3][0]
        normal = 0
        while normal < 3:
            level = int(subprocess.check_output(['sysctl', '-n', 'kern.memorystatus_vm_pressure_level'], text=True))
            normal = normal + 1 if level == 1 else 0
            status('waiting for normal memory pressure', current=name, pressure=level, normal_samples=normal)
            if normal < 3:
                time.sleep(30)
        status('P2 full correctness', current=name)
        command = [sys.executable, str(here / 'guard_display_preparation.py'),
                   '--report', str(a.runs / (name + '.guard.json')),
                   '--limit-mib', str(a.limit_mib), '--', sys.executable,
                   str(here / 'display_preparation_probe.py'), '--source', str(a.source),
                   '--source-sha', SOURCE, '--trace', str(a.trace),
                   '--output', str(a.runs / (name + '.json')), '--task', 'correctness',
                   '--threads', '4', '--consumer', 'reuse_typed', '--script', 'static',
                   '--overscan-clock', 'items', '--full-authority']
        with (a.runs / (name + '.supervisor.log')).open('w') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
        verify_job(a.runs, JOBS[3], a.limit_mib)
        completed.append(name)
        status('P2 all four passed; verifying and archiving')
        subprocess.run([sys.executable, str(here / 'finalize_display_correctness.py'),
                        '--runs', str(a.runs), '--third-limit-mib', '5120',
                        '--remaining-limit-mib', str(a.limit_mib), '--run-date', a.run_date], check=True)
        status('P2 complete; all four full correctness jobs passed')
    except BaseException as error:
        status('stopped or failed', error=repr(error))
        (a.runs / 'p2-finalization.json').write_text(json.dumps(
            dict(status='stopped or failed', error=repr(error), P2_complete=False), indent=2) + '\n')
        raise


if __name__ == '__main__':
    main()
