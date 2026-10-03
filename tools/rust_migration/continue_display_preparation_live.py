"""Continue qualified E7 confirmation into six guarded real Cocoa windows."""
import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

EXTENSION = '838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544'


def validate_live(meta, source_sha, mode):
    assert meta['source']['sha'] == source_sha and not meta['source']['dirty']
    assert meta['extension']['sha256'] == EXTENSION and meta['extension']['api'] == 18
    assert meta['display_driver'] == 'cocoa' and meta['surface_size'] == [2480, 1239]
    w = meta['workload']
    expected = dict(backend='rust', native_wire=True, native_threads=4, fps=30,
                    clock_mode='fixed', cycle_mode='post-action', jitter_seconds=5.0,
                    units=5000, agents=1000, delay='30', observation_mode='single',
                    scope='selected', layout='canonical', policy='stochastic',
                    seconds=300.0, warmup=30.0, budget_ms=8.0, gc_policy='realtime_defer',
                    display_research_mode=mode, presentation_research_mode='baseline',
                    display_research_profile=False, presentation_research_profile=False,
                    attribute=False, no_agents=False, no_encode=False)
    assert all(w[k] == v for k, v in expected.items())
    # Keep valid workload failures as negative evidence; never discard/retry them.
    assert meta['guards']['complete'] and meta['guards']['not_diagnostic']
    assert meta['pass'] == all(meta['guards'].values())
    return meta['pass']


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--source-sha', required=True)
    p.add_argument('--runs', type=Path, required=True)
    a = p.parse_args()
    here = Path(__file__).parent
    python = a.source / '.venv/bin/python'
    runtime = here.parent / 'display_preparation_runtime.py'
    progress = a.runs / 'live-progress.json'
    completed = []

    def status(stage, **extra):
        value = dict(stage=stage, completed=completed, updated_unix=time.time(),
                     source_sha=a.source_sha, capacity_claim=False, **extra)
        progress.write_text(json.dumps(value, indent=2) + '\n')
        print(json.dumps(value), flush=True)

    try:
        assert not progress.exists(), 'Refuse duplicate live supervisor'
        status('waiting for full confirmation gate')
        while True:
            upstream = json.loads((a.runs / 'confirmation-progress.json').read_text())
            assert upstream['source_sha'] == a.source_sha
            if upstream['stage'].startswith('stopped'):
                status('not entered; upstream gate stopped', upstream=upstream)
                return
            if upstream['stage'] == 'confirmation passed; three live pairs and final archive pending':
                break
            time.sleep(30)
        confirmation = json.loads((a.runs / 'p4-confirmation-analysis.json').read_text())
        assert confirmation['passed'] and all(r['passed'] for r in confirmation['results'].values())
        result_rows = []
        for round_id, modes in enumerate((('baseline', 'empty_territory'),
                                         ('empty_territory', 'baseline'),
                                         ('baseline', 'empty_territory')), 1):
            for mode in modes:
                name = f'p4-live-r{round_id}-{mode}'
                output = a.runs / (name + '.json')
                assert not output.exists(), 'Refuse repeated/selected live result'
                assert subprocess.check_output(['git', '-C', str(a.source), 'rev-parse', 'HEAD'], text=True).strip() == a.source_sha
                status('three live pairs AB/BA/AB', current=name)
                command = [str(python), str(here / 'guard_display_preparation.py'),
                           '--report', str(a.runs / (name + '.guard.json')), '--no-vmmap', '--',
                           str(python), str(runtime), '--source', str(a.source),
                           '--backend', 'rust', '--native-wire', '--native-threads', '4',
                           '--fps', '30', '--clock-mode', 'fixed', '--cycle-mode', 'post-action',
                           '--jitter-seconds', '5', '--units', '5000', '--agents', '1000',
                           '--delay', '30', '--scope', 'selected', '--layout', 'canonical',
                           '--policy', 'stochastic', '--seconds', '300', '--warmup', '30',
                           '--budget-ms', '8', '--gc-policy', 'realtime_defer',
                           '--display-research-mode', mode, '--output', str(output)]
                (a.runs / (name + '.command.json')).write_text(json.dumps(command, indent=2) + '\n')
                env = dict(os.environ, HEADLESS='0', SDL_VIDEODRIVER='cocoa', STAR_SCALE_MINIMAP_UNITS='off')
                with (a.runs / (name + '.supervisor.log')).open('w') as log:
                    subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
                meta = json.loads(output.read_text())
                passed = validate_live(meta, a.source_sha, mode)
                raw = output.with_suffix('.raw.json')
                result_rows.append(dict(run=name, passed=passed, guards=meta['guards'],
                                        frame_work_ms=meta['frame_work_ms'], world_hz=meta['world_hz'],
                                        metadata_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                                        raw_file=raw.name, raw_bytes=raw.stat().st_size,
                                        raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest()))
                completed.append(name)
        result = dict(source_sha=a.source_sha, passed=all(r['passed'] for r in result_rows),
                      runs=result_rows, capacity_claim=False,
                      interpretation='Operational guards on all six; live trajectories are not paired causal evidence',
                      tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        (a.runs / 'p4-live-analysis.json').write_text(json.dumps(result, indent=2) + '\n')
        status('live passed; authorized default integration and final archive pending' if result['passed']
               else 'live gate failed; default integration not permitted; negative archive pending')
    except BaseException as error:
        status('stopped or failed', error=repr(error))
        raise


if __name__ == '__main__':
    main()
