"""Census selection, owned wire and live statistical negative controls."""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import numpy as np
import census_observation_host as host
from analyze_census_host import analyze
from p3_local_agents import stats


def main(root):
    host.host.EXTENSION_SHA=host.EXTENSION_SHA
    selected=[]
    class Runtime:
        def __init__(self):self.mode='baseline';self._native=self
        def _set_observation_scan_research(self,mode):selected.append(mode);self.mode=mode
        def _observation_scan_research(self):return self.mode
        def execute_action(self,*a,**kw):return {'success':True}
        def get_faction_state_json(self,**kw):return '{"success":true}'
        def export_state(self):raise AssertionError('no timed full export')
    for mode in ['baseline','borrowed_census']:
        host.CensusWire.scan_mode=mode
        wire=host.CensusWire(Runtime(),None,None,{'sha256':host.EXTENSION_SHA},1)
        own=wire.observation_json(SimpleNamespace(agent_id='a'),{'faction':'wei'})
        wire.payload(own.encode());report=wire.finish()
        assert report['scan_mode']==mode and report['queries']==report['payloads']==1
    assert selected==['baseline','borrowed_census']
    host.CensusWire.scan_mode='entity_ref'
    try:host.CensusWire(Runtime(),None,None,{'sha256':host.EXTENSION_SHA},1)
    except ValueError:pass
    else:raise AssertionError('rejected unrelated scan candidate')
    assert len(selected)==2
    root=Path(root);root.mkdir(parents=True,exist_ok=False);paths=[]
    for i,mode in enumerate(['baseline','borrowed_census','borrowed_census','baseline']):
        frame=10. if mode=='baseline' else 9.;service=3. if mode=='baseline' else 2.7
        raw={'frames':[dict(t=j/30,work_ms=frame) for j in range(217)],
             'events':[dict(t=j/30+.001,event='observe',service_ms=service,response_ms=service,queue_ms=.4) for j in range(217)]+[dict(t=1.,event='act',queue_ms=.3)]}
        out=root/f'{i}.json';rp=out.with_suffix('.raw.json');rp.write_text(json.dumps(raw))
        meta=dict(raw=dict(path=rp.name,sha256=hashlib.sha256(rp.read_bytes()).hexdigest()),
                  workload=dict(warmup=0,presentation_research_mode='baseline'),source=dict(sha='8c2afd7153ebc8ec6c80dd9f3a1406be440405e0'),
                  frame_work_ms=stats([frame]*217),observation_response_ms=stats([service]*217),observation_queue_ms=stats([.4]*217),action_queue_ms=stats([.3]),
                  completed_observations=217,native_recording=dict(queries=217,payloads=217,full_world_exports_during_measurement=0,scan_mode=mode,scan_mode_persisted=True,scan_configuration_calls=1),
                  extension=dict(sha256=host.EXTENSION_SHA),host_mode='single',census_scan_mode=mode,admitted_segments=dict(count=0),
                  fixture_sha256='same',dependency_lock_sha256='same',surface_size=[2480,1235],hardware=dict(window=[2480,1235]),display_driver='cocoa',guards=dict(control=True))
        out.write_text(json.dumps(meta));out.with_suffix('.monitor.json').write_text(json.dumps(dict(status='passed',child_exit=0,samples=[dict(pressure=1)],events=[],automatic_pause=False,automatic_termination=False)))
        paths.append(out)
    good=analyze(paths);assert good['screening_positive']
    assert np.allclose(good['metrics']['frame_work_ms']['ci95_live_block_difference_ms'],[1,1])
    assert np.allclose(good['metrics']['observation_service_ms']['ci95_live_block_difference_ms'],[.3,.3])
    g=paths[1].with_suffix('.monitor.json');guard=json.loads(g.read_text());guard['events']=[dict(event='warning')];g.write_text(json.dumps(guard));assert not analyze(paths)['screening_positive']
    guard['events']=[];g.write_text(json.dumps(guard))
    out=paths[1];meta=json.loads(out.read_text());rp=out.parent/meta['raw']['path'];raw=json.loads(rp.read_text())
    for row in raw['events']:
        if row['event']=='observe':row['queue_ms']=.5
    rp.write_text(json.dumps(raw));meta['raw']['sha256']=hashlib.sha256(rp.read_bytes()).hexdigest();meta['observation_queue_ms']=stats([.5]*217);out.write_text(json.dumps(meta))
    negative=analyze(paths);assert not negative['screening_positive'] and not negative['queue_envelopes']['observation_queue_ms']['no_regression']
    (root/'controls.json').write_text(json.dumps(dict(passed=True,selection_once_before_warmup=True,ordinary_owned_wire=True,unrelated_mode_rejected=True,positive_exact_ci=True,partial_tail_17_frames=True,pressure_rejection=True,queue_tail_rejection=True,performance_evidence=False),indent=2)+'\n')
    print('PASS: census selection / ordinary owned wire / live CI / pressure and queue negative controls')


if __name__=='__main__':main(sys.argv[1])
