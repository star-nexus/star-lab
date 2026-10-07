"""Continue untouched P3 jobs after resource interruption; never retry/select.

The user authorizes subsequent jobs despite an invalid timing attempt. Every
attempt remains archived; only resource-valid runs enter unchanged speed gates.
"""
import argparse
import json
from pathlib import Path
import subprocess
import time

from run_display_preparation_p3 import (SOURCE, job_specs, sha, verify_performance,
    timing_resource_valid, archive_run, refresh_checksums, atomic_json, pressure,
    analyze, publish)


def aggregate(records):
    groups = {}
    for consumer in ('baseline', 'reuse_typed'):
        for threads in (1, 4):
            for script in ('static', 'exercise'):
                group = [r for r in records if (r['consumer'], r['threads'], r['script']) == (consumer, threads, script)]
                valid = [r for r in group if r['timing_resource_valid']]
                complete = len(group) == 3 and len(valid) == 3
                groups[f'{consumer}/native{threads}/{script}'] = dict(
                    executed=len(group), valid=len(valid), complete=complete,
                    passed=complete and all(r['analysis']['passed'] for r in valid),
                    status='evaluated' if complete else 'incomplete due to missing or resource-invalid runs')
    return groups


def parent_alive(pid):
    r = subprocess.run(['ps', '-p', str(pid), '-o', 'command='], capture_output=True, text=True)
    return r.returncode == 0 and 'run_display_preparation_p3.py' in r.stdout


