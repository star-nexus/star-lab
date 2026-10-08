"""Independent raw integrity and screen arithmetic check; no kernel re-run."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import zipfile
import numpy as np


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runs',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists();reports=[];checked=[]
    for sub,meta_name,analysis_name,guard_name in [('', 'scan.json','scan-analysis.json','scan.monitor.json'),('census','screen.json','analysis.json','screen.monitor.json')]:
        root=a.runs/sub;meta=json.loads((root/meta_name).read_text());result=json.loads((root/analysis_name).read_text());guard=json.loads((root/guard_name).read_text())
        raw_path=root/meta['raw']['file'];assert sha(raw_path)==meta['raw']['sha256'];raw=json.loads(gzip.decompress(raw_path.read_bytes()))
        assert meta['passed'] and meta['counts']==dict(requests=12148,operations=17382,ticks=2617,presentation=2617,queries=3010)
        assert [r['tick'] for r in raw['ticks']]==list(range(1,2618));assert len(raw['queries'])==3010
        assert len(set(meta['commands_sha256']))==1
        assert guard['status']=='passed' and guard['child_exit']==0 and not guard['events'] and all(s['pressure']==1 for s in guard['samples'])
        assert not guard['automatic_pause'] and not guard['automatic_termination']
        for side in range(4):
            assert sum(r['phases'][side]['open_ns']>0 for r in raw['queries'])==750
            assert sum(r['phases'][side]['drop_ns']>0 for r in raw['queries'])==750
            assert all(sum(r['phases'][side].values())==r['service_ns'][side] and min(r['phases'][side].values())>=0 for r in raw['queries'])
        for key,rows,field in [('query_service',raw['queries'],'service_ns'),('selected_total_work',raw['ticks'],'total_ns')]:
            matrix=np.array([r[field] for r in rows],dtype=float);assert np.isfinite(matrix).all() and (matrix>=0).all()
            difference=matrix[:,[0,3]].mean(1)-matrix[:,[1,2]].mean(1)
            group=np.array([(r['tick']-1)//100 for r in rows]);weight=np.bincount(group,minlength=27);summed=np.bincount(group,weights=difference,minlength=27)
            draw=np.random.default_rng(42).integers(0,27,size=(10000,27));ci=np.quantile(summed[draw].sum(1)/weight[draw].sum(1),[.025,.975])
            expected=result['metrics'][key]
            assert np.allclose(ci,expected['ci95_improvement_ns'],rtol=1e-10,atol=1e-6)
            assert np.isclose(difference.mean()/matrix[:,[0,3]].mean()*100,expected['improvement_percent'])
            for label,indices in [('baseline',[0,3]),('candidate',[1,2])]:
                v=np.sort(matrix[:,indices].ravel());stats=expected[label]
                assert v.size==stats['samples'] and v[-1]==stats['max_ns'] and v[int(np.ceil(v.size*.99))-1]==stats['p99_ns']
                assert np.isclose(v.mean(),stats['mean_ns'])
            service_gate=expected['improvement_percent']>=2 if key=='query_service' else expected['improvement_percent']>0
            p99=expected['candidate']['p99_ns']<=expected['baseline']['p99_ns'] and max(expected['sides'][i]['p99_ns'] for i in [1,2])<=max(expected['sides'][i]['p99_ns'] for i in [0,3])
            assert expected['passed']==bool(service_gate and ci[0]>0 and p99)
        assert result['screening_positive']==all(v['passed'] for v in result['metrics'].values())
        identity=json.loads((root/'extension-identity.json').read_text())
        wheel=next((root/'wheels').glob('*.whl'));assert sha(wheel)==identity['wheel_sha256']
        with zipfile.ZipFile(wheel) as z:
            members=[n for n in z.namelist() if n.startswith('star_native/') and n.endswith('.so')];assert len(members)==1
            binary=z.read(members[0]);assert hashlib.sha256(binary).hexdigest()==meta['extension_sha256']==identity['extension_sha256']
            checked.append(dict(path=str(wheel)+'::'+members[0],sha256=meta['extension_sha256'],bytes=len(binary)))
        for f in [root/meta_name,root/analysis_name,root/guard_name,raw_path,wheel]:checked.append(dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size))
        reports.append(dict(factor='shared entity lookup' if not sub else 'borrowed census keys',passed=True,queries=3010,ticks=2617,scopes_per_side=750,screening_positive=result['screening_positive']))
    d=json.loads((a.runs/'diagnosis.json').read_text());assert d['passed'];assert sha(a.runs/d['raw']['file'])==d['raw']['sha256']
    prof=json.loads((a.runs/'census/profile.json').read_text());assert prof['passed'] and prof['diagnostic_only'] and not prof['performance_claim']
    a.output.write_text(json.dumps(dict(passed=True,reports=reports,files=checked,profile_rows=len(prof['rows']),diagnostic_queries=d['counts']['queries'],
        method='Independent reconstruction of 27-block weighted bootstrap and nearest-rank raw quantiles; no kernel replay',tool_sha256=sha(__file__)),indent=2)+'\n')
    print(json.dumps(dict(passed=True,reports=reports,hashes=len(checked))))


if __name__=='__main__': main()
