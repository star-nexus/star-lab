"""Recompute full admitted-window metrics; diagnostic passes are not capacity gates."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from p3_local_agents import stats


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    root=parser.parse_args().root
    rows=[]
    for p in sorted((root/'results').glob('a[15]000*.json')):
        if p.name.endswith('.raw.json'):continue
        r=json.loads(p.read_text());rawpath=p.with_suffix('.raw.json')
        assert hashlib.sha256(rawpath.read_bytes()).hexdigest()==r['raw']['sha256']
        raw=json.loads(rawpath.read_text());warm=r['workload']['warmup']
        frames=[f for f in raw['frames'] if f['t']>=warm]
        events=[e for e in raw['events'] if e['t']>=warm]
        obs=[e for e in events if e['event']=='observe'];act=[e for e in events if e['event']=='act']
        assert stats([f['work_ms'] for f in frames])==r['frame_work_ms']
        for key,event,field in [('observation_response_ms',obs,'response_ms'),('observation_queue_ms',obs,'queue_ms'),('action_queue_ms',act,'queue_ms')]:
            assert stats([e[field] for e in event])==r[key]
        rows.append(dict(run=p.stem,source=r['source'],tooling=r['tooling'],workload=r['workload'],guards=r['guards'],passed=r['pass'],failed_guards=[k for k,v in r['guards'].items() if not v],frame=r['frame_work_ms'],world_hz=r['world_hz'],observation=r['observation_response_ms'],observation_queue=r['observation_queue_ms'],action_queue=r['action_queue_ms'],nominal_load_fraction=r['nominal_load_fraction'],oldest_overdue_ms=r['agents']['oldest_overdue_ms'],observations=len(obs),action_events=len(act),phases=r['native_phases_ms'],agent_ms=stats([f['agent_ms'] for f in frames]),non_agent_ms=stats([f['work_ms']-f['agent_ms'] for f in frames]),observation_service={k:stats([e[k] for e in obs]) for k in ['build_ms','encode_ms','decode_ms','service_ms','bytes']},alive_min=min(c['alive'] for c in r['censuses']),moving_max=max(c['moving'] for c in r['censuses']),counts_including_warmup=r['agents']['counts'],cpu_seconds=r['cpu_seconds'],maxrss=max(c['maxrss'] for c in r['censuses']),hardware=r['hardware'],driver=r['display_driver'],fixture_sha256=r['fixture_sha256'],extension=r['extension'],recording=r['native_recording'],raw=r['raw']))
    profiles=[json.loads(p.read_text())|{'run':p.stem} for p in sorted((root/'results').glob('boundary-*.json'))]
    if profiles:
        assert len({p['final_state_sha256'] for p in profiles})==1
        assert len({p['trace_sha256'] for p in profiles})==1
        assert all(p['all_responses_events_and_final_state_match'] for p in profiles)
    result=dict(all_metric_recomputations_passed=True,rows=rows,boundary_profiles=profiles,capacity_gate_passed=False,capacity_note='This phase uses 60-second diagnostics, not 300 seconds x 3 acceptance.')
    (root/'results/comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    for r in rows:print(r['run'],round(r['frame']['p99'],3),round(r['observation']['p99'],3),round(r['action_queue']['p99'],3),r['failed_guards'])

if __name__=='__main__':main()
