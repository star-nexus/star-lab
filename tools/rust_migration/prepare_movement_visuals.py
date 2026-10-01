"""Restore canonical E5 inputs/wheel and independently check complete archive.

No installation or writes to existing/frozen source directories.
"""
import argparse,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--experiment',type=Path,required=True);p.add_argument('--work-dir',type=Path,required=True);a=p.parse_args();exp=a.experiment.resolve();work=a.work_dir.resolve();m=json.loads((exp/'manifest.yaml').read_text())
subprocess.run([sys.executable,str(Path(__file__).with_name('prepare_between_systems.py')),'--experiment',str(exp.parent/'2026-10-rust-between-system-parallel'),'--work-dir',str(work/'e4')],check=True)
raw=exp/m['raw']['file'];assert hashlib.sha256(raw.read_bytes()).hexdigest()==m['raw']['sha256']
with zipfile.ZipFile(raw) as z:
    for line in z.read('SHA256SUMS').decode().splitlines():
        checksum,name=line.split('  ',1);assert hashlib.sha256(z.read(name)).hexdigest()==checksum,name
    for name in z.namelist():
        if name.startswith(('inputs/','wheels/')):
            path=work/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z.read(name))
wheel=work/m['binary']['wheel_member'];assert hashlib.sha256(wheel.read_bytes()).hexdigest()==m['binary']['wheel_sha256']
with zipfile.ZipFile(wheel) as z:
    for name in z.namelist():
        if name.startswith('star_native/'):
            path=work/'candidate'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z.read(name))
so=next((work/'candidate/star_native').glob('*.so'));assert hashlib.sha256(so.read_bytes()).hexdigest()==m['binary']['extension_sha256']
print(json.dumps(dict(work=str(work),trace_directory=str(work/'e4/e3/inputs'),contracts=str(work/'inputs/contracts.json.gz'),candidate_package=str(work/'candidate'),e4_package=str(work/'e4/candidate'),installed=False)))
