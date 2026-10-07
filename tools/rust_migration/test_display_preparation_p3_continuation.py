"""Synthetic continuation scope tests; no STAR replay or performance claim."""
import argparse
import hashlib
import json
from pathlib import Path
from continue_display_preparation_p3 import aggregate, job_specs


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    root = p.parse_args().output; root.mkdir(exist_ok=False)
    records = [dict(**s, timing_resource_valid=True, analysis=dict(passed=True)) for s in job_specs()]
    assert len(records) == 24 and len({r['name'] for r in records}) == 24
    assert all(g['complete'] and g['passed'] for g in aggregate(records).values())
    records[10].update(timing_resource_valid=False, analysis=None)
    groups = aggregate(records)
    assert groups['reuse_typed/native1/static'] == dict(executed=3, valid=2, complete=False,
        passed=False, status='incomplete due to missing or resource-invalid runs')
    assert sum(g['complete'] for g in groups.values()) == 7
    assert sum(g['valid'] for g in groups.values()) == 23
    records[0]['analysis']['passed'] = False
    assert aggregate(records)['baseline/native1/static']['complete']
    assert not aggregate(records)['baseline/native1/static']['passed']
    assert len(job_specs()[11:]) == 13
    assert not {r['name'] for r in records[:11]} & {r['name'] for r in records[11:]}
    result = dict(passed=True, kind=__doc__, original_jobs=24, pending_jobs=13,
        no_completed_or_invalid_job_rerun=True, invalid_timing_retained_and_excluded=True,
        incomplete_stratum_not_promoted=True, real_negative_gate_not_relaxed=True,
        synthetic_all_other_strata_complete=True,
        tool_sha256=hashlib.sha256(Path(__file__).with_name('continue_display_preparation_p3.py').read_bytes()).hexdigest(),
        control_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (root / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
