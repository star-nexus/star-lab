"""E5 preregistered paired gate; raw arrays, all ticks, 100-tick bootstrap seed42."""
import argparse,gzip,hashlib,json,zipfile
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.runs.is_file():
    archive=zipfile.ZipFile(a.runs)
    for line in archive.read('SHA256SUMS').decode().splitlines():
        checksum,name=line.split('  ',1)
        assert hashlib.sha256(archive.read(name)).hexdigest()==checksum,name
    names=sorted(n for n in archive.namelist() if n.startswith('replays/') and n.endswith('.json'))
    def read(name):return archive.read(name)
else:
    names=sorted(p.name for p in a.runs.glob('*.json'))
    def read(name):return (a.runs/name).read_bytes()
results=[]
identities=[]
for name in names:
    m=json.loads(read(name))
    assert m['source_sha']=='94913a4f836a3c106e08a1334cb81971cfd728c3'
    assert m['extension_sha256']=='838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544'
    assert m['trace_sha256']=='1f9b155129de9e43780c8885b40aba805e4c4794755fd2af70747058a7824b77'
    assert m['counts']==dict(request=40994,step=9880,presentation=9880)
    assert m['all_passed']
    assert m['stream_sha256']=='e01f2147b0fba41b27d15634c552bfb96ee84480a7628926890e57027a65b76b'
    assert m['final_state_sha256']=='d069c7173464d787c28f86120f1f173105f9f2c3f5cf959a758ab84290780dbf'
    for key in ['step_raw','paired_raw','timing_raw']:
        if key in m:
            member=str(Path(name).parent/m[key]['file'])
            data=read(member);assert hashlib.sha256(data).hexdigest()==m[key]['sha256']
            rows=json.loads(gzip.decompress(data));assert len(rows)==(4 if key=='paired_raw' else 9880)
    identities.append(dict(run=Path(name).name,metadata_sha256=hashlib.sha256(read(name)).hexdigest(),threads=m['threads'],mode=m['probe_mode'],threshold=m['min_damage_rows'],paired=m['paired'],all_passed=True))
    if not m.get('paired'):continue
    v=np.asarray(json.loads(gzip.decompress(read(str(Path(name).parent/m['paired_raw']['file'])))),dtype=float);assert v.shape==(4,9880)
    baseline=(v[0]+v[3])/2;candidate=(v[1]+v[2])/2;difference=baseline-candidate
    # Equal tick weighting; final 80-tick block retained. Bootstrap by block,
    # using block sums / resampled tick count rather than equal block means.
    sums=np.array([difference[i:i+100].sum() for i in range(0,len(difference),100)])
    counts=np.array([len(difference[i:i+100]) for i in range(0,len(difference),100)])
    indices=np.random.default_rng(42).integers(0,len(sums),(10000,len(sums)))
    ci=np.quantile(sums[indices].sum(1)/counts[indices].sum(1),[.025,.975]).tolist()
    def summary(v):
        ordered=np.sort(v);return dict(mean_ns=float(np.mean(v)),p99_ns=float(ordered[int(len(v)*.99)]),max_ns=float(np.max(v)))
    b,c=summary(np.concatenate((v[0],v[3]))),summary(np.concatenate((v[1],v[2])))
    passed=c['mean_ns']<b['mean_ns'] and c['p99_ns']<=b['p99_ns'] and ci[0]>0
    results.append(dict(run=Path(name).name,threads=m['threads'],control_mode=m['control_mode'],control_threshold=m['control_min_damage_rows'],candidate_mode=m['probe_mode'],threshold=m['min_damage_rows'],baseline=b,candidate=c,improvement_ns=float(difference.mean()),improvement_percent=float(difference.mean()/baseline.mean()*100),ci95_ns=ci,passed=bool(passed),raw_sha256=m['paired_raw']['sha256'],stream_sha256=m['stream_sha256'],final_state_sha256=m['final_state_sha256']))
confirmation=[]
for round_index in [1,2,3]:
    expected=[f'confirmation-t4-r{round_index}-{label}.json' for label in ['a1','b1','b2','a2']]
    found={Path(n).name:n for n in names}
    if not all(n in found for n in expected):continue
    arrays=[]
    for n in expected:
        m=json.loads(read(found[n]));arrays.append(json.loads(gzip.decompress(read(str(Path(found[n]).parent/m['step_raw']['file'])))))
    v=np.asarray(arrays,dtype=float);assert v.shape==(4,9880)
    difference=(v[0]+v[3]-v[1]-v[2])/2
    sums=np.array([difference[i:i+100].sum() for i in range(0,9880,100)])
    counts=np.array([len(difference[i:i+100]) for i in range(0,9880,100)])
    indices=np.random.default_rng(42).integers(0,len(sums),(10000,len(sums)))
    ci=np.quantile(sums[indices].sum(1)/counts[indices].sum(1),[.025,.975]).tolist()
    def summary(v):
        ordered=np.sort(v);return dict(mean_ns=float(np.mean(v)),p99_ns=float(ordered[int(len(v)*.99)]),max_ns=float(np.max(v)))
    b,c=summary(np.concatenate((v[0],v[3]))),summary(np.concatenate((v[1],v[2])))
    confirmation.append(dict(round=round_index,baseline=b,candidate=c,ci95_ns=ci,improvement_percent=float(difference.mean()/b['mean_ns']*100),passed=bool(c['mean_ns']<b['mean_ns'] and c['p99_ns']<=b['p99_ns'] and ci[0]>0)))
main=[r for r in results if r['threshold']==8 and r['control_threshold']==2**64-1 and r['control_mode']=='parallel']
gates={str(t):len([r for r in main if r['threads']==t])==3 and all(r['passed'] for r in main if r['threads']==t) for t in [2,4]}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(dict(method=dict(tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),numpy_version=np.__version__,block_ticks=100,bootstrap=10000,seed=42,all_ticks=9880,diagnostics=False,p99='all 19760 individual step samples per side; no pair averaging'),results=results,primary_gates=gates,identity_checks=identities,confirmation=confirmation,confirmation_gate=len(confirmation)==3 and all(r['passed'] for r in confirmation)),indent=2)+'\n')
print(json.dumps(dict(primary_gates=gates,rounds=len(results))))
