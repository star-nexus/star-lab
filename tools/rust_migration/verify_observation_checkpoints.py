"""E8 candidate correctness against already validated full reference fingerprints.

Only the candidate exports its whole world. A lightweight current no-reuse
runtime witnesses per-query accounting; recorded independent-old response and
authority hashes anchor the comparison. This is not a performance measurement.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--extension-dir', type=Path, required=True)
    p.add_argument('--trace', type=Path, required=True)
    p.add_argument('--reference-report', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--admission', type=Path)
    p.add_argument('--threads', type=int, choices=[1, 4], default=1)
    a = p.parse_args()
    assert not a.output.exists()
    sys.path.insert(0, str(a.source)); sys.path.insert(0, str(a.extension_dir))
    from rotk_env.runtime.native import RustRuntime
    from star_native import _native
    baseline = json.loads(a.reference_report.read_text())
    assert baseline['passed'] and baseline['mode'] == 'single'
    assert baseline['baseline_extension_sha256'] == '838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544'
    reference_raw = a.reference_report.with_suffix('.checks.jsonl')
    assert sha(reference_raw) == baseline['raw_sha256']
    trace = json.loads(gzip.decompress(a.trace.read_bytes()))
    assert sha(a.trace) == baseline['input_sha256']
    initial_path = a.trace.with_name(trace['initial']['file'])
    assert sha(initial_path) == trace['initial']['sha256']
    initial = json.loads(gzip.decompress(initial_path.read_bytes()))
    entries = trace['entries']
    rows = [json.loads(line) for line in reference_raw.read_text().splitlines()]
    assert len(rows) == len(entries) == baseline['counts']['operations']
    for op, row in zip(entries, rows):
        assert (op['seq'], op['kind']) == (row['seq'], row['kind'])
    groups = {}
    if a.admission:
        admitted = json.loads(a.admission.read_text())
        queries = [o for o in entries if o['kind'] == 'request' and o['action'] == 'get_faction_state']
        observed = [r for r in admitted['admission'] if r['entry'][2] == 'observe']
        assert len(queries) == len(observed)
        serial = {}
        for op, row in zip(queries, observed):
            assert op['parameters'] == row['params']; serial[row['entry'][1]] = op['seq']
        for segment in admitted['segments']:
            seqs = [serial[s] for s in segment['executed']]
            if len(seqs) >= 2: groups[seqs[0]] = seqs
    else:
        seqs = []
        for op in entries + [dict(kind='end')]:
            if op['kind'] == 'request' and op['action'] == 'get_faction_state': seqs.append(op['seq'])
            else:
                for start in range(0, len(seqs), 4):
                    block = seqs[start:start + 4]
                    if len(block) >= 2: groups[block[0]] = block
                seqs = []
    for seqs in groups.values():
        assert 2 <= len(seqs) <= 4 and seqs == list(range(seqs[0], seqs[-1] + 1))
    reference = RustRuntime(initial, threads=a.threads)
    candidate = RustRuntime(initial, threads=a.threads)
    counts = Counter(); started = time.perf_counter(); failure = None
    context = scope = group = None; snapshots = []
    raw = a.output.with_suffix('.checks.jsonl'); raw.parent.mkdir(parents=True, exist_ok=True)
    progress = a.output.with_suffix('.progress.json')
    state_stream = hashlib.sha256(); response_stream = hashlib.sha256()

    def authority(expected):
        payload = candidate._native.export_state_json()
        h = hashlib.sha256(payload.encode()).hexdigest()
        assert h == expected['authority_sha256'], 'Candidate full authority differs from frozen validated reference'
        counts['full_authority_checkpoints'] += 1; state_stream.update(h.encode())
        return payload, h

    try:
        assert reference.take_presentation_delta() == candidate.take_presentation_delta()
        with raw.open('w') as out:
            for op, expected in zip(entries, rows):
                seq = op['seq']; kind = op['kind']; row = dict(seq=seq, kind=kind)
                if seq in groups:
                    assert scope is None
                    group = groups[seq]; snapshots = []
                    context = candidate._admitted_observation_segment('segment_encoded', diagnostics=True)
                    scope = context.__enter__(); counts['segments'] += 1
                if kind == 'request':
                    if 'integer_string_limit' in op: sys.set_int_max_str_digits(op['integer_string_limit'])
                    if op['action'] == 'get_faction_state':
                        kwargs = dict(op['parameters'], agent_id=op['agent_id'], wall_time=op['wall_time'])
                        # Diagnostic witness only; no-reuse is not the performance baseline.
                        with reference._admitted_observation_segment('segment_no_reuse', max_requests=2, diagnostics=True) as witness:
                            old = witness.get_faction_state_json(**kwargs)
                        assert witness.report and len(witness.report['query_diagnostics']) == 1
                        snapshot = witness.report['query_diagnostics'][0]['accounting_after_request']
                        if snapshot['registered_faction'] is not None:
                            assert type(snapshot['agent_actions']) is int and type(snapshot['faction_actions']) is int
                        new = (scope.get_faction_state_json if scope else candidate.get_faction_state_json)(**kwargs)
                        assert old == new and hashlib.sha256(new.encode()).hexdigest() == op['response_wire_sha256']
                        if 'expected_accounting' in expected: assert snapshot == expected['expected_accounting']
                        response_stream.update(new.encode()); counts['queries'] += 1
                        if scope:
                            snapshots.append(snapshot)
                            if seq == group[-1]:
                                context.__exit__(None, None, None)
                                assert [r['accounting_after_request'] for r in context.report['query_diagnostics']] == snapshots
                                counts['query_accounting_snapshots'] += len(snapshots)
                                row['segment_diagnostics'] = context.report
                                context = scope = group = None
                                _, row['authority_sha256'] = authority(expected)
                        else:
                            payload, row['authority_sha256'] = authority(expected)
                            stats = json.loads(payload)['singletons'].get('GameStats', {})
                            meta = candidate.diagnostics(); agent = op['agent_id']
                            faction = stats.get('agent_id_to_faction', {}).get(agent)
                            actual = dict(wall_time=op['wall_time'], epoch=meta['epoch'], revision=meta['revision'],
                                agent=agent, registered_faction=faction,
                                agent_actions=stats.get('action_counts_by_agent', {}).get(agent),
                                faction_actions=stats.get('action_counts_by_faction', {}).get(faction))
                            assert actual == snapshot
                            row['accounting_after_request'] = snapshot
                            counts['query_accounting_snapshots'] += 1
                    else:
                        assert scope is None
                        kwargs = dict(agent_id=op['agent_id'], wall_time=op['wall_time'], registration_time=op['registration_time'])
                        old = reference.execute_action(op['action'], op['parameters'], **kwargs)
                        new = candidate.execute_action(op['action'], op['parameters'], **kwargs)
                        assert old == new and digest(new) == op['response_sha256']
                        row['response_sha256'] = digest(new); response_stream.update(row['response_sha256'].encode())
                        _, row['authority_sha256'] = authority(expected)
                        assert reference.diagnostics()['revision'] == candidate.diagnostics()['revision']
                    counts['requests'] += 1
                elif kind == 'step':
                    assert scope is None
                    reference.step(op['dt'], wall_time=op['wall_time']); candidate.step(op['dt'], wall_time=op['wall_time'])
                    _, row['authority_sha256'] = authority(expected); counts['ticks'] += 1
                elif kind == 'presentation':
                    assert scope is None
                    old = reference.take_presentation_delta(); new = candidate.take_presentation_delta()
                    assert old == new and digest(new) == expected['full_delta_sha256']
                    assert digest(new['events']) == op['events_sha256']
                    row['full_delta_sha256'] = digest(new); counts['presentation'] += 1
                else: raise AssertionError(kind)
                counts['operations'] += 1; out.write(json.dumps(row, separators=(',', ':')) + '\n')
                if seq % 500 == 0:
                    out.flush(); progress.write_text(json.dumps(dict(status='running', seq=seq, total=len(entries), counts=counts, elapsed_s=time.perf_counter()-started))+'\n')
            assert digest(reference.export_state()) == digest(candidate.export_state()) == trace['final_state_sha256']
    except BaseException as error:
        failure = dict(seq=op['seq'] if 'op' in locals() else None, error=repr(error)); raise
    finally:
        if context: context.__exit__(*sys.exc_info())
        candidate.close(); reference.close()
        report = dict(stage='P2 checkpoint reuse, correctness only', passed=failure is None, failure=failure,
            mode='segment_encoded', threads=a.threads, counts=dict(counts), elapsed_s=time.perf_counter()-started,
            input_sha256=sha(a.trace), source_extension_sha256=sha(_native.__file__),
            baseline_extension_sha256=baseline['baseline_extension_sha256'], reference_report_sha256=sha(a.reference_report),
            reference_raw_sha256=sha(reference_raw), tool_sha256=sha(__file__), raw_sha256=sha(raw) if raw.exists() else None,
            state_checkpoint_stream_sha256=state_stream.hexdigest(), response_stream_sha256=response_stream.hexdigest(),
            full_authority_scope='Every world write and step, singleton query and segment end; exact frozen full export SHA',
            query_accounting_scope='Every query: lightweight no-reuse witness, scoped actual native wall/epoch/revision/counts; singleton full state counts/epoch/revision plus supplied wall metadata',
            reference_strategy='Prevalidated independent-old authority/wire; transient current no-reuse accounting witness; no reference full exports except final',
            admission_scope='recorded admitted groups' if a.admission else 'canonical adjacent runs, not host admission evidence',
            performance_claim=False, default_adoption=False)
        a.output.write_text(json.dumps(report, indent=2)+'\n')
        progress.write_text(json.dumps(dict(status='passed' if failure is None else 'failed', counts=counts, failure=failure))+'\n')
        print(json.dumps(dict(passed=failure is None, counts=counts, failure=failure)), flush=True)


if __name__ == '__main__': main()
