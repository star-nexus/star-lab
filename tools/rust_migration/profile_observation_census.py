"""Small same-binary bare-handler attribution, never a service/adoption test."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--extension-dir', type=Path, required=True)
    p.add_argument('--extension-sha256', required=True)
    p.add_argument('--trace', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); assert not a.output.exists()
    sys.path.insert(0, str(a.source)); sys.path.insert(0, str(a.extension_dir))
    from rotk_env.runtime.native import RustRuntime
    from star_native import _native
    assert hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest() == a.extension_sha256
    trace = json.loads(gzip.decompress(a.trace.read_bytes()))
    initial = json.loads(gzip.decompress(a.trace.with_name(trace['initial']['file']).read_bytes()))
    rows = []; expected = None
    with RustRuntime(initial, threads=1) as runtime:
        runtime.take_presentation_delta()
        for op in trace['entries']:
            if op.get('action') == 'get_faction_state':
                params = [dict(op['parameters'], agent_id=op['agent_id'])]; break
            if op['kind'] == 'request':
                response = runtime.execute_action(op['action'], op['parameters'], agent_id=op['agent_id'], wall_time=op['wall_time'], registration_time=op['registration_time'])
                assert digest(response) == op['response_sha256']
            elif op['kind'] == 'step': runtime.step(op['dt'], wall_time=op['wall_time'])
            else: runtime.take_presentation_delta()
        before = digest(runtime.export_state())
        for round_id in range(5):
            for mode in (['baseline', 'borrowed_census', 'borrowed_census', 'baseline'] if round_id % 2 == 0 else ['borrowed_census', 'baseline', 'baseline', 'borrowed_census']):
                runtime._set_observation_scan_research(mode)
                report, timing = runtime._native._observation_profile_json(json.dumps(params))
                decoded = json.loads(report)
                if expected is None: expected = decoded
                assert decoded == expected
                rows.append(dict(round=round_id, mode=mode, timing=json.loads(timing)))
        assert digest(runtime.export_state()) == before
    grouped = {}
    for mode in ['baseline', 'borrowed_census']:
        values = [r['timing'] for r in rows if r['mode'] == mode]
        grouped[mode] = dict(samples=len(values), mean_census_ns=sum(v['profile']['census_ns'] for v in values)/len(values),
                             mean_batch_ns=sum(v['batch_ns'] for v in values)/len(values), mean_native_ns=sum(v['native_ns'] for v in values)/len(values))
    a.output.write_text(json.dumps(dict(passed=True, diagnostic_only=True, performance_claim=False, rows=rows, summary=grouped,
        metrics=expected['metrics'], source='same native1 binary, first recorded pre-query state, 5 short ABBA/BAAB diagnostic cycles',
        extension_sha256=a.extension_sha256, trace_sha256=hashlib.sha256(a.trace.read_bytes()).hexdigest(),
        tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), state_unchanged_sha256=before), indent=2)+'\n')
    print(json.dumps(grouped))


if __name__ == '__main__': main()
