"""E2 selected-policy gates; one benchmark process at a time, no concurrent build.

Run from a clean Lab checkout with the already installed, validated selected wheel.
Full source/binary/input identity is checked before launching and recorded per call.
"""
import argparse, datetime, hashlib, json, os, subprocess, sys
from pathlib import Path

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--source-sha',required=True)
    p.add_argument('--extension-sha256',required=True)
    p.add_argument('--trace',type=Path,required=True)
    p.add_argument('--contracts',type=Path,required=True)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--live-only',action='store_true')
    a=p.parse_args(); source=a.source.resolve(); lab=Path(__file__).resolve().parents[2]
    python=source/'.venv/bin/python'; results=a.root.resolve()/'results'; results.mkdir(parents=True,exist_ok=True)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()==a.source_sha
    for repo in [source,lab]:
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip(), repo
    actual=subprocess.check_output([str(python),'-c','from star_native import _native; from pathlib import Path; import hashlib; print(hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest())'],cwd=source,text=True).strip()
    assert actual==a.extension_sha256
    env=dict(os.environ,PYTHONUNBUFFERED='1',PYTHONHASHSEED='0',PYTHONPATH=f'{source}:{lab}/tools:{lab}/tools/rust_migration')
    commands=[]
    def run(name,argv,live=False):
        assert not (results/f'{name}.json').exists(), 'Do not overwrite prior evidence'
        call_env=dict(env,HEADLESS='0' if live else '1',SDL_VIDEODRIVER='cocoa' if live else 'dummy')
        entry=dict(run=name,command=argv,cwd=str(source),environment={k:call_env[k] for k in ['PYTHONUNBUFFERED','PYTHONHASHSEED','PYTHONPATH','HEADLESS','SDL_VIDEODRIVER']},started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha=a.source_sha,extension_sha256=a.extension_sha256)
        print('START',name,entry['started_utc'],flush=True)
        with (results/f'{name}.log').open('w') as log:
            result=subprocess.run(argv,cwd=source,env=call_env,stdout=log,stderr=subprocess.STDOUT)
        entry.update(exit_code=result.returncode,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());commands.append(entry)
        (results/'selected-commands.json').write_text(json.dumps(dict(tool_sha256=sha(Path(__file__)),commands=commands),indent=2)+'\n')
        print('END',name,result.returncode,entry['finished_utc'],flush=True)
        assert result.returncode==0, name
        if live:
            r=json.loads((results/f'{name}.json').read_text())
            print('GATES',name,r['pass'],[k for k,v in r['guards'].items() if not v],flush=True)
    if not a.live_only:
        for threads in [1,2,4]:
            name=f'selected-contracts-t{threads}'
            run(name,[str(python),str(lab/'tools/rust_migration/statistics_contract_matrix.py'),'--source',str(source),'--input',str(a.contracts.resolve()),'--output',str(results/f'{name}.json'),'--extension-sha256',a.extension_sha256,'--threads',str(threads)])
        for threads in [1,2,4]:
            name=f'selected-normal-t{threads}'
            run(name,[str(python),str(lab/'tools/rust_migration/profile_statistics_trace.py'),'--source',str(source),'--source-sha',a.source_sha,'--extension-sha256',a.extension_sha256,'--trace',str(a.trace.resolve()),'--trace-sha256',sha(a.trace),'--mode','plain','--threads',str(threads),'--output',str(results/f'{name}.json')])
    for trial in [1,2,3]:
        name=f'rust4-300-r{trial}'
        run(name,[str(python),str(lab/'tools/p3_runtime.py'),'--source',str(source),'--backend','rust','--native-threads','4','--fps','30','--clock-mode','fixed','--cycle-mode','post-action','--jitter-seconds','5','--units','5000','--agents','1000','--delay','30','--scope','selected','--layout','canonical','--policy','stochastic','--seconds','300','--warmup','30','--budget-ms','8','--gc-policy','realtime_defer','--output',str(results/f'{name}.json'),'--native-wire','--record-native-inputs'],live=True)
    print('SELECTED GATES COMPLETE',flush=True)
if __name__=='__main__':main()
