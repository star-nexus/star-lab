"""E6 compact/raw packaging and reproducible diagnostic aggregation."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import statistics
import subprocess
import zipfile


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def artifact(path):return dict(file='artifacts/'+path.name,bytes=path.stat().st_size,sha256=sha(path))
def packed(path,members):
    sums=[]
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(members.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,10,2,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,data);sums.append(hashlib.sha256(data).hexdigest()+'  '+name)
        z.writestr('SHA256SUMS','\n'.join(sums)+'\n')
    return artifact(path)


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,required=True);p.add_argument('--experiment',type=Path,required=True)
    p.add_argument('--stage',choices=['summary','raw','compact','checksums'],required=True);a=p.parse_args()
    r=a.runs;e=a.experiment;results=e/'results';artifacts=e/'artifacts';results.mkdir(exist_ok=True);artifacts.mkdir(exist_ok=True)
    if a.stage=='summary':
        for path in r.glob('*.json'):
            if path.name.endswith('.raw.json') or path.name.startswith('smoke'):continue
            if path.name in ('paired-analysis-recomputed.json','paired-analysis-prior-diagnostic.json'):continue
            shutil.copy2(path,results/path.name)
        meta=json.loads((r/'diagnose-complete-t1.json').read_text());d=meta['diagnosis'];n=9880
        rows=json.loads(gzip.decompress((r/meta['diagnostic_raw']['file']).read_bytes()))
        components={}
        for cls in ['HexPosition','Unit','UnitCount','MovementAnimation','MovementPoints','ActionPoints','UnitStatus','SkillPoints','ConstructionPoints']:
            components[cls]={phase:d.get('component.'+cls+'.'+phase,dict(calls=0,total_ns=0)) for phase in ['copy','normalize','construct']}
            components[cls]['write']=d.get('ecs.write.'+cls,dict(calls=0,total_ns=0))
        cost=dict(source=meta['source_sha'],diagnostic=True,ticks=n,components=components,
                  blocks={k:v for k,v in d.items() if k.startswith('apply.block.')},
                  systems={k:v for k,v in d.items() if k.startswith('display.')},
                  spatial_updates=d['spatial.update'],spatial_changes=d['spatial.changed']['calls'],
                  cache_invalidations=d['ecs.invalidate'],actual_evictions=d['ecs.eviction'],
                  query_counter_first=rows[0]['cache'],query_counter_last=rows[-1]['cache'],
                  reference_version_changes={cls:sum(v['reference_versions'][cls]!=u['reference_versions'][cls] for u,v in zip(rows,rows[1:])) for cls in rows[0]['reference_versions']},
                  ui_roster_rebuilds=d['reference.UI.roster_rebuild']['calls'],
                  dirty_entities=sum(v['units'] for v in rows),wire_bytes=sum(v['bytes'] for v in rows),
                  phase_summaries=meta['summaries'][0])
        live=json.loads((r/'live-diagnostic-baseline.raw.json').read_text());frames=[v for v in live['frames'] if v['t']>=30]
        keys=['work_ms','update_work_ms','inputs_ms','native_step_ms','delta_ms','presentation_apply_ms','display_systems_ms','core_screen_fill_ms','core_input_system_ms','core_scene_update_ms','core_render_engine_ms','core_display_present_ms']
        cost['live_diagnostic']=dict(samples=len(frames),means_ms={k:statistics.mean(v.get(k,0) for v in frames) for k in keys},
            unattributed_update_ms=statistics.mean(v['update_work_ms']-sum(v.get(k,0) for k in ['core_screen_fill_ms','core_input_system_ms','core_scene_update_ms','core_render_engine_ms','core_display_present_ms']) for v in frames),
            nested='scene includes inputs/native/delta/apply/display; update includes five core scopes; work includes agents+update')
        write(results/'cost-attribution-complete.json',cost)
        pixels={}
        for folder in r.glob('cocoa-*'):
            if not folder.is_dir():continue
            x=json.loads((folder/'comparison.json').read_text());pixels[folder.name]=x
            assert sha(folder/'pixels.json.gz')==x['pixel_sha256']
        for selected in ['plain','selected']:
            assert len({x['pixel_stream_sha256'] for k,x in pixels.items() if k.endswith(selected)})==1
        write(results/'window-contracts.json',pixels)
        retention=json.loads((r/'retention.json').read_text());assert retention['all_passed']
        write(results/'validation.json',dict(python_tests=2385,log='raw/full-tests.log',source='0a297a868f589dd49eb514f3c73402142df05e2c',
            complete_correctness_threads=[1,4],pixel_checks_each=29640,cocoa_frames=2880,
            retention=retention,analyzer_recomputed_identically=True,ordinary_apply_unchanged=True,native_code_unchanged=True,
            no_new_rust_build=True,live_comparison_all_six_pass=False,production_enabled=False,capacity_claim=False))
        # Full regenerated JSONL is independently re-read, without retaining frames.
        trace=json.loads(gzip.decompress((r/'rust-300-r3.trace.json.gz').read_bytes()))
        ops=[v for v in trace['entries'] if v['kind']=='presentation'];total=0;dirty=0
        with gzip.open(r/meta['regenerated_deltas']['file'],'rb') as f:
            for i,line in enumerate(f):
                delta=json.loads(line);total+=len(line)-1;dirty+=len(delta['units'])
                digest=hashlib.sha256(json.dumps(delta['events'],sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
                assert digest==ops[i]['events_sha256']
        assert i+1==9880 and total==cost['wire_bytes'] and dirty==cost['dirty_entities']
        write(results/'regenerated-delta-verification.json',dict(rows=i+1,wire_bytes=total,dirty_entities=dirty,events_match=True,sha256=meta['regenerated_deltas']['sha256']))
    elif a.stage=='raw':
        members={}
        excluded={'rust-300-r3.trace.json.gz','rust-300-r3.initial.json.gz','correctness-t1-fixed.log','paired-analysis-recomputed.json','presentation-cache-source.bundle'}
        for path in r.rglob('*'):
            if not path.is_file() or path.name in excluded or path.name.startswith(('smoke','additional-tests.py')) or path.name.endswith('.deltas.jsonl.gz'):continue
            if path.suffix in ['.json','.gz','.log','.png']:members['raw/'+str(path.relative_to(r))]=path.read_bytes()
        lab=Path(__file__).resolve().parents[2]
        for commit in ['0f4a2c2','72445ab','a452abc']:
            names=subprocess.check_output(['git','-C',str(lab),'ls-tree','-r','--name-only',commit,'tools'],text=True).splitlines()
            for name in names:
                if name.endswith('.py'):members['tooling/'+commit+'/'+name]=subprocess.check_output(['git','-C',str(lab),'show',commit+':'+name])
        e5=lab/'experiments/2026-10-rust-movement-visuals-parallel/artifacts/movement-visuals-raw.zip'
        assert sha(e5)=='a3593da48438e7c96c9e9c003b8374d4d8b393d45a806d1a2582a2d12e3c4f07'
        wheel='wheels/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl'
        with zipfile.ZipFile(e5) as z:members[wheel]=z.read(wheel)
        assert hashlib.sha256(members[wheel]).hexdigest()=='2a853d7f8d1ca9701d7ffcb39522d2c25d0824562d8ca436424f8c790cfd0e30'
        raw=packed(artifacts/'presentation-cache-raw.zip',members)
        shutil.copy2(r/'diagnose-complete-t1.deltas.jsonl.gz',artifacts/'presentation-cache-deltas.jsonl.gz')
        shutil.copy2(r/'presentation-cache-source.bundle',artifacts/'presentation-cache-source.bundle')
        write(results/'artifact-index.json',dict(raw=raw,regenerated_deltas=artifact(artifacts/'presentation-cache-deltas.jsonl.gz'),source_bundle=artifact(artifacts/'presentation-cache-source.bundle'),wheel_member=wheel,wheel_sha256=hashlib.sha256(members[wheel]).hexdigest(),raw_members={k:dict(bytes=len(v),sha256=hashlib.sha256(v).hexdigest()) for k,v in sorted(members.items())}))
    elif a.stage=='compact':
        members={p.name:p.read_bytes() for p in e.glob('*.md')}
        for path in results.glob('*.json'):members['results/'+path.name]=path.read_bytes()
        manifest=json.loads((e/'manifest.yaml').read_text());manifest.pop('compact',None);members['manifest.json']=json.dumps(manifest,indent=2).encode()
        compact=packed(artifacts/'presentation-cache-compact.zip',members);manifest['compact']=compact;write(e/'manifest.yaml',manifest)
    else:
        paths=[p for p in e.rglob('*') if p.is_file() and p.name!='SHA256SUMS']
        (artifacts/'SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(e))+'\n' for p in sorted(paths)))


if __name__=='__main__':main()
