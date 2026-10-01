"""E6 preregistered mean/P99/block-bootstrap gates; all 9880 raw ticks retained."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np


def analyze(meta,path):
    data=(path.parent/meta['raw']['file']).read_bytes()
    assert hashlib.sha256(data).hexdigest()==meta['raw']['sha256']
    rows=json.loads(gzip.decompress(data))
    assert len(rows)==4 and all(len(v)==9880 for v in rows)
    def metric(key):
        raw=np.array([[r[key] for r in side] for side in rows],dtype=float)
        b=(raw[0]+raw[3])/2;c=(raw[1]+raw[2])/2;diff=b-c
        sums=np.array([diff[i:i+100].sum() for i in range(0,9880,100)])
        counts=np.array([len(diff[i:i+100]) for i in range(0,9880,100)])
        chosen=np.random.default_rng(42).integers(0,len(sums),(10000,len(sums)))
        ci=np.quantile(sums[chosen].sum(1)/counts[chosen].sum(1),[.025,.975]).tolist()
        def stats(v):
            v=np.sort(v);return dict(samples=len(v),mean_ns=float(v.mean()),p99_ns=float(v[int(len(v)*.99)]),max_ns=float(v[-1]))
        baseline=stats(np.concatenate((raw[0],raw[3])));candidate=stats(np.concatenate((raw[1],raw[2])))
        improvement=float(diff.mean()/b.mean()*100)
        passed=candidate['mean_ns']<baseline['mean_ns'] and candidate['p99_ns']<=baseline['p99_ns'] and ci[0]>0
        if key=='apply_ns':passed=passed and improvement>=10.
        return dict(baseline=baseline,candidate=candidate,improvement_percent=improvement,ci95_ns=ci,passed=bool(passed))
    metrics={key:metric(key) for key in ['apply_ns','chain_ns','total_ns','display_ns','submit_ns']}
    return dict(run=path.name,candidate=meta['modes'][1],threads=meta['threads'],metrics=metrics,
                passed=all(metrics[k]['passed'] for k in ['apply_ns','chain_ns','total_ns']),raw_sha256=meta['raw']['sha256'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    results=[];diagnostics=[]
    for path in sorted(a.runs.glob('*.json')):
        meta=json.loads(path.read_text())
        if not isinstance(meta,dict) or meta.get('task') not in ('diagnose','paired','correctness','single'):continue
        if not meta['formal']:continue
        assert meta['all_passed'] and meta['counts']==dict(request=40994,step=9880,presentation=9880)
        assert meta['extension_sha256']=='838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544'
        assert meta['trace_sha256']=='1f9b155129de9e43780c8885b40aba805e4c4794755fd2af70747058a7824b77'
        assert meta['stream_sha256']=='e01f2147b0fba41b27d15634c552bfb96ee84480a7628926890e57027a65b76b'
        if meta['task']=='paired':results.append(analyze(meta,path))
        elif meta['task']=='diagnose':diagnostics.append(dict(run=path.name,diagnosis=meta['diagnosis'],summaries=meta['summaries']))
    gates={}
    for mode in ['reuse_constructed','reuse_typed']:
        gates[mode]={}
        for threads in (1,4):
            group=[r for r in results if r['candidate']==mode and r['threads']==threads]
            gates[mode][str(threads)]=len(group)==3 and all(r['passed'] for r in group)
    result=dict(method=dict(block_ticks=100,bootstrap=10000,seed=42,numpy=np.__version__,all_ticks=9880,
        apply_min_improvement_percent=10,p99='19760 original samples per side, no averaging',diagnostic_for_speed=False,
        tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),results=results,gates=gates,diagnostics=diagnostics)
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(gates))

if __name__=='__main__':main()
