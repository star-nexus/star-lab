"""E6 sequential execution, exact command journal and conditional stop gates."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--source-sha',required=True)
    p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=a.output.resolve();root.mkdir(parents=True,exist_ok=True);lab=Path(__file__).resolve().parents[2];python=a.source/'.venv/bin/python'
    commands=[];env=os.environ.copy();env.update(PYTHONHASHSEED='0',PYTHONUNBUFFERED='1',PYGAME_HIDE_SUPPORT_PROMPT='1')
    def run(name,args,expected):
        cmd=[str(python)]+[str(v) for v in args]
        record=dict(name=name,argv=cmd,environment={k:env.get(k) for k in ('PYTHONHASHSEED','PYTHONUNBUFFERED','HEADLESS','SDL_VIDEODRIVER','PYGAME_HIDE_SUPPORT_PROMPT')},reused=expected.exists())
        commands.append(record);(root/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
        if not expected.exists():
            print(json.dumps(dict(start=name)),flush=True)
            with (root/(name+'.log')).open('w') as log:subprocess.run(cmd,env=env,cwd=a.source,stdout=log,stderr=subprocess.STDOUT,check=True)
        print(json.dumps(dict(completed=name)),flush=True)
    common=[lab/'tools/rust_migration/presentation_cache_probe.py','--source',a.source,'--source-sha',a.source_sha,'--trace',a.inputs/'rust-300-r3.trace.json.gz']
    for t in [1,4]:
        name=f'correctness-t{t}';out=root/(name+'.json')
        run(name,common+['--output',out,'--task','correctness','--script','exercise','--overscan-clock','items','--threads',t],out)
        assert json.loads(out.read_text())['all_passed']
    for mode in ['baseline','reuse_constructed','reuse_typed']:
        for selected in [False,True]:
            name=f'cocoa-{mode}-'+('selected' if selected else 'plain');folder=root/name
            run(name,[lab/'tools/rust_migration/presentation_cache_window_contracts.py','--source',a.source,'--output',folder,'--mode',mode]+(['--selection'] if selected else []),folder/'comparison.json')
            comparison=json.loads((folder/'comparison.json').read_text())
            if mode!='baseline':
                ref=json.loads((root/('cocoa-baseline-'+('selected' if selected else 'plain'))/'comparison.json').read_text())
                assert comparison['pixel_stream_sha256']==ref['pixel_stream_sha256'],name
    for t in [1,4]:
        for r in [1,2,3]:
            for mode in ['reuse_constructed','reuse_typed']:
                name=f'paired-{mode}-t{t}-r{r}';out=root/(name+'.json')
                run(name,common+['--output',out,'--task','paired','--candidate',mode,'--threads',t],out)
    analysis=root/'paired-analysis.json'
    run('analyze-paired',[lab/'tools/rust_migration/analyze_presentation_cache.py','--runs',root,'--output',analysis],analysis)
    gates=json.loads(analysis.read_text())['gates']
    chosen=next((m for m in ['reuse_typed','reuse_constructed'] if gates[m]['4']),None)
    decision=dict(gates=gates,selected=chosen,production_enabled=False,capacity_claim=False)
    if chosen is None:
        decision.update(status='negative_complete',reason='No native4 mode passes all three mean/P99/CI gates; no confirmation/live')
        (root/'decision.json').write_text(json.dumps(decision,indent=2)+'\n');return
    for label,mode in [('a1','baseline'),('b1',chosen),('b2',chosen),('a2','baseline')]:
        name='confirmation-t4-'+label;out=root/(name+'.json')
        run(name,common+['--output',out,'--task','single','--candidate',mode,'--threads',4],out)
    # Feed the four sequential single-instance arrays into the identical gate.
    from analyze_presentation_cache import analyze
    import gzip,hashlib
    rows=[json.loads(gzip.decompress((root/('confirmation-t4-'+label+'.samples.json.gz')).read_bytes()))[0] for label in ['a1','b1','b2','a2']]
    data=gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0);combined=root/'confirmation-combined.samples.json.gz';combined.write_bytes(data)
    meta=dict(raw=dict(file=combined.name,sha256=hashlib.sha256(data).hexdigest()),modes=['baseline',chosen,chosen,'baseline'],threads=4)
    result=analyze(meta,root/'confirmation-combined.json');(root/'confirmation-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    decision['confirmation']=result
    if not result['passed']:
        decision.update(status='negative_complete',reason='Single-instance ABBA fails; no live')
        (root/'decision.json').write_text(json.dumps(decision,indent=2)+'\n');return
    env.update(HEADLESS='0',SDL_VIDEODRIVER='cocoa',STAR_SCALE_MINIMAP_UNITS='off')
    # Diagnose the real engine boundaries before acceptance. Never capacity proof.
    name='live-diagnostic-baseline';out=root/(name+'.json')
    live=[lab/'tools/p3_runtime.py','--source',a.source,'--backend','rust','--native-threads',4,'--native-wire','--clock-mode','fixed','--fps',30,'--units',5000,'--agents',1000,'--delay',30,'--jitter-seconds',5,'--cycle-mode','post-action','--scope','selected','--layout','canonical','--policy','stochastic','--budget-ms',8,'--gc-policy','realtime_defer','--warmup',30]
    run(name,live+['--seconds',60,'--presentation-research-profile','--output',out],out)
    rounds=[]
    for r in [1,2,3]:
        order=['baseline',chosen] if r%2 else [chosen,'baseline']
        for mode in order:
            name=f'live-{mode}-r{r}';out=root/(name+'.json')
            run(name,live+['--seconds',300,'--presentation-research-mode',mode,'--output',out],out)
            m=json.loads(out.read_text());assert m['surface_size']==[2480,1239],m['surface_size']
            rounds.append(dict(run=name,mode=mode,pass_guards=m['pass'],guards=m['guards'],frame=m['frame_work_ms'],world_hz=m['world_hz'],source=m['source'],tooling=m['tooling']))
    decision.update(status='complete',live=rounds,live_gate=all(r['pass_guards'] for r in rounds),reason='Research complete; default path remains baseline')
    (root/'decision.json').write_text(json.dumps(decision,indent=2)+'\n')

if __name__=='__main__':main()
