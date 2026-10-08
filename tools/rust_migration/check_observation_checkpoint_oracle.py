"""Small independent-old fixture and positive/negative validation of E8 hash reuse."""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from threading import RLock

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--extension-dir', type=Path, required=True)
    p.add_argument('--baseline-extension', type=Path, required=True)
    p.add_argument('--runs', type=Path, required=True)
    a = p.parse_args()
    a.runs.mkdir(parents=True, exist_ok=True)
    assert not (a.runs / 'validation.json').exists()
    sys.path.insert(0, str(a.source)); sys.path.insert(0, str(a.extension_dir))
    from rotk_env.tests.test_native_observation import setup
    from rotk_env.runtime.bootstrap import export_initial_state
    from rotk_env.runtime.native import RustRuntime
    world, (unit, other, enemy), _ = setup('window')
    try:
        initial = export_initial_state(world, display='window')
    finally:
        world.reset()
    initial_path = a.runs / 'mini.initial.json.gz'
    initial_path.write_bytes(gzip.compress(json.dumps(initial, allow_nan=False).encode(), mtime=0))
    spec = importlib.util.spec_from_file_location('e8_frozen_reference._native', a.baseline_extension)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    r = RustRuntime.__new__(RustRuntime)
    r._admission_lock = RLock(); r._native = module.NativeRuntime(json.dumps(initial, allow_nan=False), 1)
    entries = []; rows = []
    def request(action, params, agent='alpha'):
        seq = len(entries); wall = 1720000000. + seq
        op = dict(seq=seq, kind='request', action=action, parameters=params,
                  agent_id=agent, wall_time=wall, registration_time=None)
        row = dict(seq=seq, kind='request')
        if action == 'get_faction_state':
            wire = r.get_faction_state_json(**params, agent_id=agent, wall_time=wall)
            op['response_wire_sha256'] = hashlib.sha256(wire.encode()).hexdigest()
            stats = r.export_state()['singletons']['GameStats']; meta = r.diagnostics()
            faction = stats['agent_id_to_faction'].get(agent)
            row['expected_accounting'] = dict(wall_time=wall, epoch=meta['epoch'], revision=meta['revision'],
                agent=agent, registered_faction=faction, agent_actions=stats['action_counts_by_agent'].get(agent),
                faction_actions=stats['action_counts_by_faction'].get(faction))
        else:
            result = r.execute_action(action, params, agent_id=agent, wall_time=wall, registration_time=None)
            op['response_sha256'] = row['response_sha256'] = digest(result)
        row['authority_sha256'] = hashlib.sha256(r._native.export_state_json().encode()).hexdigest()
        entries.append(op); rows.append(row)
    def presentation():
        seq = len(entries); delta = r.take_presentation_delta()
        entries.append(dict(seq=seq, kind='presentation', events_sha256=digest(delta['events'])))
        rows.append(dict(seq=seq, kind='presentation', full_delta_sha256=digest(delta)))
    try:
        r.take_presentation_delta()
        request('get_faction_state', dict(faction='wei', unit_ids=[unit]))
        request('get_faction_state', dict(faction='wei', unit_ids=[other, unit, other]), 'beta')
        request('get_faction_state', dict(faction='shu', unit_ids=[enemy]), 'enemy')
        request('get_faction_state', dict(faction='shu'), 'alpha')
        request('get_faction_state', dict(faction='wei', unit_ids=[]))
        request('get_faction_state', dict(faction='wei', unit_ids=None))
        request('rest', dict(unit_id=unit))
        request('get_faction_state', dict(faction='wei', unit_ids=[unit]))
        request('get_faction_state', dict(faction='invalid'), 'unknown-agent')
        request('get_faction_state', dict(faction='wei', unit_ids='invalid'))
        seq = len(entries); wall = 1720000000. + seq
        r.step(1/30, wall_time=wall)
        entries.append(dict(seq=seq, kind='step', dt=1/30, wall_time=wall))
        rows.append(dict(seq=seq, kind='step', authority_sha256=hashlib.sha256(r._native.export_state_json().encode()).hexdigest()))
        presentation()
        request('get_faction_state', dict(faction='wei'))
        presentation()
        final = digest(r.export_state())
    finally:
        r.close()
    trace = a.runs / 'mini.trace.json.gz'
    trace.write_bytes(gzip.compress(json.dumps(dict(initial=dict(file=initial_path.name, sha256=sha(initial_path)),
        entries=entries, final_state_sha256=final), allow_nan=False).encode(), mtime=0))
    raw = a.runs / 'reference.checks.jsonl'
    raw.write_text(''.join(json.dumps(row)+'\n' for row in rows))
    report = a.runs / 'reference.json'
    base = dict(passed=True, mode='single', baseline_extension_sha256=sha(a.baseline_extension),
        input_sha256=sha(trace), raw_sha256=sha(raw), counts=dict(operations=len(entries)),
        fixture_scope='Tiny world; all hashes and accounting from independent old extension')
    report.write_text(json.dumps(base, indent=2)+'\n')
    tool = Path(__file__).with_name('verify_observation_checkpoints.py')
    cmd = [sys.executable, str(tool), '--source', str(a.source), '--extension-dir', str(a.extension_dir),
           '--trace', str(trace), '--reference-report', str(report)]
    outcomes = []
    for threads in (1, 4):
        output = a.runs / f'encoded-t{threads}.json'
        result = subprocess.run([*cmd, '--threads', str(threads), '--output', str(output)], capture_output=True, text=True)
        (a.runs / f'encoded-t{threads}.log').write_text(result.stdout+result.stderr)
        assert result.returncode == 0, result.stderr
        checked = json.loads(output.read_text()); assert checked['passed']
        assert checked['counts']['query_accounting_snapshots'] == sum(
            op.get('action') == 'get_faction_state' for op in entries)
        outcomes.append(dict(threads=threads, report=checked))
    # A false anchor and a false per-query counter must both be rejected.
    for field in ('authority', 'accounting'):
        altered = json.loads(json.dumps(rows))
        if field == 'authority': altered[3]['authority_sha256'] = '0'*64
        else: altered[0]['expected_accounting']['agent_actions'] += 1
        bad_raw = a.runs / f'bad-{field}.checks.jsonl'
        bad_raw.write_text(''.join(json.dumps(row)+'\n' for row in altered))
        bad_report = a.runs / f'bad-{field}.json'
        bad_report.write_text(json.dumps(dict(base, raw_sha256=sha(bad_raw)))+'\n')
        bad_output = a.runs / f'rejected-{field}.json'
        bad_cmd = [*cmd]; bad_cmd[bad_cmd.index('--reference-report')+1] = str(bad_report)
        result = subprocess.run([*bad_cmd, '--output', str(bad_output)], capture_output=True, text=True)
        (a.runs / f'rejected-{field}.log').write_text(result.stdout+result.stderr)
        assert result.returncode != 0 and not json.loads(bad_output.read_text())['passed']
    (a.runs / 'validation.json').write_text(json.dumps(dict(passed=True, positives=outcomes,
        negative_checks=['wrong full authority SHA rejected', 'wrong independent-old count rejected'],
        tool_sha256=sha(tool), fixture_tool_sha256=sha(__file__)), indent=2)+'\n')
    print('Checkpoint oracle: independent old fixture native1/4 passed; two false anchors rejected', flush=True)

if __name__ == '__main__': main()
