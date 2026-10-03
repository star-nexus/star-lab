"""Out-of-process E7 memory guard. Only signals its own child process group."""
import argparse,json,os,re,signal,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);p.add_argument('--limit-mib',type=float,default=2500);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args();cmd=a.command[1:] if a.command[:1]==['--'] else a.command
assert cmd and not a.report.exists()
def pressure():return int(subprocess.check_output(['sysctl','-n','kern.memorystatus_vm_pressure_level'],text=True))
assert pressure()==1,'Memory pressure must be normal before starting'
a.report.parent.mkdir(parents=True,exist_ok=True);rows=[];reason=None;warns=0;started=time.monotonic();log=a.report.with_suffix('.child.log')
with log.open('w') as out:
 child=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 try:
  while child.poll() is None:
   rss_result=subprocess.run(['ps','-p',str(child.pid),'-o','rss='],capture_output=True,text=True)
   if child.poll() is not None:break
   rss=int(rss_result.stdout.strip() or 0)*1024;level=pressure();warns=warns+1 if level!=1 else 0
   row=dict(elapsed_s=round(time.monotonic()-started,3),pid=child.pid,rss_bytes=rss,pressure=level)
   if not rows or row['elapsed_s']-rows[-1].get('footprint_sample_s',-1000)>=30:
    vm=subprocess.run(['vmmap','-summary',str(child.pid)],capture_output=True,text=True)
    m=re.search(r'^Physical footprint:\s*([\d.]+)([BKMG])',vm.stdout,re.M)
    if m:row.update(footprint_bytes=int(float(m[1])*{'B':1,'K':1024,'M':1024**2,'G':1024**3}[m[2]]),footprint_sample_s=row['elapsed_s'])
    else:row['footprint_unavailable']=True
   elif 'footprint_sample_s' in rows[-1]:row['footprint_sample_s']=rows[-1]['footprint_sample_s']
   rows.append(row)
   if rss>a.limit_mib*1024**2 or row.get('footprint_bytes',0)>a.limit_mib*1024**2:reason='child memory limit exceeded'
   if level>=4 or warns>=2:reason='system memory pressure guard'
   if reason:break
   a.report.write_text(json.dumps(dict(status='running',command=cmd,limit_mib=a.limit_mib,samples=rows),indent=2)+'\n')
   if len(rows)%6==1:print(json.dumps(row),flush=True)
   time.sleep(5)
 finally:
  if child.poll() is None:
   os.killpg(child.pid,signal.SIGINT)
   try:child.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
code=child.returncode
result=dict(status='passed' if code==0 and reason is None else 'stopped_or_failed',command=cmd,child_exit=code,stop_reason=reason,limit_mib=a.limit_mib,samples=rows,elapsed_s=time.monotonic()-started)
a.report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='samples'}),flush=True)
raise SystemExit(0 if result['status']=='passed' else 1)
