"""Recover E8 supervisors after ENOSPC, retaining the existing oracle PID.

Never kill/pause the v1 child, restart an attempt, or enter P3. The staged v2
extension keeps the installed v1 extension immutable for its active oracle.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import run_observation_admission_p2 as common

LAB = common.LAB
SOURCE = common.SOURCE
EXP = common.EXP
ROOT = Path('/Users/liyang/Developer/star-lab-runs/e8-accounting-v2-20261007')
PREVIOUS = Path('/Users/liyang/Developer/star-lab-runs/e8-p2-20261007')
SHA = '11d9927f7a1bffa32dd85c9009944424826508e5'
EXT = '9bb2fa4412bc810fbd751c42f525614f8cddb42e8c136612a51495fa0679f0d9'


def identity():
    assert subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip() == SHA
    assert not subprocess.check_output(['git', '-C', str(SOURCE), 'status', '--porcelain'], text=True)
    so = ROOT / 'extension/star_native/_native.cpython-313-darwin.so'
    assert common.sha(so) == EXT
    return dict(source_sha=SHA, extension_sha256=EXT, extension_path=str(so))


def active(pid):
    value = subprocess.run(['ps', '-p', str(pid), '-o', 'stat='], capture_output=True, text=True).stdout.strip()
    return bool(value) and not value.startswith('Z')


def corrected_contracts():
    assert '88 passed' in (ROOT / 'contracts.log').read_text()
    reports = [json.loads((ROOT / (name + '.json')).read_text()) for name in
               ('screen-encoded-diagnostic', 'screen-no-reuse-diagnostic')]
    for report in reports:
        assert report['extension_sha256'] == EXT and report['requests'] == 19
        for segment in report['diagnostics']:
            for query in segment['report']['query_diagnostics']:
                stats = query['accounting_after_request']
                assert type(stats['agent_actions']) is int and type(stats['faction_actions']) is int
    for field in ('final_state_sha256', 'response_stream_sha256', 'commands_sha256'):
        assert reports[0][field] == reports[1][field]
        old = json.loads((common.P1 / 'screen-encoded-diagnostic.json').read_text())
        assert reports[0][field] == old[field]
    common.archive('e8-accounting-v2-20261007', [('raw/' + str(p.relative_to(ROOT)), p)
        for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts])
    common.checksums()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=Path, required=True)
    parser.add_argument('--preregister', type=Path, required=True)
    a = parser.parse_args()
    a.runs.mkdir(parents=True, exist_ok=True)
    lock = (a.runs / 'matrix.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    progress = a.runs / 'p2-progress.json'
    assert not progress.exists(), 'Never duplicate a started matrix'
    reg = json.loads(a.preregister.read_text())
    assert common.sha(__file__) == reg['runner_sha256']
    assert common.sha(Path(common.__file__)) == reg['common_runner_sha256']
    oracle = Path(__file__).with_name('verify_admitted_observation_replay_v2.py')
    monitor_tool = Path(__file__).with_name('monitor_observation_admission.py')
    assert common.sha(oracle) == reg['oracle_sha256'] and common.sha(monitor_tool) == reg['monitor_sha256']
    identity()
    completed = []
    common.write(progress, dict(status='recovering_existing_ordinary_child', parent_pid=os.getpid(), completed=[]))
    try:
        # Changed source deliberately prevents v1 launching a cached mode.
        # Let its ongoing single ordinary oracle finish and archive normally.
        recovery = reg['recovery']
        child_pid = recovery['existing_child_pid']
        monitor_path = Path(recovery['adopted_monitor'])
        while active(child_pid):
            time.sleep(5)
        while json.loads(monitor_path.read_text())['status'] == 'running':
            assert active(recovery['adopted_monitor_pid']), 'Adopted monitor exited without final status'
            time.sleep(5)
        adopted = json.loads(monitor_path.read_text())
        assert adopted['status'] == 'adopted_process_exited'
        baseline = common.verify(PREVIOUS / 'canonical-single-t1.json', common.CANONICAL, 'single', 1)
        assert not (PREVIOUS / 'canonical-segment_no_reuse-t1.monitor.json').exists()
        files = [('raw/' + p.name, p) for p in sorted(PREVIOUS.glob('canonical-single-t1.*')) if p.is_file()]
        files += [('recovery/' + monitor_path.name, monitor_path)]
        package = common.archive('e8-p2-recovered-ordinary-20261008', files)
        common.write(EXP / 'results/p2-recovered-ordinary.json', dict(
            report=baseline, raw=package, original_supervisor_exited=True,
            child_retained_without_restart=True, child_exit_status='unknown; adopted non-child PID',
            complete_oracle_checks_verified=True, normal_guard_pass_claim=False,
            cause='Supervisors exited on historical ENOSPC; existing oracle ran to completion',
            performance_claim=False))
        corrected_contracts()
        common.EXTENSION_SHA = EXT
        common.SOURCE_SHA = SHA
        common.record_stage('P2 v2 trajectory matrix running; corrected non-null accounting; targeted checks pending', a.runs)
        for spec in reg['jobs']:
            identity()
            trace = Path(spec['trace'])
            assert common.sha(trace) == spec['trace_sha256']
            output = a.runs / (spec['name'] + '.json')
            monitor = a.runs / (spec['name'] + '.monitor.json')
            assert not output.exists() and not monitor.exists()
            cmd = [sys.executable, str(oracle), '--source', str(SOURCE), '--extension-dir', str(ROOT / 'extension'),
                   '--trace', str(trace), '--baseline-extension',
                   str(common.P1 / 'baseline/star_native/_native.cpython-313-darwin.so'),
                   '--output', str(output), '--mode', spec['mode'], '--threads', str(spec['threads'])]
            if spec.get('admission'):
                assert common.sha(spec['admission']) == spec['admission_sha256']
                cmd += ['--admission', spec['admission']]
            common.write(progress, dict(status='running', parent_pid=os.getpid(), current=spec, completed=completed))
            subprocess.run([sys.executable, str(monitor_tool), '--report', str(monitor), '--', *cmd], check=True, cwd=LAB)
            report = common.verify(output, trace, spec['mode'], spec['threads'])
            guard = json.loads(monitor.read_text())
            assert guard['status'] == 'passed' and not guard['automatic_pause'] and not guard['automatic_termination']
            files = [('raw/' + p.name, p) for p in sorted(a.runs.glob(spec['name'] + '.*')) if p.is_file()]
            package = common.archive('e8-p2-recovery-20261008-' + spec['name'], files)
            completed.append(dict(spec=spec, report=report, raw=package, resource_events=len(guard['events'])))
            common.write(EXP / 'results/p2-v2-trajectory-progress.json', dict(completed=completed, planned=len(reg['jobs']), correctness_only=True))
            common.checksums()
        result = dict(status='trajectory_matrix_passed', completed=completed, source=identity(),
                      targeted_checks_complete=False, P2_complete=False, P3_started=False, performance_claim=False)
        common.write(a.runs / 'p2-trajectory-complete.json', result)
        common.write(EXP / 'results/p2-v2-trajectory-complete.json', result)
        common.write(progress, result)
        common.record_stage('P2 v2 trajectory matrix passed; targeted checks pending', a.runs)
        common.checksums()
    except BaseException as error:
        common.write(progress, dict(status='failed', error=repr(error), completed=completed,
                                    automatic_restart=False, raw_preserved=True))
        raise


if __name__ == '__main__':
    main()
