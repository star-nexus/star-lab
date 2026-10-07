"""P3 only: reuse completed P2, serial 24 full paired traces, no auto-kill/retry.

Pressure pauses preserve child state but invalidate the entire timing run.
Original performance driver/analyzer and pinned product remain unchanged.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import zipfile

from finalize_display_correctness_pause import JOBS, SOURCE, EXTENSION, STREAM, FINAL, verify_job
from guard_display_preparation_resumable import atomic_json, pressure
from guard_display_preparation_pause_only import POLICY
from analyze_display_preparation import analyze


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as file:
        for block in iter(lambda: file.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def job_specs():
    return [dict(name=f'p3-{consumer}-t{threads}-{script}-r{round_id}',
                 consumer=consumer, threads=threads, script=script, round=round_id)
            for round_id in (1, 2, 3) for script in ('static', 'exercise')
            for consumer in ('baseline', 'reuse_typed') for threads in (1, 4)]


def timing_resource_valid(guard):
    return (guard.get('status') == 'passed' and guard.get('child_exit') == 0
            and guard.get('stop_reason') is None and guard.get('policy') == POLICY
            and guard.get('automatic_termination') is False
            and guard.get('budget_enforced') is False
            and guard.get('paused_seconds') == 0 and not guard.get('paused')
            and not guard.get('events') and bool(guard.get('samples'))
            and all(row['pressure'] == 1 for row in guard['samples']))


def archive_run(exp, runs, name):
    files = sorted(p for p in runs.glob(name + '.*') if p.is_file())
    assert files
    target = exp / 'artifacts' / ('display-preparation-p3-20261007-' + name + '-raw.zip')
    assert not target.exists(), 'Do not replace/select evidence'
    temporary = target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in files:
            z.write(file, 'raw/' + file.name)
        z.writestr('SHA256SUMS', ''.join(sha(p) + '  raw/' + p.name + '\n' for p in files))
    temporary.rename(target)
    with zipfile.ZipFile(target) as z:
        for line in z.read('SHA256SUMS').decode().splitlines():
            digest, member = line.split('  ', 1)
            assert hashlib.sha256(z.read(member)).hexdigest() == digest
        for file in files:
            assert hashlib.sha256(z.read('raw/' + file.name)).hexdigest() == sha(file)
    return dict(file=target.name, sha256=sha(target), bytes=target.stat().st_size)


def refresh_checksums(exp):
    files = sorted(p for folder in ('results', 'artifacts')
                   for p in (exp / folder).rglob('*') if p.is_file() and p.name != 'SHA256SUMS')
    (exp / 'artifacts/SHA256SUMS').write_text(''.join(sha(p) + '  ' + p.relative_to(exp).as_posix() + '\n' for p in files))


def verify_performance(runs, spec, reference):
    m = json.loads((runs / (spec['name'] + '.json')).read_text())
    assert m['task'] == 'paired' and m['formal'] and m['all_passed']
    assert not m['diagnostic'] and not m['probe_control'] and not m['full_authority']
    assert not m['source_dirty'] and m['source_sha'] == SOURCE
    assert (m['consumer'], m['threads'], m['display_script']) == (spec['consumer'], spec['threads'], spec['script'])
    assert m['modes'] == ['baseline', 'empty_territory', 'empty_territory', 'baseline']
    assert m['overscan_clock'] == 'wall' and m['display_clock'] == 'fixed'
    assert m['driver'] == 'dummy' and m['surface'] == [2480, 1239]
    assert m['counts'] == dict(request=40994, step=9880, presentation=9880)
    assert m['stream_sha256'] == STREAM and m['final_state_sha256'] == FINAL
    for key in ('extension_sha256', 'trace_sha256', 'initial_sha256', 'display_script_sha256', 'fixture_sha256', 'dependency_lock_sha256'):
        assert m[key] == reference[key], key
    assert m['tool_sha256'] == sha(Path(__file__).with_name('display_preparation_performance.py'))
    for key in ('raw', 'workload_raw'):
        item = m[key]; p = runs / item['file']
        assert sha(p) == item['sha256'] and p.stat().st_size == item['bytes']
        rows = json.loads(gzip.decompress(p.read_bytes()))
        assert len(rows) == 4 and all(len(side) == 9880 for side in rows)
        if key == 'workload_raw':
            assert all([r['tick'] for r in side] == list(range(1, 9881)) for side in rows)
    return m


def publish(lab, exp, runs, value, complete):
    filename = 'p3-complete.json' if complete else 'p3-interruption-20261007.json'
    atomic_json(exp / 'results' / filename, value)
    for name in ('manifest.yaml', 'results/open-gap-status-resume.json', 'results/p3-preregister-20261007.json'):
        p = exp / name; data = json.loads(p.read_text())
        data.update(status=value['stage'], p3_evidence='results/' + filename, p3_completed_jobs=len(value['completed']))
        if name.endswith('open-gap-status-resume.json'):
            data.update(stage=value['stage'], current=None)
        p.write_text(json.dumps(data, indent=2) + '\n')
    report = ('## E7 P3阶段收尾（2026-10-07）\n\n' + value['stage'] + '；完整计时通过资源有效性核验的组数'
              + str(len(value['completed'])) + '/24。原始样本、慢尾、失败尝试全部保留；门槛和分析见E7 results/'
              + filename + '。P2完整正确性4/4保持，不启用默认、不进入单实例确认或窗口，不改容量/Frontier或关闭既有GAP。\n'
              + '进度：`P2 █ | P3 ' + str(len(value['completed'])) + '/24 | 单实例确认/窗口/默认接入 ░`。\n\n')
    for name in ('records/rust-parallel-handoff.md', 'records/rust-system-parallel-status.md'):
        p = lab / name; first, rest = p.read_text().split('\n', 1); p.write_text(first + '\n\n' + report + rest.lstrip('\n'))
    for name in ('README.md', 'analysis.md', 'decision.md'):
        p = exp / name; p.write_text(report + p.read_text())
    refresh_checksums(exp)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--trace', type=Path, required=True)
    p.add_argument('--p2-runs', type=Path, required=True)
    p.add_argument('--runs', type=Path, required=True)
    a = p.parse_args(); a.runs.mkdir(exist_ok=False)
    here = Path(__file__).resolve().parent; lab = here.parents[1]
    exp = lab / 'experiments/2026-10-rust-display-preparation'
    prereg = json.loads((exp / 'results/p3-preregister-20261007.json').read_text())
    completed, records = [], []
    current = None
    attempt_artifact = None

    def status(stage, **extra):
        value = dict(stage=stage, completed=completed, total=24, current=current, source_sha=SOURCE,
                     updated_unix=time.time(), capacity_claim=False, production_enabled=False, **extra)
        atomic_json(a.runs / 'p3-progress.json', value)
        print(json.dumps(value), flush=True)
        return value

    try:
        assert prereg['source_sha'] == SOURCE and prereg['runs_directory'] == str(a.runs)
        for name, digest in prereg['tool_sha256'].items(): assert sha(here / name) == digest
        assert subprocess.check_output(['git', '-C', str(a.source), 'rev-parse', 'HEAD'], text=True).strip() == SOURCE
        assert not subprocess.check_output(['git', '-C', str(a.source), 'status', '--porcelain', '--untracked-files=no'], text=True).strip()
        assert sha(a.source / '.venv/lib/python3.13/site-packages/star_native/_native.cpython-313-darwin.so') == EXTENSION
        full = json.loads((exp / 'results/p2-complete.json').read_text()); assert full['passed'] and full['completed_jobs'] == 4
        for index, job in enumerate(JOBS):
            m, guard = verify_job(a.p2_runs, job, (2500, 2500, 5120, 6144)[index])
            assert {k: m[k] for k in full['identity']} == full['identity']
        assert sha(a.trace) == full['identity']['trace_sha256']
        specs = job_specs(); assert specs == prereg['jobs']
        commands = []
        for spec in specs:
            command = [str(a.source / '.venv/bin/python'), str(here / 'display_preparation_performance.py'),
                '--source', str(a.source), '--source-sha', SOURCE, '--trace', str(a.trace),
                '--output', str(a.runs / (spec['name'] + '.json')), '--task', 'paired', '--candidate', 'empty_territory',
                '--threads', str(spec['threads']), '--consumer', spec['consumer'], '--script', spec['script'], '--overscan-clock', 'wall']
            commands.append(dict(**spec, argv=command))
        atomic_json(a.runs / 'p3-commands.json', commands)
        for item in commands:
            current = item['name']; normal = 0; attempt_artifact = None
            while normal < 3:
                level = pressure(); normal = normal + 1 if level == 1 else 0
                status('waiting for normal pressure before timing', pressure=level, normal_samples=normal)
                if normal < 3: time.sleep(30)
            status('P3 serial full paired timing')
            command = [str(a.source / '.venv/bin/python'), str(here / 'guard_display_preparation_pause_only.py'),
                '--report', str(a.runs / (current + '.guard.json')), '--no-vmmap', '--limit-mib', '6144', '--', *item['argv']]
            with (a.runs / (current + '.supervisor.log')).open('w') as log:
                result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
            artifact = archive_run(exp, a.runs, current)
            attempt_artifact = artifact
            assert result.returncode == 0, 'Child/monitor failed; raw preserved'
            m = verify_performance(a.runs, item, full['identity'])
            guard = json.loads((a.runs / (current + '.guard.json')).read_text())
            assert timing_resource_valid(guard), 'Entire timing run invalidated by pressure/pause/monitor event; raw retained; no retry'
            record = dict(**item, artifact=artifact, metadata_sha256=sha(a.runs / (current + '.json')),
                          analysis=analyze(a.runs / (current + '.json')), timing_resource_valid=True)
            records.append(record); completed.append(current)
            atomic_json(a.runs / 'p3-completed-evidence.json', records)
            subprocess.run([str(a.source / '.venv/bin/python'), str(here / 'analyze_display_preparation.py'),
                            '--runs', str(a.runs), '--output', str(a.runs / 'p3-analysis.json')], check=True)
            status('P3 timing job archived', completed_jobs=len(completed))
        analysis = json.loads((a.runs / 'p3-analysis.json').read_text())
        assert len(analysis['results']) == 24
        stage = 'P3 complete; formal gates evaluated; confirmation/window pending'
        value = status(stage, records=records, analysis=analysis, performance_gate_passed=analysis['gates'],
                       next='No confirmation, live window or default adoption launched by this tool')
        publish(lab, exp, a.runs, value, True)
        atomic_json(a.runs / 'p3-finalization.json', dict(status=stage, evidence='results/p3-complete.json', raw_archived=True))
    except BaseException as error:
        if current and list(a.runs.glob(current + '.*')):
            target = exp / 'artifacts' / ('display-preparation-p3-20261007-' + current + '-raw.zip')
            if not target.exists(): attempt_artifact = archive_run(exp, a.runs, current)
        value = status('P3 stopped or timing invalid; no automatic retry', error=repr(error), records=records,
                       last_attempt_artifact=attempt_artifact)
        publish(lab, exp, a.runs, value, False)
        raise


if __name__ == '__main__':
    main()
