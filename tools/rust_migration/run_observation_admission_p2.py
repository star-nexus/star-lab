"""Finite E8 P2 trajectory matrix, serial, telemetry only, no retry or P3.

This script never terminates or pauses a child for memory pressure. A failed
correctness check stops future launches, preserving every started attempt.
Completed trajectory checks do not close remaining targeted fault/VLM checks.
"""
import argparse
import fcntl
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import zipfile

LAB = Path(__file__).resolve().parents[2]
SOURCE = Path('/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main')
SOURCE_SHA = '6ec8e05d68c82d2731a382e00411bd58f2ed6f56'
EXTENSION_SHA = '3e0ebb663e7dc081948658ed2d61bb70ecc56e76fc87c405f70d098a807b7fc6'
P1 = Path('/Users/liyang/Developer/star-lab-runs/e8-p1-20261007')
P0 = Path('/Users/liyang/Developer/star-lab-runs/e8-p0-20261007')
CANONICAL = Path('/Users/liyang/Developer/star-lab-runs/e7-p2-20261005/inputs/rust-300-r3.trace.json.gz')
EXP = LAB / 'experiments/2026-10-rust-observation-admission'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(path)


def source_identity():
    assert subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip() == SOURCE_SHA
    assert not subprocess.check_output(['git', '-C', str(SOURCE), 'status', '--porcelain'], text=True)
    extension = SOURCE / '.venv/lib/python3.13/site-packages/star_native/_native.cpython-313-darwin.so'
    assert sha(extension) == EXTENSION_SHA
    return dict(source_sha=SOURCE_SHA, extension_sha256=EXTENSION_SHA)


def archive(name, files):
    target = EXP / 'artifacts' / (name + '-raw.zip')
    assert not target.exists(), 'Never overwrite evidence'
    members = {str(label): Path(p) for label, p in files}
    assert len(members) == len(files)
    sums = {label: sha(p) for label, p in members.items()}
    tmp = target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for label, p in members.items():
            z.write(p, label)
        z.writestr('SHA256SUMS', ''.join(d + '  ' + label + '\n' for label, d in sorted(sums.items())))
    tmp.replace(target)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for label, digest in sums.items():
            assert hashlib.sha256(z.read(label)).hexdigest() == digest
    return dict(file=str(target.relative_to(EXP)), bytes=target.stat().st_size, sha256=sha(target), inner_sha_verified=True)


def checksums():
    files = sorted(p for folder in ('results', 'artifacts') for p in (EXP / folder).rglob('*')
                   if p.is_file() and p.name != 'SHA256SUMS')
    (EXP / 'SHA256SUMS').write_text(''.join(sha(p) + '  ' + str(p.relative_to(EXP)) + '\n' for p in files))


def verify(output, trace, mode, threads):
    report = json.loads(output.read_text())
    recorded = json.loads(gzip.decompress(trace.read_bytes()))
    counts = report['counts']
    entries = recorded['entries']
    assert report['passed'] and report['failure'] is None
    assert report['mode'] == mode and report['threads'] == threads
    assert report['source_extension_sha256'] == EXTENSION_SHA
    assert report['baseline_extension_sha256'] == '838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544'
    assert report['input_sha256'] == sha(trace)
    assert counts['operations'] == len(entries)
    for key, kind in [('requests', 'request'), ('ticks', 'step'), ('presentation', 'presentation')]:
        assert counts.get(key, 0) == sum(op['kind'] == kind for op in entries)
    assert sha(output.with_suffix('.checks.jsonl')) == report['raw_sha256']
    with output.with_suffix('.checks.jsonl').open() as f:
        n = 0
        for expected, line in zip(entries, f):
            row = json.loads(line)
            assert (row['seq'], row['kind']) == (expected['seq'], expected['kind'])
            n += 1
        assert n == len(entries) and not f.read()
    return report


