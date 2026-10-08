"""Four serial ordinary-ingestion census host attempts, no automatic retries."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile
from analyze_census_host import analyze, verify_point

LAB=Path(__file__).resolve().parents[2]
EXP=LAB/'experiments/2026-10-rust-observation-service'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n');temp.replace(path)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--preregister',type=Path,required=True);a=p.parse_args()
    reg=json.loads(a.preregister.read_text());source=Path(reg['source']);root=Path(reg['runs']);root.mkdir(parents=True,exist_ok=True)
    lock=(root/'owner.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not (root/'progress.json').exists(),'no duplicate launch or automatic retry'
    assert reg['order']==['baseline','borrowed_census','borrowed_census','baseline'] and reg['fixed_window']
    env=dict(os.environ);env['PYTHONPATH']=reg['extension_dir']+os.pathsep+str(source)
    env.pop('HEADLESS',None);env.pop('SDL_VIDEODRIVER',None)
    points=[];progress=root/'progress.json'
    def identity():
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()==reg['source_sha']
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
        assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=LAB,text=True)
        for name,h in reg['frozen_files'].items():assert sha(LAB/name)==h,name
        assert sha(Path(reg['extension_dir'])/'star_native/_native.cpython-313-darwin.so')==reg['extension_sha256']
    error=None
    try:
        for i,mode in enumerate(reg['order']):
            identity();out=root/f'{i+1}-{mode}.json';assert not out.exists()
            write(progress,dict(status='running',attempt=i+1,total=4,mode=mode,completed=len(points),child_report=str(out)))
            command=[str(source/'.venv/bin/python'),str(LAB/'tools/rust_migration/monitor_observation_admission.py'),'--report',str(out.with_suffix('.monitor.json')),'--',str(source/'.venv/bin/python'),str(LAB/'tools/rust_migration/census_observation_host.py'),'--scan-mode',mode,*reg['runtime_args'],'--output',str(out)]
            with (root/f'{i+1}.supervisor.log').open('w') as log:r=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT)
            assert r.returncode==0,f'attempt {i+1} child failure; no retry'
            meta,_,_,_=verify_point(out)
            assert not meta['smoke'] and meta['hardware']['window']==reg['fixed_window'] and meta['surface_size']==reg['fixed_window'] and meta['display_driver']==reg['display_driver']
            points.append(out);write(progress,dict(status='attempt_complete',completed=len(points),total=4,mode=mode))
        identity();result=analyze(points);write(root/'analysis.json',result)
    except BaseException as exc:
        error=repr(exc);write(root/'failure.json',dict(failure=error,completed=len(points),automatic_retry=False))
    # No next attempt is active when archiving; preserve invalid/resource attempts.
    files={f'raw/{p.name}':p for p in root.iterdir() if p.is_file() and p.name not in ('owner.lock','parent.log','progress.json')}
    files.update({f'tools/{Path(n).name}':LAB/n for n in reg['frozen_files']})
    files['preregister.json']=a.preregister
    package=EXP/'artifacts/e8-census-host-20261009-raw.zip';assert not package.exists()
    with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for n,path in sorted(files.items()):z.write(path,n)
        z.writestr('SHA256SUMS',''.join(f'{sha(path)}  {n}\n' for n,path in sorted(files.items())))
    record=dict(status='failed' if error else 'complete',completed=len(points),total=4,failure=error,analysis=None if error else result,
                raw=dict(path=str(package.relative_to(EXP)),sha256=sha(package),bytes=package.stat().st_size,members=len(files)),default_adoption=False,automatic_retry=False)
    write(EXP/'results/census-host-complete.json',record);write(progress,record)
    if error:raise RuntimeError(error)


if __name__=='__main__':main()
