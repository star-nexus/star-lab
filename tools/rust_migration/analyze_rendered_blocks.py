"""Derive 30-second phase and payload trends from retained admitted raw samples."""
import argparse,gzip,json,sys
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,required=True);root=parser.parse_args().root;sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from p3_local_agents import stats
rows={}
for p in sorted((root/'results').glob('t1*.json')):
 if p.name.endswith('.raw.json'):continue
 r=json.loads(p.read_text());rp=p.with_suffix('.raw.json');x=json.loads(rp.read_text() if rp.exists() else gzip.decompress(rp.with_suffix('.json.gz').read_bytes()))
 blocks=[]
 for offset in range(0,int(r['workload']['seconds']),30):
  start=r['workload']['warmup']+offset;stop=start+30;fs=[f for f in x['frames'] if start<=f['t']<stop];es=[e for e in x['events'] if start<=e['t']<stop and e['event']=='observe']
  blocks.append(dict(start=start,end=stop,frame_ms=stats([f['work_ms'] for f in fs]),phases={k:stats([f[k] for f in fs]) for k in ['agent_ms','native_step_ms','delta_ms','presentation_apply_ms','display_systems_ms']},observation={k:stats([e[k] for e in es]) for k in ['service_ms','bytes','terrain','enemies']},residual_ms=stats([f['work_ms']-sum(f[k] for k in ['agent_ms','native_step_ms','delta_ms','presentation_apply_ms','display_systems_ms','inputs_ms']) for f in fs])))
 rows[p.stem]=blocks
(root/'results/blocks.json').write_text(json.dumps(rows,indent=2)+'\n')
