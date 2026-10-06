"""Run remaining guarded P2 jobs, then automatically verify and archive P2."""
import argparse
import json
import subprocess
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--source-sha', required=True)
    p.add_argument('--trace', type=Path, required=True)
    p.add_argument('--previous-runs', type=Path, required=True)
    p.add_argument('--runs', type=Path, required=True)
    p.add_argument('--limit-mib', type=float, default=2500)
    p.add_argument('--run-date', default='2026-10-05')
    a = p.parse_args()
    here = Path(__file__).parent
    python = a.source / '.venv/bin/python'
    args = ['--source', str(a.source), '--source-sha', a.source_sha,
            '--trace', str(a.trace), '--previous-runs', str(a.previous_runs), '--runs', str(a.runs),
            '--limit-mib', str(a.limit_mib)]
    try:
        subprocess.run([str(python), str(here / 'resume_remaining_display_correctness.py'), *args], check=True)
        subprocess.run([str(python), str(here / 'finalize_display_correctness.py'), '--runs', str(a.runs),
                        '--remaining-limit-mib', str(a.limit_mib), '--run-date', a.run_date], check=True)
    except BaseException as error:
        if a.runs.exists():
            (a.runs / 'p2-finalization.json').write_text(json.dumps(dict(status='stopped or failed',
                                            error=repr(error), P2_complete=False), indent=2) + '\n')
        raise


if __name__ == '__main__':
    main()
