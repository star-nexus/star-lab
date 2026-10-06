"""Keep a live E7 correctness process at warning; resume its existing state.

This is an in-memory pause, not a durable World snapshot. Critical pressure,
child budget violations, process exit or reboot still end the attempt.
The historical terminating guard is deliberately unchanged.
"""
import argparse
import json
import math
import os
import re
import signal
import subprocess
import time
from pathlib import Path


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w') as out:
        out.write(json.dumps(value, indent=2) + '\n')
        out.flush()
        os.fsync(out.fileno())
    temporary.replace(path)


def pressure():
    return int(subprocess.check_output(
        ['sysctl', '-n', 'kern.memorystatus_vm_pressure_level'], text=True))


def system_snapshot():
    result = {}
    for key, command in (('vm_stat', ['vm_stat']), ('swap', ['sysctl', 'vm.swapusage']),
                         ('memory_query', ['memory_pressure', '-Q'])):
        try:
            row = subprocess.run(command, capture_output=True, text=True, timeout=10)
            result[key] = dict(exit=row.returncode, stdout=row.stdout, stderr=row.stderr)
        except (OSError, subprocess.TimeoutExpired) as error:
            result[key] = dict(error=repr(error))
    return result


def last_tick(log):
    if not log.exists():
        return None
    with log.open('rb') as file:
        file.seek(max(0, log.stat().st_size - 65536))
        lines = file.read().decode(errors='replace').splitlines()
    for line in reversed(lines):
        if line.startswith('{'):
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value.get('progress'), int):
                return value['progress']
    return None


class PausePolicy:
    def __init__(self, normal_seconds):
        self.normal_seconds = normal_seconds
        self.warnings = 0
        self.normal_since = None

    def action(self, level, paused, now):
        if level >= 4:
            return 'terminate'
        if level not in (1, 2):
            return 'terminate'
        self.warnings = self.warnings + 1 if level != 1 else 0
        if paused:
            if level != 1:
                self.normal_since = None
            elif self.normal_since is None:
                self.normal_since = now
            elif now - self.normal_since >= self.normal_seconds:
                self.normal_since = None
                return 'resume'
        elif self.warnings >= 2:
            self.normal_since = None
            return 'pause'
        return None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--limit-mib', type=float, default=6144)
    p.add_argument('--poll-seconds', type=float, default=5)
    p.add_argument('--resume-normal-seconds', type=float, default=60)
    p.add_argument('--no-vmmap', action='store_true')
    p.add_argument('command', nargs=argparse.REMAINDER)
    a = p.parse_args()
    for value in (a.limit_mib, a.poll_seconds, a.resume_normal_seconds):
        assert math.isfinite(value) and value > 0
    command = a.command[1:] if a.command[:1] == ['--'] else a.command
    assert command and not a.report.exists()
    assert pressure() == 1, 'Memory pressure must be normal before starting'
    a.report.parent.mkdir(parents=True, exist_ok=True)
    samples = []
    events = []
    reason = None
    paused = False
    paused_started = None
    paused_seconds = 0
    started = time.monotonic()
    last_footprint_at = -30
    policy = PausePolicy(a.resume_normal_seconds)
    log = a.report.with_suffix('.child.log')

    def report(status, **extra):
        elapsed = time.monotonic() - started
        current_pause = elapsed - paused_started if paused_started is not None else 0
        atomic_json(a.report, dict(status=status, command=command, child_pid=child.pid,
            limit_mib=a.limit_mib, policy='warning pause; critical/budget terminate',
            resume_normal_seconds=a.resume_normal_seconds, paused=paused,
            elapsed_s=elapsed, paused_seconds=paused_seconds + current_pause,
            last_logged_tick=last_tick(log), samples=samples, events=events, **extra))

    with log.open('w') as output:
        child = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        try:
            while child.poll() is None:
                now = time.monotonic() - started
                rss_result = subprocess.run(['ps', '-p', str(child.pid), '-o', 'rss='],
                                            capture_output=True, text=True)
                if child.poll() is not None:
                    break
                rss = int(rss_result.stdout.strip() or 0) * 1024
                level = pressure()
                row = dict(elapsed_s=round(now, 3), pid=child.pid, rss_bytes=rss,
                           pressure=level, paused=paused)
                # vmmap may require a runnable target; never inspect a SIGSTOP target.
                if not a.no_vmmap and not paused and now - last_footprint_at >= 30:
                    vm = subprocess.run(['vmmap', '-summary', str(child.pid)],
                                        capture_output=True, text=True, timeout=10)
                    match = re.search(r'^Physical footprint:\s*([\d.]+)([BKMG])', vm.stdout, re.M)
                    if match:
                        row['footprint_bytes'] = int(float(match[1]) *
                            {'B': 1, 'K': 1024, 'M': 1024**2, 'G': 1024**3}[match[2]])
                    else:
                        row['footprint_unavailable'] = True
                    last_footprint_at = now
                samples.append(row)
                if max(rss, row.get('footprint_bytes', 0)) > a.limit_mib * 1024**2:
                    reason = 'child memory limit exceeded'
                    break
                action = policy.action(level, paused, now)
                if action == 'terminate':
                    reason = 'critical or unknown system memory pressure'
                    events.append(dict(event='terminate', elapsed_s=now, pressure=level,
                                       system=system_snapshot()))
                    break
                if action == 'pause':
                    os.killpg(child.pid, signal.SIGSTOP)
                    paused = True
                    paused_started = time.monotonic() - started
                    events.append(dict(event='pause', elapsed_s=paused_started,
                                       pressure=level, last_logged_tick=last_tick(log),
                                       system=system_snapshot()))
                    report('paused')
                    print(json.dumps(events[-1]), flush=True)
                elif action == 'resume':
                    os.killpg(child.pid, signal.SIGCONT)
                    resumed_at = time.monotonic() - started
                    paused_seconds += resumed_at - paused_started
                    paused_started = None
                    paused = False
                    events.append(dict(event='resume', elapsed_s=resumed_at,
                                       pressure=level, last_logged_tick=last_tick(log)))
                    print(json.dumps(events[-1]), flush=True)
                report('paused' if paused else 'running')
                time.sleep(a.poll_seconds)
        except BaseException as error:
            reason = 'monitor interrupted or failed: ' + repr(error)
            raise
        finally:
            if child.poll() is None:
                # A stopped process must run again to receive SIGINT and clean up.
                if paused:
                    os.killpg(child.pid, signal.SIGCONT)
                    paused_seconds += time.monotonic() - started - paused_started
                    paused_started = None
                    paused = False
                os.killpg(child.pid, signal.SIGINT)
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
            report('passed' if child.returncode == 0 and reason is None else 'stopped_or_failed',
                   child_exit=child.returncode, stop_reason=reason)
    raise SystemExit(0 if child.returncode == 0 and reason is None else 1)


if __name__ == '__main__':
    main()
