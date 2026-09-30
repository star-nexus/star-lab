"""Re-audit E2 compact/raw evidence, including after only canonical archives remain.

This recomputes recorded metrics; it is not a benchmark and must run after live gates.
"""
import argparse,gzip,hashlib,json,statistics,zipfile
from pathlib import Path

def sha(body):return hashlib.sha256(body).hexdigest()
def summary(values):
    ordered=sorted(values)
    return dict(samples=len(values),mean_ns=sum(values)/len(values),p99_ns=ordered[min(len(values)-1,int(len(values)*.99))],max_ns=max(values))
def micro_summary(values):
    ordered=sorted(values)
    return dict(samples=len(values),mean_ns=sum(values)/len(values),median_ns=ordered[len(values)//2],p99_ns=ordered[min(len(values)-1,int(len(values)*.99))])
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);a=p.parse_args();root=a.root.resolve();results=root/'results'
    archive_cache={}
    packages=json.loads((results/'packages.json').read_text()) if (results/'packages.json').exists() else None
    def body(relative):
        path=root/relative
        if path.exists() and (packages is None or relative not in packages['files']):return path.read_bytes()
        assert packages is not None,relative
        entry=packages['files'][relative]
        archive=root/packages['archive']['file']
        if 'zip' not in archive_cache:
            assert sha(archive.read_bytes())==packages['archive']['sha256']
            archive_cache['zip']=zipfile.ZipFile(archive)
        b=archive_cache['zip'].read(entry['member'])
        assert len(b)==entry['bytes'] and sha(b)==entry['sha256'],relative
        return b
    def raw(desc,prefix='results/'):
        b=body(prefix+desc.get('file',desc.get('path','')))
        assert sha(b)==desc['sha256'] and len(b)==desc.get('bytes',desc.get('size'))
        return b
    reference=json.loads((results/'baseline-t1.json').read_text());replays=[];profiles={}
    for file in sorted(results.glob('*.json')):
        r=json.loads(file.read_text())
        if 'stream_sha256' not in r:continue
        assert r['all_passed'] and r['counts']==dict(request=40994,step=9880,presentation=9880)
        for key in ['stream_sha256','final_state_sha256','trace_sha256','initial_sha256']:assert r[key]==reference[key],(file.name,key)
        samples=json.loads(gzip.decompress(raw(r['step_raw'])));assert len(samples)==9880 and summary(samples)==r['ordinary_step_summary']
        if 'timing_raw' in r:
            timings=json.loads(gzip.decompress(raw(r['timing_raw'])));assert len(timings)==9880
            phases={};stats={}
            for t in timings:
                for k,v in t['phases_ns'].items():phases.setdefault(k,[]).append(v)
                for k,v in t['statistics'].items():stats.setdefault(k,[]).append(v)
            assert {k:summary(v) for k,v in phases.items()}==r['phase_summary']
            assert {k:summary(v) for k,v in stats.items()}==r['statistics_summary']
            nonempty=[t['statistics'] for t in timings if t['statistics']['observation_rows']>0]
            profiles[file.stem]=dict(nonempty_ticks=len(nonempty),mean_candidate_rows=statistics.mean(t['observation_rows'] for t in nonempty),mean_nonempty_ns={k:statistics.mean(t[k] for t in nonempty) for k in nonempty[0] if k.endswith('_ns')},parallel_batches=sum(t.get('parallel_batches',0) for t in nonempty),max_worker_threads=max(t.get('worker_threads',0) for t in nonempty),max_jobs=max(t.get('jobs',0) for t in nonempty))
        replays.append(dict(run=file.stem,source_sha=r['source_sha'],kernel_source_sha=r['kernel_source_sha'],extension_sha256=r['extension_sha256'],mode=r['mode'],threads=r['threads'],min_rows=r.get('min_rows'),step=r['ordinary_step_summary']))
    assert len(replays)==20,len(replays)
    canonical=raw(json.loads((results/'baseline-contracts-t1.json').read_text())['raw']);contracts=[]
    for file in sorted(results.glob('*contracts-t*.json')):
        r=json.loads(file.read_text());assert r['all_passed'] and r['cases']==36 and r['steps']==174
        assert raw(r['raw'])==canonical,('complete serialized exports/deltas/errors/resets',file.name)
        assert r['input_sha256']=='11b33c95ad2b22e1842e24e0d0ce6b8c24e25bf19f05ae0761b6ca7ca2ffcf75'
        contracts.append(dict(run=file.stem,threads=r['threads'],min_rows=r['min_rows'],extension_sha256=r['extension_sha256']))
    assert len(contracts)==8,len(contracts)
    pairs=[]
    for threads in [2,4]:
        for trial in [1,2,3]:
            before=json.loads((results/f'net-t{threads}-inline-r{trial}.json').read_text());after=json.loads((results/f'net-t{threads}-m128-r{trial}.json').read_text())
            for key in ['source_sha','extension_sha256','trace_sha256','initial_sha256','threads','mode','counts']:assert before[key]==after[key]
            assert before['mode']=='plain' and before['min_rows']==1<<60 and after['min_rows']==128
            b=before['ordinary_step_summary'];f=after['ordinary_step_summary'];gain=1-f['mean_ns']/b['mean_ns'];p99gain=1-f['p99_ns']/b['p99_ns']
            assert gain>0 and p99gain>0
            pairs.append(dict(threads=threads,trial=trial,inline=b,min128=f,mean_reduction_fraction=gain,p99_reduction_fraction=p99gain))
    micro=json.loads((results/'crossover.json').read_text());micro_raw=json.loads(gzip.decompress(raw(micro['raw'])));assert micro['all_passed'] and len(micro_raw)==len(micro['rows'])==16
    for r,t in zip(micro['rows'],micro_raw):
        assert (r['rows'],r['threads'])==(t['rows'],t['threads'])
        assert r['full_state_delta_equal']
        for policy in ['inline','forced']:
            assert len(t['samples_ns'][policy])==200 and micro_summary(t['samples_ns'][policy])==r[policy]
            assert r['metrics'][policy]['observation_rows']==r['rows']
            assert r['metrics'][policy]['parallel_batches']==int(policy=='forced' and r['rows']>0)
    for threads in [2,4]:
        rows=[r for r in micro['rows'] if r['threads']==threads and r['rows']>0]
        assert all(r['forced']['mean_ns']>r['inline']['mean_ns'] for r in rows if r['rows']<=32)
        assert min(r['rows'] for r in rows if r['forced']['mean_ns']<r['inline']['mean_ns'])==64
        assert all(r['forced']['mean_ns']<r['inline']['mean_ns'] for r in rows if r['rows']>=128)
    validation=json.loads((results/'validation.json').read_text());assert validation['all_passed'] and validation['python_tests']==2291 and validation['rust_tests']==4
    for r in validation['checks']:
        b=body(r['log']);assert sha(b)==r['sha256'] and len(b)==r['bytes'] and r['exit_code']==0
    # Capacity arithmetic was independently recomputed by analyze_statistics_capacity.
    capacity=json.loads((results/'capacity-comparison.json').read_text());assert capacity['all_raw_recomputations_passed'] and capacity['rust_long_runs']==3 and capacity['declared_native_threads']==4
    for r in capacity['rows']:
        live=json.loads((results/f"{r['run']}.json").read_text());raw(live['raw'])
        for desc in live['native_recording'].values():
            if isinstance(desc,dict) and 'sha256' in desc:raw(desc)
    result=dict(all_raw_recomputations_passed=True,full_trace_replays=len(replays),complete_matrix_variants=len(contracts),reference_stream_sha256=reference['stream_sha256'],reference_final_state_sha256=reference['final_state_sha256'],matrix_full_bytes_sha256=sha(canonical),profiles=profiles,replay_rows=replays,contracts=contracts,controlled_net_pairs=pairs,crossover_measured_mean_positive_rows=64,operational_min_rows=128,capacity_gate_passed=capacity['rust_long_gate_passed'],python_tests=2291,rust_tests=4,scope='Whole-step controls isolate dispatch in same7ab binary, not old-vs-new total transformation. No frame speedup, universal crossover or5000Agent claim. No samples/tails removed.')
    (results/'compute-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['profiles','replay_rows','contracts','controlled_net_pairs']}))
if __name__=='__main__':main()
