"""Archive E4 small canonical raw evidence, with deterministic ZIP and checksums."""
import argparse
import hashlib
from pathlib import Path
import zipfile
import subprocess


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment',type=Path,required=True)
    p.add_argument('--run',type=Path,required=True)
    a=p.parse_args()
    entries={}
    for folder in ['replays','contracts','validation','wheels']:
        for path in sorted((a.run/folder).glob('*')):
            # Successful replay stdout duplicates JSON metadata. No raw tail is
            # removed: every timing/step array and all validation logs are kept.
            if path.is_file() and not (folder=='replays' and path.suffix=='.log') and not (folder=='contracts' and path.name.endswith('.raw.json.gz')):
                entries[f'{folder}/{path.name}']=path.read_bytes()
    lab = Path(__file__).resolve().parents[2]
    for name in ['profile_between_systems.py', 'analyze_between_systems.py', 'statistics_contract_matrix.py', 'package_between_systems.py', 'prepare_between_systems.py', 'prepare_system_candidates.py']:
        entries['tools/'+name] = Path(__file__).with_name(name).read_bytes()
    entries['tools/profile_between_systems-stage1.py'] = subprocess.check_output(['git','-C',str(lab),'show','28d5bf1:tools/rust_migration/profile_between_systems.py'])
    entries['SHA256SUMS']=''.join(f'{sha(data)}  {name}\n'for name,data in sorted(entries.items())).encode()
    output=a.experiment/'artifacts/between-systems-raw.zip'
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(entries.items()):
            info=zipfile.ZipInfo(name,(2026,10,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,data)
    with zipfile.ZipFile(output) as z:
        for line in z.read('SHA256SUMS').decode().splitlines():
            checksum,name=line.split('  ',1);assert sha(z.read(name))==checksum
    print(f'{sha(output.read_bytes())}  {output} ({output.stat().st_size} bytes)')


if __name__=='__main__':
    main()
