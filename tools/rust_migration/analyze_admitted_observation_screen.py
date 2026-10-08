"""Bounded E8 screen, explicitly distinct from full-host formal acceptance."""
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np

def analyze(path,monitor_path):
    path=Path(path);meta=json.loads(path.read_text());guard=json.loads(Path(monitor_path).read_text())
    assert meta['passed'] and not meta['smoke'] and meta['counts']['ticks']==2617
    payload=(path.parent/meta['raw']['file']).read_bytes()
    assert hashlib.sha256(payload).hexdigest()==meta['raw']['sha256']
    raw=json.loads(gzip.decompress(payload));assert len(raw['queries'])==3010 and len(raw['ticks'])==2617
    metrics={}
    for key,rows,field in [('query_service',raw['queries'],'service_ns'),('selected_total_work',raw['ticks'],'total_ns')]:
        values=np.asarray([r[field] for r in rows],dtype=np.float64)
        assert values.shape==(len(rows),4)
        base=(values[:,0]+values[:,3])/2;candidate=(values[:,1]+values[:,2])/2;diff=base-candidate
        blocks=defaultdict(lambda:[0.,0])
        for row,improvement in zip(rows,diff):
            block=max(0,row['tick']-1)//100;blocks[block][0]+=float(improvement);blocks[block][1]+=1
        sums=np.array([blocks[i][0] for i in sorted(blocks)]);counts=np.array([blocks[i][1] for i in sorted(blocks)])
        chosen=np.random.default_rng(42).integers(0,len(sums),(10000,len(sums)))
        ci=np.quantile(sums[chosen].sum(1)/counts[chosen].sum(1),[.025,.975]).tolist()
        def stats(v):
            ordered=np.sort(v);return dict(samples=len(v),mean_ns=float(v.mean()),p99_ns=float(ordered[int(np.ceil(.99*len(v)))-1]),max_ns=float(ordered[-1]))
        b=stats(np.concatenate([values[:,0],values[:,3]]));c=stats(np.concatenate([values[:,1],values[:,2]]))
        improvement=float(diff.mean()/base.mean()*100)
        passed=improvement>0 and ci[0]>0 and c['p99_ns']<=b['p99_ns']
        if key=='query_service':passed=passed and improvement>=5
        metrics[key]=dict(baseline=b,candidate=c,improvement_percent=improvement,ci95_improvement_ns=ci,passed=bool(passed),
                          block_counts=counts.tolist())
    resource_valid=(guard['status']=='passed' and guard['child_exit']==0 and not guard['events'] and
        guard['samples'] and all(v['pressure']==1 for v in guard['samples']) and not guard['automatic_pause'] and not guard['automatic_termination'])
    positive=all(v['passed'] for v in metrics.values())
    return dict(stage='P3 single moving-world service screen',timing_resource_valid=bool(resource_valid),metrics=metrics,
        screening_positive=bool(resource_valid and positive),
        decision='worth formal full-host investigation' if resource_valid and positive else 'inconclusive resource interference' if not resource_valid else 'stop this candidate; screen lacks required benefit',
        method=dict(block_ticks=100,bootstrap=10000,seed=42,partial_block_actual_counts=True,all_ticks=2617,all_queries=3010,
            query_min_improvement_percent=5,p99='all two original side samples; nearest rank',all_warm_and_tails_retained=True),
        scope=meta['scope'],formal_full_host_acceptance=False,default_adoption=False,automatic_retry=False)