def existing_artifact(exp, runs, name):
    from zipfile import ZipFile
    import hashlib
    path = exp / 'artifacts' / ('display-preparation-p3-20261007-' + name + '-raw.zip')
    assert path.exists()
    with ZipFile(path) as z:
        for line in z.read('SHA256SUMS').decode().splitlines():
            digest, member = line.split('  ', 1)
            assert hashlib.sha256(z.read(member)).hexdigest() == digest
        for file in sorted(p for p in runs.glob(name + '.*') if p.is_file()):
            assert hashlib.sha256(z.read('raw/' + file.name)).hexdigest() == sha(file)
    return dict(file=path.name, sha256=sha(path), bytes=path.stat().st_size)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--trace', type=Path, required=True)
    p.add_argument('--runs', type=Path, required=True)
    p.add_argument('--previous-parent', type=int, required=True)
    a = p.parse_args(); here = Path(__file__).resolve().parent
    lab = here.parents[1]; exp = lab / 'experiments/2026-10-rust-display-preparation'
    progress = a.runs / 'p3-continuation-progress.json'
    assert not progress.exists(), 'Refuse duplicate continuation'
    amendment = json.loads((exp / 'results/p3-continuation-20261007.json').read_text())
    records = []; current = None

    def status(stage, **extra):
        value = dict(stage=stage, completed=[r['name'] for r in records if r['timing_resource_valid']],
            executed=[r['name'] for r in records], invalid=[r['name'] for r in records if not r['timing_resource_valid']],
            total=24, current=current, source_sha=SOURCE, updated_unix=time.time(),
            production_enabled=False, capacity_claim=False, **extra)
        atomic_json(progress, value); print(json.dumps(value), flush=True)
        return value

    try:
        for name, digest in amendment['tool_sha256'].items(): assert sha(here / name) == digest
        while parent_alive(a.previous_parent):
            status('waiting for prior timing run and supervisor to finish; no competing child')
            time.sleep(15)
        upstream = json.loads((a.runs / 'p3-progress.json').read_text())
        assert upstream['stage'] == 'P3 stopped or timing invalid; no automatic retry'
        assert 'Entire timing run invalidated by pressure/pause/monitor event' in upstream['error'], upstream
        assert subprocess.check_output(['git', '-C', str(a.source), 'rev-parse', 'HEAD'], text=True).strip() == SOURCE
        assert not subprocess.check_output(['git', '-C', str(a.source), 'status', '--porcelain', '--untracked-files=no'], text=True).strip()
        full = json.loads((exp / 'results/p2-complete.json').read_text())
        assert full['passed'] and full['completed_jobs'] == 4 and sha(a.trace) == full['identity']['trace_sha256']
        specs = job_specs()
        assert upstream['completed'] == [s['name'] for s in specs[:10]]
        assert upstream['current'] == specs[10]['name']
        # Validate and retain every completed attempt, including the interrupted timing.
        for spec in specs[:11]:
            verify_performance(a.runs, spec, full['identity'])
            guard = json.loads((a.runs / (spec['name'] + '.guard.json')).read_text())
            assert guard['status'] == 'passed' and guard['child_exit'] == 0
            valid = timing_resource_valid(guard)
            assert valid == (spec['name'] in upstream['completed'])
            records.append(dict(**spec, artifact=existing_artifact(exp, a.runs, spec['name']),
                metadata_sha256=sha(a.runs / (spec['name'] + '.json')), timing_resource_valid=valid,
                analysis=analyze(a.runs / (spec['name'] + '.json')) if valid else None,
                rerun=False, inherited=True))
        for spec in specs[11:]:
            current = spec['name']; assert not list(a.runs.glob(current + '.*')), 'Do not repeat/select any started job'
            normal = 0
            while normal < 3:
                level = pressure(); normal = normal + 1 if level == 1 else 0
                status('waiting for normal pressure before next timing', pressure=level, normal_samples=normal)
                if normal < 3: time.sleep(30)
            status('P3 remaining serial full paired timing')
            cmd = [str(a.source / '.venv/bin/python'), str(here / 'display_preparation_performance.py'),
                '--source', str(a.source), '--source-sha', SOURCE, '--trace', str(a.trace),
                '--output', str(a.runs / (current + '.json')), '--task', 'paired', '--candidate', 'empty_territory',
                '--threads', str(spec['threads']), '--consumer', spec['consumer'], '--script', spec['script'], '--overscan-clock', 'wall']
            guarded = [str(a.source / '.venv/bin/python'), str(here / 'guard_display_preparation_pause_only.py'),
                '--report', str(a.runs / (current + '.guard.json')), '--no-vmmap', '--limit-mib', '6144', '--', *cmd]
            with (a.runs / (current + '.supervisor.log')).open('w') as log:
                result = subprocess.run(guarded, stdout=log, stderr=subprocess.STDOUT)
            artifact = archive_run(exp, a.runs, current)
            assert result.returncode == 0, 'Real child/monitor failure; preserve and stop, no retry'
            verify_performance(a.runs, spec, full['identity'])
            guard = json.loads((a.runs / (current + '.guard.json')).read_text())
            valid = timing_resource_valid(guard)
            records.append(dict(**spec, artifact=artifact, metadata_sha256=sha(a.runs / (current + '.json')),
                timing_resource_valid=valid, analysis=analyze(a.runs / (current + '.json')) if valid else None,
                rerun=False, inherited=False))
            # This explicit list never feeds a resource-invalid result to the speed analyzer.
            atomic_json(a.runs / 'p3-continuation-completed-evidence.json', records)
            atomic_json(a.runs / 'p3-continuation-analysis.json', dict(groups=aggregate(records),
                resource_invalid=[r['name'] for r in records if not r['timing_resource_valid']],
                valid_results=[r['analysis'] for r in records if r['timing_resource_valid']]))
            status('P3 remaining job archived; proceeding regardless of resource-invalid attempts')
        current = None
        assert [r['name'] for r in records] == [s['name'] for s in specs]
        value = status('P3 original 24 jobs executed; resource-invalid strata remain inconclusive',
            records=records, analysis=aggregate(records), all_original_jobs_executed=True,
            all_formal_strata_complete=all(g['complete'] for g in aggregate(records).values()),
            next='No automatic retries, confirmation, windows or default adoption')
        publish(lab, exp, a.runs, value, True)
        atomic_json(a.runs / 'p3-finalization.json', dict(status=value['stage'], evidence='results/p3-complete.json',
            original_jobs_executed=24, valid_jobs=len(value['completed']), invalid_jobs=len(value['invalid'])))
    except BaseException as error:
        value = status('P3 continuation failed; preserve evidence and child state, no automatic retry',
                       error=repr(error), records=records)
        # Do not race with the old supervisor's archive while it remains alive.
        if not parent_alive(a.previous_parent): publish(lab, exp, a.runs, value, False)
        raise


if __name__ == '__main__':
    main()
