"""Owned JSON assembly: handler and authenticated batch; not a world FPS gate."""
import argparse
import hashlib
import json
import lzma
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from kernel_attack_candidates_probe import digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--threads', type=int, choices=(1,2,4), default=1)
    parser.add_argument('--mp', type=int, choices=(0,6), default=0)
    args = parser.parse_args()
    source, out = args.source.resolve(), args.output.resolve()
    lab = Path(__file__).resolve().parents[2]
    os.chdir(source); sys.path.insert(0, str(source))
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    from star_native import NativeRuntime, API_VERSION, _native
    out.mkdir(parents=True, exist_ok=True)
    def git(root, *cmd):
        return subprocess.check_output(['git', *cmd], cwd=root, text=True).strip()
    inputs = [
        ('catalog', lab/'experiments/2026-09-rust-kernel-catalog/results/after/raw.json.xz'),
        ('targets', lab/'experiments/2026-09-rust-kernel-targets/results/after/raw.json.xz'),
    ]
    scenarios, references = [], []
    for kind, path in inputs:
        blob = path.read_bytes()
        references.append(dict(path=str(path.relative_to(lab)), sha256=hashlib.sha256(blob).hexdigest()))
        for case in json.loads(lzma.decompress(blob)):
            s = case['summary']
            if kind == 'catalog' and s['radius'] == 45 and s['fog'] in ('local', 'disabled'):
                scenarios.append((f"terrain-{s['fog']}", case))
            if kind == 'targets' and s['units'] == 5000 and s['radius'] == 3 and s['ap'] == 2:
                scenarios.append(('units-5000', case))
    assert len(scenarios) == 3
    rows, raw = [], []
    for name, case in scenarios:
        initial = json.loads(json.dumps(case['initial']))
        if args.mp:
            for entity in initial['entities']:
                movement = entity['components'].get('MovementPoints')
                if movement is not None:
                    movement.update(current_mp=args.mp,max_mp=args.mp,base_mp=args.mp)
        initial_wire = json.dumps(initial)
        for count in (1, 8):
            params = [dict(case['parameters'], agent_id=f'agent-{i}') for i in range(count)]
            requests = [dict(agent_id=f'agent-{i}', action='get_faction_state', parameters=p, wall_time=1720000000.+i) for i,p in enumerate(params)]
            import_start = time.perf_counter_ns()
            n = NativeRuntime(initial_wire, args.threads)
            import_ms = (time.perf_counter_ns()-import_start)/1e6
            try:
                for i in range(count):
                    reg = dict(agent_id=f'agent-{i}', action='register_agent_info', parameters=dict(faction='wei',provider='synthetic',model_id='fake',base_url='https://host'),wall_time=1720000000.,registration_time='2026-09-24T12:00:00',sanitized_base_url='https://host')
                    assert json.loads(n.execute_action_json(json.dumps(reg)))['success']
                registered_wire = n.export_state_json()
                registered = json.loads(registered_wire)
                expected = [json.loads(n.execute_action_json(json.dumps(r))) for r in requests]
                expected_final = json.loads(n.export_state_json())
                if not args.mp:
                    for result in expected:
                        assert result == case['response'][0]
                elif name == 'units-5000':
                    assert sum(len(u['reachable']) for u in expected[0]['units']) > 0
                for mode in (('handler', 'public', 'single') if count == 1 else ('handler', 'public')):
                    wire = json.dumps(params if mode == 'handler' else requests[0] if mode == 'single' else requests)
                    operation = (n._observation_probe_json if mode == 'handler' else n.execute_action_json if mode == 'single' else n.execute_actions_json)
                    samples = []
                    sample_metrics = []
                    report = None
                    for iteration in range(6):
                        n.reset(registered_wire)  # Reset/import deliberately excluded from timing.
                        start = time.perf_counter_ns()
                        encoded = operation(wire)
                        elapsed = (time.perf_counter_ns()-start)/1e6
                        report = json.loads(encoded)
                        if mode == 'single':
                            report = dict(results=[report])
                        assert report['results'] == expected
                        if iteration:
                            samples.append(elapsed)
                            sample_metrics.append(report.get('metrics', report.get('observation_segments', [{}])[0].get('metrics', {})))
                    final = json.loads(n.export_state_json())
                    assert final == (registered if mode == 'handler' else expected_final)
                    metrics = (report['metrics'] if mode == 'handler' else report['observation_segments'][0]['metrics'] if mode == 'public' else {})
                    if metrics:
                        assert metrics['census_builds'] == metrics['faction_builds'] == 1
                    if 'public_encodes' in metrics:
                        assert metrics['public_encodes'] == 1
                        assert metrics['panel_encodes'] == len(params[0]['unit_ids'])
                        assert metrics['shared_public_results'] == count
                        assert metrics['shared_panel_results'] == count * len(params[0]['unit_ids'])
                    row = dict(scenario=name, mode=mode, requests=count, threads=args.threads,mp=args.mp,import_ms=import_ms, selected_units=len(params[0]['unit_ids']),
                               initial_sha256=digest(registered),final_sha256=digest(final),response_sha256=digest(report),agent_response_sha256=digest(report['results']),
                               wire_bytes=len(encoded.encode()),metrics=metrics,sample_metrics=sample_metrics,reachable_cells=sum(len(u['reachable']) for u in expected[0]['units']),samples_ms=samples,median_ms=sorted(samples)[2],
                               matches_sequential=True,matches_archived_response=True if not args.mp else None)
                    rows.append(row)
                    # Initial world lives only in the canonical input archive. Keep all actual
                    # envelopes/results and the post-registration/final state hashes here.
                    raw.append(dict(summary=row,requests=requests,handler_parameters=params,response=report))
            finally:
                n.close()
    raw_path = out/'raw.json.xz'
    raw_path.write_bytes(lzma.compress(json.dumps(raw,separators=(',',':')).encode()))
    report = dict(source_sha=git(source,'rev-parse','HEAD'),source_dirty=git(source,'status','--porcelain'),
                  tool_sha=git(lab,'rev-parse','HEAD'),api=API_VERSION,threads=args.threads,mp=args.mp,
                  extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),
                  inputs=references,platform=platform.platform(),python=sys.version,rows=rows,
                  timing='Native query/batch including JSON encoding; excludes import/reset/Python decode; 1 warmup +5 samples',
                  raw_sha256=hashlib.sha256(raw_path.read_bytes()).hexdigest(),all_guards_passed=True,capacity_claim=False)
    assert not report['source_dirty']
    (out/'compact.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
    print(json.dumps(rows))


if __name__ == '__main__':
    main()
