"""Reproduce pause-only policy using synthetic children and fake sysctl input.

Does not alter macOS pressure, run STAR, or count as E7 correctness evidence.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import shlex
import time


def wait_until(predicate, seconds=8):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if predicate():
            return
        time.sleep(.03)
    raise AssertionError('Synthetic guard control timed out')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(exist_ok=False)
    d = a.output.resolve()
    guard = Path(__file__).with_name('guard_display_preparation_pause_only.py')
    spec = importlib.util.spec_from_file_location('pauseguard', guard)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    policy = m.PauseOnlyPolicy(60)
    assert policy.action(2, False, 0) is None
    assert policy.action(2, False, 5) == 'pause'
    assert policy.action(1, True, 10) is None
    assert policy.action(1, True, 69) is None
    assert policy.action(1, True, 70) == 'resume'
    assert policy.action(4, False, 71) == 'pause'
    assert m.PauseOnlyPolicy(60).action(8, False, 0) == 'pause'
    binary = d / 'bin'
    binary.mkdir()
    level = d / 'level'
    level.write_text('1')
    stub = binary / 'sysctl'
    stub.write_text('#!/bin/sh\nif [ "$1" = "-n" ]; then cat ' + shlex.quote(str(level)) + '\nelse echo simulated_swap_snapshot\nfi\n')
    stub.chmod(0o755)
    child = d / 'child.py'
    child.write_text('import json,time\nfrom pathlib import Path\nfor i in range(40):\n'
        ' Path(' + repr(str(d / 'count')) + ').write_text(str(i))\n'
        ' print(json.dumps(dict(progress=i)),flush=True)\n time.sleep(.05)\n')
    env = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ['PATH'])

    def state(report):
        return json.loads(report.read_text()) if report.exists() else {}

    def run(case, limit=6144):
        level.write_text('1')
        (d / 'count').unlink(missing_ok=True)
        report = d / (case + '.json')
        command = [sys.executable, str(guard), '--report', str(report),
                   '--limit-mib', str(limit), '--poll-seconds', '.05',
                   '--resume-normal-seconds', '.2', '--no-vmmap', '--',
                   sys.executable, str(child)]
        process = subprocess.Popen(command, env=env, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
        return process, report

    def progressed(n):
        return (d / 'count').exists() and int((d / 'count').read_text() or '0') >= n

    process, report = run('pause-resume')
    try:
        wait_until(lambda: progressed(5))
        level.write_text('2')
        wait_until(lambda: state(report).get('status') == 'paused')
        pid = state(report)['child_pid']
        count = (d / 'count').read_text()
        time.sleep(.2)
        assert (d / 'count').read_text() == count
        level.write_text('1')
        wait_until(lambda: any(e['event'] == 'resume' for e in state(report).get('events', [])))
        assert state(report)['child_pid'] == pid
        assert process.wait(timeout=8) == 0
        final = state(report)
        assert final['status'] == 'passed' and final['paused_seconds'] > 0 and not final['paused']
        rows = [json.loads(line)['progress'] for line in report.with_suffix('.child.log').read_text().splitlines()]
        assert rows == list(range(40))
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=12)
    process, report = run('critical')
    try:
        wait_until(lambda: progressed(3))
        level.write_text('2')
        wait_until(lambda: state(report).get('status') == 'paused')
        level.write_text('4')
        time.sleep(.25)
        assert process.poll() is None and state(report)['paused']
        level.write_text('1')
        assert process.wait(timeout=8) == 0
        final = state(report)
        assert final['status'] == 'passed' and final['automatic_termination'] is False
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=12)
    process, report = run('budget', .001)
    assert process.wait(timeout=8) == 0
    assert state(report)['status'] == 'passed'
    assert any(row['above_reference_budget'] for row in state(report)['samples'])
    result = dict(passed=True, kind='synthetic guard lifecycle; not E7 correctness',
        guard_sha256=hashlib.sha256(guard.read_bytes()).hexdigest(),
        control_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        cases=['warning pauses', 'same PID resumes', 'progress stops while paused',
               'all 40 progress rows preserved exactly once', 'critical preserves paused child then resumes',
               'budget telemetry never terminates', 'unknown pressure pauses',
               '60s default normal-recovery policy'], production_defaults_changed=False)
    (d / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
