"""Check the new no-hash live boundary and live-block analysis controls."""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from admitted_observation_host import LiveWire, EXTENSION_SHA
from analyze_admitted_host import analyze


def main(root):
    calls = []
    class Runtime:
        def execute_action(self, *a, **kw):
            calls.append(('action', a, kw));return {'success': True}
        def get_faction_state_json(self, **kw):
            calls.append(('ordinary', kw));return '{"success":true}'
        def export_state(self):
            raise AssertionError('Full export must not be called')
    wire = LiveWire(Runtime(), None, None, {'sha256': EXTENSION_SHA}, 1)
    session = SimpleNamespace(agent_id='a')
    assert wire.call(session, 'move', {'unit_id': 1}) == {'success': True}
    owned = wire.observation_json(session, {'faction': 'wei'})
    assert calls[-1] == ('ordinary', {'faction': 'wei', 'agent_id': 'a'})
    try:
        wire.observation_json(session, {'faction': 'wei'})
    except AssertionError:
        pass
    else:
        raise AssertionError('Pending response must prevent extra request')
    wire.payload(owned.encode())
    scoped = SimpleNamespace(get_faction_state_json=lambda **kw: '{"scoped":true}')
    wire.query_scope = scoped
    second = wire.observation_json(session, {'faction': 'shu'})
    wire.payload(second.encode());wire.query_scope = None
    result = wire.finish()
    assert result['queries'] == result['payloads'] == 2
    assert result['full_world_exports_during_measurement'] == 0 and owned == '{"success":true}'
    root = Path(root);root.mkdir(exist_ok=False)
    paths = []
    for i, mode in enumerate(['single', 'segment_encoded', 'segment_encoded', 'single']):
        value = 10. if mode == 'single' else 9.
        raw = {'frames': [{'t': j / 30, 'work_ms': value} for j in range(217)],
               'events': [{'t': j / 30 + .001, 'event': 'observe', 'service_ms': value,
                           'response_ms': value, 'queue_ms': 0.} for j in range(217)]}
        p = root / f'{i}.json';rp = p.with_suffix('.raw.json');rp.write_text(json.dumps(raw))
        from p3_local_agents import stats
        meta = dict(raw={'path': rp.name, 'sha256': hashlib.sha256(rp.read_bytes()).hexdigest()},
                    workload={'warmup': 0., 'presentation_research_mode': 'baseline'},
                    frame_work_ms=stats([value]*217), observation_response_ms=stats([value]*217),
                    action_queue_ms={'count':0}, completed_observations=217,
                    native_recording={'queries':217, 'payloads':217, 'full_world_exports_during_measurement':0},
                    extension={'sha256':EXTENSION_SHA}, host_mode=mode, fixture_sha256='same',
                    dependency_lock_sha256='same', surface_size=[2480,1235], hardware={'window':[2480,1235]},
                    display_driver='cocoa', guards={'control':True})
        p.write_text(json.dumps(meta))
        p.with_suffix('.monitor.json').write_text(json.dumps(dict(status='passed', child_exit=0,
            samples=[{'pressure':1}],events=[],automatic_pause=False,automatic_termination=False)))
        paths.append(p)
    positive = analyze(paths)
    assert positive['screening_positive']
    for m in positive['metrics'].values():
        assert m['ci95_live_block_difference_ms'] == [1.,1.] and m['improvement_percent'] == 10.
    g = paths[1].with_suffix('.monitor.json');data = json.loads(g.read_text());data['events'] = [{'event':'warning'}]
    g.write_text(json.dumps(data));invalid = analyze(paths)
    assert not invalid['screening_positive'] and invalid['decision'] == 'inconclusive resource interference'
    (root/'validation.json').write_text(json.dumps(dict(passed=True, boundary_owned_no_export=True,
            exact_positive_control=True, weighted_partial_17_frames=True, resource_invalid_rejected=True,
            performance_evidence=False),indent=2)+'\n')
    print('PASS: owned wire / no export / pending callback / exact live-block control / invalid resource rejection')


if __name__ == '__main__':
    main(sys.argv[1])
