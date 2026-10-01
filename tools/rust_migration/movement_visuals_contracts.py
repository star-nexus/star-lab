"""E5 independent binary prefix/state/delta oracle with archived exact inputs."""
import argparse,gzip,hashlib,json,sys,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path);p.add_argument('--generate',action='store_true');p.add_argument('--native-package',type=Path);p.add_argument('--mode',default='ordinary');p.add_argument('--threads',type=int,default=1);p.add_argument('--extension-sha256');a=p.parse_args()
sys.path.insert(0,str(a.source.resolve()))
if a.native_package:sys.path.insert(0,str(a.native_package.resolve()))
from star_native import NativeRuntime,_native
if a.generate:
    from rotk_env.tests.test_native_movement_visuals import cases
    a.input.parent.mkdir(parents=True,exist_ok=True)
    a.input.write_bytes(gzip.compress(json.dumps(cases(),sort_keys=True,separators=(',',':')).encode(),mtime=0));sys.exit()
assert hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest()==a.extension_sha256
reports=[]
for case in json.loads(gzip.decompress(a.input.read_bytes())):
    r=NativeRuntime(json.dumps(case['initial']),a.threads)
    rows=[]
    def snapshot(error=None):return dict(error=error,state=json.loads(r.export_state_json()),delta=json.loads(r.take_presentation_delta_json()))
    rows.append(snapshot())
    for i,dt in enumerate(case['steps']):
        error=None
        try:
            if a.mode=='ordinary':r.step(dt,1720000000.+i)
            else:r._movement_visuals_step_json(dt,1720000000.+i,a.mode,0,False)
        except RuntimeError as e:error=str(e)
        rows.append(snapshot(error))
        if i==10:
            r.reset(r.export_state_json());rows.append(snapshot())
    r.close();reports.append(dict(name=case['name'],rows=rows))
a.output.parent.mkdir(parents=True,exist_ok=True)
raw=a.output.with_suffix('.raw.json.gz');raw.write_bytes(gzip.compress(json.dumps(reports,sort_keys=True,separators=(',',':')).encode(),mtime=0))
a.output.write_text(json.dumps(dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=a.source,text=True).strip(),tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),argv=sys.argv,extension_sha256=a.extension_sha256,input_sha256=hashlib.sha256(a.input.read_bytes()).hexdigest(),mode=a.mode,threads=a.threads,cases=len(reports),steps=sum(len(c['rows'])-2 for c in reports),raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest()),indent=2)+'\n')
