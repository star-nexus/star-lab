"""Sequential E5 fixed-input series; no live/default policy changes.

All prerequisite correctness/build checks must complete before this runner. Do not
run other benchmarks/tests/compression concurrently with timed replay series.
"""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--source-sha',required=True);p.add_argument('--extension-sha256',required=True);p.add_argument('--phase',choices=['replays','confirmation'],default='replays');a=p.parse_args()
env=dict(os.environ,HEADLESS='1',SDL_VIDEODRIVER='dummy',PYGAME_HIDE_SUPPORT_PROMPT='1')
trace=a.inputs/'rust-300-r3.trace.json.gz';assert hashlib.sha256(trace.read_bytes()).hexdigest()=='1f9b155129de9e43780c8885b40aba805e4c4794755fd2af70747058a7824b77'
base=[sys.executable,str(Path(__file__).with_name('profile_movement_visuals.py')),'--source',str(a.source),'--trace',str(trace),'--trace-sha256',hashlib.sha256(trace.read_bytes()).hexdigest(),'--source-sha',a.source_sha,'--extension-sha256',a.extension_sha256]
commands=[]
def replay(name,args):
    output=a.output/f'replays/{name}.json';output.parent.mkdir(parents=True,exist_ok=True)
    argv=base+['--output',str(output)]+args;commands.append(argv);(a.output/f'{a.phase}-commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    # Never silently reuse an old run under a new series.
    assert not output.exists(),output
    with output.with_suffix('.log').open('w') as log:subprocess.run(argv,check=True,env=env,stdout=log,stderr=subprocess.STDOUT)
    print('COMPLETE',name,flush=True)
if a.phase=='replays':
    replay('split-serial-t1',['--threads','1','--mode','compare','--probe-mode','split_serial','--min-damage-rows','0'])
    for t in [2,4]:
        for r in range(1,4):
            replay(f'primary-t{t}-r{r}',['--threads',str(t),'--mode','plain','--probe-mode','parallel','--paired'])
            replay(f'split-control-t{t}-r{r}',['--threads',str(t),'--mode','plain','--probe-mode','parallel','--paired','--control-mode','split_serial','--control-min-damage-rows','8'])
    for t in [2,4]:
        for mode in ['baseline','empty_fork','split_serial','parallel']:
            replay(f'diagnostic-{mode}-t{t}',['--threads',str(t),'--mode','compare','--probe-mode',mode])
        for threshold in [0,4,16]:
            replay(f'sensitivity-{threshold}-t{t}',['--threads',str(t),'--mode','plain','--probe-mode','parallel','--paired','--min-damage-rows',str(threshold)])
else:
    analysis=json.loads((a.output/'analysis.json').read_text());assert analysis['primary_gates']['4'],'native4 gate required'
    for r in range(1,4):
        for label,threshold in [('a1',2**64-1),('b1',8),('b2',8),('a2',2**64-1)]:
            replay(f'confirmation-t4-r{r}-{label}',['--threads','4','--mode','plain','--probe-mode','parallel','--min-damage-rows',str(threshold)])
subprocess.run([sys.executable,str(Path(__file__).with_name('analyze_movement_visuals.py')),'--runs',str(a.output/'replays'),'--output',str(a.output/'analysis.json')],check=True,env=env)
