"""E8 telemetry-only supervisor. Never pauses, kills, or times out a workload.

User authorization: 2026-10-07 continue despite memory pressure warnings.
Pressure is evidence about timing validity, not an automatic control signal.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
from guard_display_preparation_resumable import atomic_json, pressure


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--adopt-pid', type=int)
    p.add_argument('--previous-report', type=Path)
    p.add_argument('--poll-seconds', type=float, default=5)
    p.add_argument('command', nargs=argparse.REMAINDER)
    a = p.parse_args()
    assert not a.report.exists() and a.poll_seconds > 0
    cmd = a.command[1:] if a.command[:1] == ['--'] else a.command
    assert bool(a.adopt_pid) != bool(cmd)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    previous = json.loads(a.previous_report.read_text()) if a.previous_report else None
    samples, events = [], []
    began = time.monotonic()
    output = None
    child = None
    if cmd:
        output = a.report.with_suffix('.child.log').open('w')
        child = subprocess.Popen(cmd,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
    pid = child.pid if child else a.adopt_pid

    def save(status):
        atomic_json(a.report,dict(status=status,child_pid=pid,command=cmd,
            policy='telemetry only; no automatic pause/kill/timeout',
            authorization='2026-10-07 user: warning despite free memory; 尽管测',
            budget_enforced=False,automatic_termination=False,automatic_pause=False,
            reference_mib=6144,elapsed_s=time.monotonic()-began,
            source_tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            previous_policy_evidence=previous,samples=samples,events=events,
            child_exit=child.returncode if child else None,
            adopted_exit_status='unknown; verify workload completion evidence' if not child else None))
    save('running')
    try:
        while True:
            if child and child.poll() is not None:
                break
            row = dict(elapsed_s=time.monotonic()-began)
            proc = subprocess.run(['ps','-p',str(pid),'-o','stat=,rss='],capture_output=True,text=True,timeout=10)
            if not proc.stdout.strip():
                break
            status, rss = proc.stdout.split()[:2]
            if status.startswith('Z'):
                break
            row.update(process_status=status,rss_bytes=int(rss)*1024)
            try:
                row['pressure'] = pressure()
            except Exception as e:
                row['pressure'] = None
                events.append(dict(event='monitor_error',error=repr(e),elapsed_s=row['elapsed_s']))
            if row['pressure'] != 1:
                events.append(dict(event='non_normal_pressure',pressure=row['pressure'],elapsed_s=row['elapsed_s']))
            samples.append(row)
            save('running')
            time.sleep(a.poll_seconds)
        if child:
            child.wait()
        save('passed' if child and child.returncode == 0 else 'child_failed' if child else 'adopted_process_exited')
    finally:
        if output:
            output.close()
    if child and child.returncode:
        raise SystemExit(child.returncode)


if __name__ == '__main__':
    main()
