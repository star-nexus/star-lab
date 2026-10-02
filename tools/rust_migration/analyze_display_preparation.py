"""E7 fixed complete-display, chain and total gates, preserving every tick."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np


def analyze(path):
    meta=json.loads(path.read_text())
    assert meta['task']=='paired' and meta['formal'] and meta['all_passed'] and not meta['diagnostic']
    data=(path.parent/meta['raw']['file']).read_bytes()
    assert hashlib.sha256(data).hexdigest()==meta['raw']['sha256']
    rows=json.loads(gzip.decompress(data))
    assert len(rows)==4 and all(len(side)==9880 for side in rows)
    metrics={}
    for key in ('render_ns','chain_ns','total_ns','display_ns','submit_ns','apply_ns'):
        raw=np.array([[r[key] for r in side] for side in rows],dtype=float)
        b=(raw[0]+raw[3])/2;c=(raw[1]+raw[2])/2;diff=b-c
        sums=np.array([diff[i:i+100].sum() for i in range(0,9880,100)])
        counts=np.array([len(diff[i:i+100]) for i in range(0,9880,100)])
        chosen=np.random.default_rng(42).integers(0,len(sums),(10000,len(sums)))
        ci=np.quantile(sums[chosen].sum(1)/counts[chosen].sum(1),[.025,.975]).tolist()
        def stats(v):
            v=np.sort(v)
            return dict(samples=len(v),mean_ns=float(v.mean()),p99_ns=float(v[int(len(v)*.99)]),max_ns=float(v[-1]))
        baseline=stats(np.concatenate((raw[0],raw[3])));candidate=stats(np.concatenate((raw[1],raw[2])))
        improvement=float(diff.mean()/b.mean()*100)
        passed=candidate['mean_ns']<baseline['mean_ns'] and candidate['p99_ns']<=baseline['p99_ns'] and ci[0]>0
        if key=='render_ns':passed=passed and improvement>=5
        metrics[key]=dict(baseline=baseline,candidate=candidate,improvement_percent=improvement,ci95_ns=ci,passed=bool(passed))
    return dict(run=path.name,consumer=meta['consumer'],threads=meta['threads'],script=meta['display_script'],metrics=metrics,
                passed=all(metrics[k]['passed'] for k in ('render_ns','chain_ns','total_ns')),raw_sha256=meta['raw']['sha256'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    results=[]
    for path in sorted(a.runs.glob('*.json')):
        meta=json.loads(path.read_text())
        if isinstance(meta,dict) and meta.get('task')=='paired':results.append(analyze(path))
    gates={f'{consumer}/native{threads}/{script}':len(group)==3 and all(r['passed'] for r in group)
           for consumer in ('baseline','reuse_typed') for threads in (1,4) for script in ('static','exercise')
           for group in [[r for r in results if (r['consumer'],r['threads'],r['script'])==(consumer,threads,script)]]}
    result=dict(method=dict(block_ticks=100,bootstrap=10000,seed=42,all_ticks=9880,render_min_improvement_percent=5,
                p99='19760 original samples per side',diagnostic_for_speed=False,numpy=np.__version__,
                tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),results=results,gates=gates)
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(gates))
if __name__=='__main__':main()
