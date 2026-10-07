"""Synthetic P3 ordering/resource/gate controls; no STAR run or speed claim."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
from run_display_preparation_p3 import job_specs, timing_resource_valid
from guard_display_preparation_pause_only import POLICY
from analyze_display_preparation import analyze


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    root = p.parse_args().output; root.mkdir(exist_ok=False)
    jobs = job_specs(); assert len(jobs) == 24 and len({j['name'] for j in jobs}) == 24
    for consumer in ('baseline', 'reuse_typed'):
        for threads in (1, 4):
            for script in ('static', 'exercise'):
                assert sum((j['consumer'], j['threads'], j['script']) == (consumer, threads, script) for j in jobs) == 3
    g = dict(status='passed', child_exit=0, stop_reason=None, policy=POLICY,
             automatic_termination=False, budget_enforced=False, paused_seconds=0,
             paused=False, events=[], samples=[dict(pressure=1, above_reference_budget=True)])
    assert timing_resource_valid(g)
    for mutation in (dict(events=[dict(event='pause')]), dict(paused_seconds=60),
                     dict(samples=[dict(pressure=2)]), dict(status='stopped_or_failed'),
                     dict(samples=[]), dict(automatic_termination=True), dict(budget_enforced=True)):
        assert not timing_resource_valid({**g, **mutation}), mutation
    cases = []
    for name, c in (('positive', 90), ('below-five-percent', 97), ('negative', 110)):
        keys = ('render_ns', 'chain_ns', 'total_ns', 'display_ns', 'submit_ns', 'apply_ns')
        rows = [[{k: (100 if side in (0, 3) else c) for k in keys} for tick in range(9880)] for side in range(4)]
        raw = gzip.compress(json.dumps(rows, separators=(',', ':')).encode(), mtime=0)
        rawp = root / (name + '.samples.json.gz'); rawp.write_bytes(raw)
        m = dict(task='paired', formal=True, all_passed=True, diagnostic=False,
                 consumer='baseline', threads=1, display_script='static',
                 raw=dict(file=rawp.name, sha256=hashlib.sha256(raw).hexdigest()))
        path = root / (name + '.json'); path.write_text(json.dumps(m))
        result = analyze(path); assert result['passed'] == (name == 'positive')
        (root / (name + '.analysis.json')).write_text(json.dumps(result, indent=2) + '\n')
        cases.append(dict(case=name, gate=result['passed']))
    result = dict(passed=True, kind=__doc__, jobs=24, three_rounds_per_stratum=True,
                  cases=cases, pressure_or_pause_rejected=True, budget_telemetry_is_not_enforced=True,
                  runner_sha256=hashlib.sha256(Path(__file__).with_name('run_display_preparation_p3.py').read_bytes()).hexdigest(),
                  control_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (root / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
