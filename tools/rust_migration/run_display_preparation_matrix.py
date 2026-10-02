"""E7 fixed preregistered matrix; sequential speed runs after full correctness."""
import argparse,json,subprocess,sys,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--source-sha',required=True);p.add_argument('--runs',type=Path,required=True);p.add_argument('--trace',type=Path,required=True);a=p.parse_args()
incident=Path(__file__).resolve().parents[2]/'experiments/2026-10-rust-display-preparation/results/memory-exhaustion-incident.json'
if incident.exists() and not json.loads(incident.read_text()).get('resolved_safety',False):
 raise RuntimeError('E7 memory exhaustion incident unresolved; automatic performance restart is disabled')
a.runs.mkdir(exist_ok=True);python=a.source/'.venv/bin/python';tool=Path(__file__).with_name('display_preparation_performance.py');commands=[]
for round_id in (1,2,3):
 for script in ('static','exercise'):
  for consumer in ('baseline','reuse_typed'):
   for threads in (1,4):
    name=f'p3-{consumer}-t{threads}-{script}-r{round_id}'
    command=[str(python),str(tool),'--source',str(a.source),'--source-sha',a.source_sha,'--trace',str(a.trace),'--output',str(a.runs/(name+'.json')),'--task','paired','--candidate','empty_territory','--threads',str(threads),'--consumer',consumer,'--script',script,'--overscan-clock','wall']
    commands.append(dict(name=name,argv=command))
(a.runs/'p3-commands.json').write_text(json.dumps(commands,indent=2)+'\n')
correctness=['p2-correctness-t1-static','p2-correctness-t4-exercise','p2-correctness-typed-t1-exercise','p2-correctness-typed-t4-static']
for name in correctness:
 while not (a.runs/(name+'.json')).exists():
  log=a.runs/(name+'.log')
  if log.exists() and 'Traceback (most recent call last)' in log.read_text():raise RuntimeError('Correctness failed: '+name)
  time.sleep(15)
 meta=json.loads((a.runs/(name+'.json')).read_text());assert meta['all_passed'] and meta['formal'] and meta['full_authority']
 assert meta['counts']==dict(request=40994,step=9880,presentation=9880)
# Metadata is emitted immediately before process cleanup; allow all lifecycle
# teardown to finish before the sole formal timing process starts.
time.sleep(15)
while any(str(a.runs) in line and '--task correctness' in line and 'display_preparation_probe.py' in line
          for line in subprocess.check_output(['ps','-ax','-o','command='],text=True).splitlines()):
 time.sleep(15)
for index,item in enumerate(commands):
 output=a.runs/(item['name']+'.json')
 if output.exists():raise RuntimeError('Refusing repeat/selection: '+str(output))
 print(json.dumps(dict(stage='P3',run=item['name'],index=index+1,total=len(commands))),flush=True)
 with (a.runs/(item['name']+'.log')).open('w') as log:subprocess.run(item['argv'],stdout=log,stderr=subprocess.STDOUT,check=True)
 subprocess.run([str(python),str(Path(__file__).with_name('analyze_display_preparation.py')),'--runs',str(a.runs),'--output',str(a.runs/'p3-analysis.json')],check=True)
print(json.dumps(dict(stage='P3',all_runs_complete=True)),flush=True)
