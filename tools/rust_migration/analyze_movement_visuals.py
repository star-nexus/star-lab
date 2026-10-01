"""E5 preregistered paired gate; raw arrays, all ticks, 100-tick bootstrap seed42."""
import argparse,gzip,hashlib,json
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
results=[]
for meta in sorted(a.runs.glob('*.json')):
    m=json.loads(meta.read_text())
    if not m.get('paired'):continue
    raw=meta.parent/m['paired_raw']['file'];assert hashlib.sha256(raw.read_bytes()).hexdigest()==m['paired_raw']['sha256']
    v=np.asarray(json.loads(gzip.decompress(raw.read_bytes())),dtype=float);assert v.shape==(4,9880)
    baseline=(v[0]+v[3])/2;candidate=(v[1]+v[2])/2;difference=baseline-candidate
    # Equal tick weighting; final 80-tick block retained. Bootstrap by block,
    # using block sums / resampled tick count rather than equal block means.
    sums=np.array([difference[i:i+100].sum() for i in range(0,len(difference),100)])
    counts=np.array([len(difference[i:i+100]) for i in range(0,len(difference),100)])
    indices=np.random.default_rng(42).integers(0,len(sums),(10000,len(sums)))
    ci=np.quantile(sums[indices].sum(1)/counts[indices].sum(1),[.025,.975]).tolist()
    def summary(v):
        ordered=np.sort(v);return dict(mean_ns=float(np.mean(v)),p99_ns=float(ordered[int(len(v)*.99)]),max_ns=float(np.max(v)))
    b,c=summary(baseline),summary(candidate)
    passed=c['mean_ns']<b['mean_ns'] and c['p99_ns']<=b['p99_ns'] and ci[0]>0
    results.append(dict(run=meta.name,threads=m['threads'],control_mode=m['control_mode'],control_threshold=m['control_min_damage_rows'],candidate_mode=m['probe_mode'],threshold=m['min_damage_rows'],baseline=b,candidate=c,improvement_ns=float(difference.mean()),improvement_percent=float(difference.mean()/baseline.mean()*100),ci95_ns=ci,passed=bool(passed),raw_sha256=m['paired_raw']['sha256'],stream_sha256=m['stream_sha256'],final_state_sha256=m['final_state_sha256']))
main=[r for r in results if r['threshold']==8 and r['control_threshold']==2**64-1 and r['control_mode']=='parallel']
gates={str(t):len([r for r in main if r['threads']==t])==3 and all(r['passed'] for r in main if r['threads']==t) for t in [2,4]}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(dict(method=dict(block_ticks=100,bootstrap=10000,seed=42,all_ticks=9880,diagnostics=False),results=results,primary_gates=gates),indent=2)+'\n')
print(json.dumps(dict(primary_gates=gates,rounds=len(results))))
