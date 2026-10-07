"""E8 P0: replay recorded single requests; profile handler facts off live path.

The existing batch profiler isolates removable builds, not an E8 implementation
or authenticated service comparison. JSON report packing is deliberately not
included in the estimated savings; final per-request responses remain required.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--run', type=Path, required=True, help='P0 window metadata .json')
    p.add_argument('--admission', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--samples-per-kind', type=int, default=10)
    a = p.parse_args()
    assert not a.output.exists()
    sys.path.insert(0, str(a.source))
    from star_native import NativeRuntime, _native
    from rotk_env.runtime.native import ActionRequest
    meta = json.loads(a.run.read_text())
    admission = json.loads(a.admission.read_text())
    trace_path = a.run.with_suffix('.trace.json.gz')
    initial_path = a.run.with_suffix('.initial.json.gz')
    trace = json.loads(gzip.decompress(trace_path.read_bytes()))
    initial = json.loads(gzip.decompress(initial_path.read_bytes()))
    assert hashlib.sha256(trace_path.read_bytes()).hexdigest() == meta['native_recording']['trace']['sha256']
    assert hashlib.sha256(initial_path.read_bytes()).hexdigest() == meta['native_recording']['initial']['sha256']
    queries = [op for op in trace['entries'] if op['kind']=='request' and op['action']=='get_faction_state']
    observed = [r for r in admission['admission'] if r['entry'][2]=='observe']
    assert len(queries) == len(observed)
    by_serial = {}
    for op, r in zip(queries, observed):
        assert op['parameters'] == r['params']
        by_serial[r['entry'][1]] = op
    segment_at = {by_serial[s['executed'][0]]['seq']: s for s in admission['segments'] if s['executed']}
    n = NativeRuntime(json.dumps(initial,separators=(',',':')), 1)
    # Recorder begins after the session's initial presentation refresh.
    n.take_presentation_delta_json(None)
    profiles = []
    counts = Counter()
    checked = Counter()
    started = time.perf_counter()
    try:
        for op in trace['entries']:
            if op['seq'] in segment_at:
                segment = segment_at[op['seq']]
                batch_ops = [by_serial[x] for x in segment['executed']]
                factions = [x['parameters']['faction'] for x in batch_ops]
                kind = f"{len(batch_ops)}-{'same' if len(set(factions))==1 else 'mixed'}"
                counts[kind] += 1
                if counts[kind] <= a.samples_per_kind:
                    params = [dict(x['parameters'],agent_id=x['agent_id']) for x in batch_ops]
                    before = n.export_state_json()
                    singles, times = [], []
                    for value in params:
                        encoded, timing = n._observation_profile_json(json.dumps([value]))
                        singles.append(json.loads(encoded))
                        times.append(json.loads(timing))
                    encoded, timing = n._observation_profile_json(json.dumps(params))
                    combined = json.loads(encoded)
                    assert combined['results'] == [v['results'][0] for v in singles]
                    assert n.export_state_json() == before, 'Diagnostic handler changed authority'
                    profiles.append(dict(kind=kind, first_seq=op['seq'], segment=segment,
                                         parameters=params, single_reports=singles,
                                         single_profiles=times, combined_report=combined,
                                         combined_profile=json.loads(timing)))
            if op['kind'] == 'request':
                # Preserve ingress normalization, notably registration URL and
                # null-vs-empty registration metadata. Trace operations are not
                # already-normalized native Request envelopes.
                request = ActionRequest(op['agent_id'],op['action'],op['parameters'],
                                        op['wall_time'],op['registration_time']).to_wire()
                wire = n.execute_action_json(json.dumps(request,allow_nan=False))
                if op['action']=='get_faction_state':
                    assert hashlib.sha256(wire.encode()).hexdigest() == op['response_wire_sha256']
                else:
                    assert digest(json.loads(wire)) == op['response_sha256'], f"response at seq {op['seq']}"
                checked['requests'] += 1
            elif op['kind'] == 'step':
                n.step(op['dt'], op['wall_time'])
                checked['ticks'] += 1
            elif op['kind'] == 'presentation':
                delta = json.loads(n.take_presentation_delta_json(None))
                assert digest(delta['events']) == op['events_sha256']
                checked['presentation'] += 1
            else:
                raise AssertionError(f"Unexpected trace kind: {op['kind']}")
        assert digest(json.loads(n.export_state_json())) == trace['final_state_sha256']
    finally:
        n.close()
    a.output.write_text(json.dumps(dict(schema='star-e8-cost-p0-v1',diagnostic_only=True,
        authenticated_speedup_claim=False, source=meta['source'], extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),
        inputs={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in (trace_path,initial_path,a.admission)},
        segment_counts=dict(counts), profiles=profiles, checked=dict(checked),
        final_state_sha256=trace['final_state_sha256'], elapsed_s=time.perf_counter()-started),separators=(',',':'))+'\n')
    print(json.dumps(dict(cost_diagnostic='passed',checked=checked,sampled=len(profiles),segments=counts)),flush=True)


if __name__ == '__main__':
    main()
