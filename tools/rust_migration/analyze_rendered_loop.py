"""Recompute admitted metrics and compare exact presentation deltas across builds."""
import argparse,gzip,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from p3_local_agents import stats
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,required=True);root=parser.parse_args().root;rows=[]
for p in sorted((root/'results').glob('t1*.json')):
 if p.name.endswith('.raw.json'):continue
 r=json.loads(p.read_text());rp=p.with_suffix('.raw.json');raw=json.loads(rp.read_text() if rp.exists() else gzip.decompress(rp.with_suffix('.json.gz').read_bytes()));f=[x for x in raw['frames'] if x['t']>=r['workload']['warmup']];e=[x for x in raw['events'] if x['t']>=r['workload']['warmup']]
 assert len(f)==r['frame_count']
 assert stats([x['work_ms'] for x in f])==r['frame_work_ms']
 assert stats([x['response_ms'] for x in e if x['event']=='observe'])==r['observation_response_ms']
 assert stats([x['queue_ms'] for x in e if x['event']=='act'])==r['action_queue_ms']
 rows.append(dict(run=p.stem,source=r['source'],tool=r['tooling'],budget_ms=r['workload']['budget_ms'],warmup=r['workload']['warmup'],seconds=r['workload']['seconds'],passed=r['pass'],failed_guards=[k for k,v in r['guards'].items() if not v],frame=r['frame_work_ms'],observation=r['observation_response_ms'],action_queue=r['action_queue_ms'],observation_queue=r['observation_queue_ms'],world_hz=r['world_hz'],non_agent_ms=stats([x['work_ms']-x['agent_ms'] for x in f]),agent_ms=stats([x['agent_ms'] for x in f]),phases=r['native_phases_ms'],moving=stats([x['moving'] for x in r['censuses']]),alive_min=min(x['alive'] for x in r['censuses']),counts=r['agents']['counts'],nominal_load_fraction=r['nominal_load_fraction'],oldest_overdue_ms=r['agents']['oldest_overdue_ms'],cpu_seconds=r['cpu_seconds'],maxrss=max(x['maxrss'] for x in r['censuses']),response_bytes=r['agents']['response_bytes'],input_recording=r.get('native_recording'),window=r['hardware']['window'],driver=r.get('display_driver'),surface_size=r.get('surface_size')))
groups={}
for r in rows:
    key=r['source']['sha'];groups.setdefault(key,[]).append(r)
acceptance={key:dict(completed=sum(r['seconds']==300 for r in rs),passed=sum(r['seconds']==300 and r['passed'] for r in rs),capacity_gate_passed=sum(r['seconds']==300 and r['passed'] for r in rs)>=3) for key,rs in groups.items()}
result=dict(analyzer_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=Path(__file__).resolve().parents[2],text=True).strip(),rows=rows,acceptance_by_source=acceptance,capacity_gate_passed=any(r['capacity_gate_passed'] for r in acceptance.values()),all_metric_recomputations_passed=True)
before=root/'results/delta-before';after=root/'results/delta-after'
if (after/'compact.json').exists():
    b=json.loads((before/'compact.json').read_text());a=json.loads((after/'compact.json').read_text())
    br=json.loads(gzip.decompress((before/'rows.json.gz').read_bytes()));ar=json.loads(gzip.decompress((after/'rows.json.gz').read_bytes()))
    assert len(br)==len(ar)
    assert all({k:r[k] for k in ['tick','units','bytes','delta_sha256']}=={k:s[k] for k in ['tick','units','bytes','delta_sha256']} for r,s in zip(br,ar))
    assert all(b[k]==a[k] for k in ['trace_sha256','ticks','requests','request_hashes_sha256','final_state_sha256'])
    result['delta_comparison']=dict(before=b,after=a,all_deltas_equal=True,delta_rows=len(br),bytes_equal=True)
(root/'results/comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['rows','delta_comparison']}))
for r in rows:print(r['run'],r['frame']['p99'],r['observation']['p99'],r['action_queue']['p99'],r['failed_guards'])
