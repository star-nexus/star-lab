"""Diagnostic replay of E8 accepted input; no performance/adoption claim.

Actual scoped metrics establish work reuse. The existing bare handler profiler
is sampled before scope entry and does not represent authenticated service.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import random
import sys
import time


def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--extension-dir', type=Path, required=True)
    p.add_argument('--trace', type=Path, required=True)
    p.add_argument('--admission', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args();assert not a.output.exists();a.output.parent.mkdir(parents=True, exist_ok=True)
    lab = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(lab/'tools'));sys.path.insert(0, str(a.source));sys.path.insert(0, str(a.extension_dir))
    from rotk_env.runtime.native import RustRuntime
    from star_native import _native
    from p3_local_agents import LocalAgents, Session, stats
    trace = json.loads(gzip.decompress(a.trace.read_bytes()))
    initial = json.loads(gzip.decompress(a.trace.with_name(trace['initial']['file']).read_bytes()))
    admitted = json.loads(a.admission.read_text())
    queries = [e for e in trace['entries'] if e.get('action') == 'get_faction_state']
    admissions = [r for r in admitted['admission'] if r['entry'][2] == 'observe']
    assert len(queries) == len(admissions)
    seqs = {}
    for r, e in zip(admissions, queries):
        assert r['params'] == e['parameters'];seqs[r['entry'][1]] = e['seq']
    groups = {}
    for s in admitted['segments']:
        ids = [seqs[n] for n in s['executed']]
        if len(ids) >= 2:
            assert 2 <= len(ids) <= 4 and ids == list(range(ids[0], ids[-1]+1));groups[ids[0]] = ids
    by_seq = {e['seq']: e for e in queries}
    consumer = LocalAgents.__new__(LocalAgents)
    consumer.clock = lambda: 0.;consumer.policy = 'stochastic';consumer.rng = random.Random(42)
    consumer.cycle_mode = 'post-action';consumer.observation_hz = None;consumer.counts = Counter();consumer.heap = [];consumer.serial = 0
    rows = [];profiles = [];sampled = Counter();counts = Counter();context = scope = None;group = None
    response_hash = hashlib.sha256();began = time.perf_counter();failure = None
    with RustRuntime(initial, threads=1) as runtime:
        runtime.take_presentation_delta()
        try:
            for op in trace['entries']:
                seq = op['seq'];kind = op['kind']
                if kind == 'request':
                    if op['action'] == 'get_faction_state':
                        if scope is None:
                            group = groups.get(seq, [seq]);batch = [by_seq[n] for n in group]
                            kind_label = f"{len(group)}-{'same' if len({x['parameters']['faction'] for x in batch}) == 1 else 'mixed'}"
                            if sampled[kind_label] < 5:
                                params = [dict(x['parameters'], agent_id=x['agent_id']) for x in batch]
                                encoded, timing = runtime._native._observation_profile_json(json.dumps(params))
                                profiles.append(dict(first_seq=seq, kind=kind_label, timing=json.loads(timing),
                                    results_sha256=[digest(x) for x in json.loads(encoded)['results']],
                                    scope='Sampled bare read-only handler; inclusive timings, no authorization/accounting'))
                                sampled[kind_label] += 1
                            context = runtime._admitted_observation_segment('segment_encoded', max_requests=max(2, len(group)), diagnostics=True)
                            scope = context.__enter__();counts['contexts'] += 1
                        start = time.perf_counter_ns()
                        wire = scope.get_faction_state_json(**op['parameters'], agent_id=op['agent_id'], wall_time=op['wall_time'])
                        after_native = time.perf_counter_ns();payload = wire.encode();after_bytes = time.perf_counter_ns()
                        decoded = json.loads(payload);after_decode = time.perf_counter_ns()
                        session = Session(op['agent_id'], op['parameters']['faction'], op['parameters'].get('unit_ids') or [], 30.)
                        consumer.heap.clear();consumer._consume_observation(decoded, {}, session, 0, 0.)
                        after_consume = time.perf_counter_ns()
                        assert hashlib.sha256(payload).hexdigest() == op['response_wire_sha256']
                        response_hash.update(payload)
                        rows.append(dict(seq=seq, tick=counts['ticks'], role='singleton' if len(group)==1 else 'segment_first' if seq==group[0] else 'segment_later',
                            phases_ns=dict(native=after_native-start, bytes=after_bytes-after_native, decode=after_decode-after_bytes, consume=after_consume-after_decode),
                            selected_units=len(decoded.get('units', [])), bytes=len(payload), response_sha256=digest(decoded)))
                        counts['queries'] += 1
                        if seq == group[-1]:
                            context.__exit__(None, None, None)
                            for row, diagnostic in zip(rows[-len(group):], context.report['query_diagnostics']):
                                row['diagnostic'] = diagnostic
                                metrics = diagnostic['metrics']
                                row['reuse'] = ('public_and_requested_panels_reused' if metrics['faction_builds']==0 and metrics['panel_builds']==0 and row['selected_units']>0 else
                                               'public_reused_panels_built' if metrics['faction_builds']==0 and metrics['panel_builds']>0 else 'public_built')
                            context = scope = None;group = None
                    else:
                        assert scope is None
                        result = runtime.execute_action(op['action'], op['parameters'], agent_id=op['agent_id'], wall_time=op['wall_time'], registration_time=op['registration_time'])
                        assert digest(result) == op['response_sha256']
                    counts['requests'] += 1
                elif kind == 'step':
                    assert scope is None;runtime.step(op['dt'], wall_time=op['wall_time']);counts['ticks'] += 1
                elif kind == 'presentation':
                    assert scope is None;delta = runtime.take_presentation_delta();assert digest(delta['events']) == op['events_sha256'];counts['presentation'] += 1
                else:raise AssertionError(kind)
                counts['operations'] += 1
            final = digest(runtime.export_state());assert final == trace['final_state_sha256']
            by_row = {r['seq']: r for r in rows}
            for profile in profiles:
                ids = groups.get(profile['first_seq'], [profile['first_seq']])
                assert profile['results_sha256'] == [by_row[n]['response_sha256'] for n in ids]
        except BaseException as error:
            failure = dict(seq=op.get('seq'), error=repr(error));raise
        finally:
            if context:context.__exit__(*sys.exc_info())
            raw = a.output.with_suffix('.raw.json.gz')
            raw.write_bytes(gzip.compress(json.dumps(dict(rows=rows, bare_profiles=profiles), separators=(',', ':')).encode(), mtime=0))
            summary = {}
            for key in ['role', 'reuse']:
                summary[key] = {}
                for value in sorted({r.get(key) for r in rows if key in r}):
                    rs = [r for r in rows if r.get(key) == value]
                    summary[key][value] = dict(count=len(rs), phases_us={phase:stats([r['phases_ns'][phase]/1000 for r in rs]) for phase in ['native','bytes','decode','consume']})
            report = dict(passed=failure is None, failure=failure, diagnostic_only=True, counts=dict(counts), elapsed_s=time.perf_counter()-began,
                extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(), tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.trace,a.admission]}, summary=summary,
                bare_handler_samples=dict(sampled), raw=dict(file=raw.name,sha256=hashlib.sha256(raw.read_bytes()).hexdigest()),
                scope='Singletons use 1-request diagnostic scope; timing includes diagnostic cache/accounting overhead. Fresh Session consumer, fixed recorded accepted input; not live pump.',
                performance_claim=False, default_adoption=False)
            a.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
            print(json.dumps(dict(passed=report['passed'],counts=counts,failure=failure)),flush=True)


if __name__ == '__main__':
    main()
