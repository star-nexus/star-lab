"""E5 fixed-input replay: Movement/Visuals overlap with paired ABBA/BAAB.

Compare mode evaluates complete decoded responses/deltas in two candidate worlds.
Plain mode supplies the independent frozen-binary stream comparator. Neither mode
is a live capacity or profiler-overhead benchmark. Input hashes are mandatory.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def summary(values):
    ordered = sorted(values)
    return dict(samples=len(values), mean_ns=sum(values)/len(values),
                p99_ns=ordered[min(len(values)-1, int(len(values)*.99))], max_ns=max(values))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--trace', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--trace-sha256', required=True)
    p.add_argument('--source-sha', required=True)
    p.add_argument('--extension-sha256', required=True)
    p.add_argument('--native-package', type=Path, help='parent containing a preserved star_native package')
    p.add_argument('--kernel-source-sha', help='identity of preserved binary if different from wrapper source')
    p.add_argument('--reference-profile', action='store_true', help='paired baseline diagnostic; not unprofiled performance')
    p.add_argument('--probe-mode', choices=['baseline', 'empty_fork', 'split_serial', 'parallel', 'ordinary'], required=True)
    p.add_argument('--threads', type=int, choices=[1, 2, 4], default=1)
    p.add_argument('--mode', choices=['plain', 'compare'], required=True)
    p.add_argument('--min-damage-rows', type=int, default=8)
    p.add_argument('--paired', action='store_true')
    p.add_argument('--control-mode', default='parallel', choices=['parallel','split_serial','baseline','empty_fork'])
    p.add_argument('--control-min-damage-rows', type=int, default=2**64-1)
    a = p.parse_args()
    source = a.source.resolve()
    os.chdir(source)
    sys.path.insert(0, str(source))
    if a.native_package:
        sys.path.insert(0, str(a.native_package.resolve()))
    from rotk_env.runtime.native import RustRuntime
    from star_native import _native
    actual_source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    assert actual_source == a.source_sha
    assert sha(Path(_native.__file__)) == a.extension_sha256
    assert sha(a.trace) == a.trace_sha256
    trace = json.loads(gzip.decompress(a.trace.read_bytes()))
    initial_path = a.trace.with_name(trace['initial']['file'])
    assert sha(initial_path) == trace['initial']['sha256']
    initial = json.loads(gzip.decompress(initial_path.read_bytes()))
    plain = RustRuntime(initial, threads=a.threads)
    measured = RustRuntime(initial, threads=a.threads) if a.mode == 'compare' else None
    if a.paired:
        assert a.mode == 'plain' and not a.reference_profile
        worlds = [plain] + [RustRuntime(initial, threads=a.threads) for _ in range(3)]
        samples = [[] for _ in worlds]
    else:
        worlds = [plain] + ([measured] if measured else [])
    def advance(runtime, op, mode, threshold, profile=False):
        if mode == 'ordinary':
            runtime.step(op['dt'], wall_time=op['wall_time'])
            return None
        return runtime._native._movement_visuals_step_json(op['dt'], op['wall_time'], mode, threshold, profile)
    stream = hashlib.sha256()
    counts, segments = Counter(), Counter()
    run = 0
    timings = []
    step_samples = []
    started = time.perf_counter()
    try:
        first = plain.take_presentation_delta()
        for other in worlds[1:]:
            assert first == other.take_presentation_delta()
        for index, op in enumerate(trace['entries']):
            assert index == op['seq']
            kind = op['kind']
            counts[kind] += 1
            is_query = kind == 'request' and op['action'] == 'get_faction_state'
            if is_query:
                run += 1
            elif run:
                segments[run] += 1
                run = 0
            if kind == 'step':
                if a.paired:
                    # A1,B1,B2,A2; reverse on alternate ticks. Four persistent worlds,
                    # no world copy and no overlapping steps/pools across instances.
                    order = [0,1,2,3] if len(samples[0]) % 2 == 0 else [1,0,3,2]
                    for wi in order:
                        control = wi in (0,3)
                        started_step = time.perf_counter_ns()
                        advance(worlds[wi], op, a.control_mode if control else a.probe_mode,
                                a.control_min_damage_rows if control else a.min_damage_rows)
                        samples[wi].append(time.perf_counter_ns()-started_step)
                    step_samples.append((samples[1][-1]+samples[2][-1])/2)
                else:
                    step_start = time.perf_counter_ns()
                    advance(plain, op, a.probe_mode, a.min_damage_rows)
                    step_samples.append(time.perf_counter_ns()-step_start)
                    if measured:
                        timing = json.loads(advance(measured, op, a.probe_mode, a.min_damage_rows, True))
                        timing['seq'] = index
                        timings.append(timing)
                continue
            if kind == 'presentation':
                result = plain.take_presentation_delta()
                for other in worlds[1:]:
                    assert result == other.take_presentation_delta(), ('full delta', index)
                assert digest(result['events']) == op['events_sha256'], ('trace events', index)
            elif kind == 'request':
                if 'integer_string_limit' in op:
                    sys.set_int_max_str_digits(op['integer_string_limit'])
                def request(runtime):
                    if op.get('response_wire_format') == 'native-json':
                        wire = runtime.get_faction_state_json(**op['parameters'], agent_id=op['agent_id'], wall_time=op['wall_time'])
                        return json.loads(wire), hashlib.sha256(wire.encode()).hexdigest()
                    value = runtime.execute_action(op['action'], op['parameters'], agent_id=op['agent_id'], wall_time=op['wall_time'], registration_time=op['registration_time'])
                    wire_sha = hashlib.sha256(json.dumps(value, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
                    return value, wire_sha
                result, wire_sha = request(plain)
                for other_world in worlds[1:]:
                    other, _ = request(other_world)
                    assert result == other, ('full response', index)
                expected = op.get('response_wire_sha256', op.get('response_sha256'))
                actual = wire_sha if 'response_wire_sha256' in op else digest(result)
                assert actual == expected, ('trace response', index)
            else:
                raise ValueError(kind)
            stream.update(bytes.fromhex(digest(result)))
        if run:
            segments[run] += 1
        final = plain.export_state()
        for other in worlds[1:]:
            assert final == other.export_state(), 'full final state'
        assert digest(final) == trace['final_state_sha256']
    finally:
        for runtime in worlds:
            runtime.close()
    phase_values = {}
    statistics_values = {}
    candidate_values = {}
    for row in timings:
        for name, value in row['phases_ns'].items():
            phase_values.setdefault(name, []).append(value)
        for name, value in row.get('statistics', {}).items():
            statistics_values.setdefault(name, []).append(value)
        for system, fields in row.get('candidates', {}).items():
            for metric, value in fields.items():
                candidate_values.setdefault(system, {}).setdefault(metric, []).append(value)
    def candidate_summary(values, metric):
        ordered = sorted(values)
        return dict(unit='ns' if metric.endswith('_ns') else 'count', samples=len(values),
                    total=sum(values), mean=sum(values)/len(values),
                    p99=ordered[min(len(values)-1, int(len(values)*.99))], max=max(values),
                    nonzero_samples=sum(value != 0 for value in values))
    result = dict(source_sha=actual_source, tool_sha256=sha(Path(__file__)),
                  argv=sys.argv, environment={key: os.environ.get(key) for key in ('HEADLESS', 'SDL_VIDEODRIVER', 'PYGAME_HIDE_SUPPORT_PROMPT')},
                  tooling_commit=subprocess.check_output(['git', '-C', str(Path(__file__).resolve().parents[2]), 'rev-parse', 'HEAD'], text=True).strip(),
                  extension_sha256=a.extension_sha256, trace_sha256=a.trace_sha256,
                  initial_sha256=sha(initial_path), original_source=trace['source'],
                  mode=a.mode, threads=a.threads, counts=dict(counts),
                  kernel_source_sha=a.kernel_source_sha or actual_source,
                  probe_mode=a.probe_mode, min_damage_rows=a.min_damage_rows, paired=a.paired,
                  control_mode=a.control_mode, control_min_damage_rows=a.control_min_damage_rows,
                  read_segment_histogram=dict(sorted(segments.items())),
                  observations_in_shareable_segments=sum(n*c for n, c in segments.items() if n > 1),
                  stream_sha256=stream.hexdigest(), final_state_sha256=digest(final),
                  phase_summary={name: summary(values) for name, values in phase_values.items()},
                  statistics_summary={name: summary(values) for name, values in statistics_values.items()},
                  candidate_summary={system: {metric: candidate_summary(values, metric)
                                      for metric, values in fields.items()}
                                      for system, fields in candidate_values.items()},
                  ordinary_step_summary=summary(step_samples),
                  elapsed_seconds=time.perf_counter()-started, all_passed=True,
                  scope='fixed recorded input incl warmup and tails; paired mode alternates ABBA/BAAB within each tick; compare mode diagnostic only; no capacity claim')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2)+'\n')
    step_raw = a.output.with_suffix('.steps.json.gz')
    step_raw.write_bytes(gzip.compress(json.dumps(step_samples, separators=(',', ':')).encode(), mtime=0))
    result['step_raw'] = dict(file=step_raw.name, sha256=sha(step_raw), bytes=step_raw.stat().st_size)
    if a.paired:
        paired = a.output.with_suffix('.paired.json.gz')
        paired.write_bytes(gzip.compress(json.dumps(samples,separators=(',',':')).encode(),mtime=0))
        result['paired_raw'] = dict(file=paired.name,sha256=sha(paired),bytes=paired.stat().st_size)
    if timings:
        raw = a.output.with_suffix('.timings.json.gz')
        raw.write_bytes(gzip.compress(json.dumps(timings, separators=(',', ':')).encode(), mtime=0))
        result['timing_raw'] = dict(file=raw.name, sha256=sha(raw), bytes=raw.stat().st_size)
    a.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
