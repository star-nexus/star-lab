"""Resume interrupted E7 in fresh output directory, one guarded process at a time."""
import argparse,json,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--source-sha',required=True);p.add_argument('--trace',type=Path,required=True);p.add_argument('--runs',type=Path,required=True);a=p.parse_args()
python=a.source/'.venv/bin/python';here=Path(__file__).parent;progress=a.runs/'resume-progress.json';jobs=[('p2-correctness-t1-static',1,'baseline','static'),('p2-correctness-t4-exercise',4,'baseline','exercise'),('p2-correctness-typed-t1-exercise',1,'reuse_typed','exercise'),('p2-correctness-typed-t4-static',4,'reuse_typed','static')];completed=[]
def status(stage,current=None,error=None):
 m=dict(stage=stage,current=current,completed=completed,source_sha=a.source_sha,updated_unix=time.time(),error=error,capacity_claim=False)
 progress.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m),flush=True)
try:
 for name,threads,consumer,script in jobs:
  assert not (a.runs/(name+'.json')).exists(),'Do not repeat/select completed results'
  status('P2 full correctness',name)
  cmd=[str(python),str(here/'guard_display_preparation.py'),'--report',str(a.runs/(name+'.guard.json')),'--',str(python),str(here/'display_preparation_probe.py'),'--source',str(a.source),'--source-sha',a.source_sha,'--trace',str(a.trace),'--output',str(a.runs/(name+'.json')),'--task','correctness','--threads',str(threads),'--consumer',consumer,'--script',script,'--overscan-clock','items','--full-authority']
  with (a.runs/(name+'.supervisor.log')).open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
  # Preserve driver's log naming expected by the matrix prerequisite audit.
  (a.runs/(name+'.log')).write_bytes((a.runs/(name+'.guard.child.log')).read_bytes())
  m=json.loads((a.runs/(name+'.json')).read_text());assert m['all_passed'] and m['formal'] and m['counts']==dict(request=40994,step=9880,presentation=9880)
  completed.append(name)
 status('P3 sequential performance matrix')
 subprocess.run([str(python),str(here/'run_display_preparation_matrix.py'),'--source',str(a.source),'--source-sha',a.source_sha,'--trace',str(a.trace),'--runs',str(a.runs)],check=True)
 status('P3 complete; conditional confirmation/window decision required')
except BaseException as e:
 status('stopped or failed',error=repr(e));raise
