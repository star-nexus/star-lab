"""Opt-in handler phase attribution with realistic five-Unit subsets; no frame claim."""
import argparse, hashlib, json, lzma, os, platform, statistics, subprocess, sys, time
from pathlib import Path
from kernel_attack_candidates_probe import digest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    lab=Path(__file__).resolve().parents[2];src=a.source.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    os.chdir(src);sys.path.insert(0,str(src));os.environ['SDL_VIDEODRIVER']='dummy'
    from star_native import NativeRuntime,API_VERSION,_native
    def git(root,*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
    scenarios=[];inputs=[]
    for kind,path in [('catalog',lab/'experiments/2026-09-rust-kernel-catalog/results/after/raw.json.xz'),('targets',lab/'experiments/2026-09-rust-kernel-targets/results/after/raw.json.xz')]:
        blob=path.read_bytes();inputs.append(dict(path=str(path.relative_to(lab)),sha256=hashlib.sha256(blob).hexdigest()))
        for case in json.loads(lzma.decompress(blob)):
            s=case['summary']
            if kind=='catalog' and s['radius']==45 and s['fog'] in ('local','disabled'):scenarios.append((f"terrain-{s['fog']}",case))
            if kind=='targets' and s['units']==5000 and s['radius']==3 and s['ap']==2:scenarios.append(('units-5000',case))
    rows=[];raw=[]
    for name,case in scenarios:
        initial=case['initial'];units=[e for e in initial['entities'] if 'Unit' in e['components']]
        for e in units:
            m=e['components'].get('MovementPoints')
            if m is not None:m.update(current_mp=6,max_mp=6,base_mp=6)
        if name=='units-5000':
            cells=sorted((e['components']['HexPosition']['col'],e['components']['HexPosition']['row']) for e in initial['entities'] if 'Terrain' in e['components'])
            for i,e in enumerate(units):
                col,row=cells[i*len(cells)//len(units)];e['components']['HexPosition'].update(col=col,row=row)
        wire=json.dumps(initial)
        selected=case['parameters']['unit_ids']
        variants=[('single5',[selected[:5]])]
        if name=='units-5000':variants += [('single100',[selected]),('repeat100',[selected]*8),('disjoint5',[selected[i*5:(i+1)*5] for i in range(8)])]
        for threads in (1,2,4):
            for label,subsets in variants:
                params=[dict(faction='wei',unit_ids=ids,agent_id=f'agent-{i}') for i,ids in enumerate(subsets)]
                request=json.dumps(params);n=NativeRuntime(wire,threads)
                try:
                    expected=json.loads(n._observation_probe_json(request));samples=[];profile_samples=[];phase=[]
                    has_profile=hasattr(n,'_observation_profile_json')
                    for i in range(6):
                        # Alternate order to avoid systematically timing one on a warmer cache.
                        operations=['ordinary','profile'] if i%2==0 else ['profile','ordinary']
                        for op in operations:
                            if op=='profile' and not has_profile:continue
                            start=time.perf_counter_ns()
                            if op=='ordinary':encoded=n._observation_probe_json(request)
                            else:encoded,timing=n._observation_profile_json(request)
                            elapsed=(time.perf_counter_ns()-start)/1e6
                            report=json.loads(encoded);assert report['results']==expected['results']
                            assert {k:v for k,v in report['metrics'].items() if k!='panel_worker_threads'}=={k:v for k,v in expected['metrics'].items() if k!='panel_worker_threads'}
                            if i:
                                if op=='ordinary':samples.append(elapsed)
                                else:profile_samples.append(elapsed);phase.append(json.loads(timing))
                    final=json.loads(n.export_state_json());assert final==initial
                    phases={}
                    if phase:
                        for k in ('parse_ns','batch_ns','final_encode_ns','drop_ns','native_ns'):phases[k]=statistics.median(t[k] for t in phase)/1e6
                        for k in phase[0]['profile']:phases[k]=statistics.median(t['profile'][k] for t in phase)/1e6
                    row=dict(scenario=name,variant=label,threads=threads,requests=len(params),distinct_panels=len(set(x for ids in subsets for x in ids)),initial_sha256=digest(initial),final_sha256=digest(final),agent_response_sha256=digest(expected['results']),metrics=expected['metrics'],bytes=len(encoded.encode()),reachable_cells=sum(len(u['reachable']) for u in expected['results'][0]['units']),samples_ms=samples,profile_samples_ms=profile_samples,median_ms=statistics.median(samples),phase_medians_ms=phases)
                    rows.append(row);raw.append(dict(summary=row,parameters=params,response=expected,phase_samples=phase))
                finally:n.close()
    b=lzma.compress(json.dumps(raw,separators=(',',':')).encode());(out/'raw.json.xz').write_bytes(b)
    r=dict(source_sha=git(src,'rev-parse','HEAD'),source_dirty=git(src,'status','--porcelain'),tool_sha=git(lab,'rev-parse','HEAD'),api=API_VERSION,extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),inputs=inputs,rows=rows,raw_sha256=hashlib.sha256(b).hexdigest(),raw_bytes=len(b),python=sys.version,platform=platform.platform(),all_guards_passed=True,capacity_claim=False,timing='ordinary handler call including conversion to Python string, no decode; optional profile separately;1warmup+5samples; no reset or world writes between calls')
    assert not r['source_dirty'];(out/'compact.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(rows=len(rows),guards=True,source=r['source_sha'])))

if __name__=='__main__':main()
