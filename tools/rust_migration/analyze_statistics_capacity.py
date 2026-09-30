"""Audit E2 real Cocoa Statistics-parallel 1000-Agent long capacity gate."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from p3_local_agents import stats

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);root=p.parse_args().root
 rows=[]
 for file in sorted((root/'results').glob('*.json')):
  if file.name.endswith('.raw.json'):continue
  r=json.loads(file.read_text())
  if not isinstance(r,dict) or 'frame_work_ms' not in r:continue
  rawpath=file.with_suffix('.raw.json');body=rawpath.read_bytes();assert hashlib.sha256(body).hexdigest()==r['raw']['sha256'];raw=json.loads(body)
  warm=r['workload']['warmup'];frames=[x for x in raw['frames'] if x['t']>=warm];events=[x for x in raw['events'] if x['t']>=warm];obs=[x for x in events if x['event']=='observe'];act=[x for x in events if x['event']=='act']
  assert stats([x['work_ms'] for x in frames])==r['frame_work_ms']
  for metric,es,key in [('observation_response_ms',obs,'response_ms'),('observation_queue_ms',obs,'queue_ms'),('action_queue_ms',act,'queue_ms')]:assert stats([x[key] for x in es])==r[metric]
  rows.append(dict(run=file.stem,source=r['source'],tooling=r['tooling'],workload=r['workload'],passed=r['pass'],guards=r['guards'],failed_guards=[k for k,v in r['guards'].items() if not v],frame=r['frame_work_ms'],world_hz=r['world_hz'],observation=r['observation_response_ms'],observation_queue=r['observation_queue_ms'],action_queue=r['action_queue_ms'],nominal_load_fraction=r['nominal_load_fraction'],oldest_overdue_ms=r['agents']['oldest_overdue_ms'],service={k:stats([x[k] for x in obs]) for k in ['build_ms','encode_ms','decode_ms','service_ms','bytes']},agent_ms=stats([f['agent_ms'] for f in frames]),non_agent_ms=stats([f['work_ms']-f['agent_ms'] for f in frames]),native_phases=r['native_phases_ms'],alive_min=min(c['alive'] for c in r['censuses']),peak_moving=max(c['moving'] for c in r['censuses']),cpu_seconds=r['cpu_seconds'],maxrss=max(c['maxrss'] for c in r['censuses']),counts_including_warmup=r['agents']['counts'],hardware=r['hardware'],display_driver=r['display_driver'],fixture_sha256=r['fixture_sha256'],extension=r['extension'],native_recording=r['native_recording'],raw=r['raw']))
 long=[r for r in rows if r['workload']['backend']=='rust' and r['workload']['seconds']==300]
 gate=len(long)==3 and all(r['passed'] for r in long)
 if long:
  assert len({r['source']['sha'] for r in long})==1
  assert len({r['extension']['sha256'] for r in long})==1
  assert len({r['fixture_sha256'] for r in long})==1
  assert len({tuple(r['hardware']['window']) for r in long})==1
  assert len({r['display_driver'] for r in long})==1
  assert all(r['workload']['agents']==1000 and r['workload']['units']==5000 and r['workload']['fps']==30 and r['workload']['warmup']==30 and r['workload']['budget_ms']==8 and r['workload']['native_threads']==4 and r['workload']['native_wire'] for r in long)
  assert all(r['display_driver']=='cocoa' and r['hardware']['window']==[2480,1239] for r in long)
 short={r['run']:r for r in rows if r['workload']['seconds']==60};ratios={}
 if 'rust-60' in short:
  after=short['rust-60']
  for key,before in short.items():
   if before['workload']['backend']!='python':continue
   for shared in ['fixture_sha256','display_driver']:assert before[shared]==after[shared]
   assert before['hardware']['window']==after['hardware']['window']
   for shared in ['fps','clock_mode','cycle_mode','jitter_seconds','units','agents','delay','scope','layout','policy','seconds','warmup','budget_ms','gc_policy']:assert before['workload'][shared]==after['workload'][shared]
   ratios[key]=dict(frame_p99_time_ratio=before['frame']['p99']/after['frame']['p99'],observation_service_mean_time_ratio=before['service']['service_ms']['avg']/after['service']['service_ms']['avg'],frame_p99_reduction_fraction=1-after['frame']['p99']/before['frame']['p99'],observation_service_reduction_fraction=1-after['service']['service_ms']['avg']/before['service']['service_ms']['avg'],note='One independent live run per backend, same workload parameters; actual admitted actions and state trajectories differ. Not a pure language or fixed-input speedup.')
 result=dict(all_raw_recomputations_passed=True,rows=rows,short_live_ratios=ratios,rust_long_runs=len(long),rust_long_gate_passed=gate,declared_native_threads=4,note='Same canonical profile; optional4-worker E2. No fixed-input whole-frame speedup claim or expanded unit/Agent Frontier.')
 (root/'results/capacity-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
 for r in rows:print(r['run'],r['frame']['p99'],r['observation']['p99'],r['action_queue']['p99'],r['failed_guards'])
 print('long gate',gate)
if __name__=='__main__':main()