def p1_complete():
    prerequisite = P1 / 'host-old-reference.json'
    guard = P1 / 'host-old-reference.monitor.json'
    while not prerequisite.exists() or json.loads(guard.read_text())['status'] == 'running':
        pid = json.loads(guard.read_text())['child_pid']
        alive = subprocess.run(['ps', '-p', str(pid), '-o', 'stat='], capture_output=True, text=True).stdout.strip()
        assert alive and not alive.startswith('Z'), 'Oracle exited without completed evidence; do not restart'
        time.sleep(5)
    verify(prerequisite, P1 / 'host-no-reuse.trace.json.gz', 'single', 1)
    g = json.loads(guard.read_text())
    assert g['status'] == 'passed' and g['child_exit'] == 0
    assert g['automatic_pause'] is False and g['automatic_termination'] is False
    assert '88 passed' in (P1 / 'contracts.log').read_text()
    assert 'test result: ok.' in (P1 / 'rust-contracts.log').read_text()
    screens = [json.loads((P1 / (name + '.json')).read_text()) for name in
               ('screen-single', 'screen-no-reuse', 'screen-encoded', 'screen-old-single')]
    for field in ('final_state_sha256', 'response_stream_sha256', 'commands_sha256', 'requests'):
        assert len({r[field] for r in screens}) == 1, field
    files = [('raw/' + str(p.relative_to(P1)), p) for p in sorted(P1.rglob('*'))
             if p.is_file() and '__pycache__' not in p.parts]
    files += [('tools/' + p.name, p) for p in sorted((LAB / 'tools/rust_migration').glob('*observation_admission*.py'))]
    files += [('tools/' + p.name, p) for p in (LAB / 'tools/rust_migration').glob('*admitted_observation*.py')]
    bundle = P1 / 'admitted-observation-source.bundle'
    subprocess.run(['git', '-C', str(SOURCE), 'bundle', 'verify', str(bundle)], check=True, capture_output=True)
    package = archive('e8-p1-20261007', files)
    summary = dict(stage='P1', passed=True, source=source_identity(), raw=package,
        pytest_passed=88, rust_library_tests_passed=1, host_oracle=json.loads(prerequisite.read_text()),
        screening=[dict(mode=r['mode'], requests=r['requests'], extension_sha256=r['extension_sha256'],
                        mean_service_ms=sum(sum(s['query_service_ns']) for s in r['samples']) / r['requests'] / 1e6,
                        formal_performance=False, excludes=r['excludes']) for r in screens],
        ordinary_old_comparison='Unpaired small screen; candidate ordinary ~7.8% slower in this attempt, drift not isolated',
        performance_acceptance=False, default_adoption=False,
        dependency_proof='cached facts do not read wall metadata or action counters; available_skills reads sorted cold UnitSkills only',
        source_bundle_prerequisite='5b9658bc668b7d13f801351162f255f30622b32a; E7 display-preparation source/resume bundles preserved',
        remaining_targeted_checks=['cold GameStats', 'revision exhaustion', 'encoding failure commit prefix', 'panic/poison scope', 'VLM barrier'])
    write(EXP / 'results/p1-complete.json', summary)
    checksums()
    return summary


