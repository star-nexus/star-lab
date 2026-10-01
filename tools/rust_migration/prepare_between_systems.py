"""Verify E4 raw/wheel and restore input/E3 contracts via the canonical E3 chain.

Extracts packages; does not install, modify any venv, or alter frozen directories.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment',type=Path,required=True)
    p.add_argument('--work-dir',type=Path,required=True)
    a=p.parse_args()
    experiment=a.experiment.resolve();work=a.work_dir.resolve()
    manifest=json.loads((experiment/'manifest.yaml').read_text())
    subprocess.run([sys.executable,str(Path(__file__).with_name('prepare_system_candidates.py')),
                    '--experiment',str(experiment.parent/'2026-10-rust-internal-system-candidates'),
                    '--work-dir',str(work/'e3')],check=True)
    raw=experiment/manifest['raw']['file']
    assert hashlib.sha256(raw.read_bytes()).hexdigest()==manifest['raw']['sha256']
    with zipfile.ZipFile(raw) as z:
        for line in z.read('SHA256SUMS').decode().splitlines():
            checksum,name=line.split('  ',1)
            assert hashlib.sha256(z.read(name)).hexdigest()==checksum,name
        member=manifest['binary']['wheel_member'];data=z.read(member)
        assert hashlib.sha256(data).hexdigest()==manifest['binary']['wheel_sha256']
        work.mkdir(parents=True,exist_ok=True)
        wheel=work/Path(member).name;wheel.write_bytes(data)
    with zipfile.ZipFile(wheel) as z:
        for name in z.namelist():
            if name.startswith('star_native/'):
                path=work/'candidate'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z.read(name))
    binary=next((work/'candidate/star_native').glob('*.so'))
    assert hashlib.sha256(binary.read_bytes()).hexdigest()==manifest['binary']['extension_sha256']
    print(json.dumps({'work':str(work),'wheel':str(wheel),'input_directory':str(work/'e3/inputs'),'installed':False}))


if __name__=='__main__':
    main()
