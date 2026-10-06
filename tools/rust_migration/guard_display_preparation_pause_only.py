"""E7 correctness supervisor: pause on pressure, never auto-kill the child.

Budget is telemetry only. SIGSTOP preserves live state; no durable checkpoint.
This policy is authorized for this correctness attempt, not performance runs.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import time

from guard_display_preparation_resumable import atomic_json, pressure, last_tick, system_snapshot

POLICY = 'pressure pause only; memory budget telemetry; no automatic termination'


class PauseOnlyPolicy:
    def __init__(self, seconds):
        self.seconds = seconds
        self.warnings = 0
        self.normal_since = None

    def action(self, level, paused, now):
        self.warnings = self.warnings + 1 if level == 2 else 0
        if level != 1:
            self.normal_since = None
            if not paused and (level != 2 or self.warnings >= 2):
                return 'pause'
        elif paused:
            if self.normal_since is None:
                self.normal_since = now
            elif now - self.normal_since >= self.seconds:
                self.normal_since = None
                return 'resume'
        return None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--limit-mib', type=float, default=6144, help='Telemetry reference; does not stop child')
    p.add_argument('--poll-seconds', type=float, default=5)
    p.add_argument('--resume-normal-seconds', type=float, default=60)
    p.add_argument('--no-vmmap', action='store_true')
    p.add_argument('command', nargs=argparse.REMAINDER)
    a = p.parse_args()
    assert all(math.isfinite(x) and x > 0 for x in (a.limit_mib, a.poll_seconds, a.resume_normal_seconds))
    command = a.command[1:] if a.command[:1] == ['--'] else a.command
    assert command and not a.report.exists()
    a.report.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    paused = False
    paused_at = None
    pause_duration = 0
    samples, events = [], []
    policy = PauseOnlyPolicy(a.resume_normal_seconds)
    log = a.report.with_suffix('.child.log')
    last_footprint = -30
    tool_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

    with log.open('w') as output:
        child = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)

        def save(status, **extra):
            elapsed = time.monotonic() - started
            atomic_json(a.report, dict(status=status, command=command, child_pid=child.pid,
                limit_mib=a.limit_mib, budget_enforced=False, automatic_termination=False,
                policy=POLICY, tool_sha256=tool_sha, paused=paused,
                resume_normal_seconds=a.resume_normal_seconds, elapsed_s=elapsed,
                paused_seconds=pause_duration + (elapsed - paused_at if paused_at is not None else 0),
                last_logged_tick=last_tick(log), samples=samples, events=events, **extra))

        def pause(reason, level):
            nonlocal paused, paused_at
            if not paused and child.poll() is None:
                try:
                    os.killpg(child.pid, signal.SIGSTOP)
                except ProcessLookupError:
                    return
                paused = True
                paused_at = time.monotonic() - started
                events.append(dict(event='pause', elapsed_s=paused_at, pressure=level,
                    reason=reason, last_logged_tick=last_tick(log), system=system_snapshot()))

        try:
            save('running')
            while child.poll() is None:
                now = time.monotonic() - started
                try:
                    rss_out = subprocess.run(['ps', '-p', str(child.pid), '-o', 'rss='],
                        capture_output=True, text=True, timeout=10)
                    if child.poll() is not None:
                        break
                    assert rss_out.returncode == 0 and rss_out.stdout.strip(), 'RSS query unavailable'
                    rss = int(rss_out.stdout.strip()) * 1024
                    level = pressure()
                    row = dict(elapsed_s=now, rss_bytes=rss, pressure=level, paused=paused)
                    if not a.no_vmmap and not paused and now - last_footprint >= 30:
                        try:
                            vm = subprocess.run(['vmmap', '-summary', str(child.pid)],
                                capture_output=True, text=True, timeout=10)
                            match = re.search(r'^Physical footprint:\s*([\d.]+)([BKMG])', vm.stdout, re.M)
                            if match:
                                row['footprint_bytes'] = int(float(match[1]) * {'B':1,'K':1024,'M':1024**2,'G':1024**3}[match[2]])
                            else:
                                row['footprint_unavailable'] = True
                        except (OSError, subprocess.TimeoutExpired) as error:
                            row['footprint_error'] = repr(error)
                        last_footprint = now
                    row['above_reference_budget'] = max(rss, row.get('footprint_bytes', 0)) > a.limit_mib * 1024**2
                    samples.append(row)
                    action = policy.action(level, paused, now)
                    if action == 'pause':
                        pause('system memory pressure', level)
                    elif action == 'resume':
                        os.killpg(child.pid, signal.SIGCONT)
                        resumed = time.monotonic() - started
                        pause_duration += resumed - paused_at
                        paused_at = None
                        paused = False
                        events.append(dict(event='resume', elapsed_s=resumed, pressure=level,
                            last_logged_tick=last_tick(log)))
                except Exception as error:
                    # Failed monitoring must not discard hours of live correctness state.
                    policy.normal_since = None
                    pause('monitor query failed: ' + repr(error), None)
                    events.append(dict(event='monitor_error', elapsed_s=now, error=repr(error)))
                save('paused' if paused else 'running')
                time.sleep(a.poll_seconds)
        except BaseException as error:
            # Even a supervisor interruption leaves the child alive, paused for recovery.
            pause('supervisor interrupted: ' + repr(error), None)
            try:
                save('supervisor_interrupted_child_preserved', error=repr(error))
            finally:
                raise
        save('passed' if child.returncode == 0 else 'stopped_or_failed',
             child_exit=child.returncode, stop_reason=None if child.returncode == 0 else 'child exited unsuccessfully')
    raise SystemExit(0 if child.returncode == 0 else 1)


if __name__ == '__main__':
    main()