def record_stage(stage, runs):
    path = LAB / 'records/rust-observation-admission-status.json'
    state = json.loads(path.read_text())
    state.update(stage=stage, source_sha=SOURCE_SHA, persistent_runs=str(runs),
                 resource_policy='telemetry only; no automatic pause/kill/timeout')
    state['phases']['P1_owned_cache_prototype'] = 'complete; 88 contracts and independent short host oracle passed'
    state['phases']['P2_correctness'] = stage
    write(path, state)
    names = ['rust-observation-admission-plan.md', 'rust-observation-admission-plan.json', 'rust-observation-admission-status.json']
    (LAB / 'records/rust-observation-admission-SHA256SUMS').write_text(''.join(
        sha(LAB / 'records' / name) + '  records/' + name + '\n' for name in names))
    handoff = LAB / 'records/rust-parallel-handoff.md'
    marker = '## E8 P1已归档、P2串行校验（2026-10-07）'
    if marker not in handoff.read_text():
        text = f'{marker}\n\nP1 source `{SOURCE_SHA}`、88项契约通过，代表段完整响应/消费命令/最终状态一致；独立旧扩展短宿主轨迹全节点核验通过。小屏幕计时仅筛选，不作正式提速；ordinary与旧扩展单次未配对差异已保留。P2恢复先读 `{runs}/p2-progress.json`、当前组 `.progress.json` 和 `.monitor.json`。只串行校验，不启动P3；不得重复启动活进程。\n\n压力仅监测，不自动暂停/终止/超时；所有尝试保留，不重跑择优。P2轨迹全通过后仍须完成targeted错误/故障/VLM检查，不能把轨迹矩阵通过称全部P2完成。\n\n进度：`P0 █ | P1 █ | P2轨迹 ▓ | P2 targeted ░ | P3 ░ | 默认 ░`。既有GAP、容量、Frontier及5000Agents暂缓保持。\n\n'
        handoff.write_text(text + handoff.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=Path, required=True)
    parser.add_argument('--preregister', type=Path, required=True)
    a = parser.parse_args()
    a.runs.mkdir(parents=True, exist_ok=True)
    lock = (a.runs / 'matrix.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    progress = a.runs / 'p2-progress.json'
    assert not progress.exists(), 'Inspect existing execution; never restart automatically'
    reg = json.loads(a.preregister.read_text())
    assert reg['runner_sha256'] == sha(__file__)
    assert reg['oracle_sha256'] == sha(Path(__file__).with_name('verify_admitted_observation_replay.py'))
    assert reg['monitor_sha256'] == sha(Path(__file__).with_name('monitor_observation_admission.py'))
    source_identity()
    completed = []
    write(progress, dict(status='waiting_for_P1_oracle', parent_pid=__import__('os').getpid(), completed=[]))
    try:
        p1_complete()
        record_stage('P2 trajectory matrix running; targeted checks pending', a.runs)
        for spec in reg['jobs']:
            source_identity()
            trace = Path(spec['trace'])
            assert sha(trace) == spec['trace_sha256']
            output = a.runs / (spec['name'] + '.json')
            monitor = a.runs / (spec['name'] + '.monitor.json')
            assert not output.exists() and not monitor.exists()
            cmd = [sys.executable, str(Path(__file__).with_name('verify_admitted_observation_replay.py')),
                   '--source', str(SOURCE), '--trace', str(trace), '--baseline-extension',
                   str(P1 / 'baseline/star_native/_native.cpython-313-darwin.so'),
                   '--output', str(output), '--mode', spec['mode'], '--threads', str(spec['threads'])]
            if spec.get('admission'):
                assert sha(spec['admission']) == spec['admission_sha256']
                cmd += ['--admission', spec['admission']]
            write(progress, dict(status='running', current=spec, completed=completed))
            subprocess.run([sys.executable, str(Path(__file__).with_name('monitor_observation_admission.py')),
                            '--report', str(monitor), '--', *cmd], check=True, cwd=LAB)
            report = verify(output, trace, spec['mode'], spec['threads'])
            g = json.loads(monitor.read_text())
            assert g['status'] == 'passed' and g['automatic_pause'] is False and g['automatic_termination'] is False
            files = [('raw/' + p.name, p) for p in sorted(a.runs.glob(spec['name'] + '.*')) if p.is_file()]
            package = archive('e8-p2-20261007-' + spec['name'], files)
            completed.append(dict(spec=spec, report=report, raw=package, resource_events=len(g['events'])))
            write(EXP / 'results/p2-trajectory-progress.json', dict(completed=completed, planned=len(reg['jobs']), correctness_only=True))
            checksums()
        result = dict(status='trajectory_matrix_passed', completed=completed,
            targeted_checks_complete=False, P2_complete=False, P3_started=False,
            performance_claim=False, default_adoption=False)
        write(a.runs / 'p2-trajectory-complete.json', result)
        write(EXP / 'results/p2-trajectory-complete.json', result)
        write(progress, result)
        record_stage('P2 trajectory matrix passed; targeted checks pending', a.runs)
        checksums()
    except BaseException as error:
        failure = dict(status='failed', error=repr(error), completed=completed,
                       automatic_restart=False, raw_preserved=True)
        write(progress, failure)
        write(a.runs / 'p2-failure.json', failure)
        raise


if __name__ == '__main__':
    main()
