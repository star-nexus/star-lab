"""Wait for E7 P3, then run conditional native4 single-instance confirmation."""
import argparse
import json
import subprocess
import time
from pathlib import Path

from analyze_display_preparation import analyze


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--source-sha', required=True)
    p.add_argument('--trace', type=Path, required=True)
    p.add_argument('--runs', type=Path, required=True)
    a = p.parse_args()
    here = Path(__file__).parent
    python = a.source / '.venv/bin/python'
    progress = a.runs / 'confirmation-progress.json'
    completed = []

    def status(stage, **extra):
        value = dict(stage=stage, completed=completed, updated_unix=time.time(),
                     source_sha=a.source_sha, capacity_claim=False, **extra)
        progress.write_text(json.dumps(value, indent=2) + '\n')
        print(json.dumps(value), flush=True)

    try:
        assert not progress.exists(), 'Refuse duplicate supervisor'
        status('waiting for full P2 and exclusive P3 completion')
        while True:
            upstream = json.loads((a.runs / 'resume-progress.json').read_text())
            assert upstream['source_sha'] == a.source_sha
            if upstream['stage'] == 'stopped or failed':
                raise RuntimeError('Upstream stopped: ' + str(upstream.get('error')))
            if upstream['stage'] == 'P3 complete; conditional confirmation/window decision required':
                break
            time.sleep(30)
        # Recompute every preregistered run; never select a favorable subset.
        results = []
        for consumer in ('baseline', 'reuse_typed'):
            for threads in (1, 4):
                for script in ('static', 'exercise'):
                    for round_id in (1, 2, 3):
                        path = a.runs / f'p3-{consumer}-t{threads}-{script}-r{round_id}.json'
                        meta = json.loads(path.read_text())
                        assert meta['source_sha'] == a.source_sha
                        assert meta['overscan_clock'] == 'wall' and meta['driver'] == 'dummy'
                        results.append(analyze(path))
        qualifies = all(r['passed'] for r in results
                        if r['consumer'] == 'baseline' and r['threads'] == 4)
        if not qualifies:
            status('stopped at P3 gate; confirmation and live not entered')
            return
        for script in ('static', 'exercise'):
            for i, mode in enumerate(('baseline', 'empty_territory', 'empty_territory', 'baseline'), 1):
                name = f'p4-confirm-{script}-{i}-{mode}'
                output = a.runs / (name + '.json')
                assert not output.exists(), 'Refuse repeated/selected confirmation'
                status('single-instance ABBA confirmation', current=name)
                command = [str(python), str(here / 'guard_display_preparation.py'),
                           '--report', str(a.runs / (name + '.guard.json')), '--no-vmmap', '--',
                           str(python), str(here / 'display_preparation_performance.py'),
                           '--source', str(a.source), '--source-sha', a.source_sha,
                           '--trace', str(a.trace), '--output', str(output),
                           '--task', 'single', '--candidate', mode, '--threads', '4',
                           '--consumer', 'baseline', '--script', script, '--overscan-clock', 'wall']
                with (a.runs / (name + '.supervisor.log')).open('w') as log:
                    subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
                completed.append(name)
        output = a.runs / 'p4-confirmation-analysis.json'
        subprocess.run([str(python), str(here / 'analyze_display_preparation_confirmation.py'),
                        '--runs', str(a.runs), '--output', str(output)], check=True)
        passed = json.loads(output.read_text())['passed']
        status('confirmation passed; three live pairs and final archive pending' if passed
               else 'stopped at confirmation gate; live not entered')
    except BaseException as error:
        status('stopped or failed', error=repr(error))
        raise


if __name__ == '__main__':
    main()
