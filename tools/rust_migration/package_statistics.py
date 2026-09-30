"""Canonical E2 raw package and compact/member alias index; run after measurement."""
import argparse,hashlib,json,zipfile
from pathlib import Path

def sha(body):return hashlib.sha256(body).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--build',type=Path,required=True);p.add_argument('--contracts',type=Path,required=True);a=p.parse_args();root=a.root.resolve();results=root/'results';artifacts=root/'artifacts';artifacts.mkdir(exist_ok=True)
 files={};members={}
 def add(relative,path,canonical=None,classification='formal'):
  b=path.read_bytes();member=canonical or relative;entry=dict(member=member,sha256=sha(b),bytes=len(b),classification=classification)
  files[relative]=entry
  if member in members:assert members[member]==b
  else:members[member]=b
 for path in sorted(results.iterdir()):
  if path.suffix in ['.gz','.log','.png'] or path.name.endswith('.raw.json'):
   relative='results/'+path.name;canonical='results/contracts-canonical.raw.json.gz' if 'contracts-t' in path.name and path.name.endswith('.raw.json.gz') else None
   add(relative,path,canonical)
 for name in ['pytest.log','cargo-test.log','fmt.log','clippy.log']:add('validation/'+name,a.build/'selected'/name)
 add('validation/selected-gates.log',a.build/'selected/gates.log')
 for stage in ['serial','parallel','selected']:
  wheel=a.build/stage/'star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl';add('wheels/'+stage+'/'+wheel.name,wheel)
 add('inputs/contracts.json.gz',a.contracts)
 # Root compact files remain ordinary Git files. Native wheels/raw are canonical only here.
 checks=''.join(f'{sha(b)}  {n}\n' for n,b in sorted(members.items())).encode();members['SHA256SUMS']=checks
 archive=artifacts/'statistics-compute-raw.zip'
 assert not archive.exists(), 'Never replace a formal evidence package'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name,b in sorted(members.items()):
   entry=zipfile.ZipInfo(name,date_time=(2026,10,1,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=0o644<<16;z.writestr(entry,b)
 # Re-read all archive members and validate their original bytes before publishing the index.
 with zipfile.ZipFile(archive) as z:
  for name,b in members.items():assert z.read(name)==b,name
 index=dict(archive=dict(file=str(archive.relative_to(root)),sha256=sha(archive.read_bytes()),bytes=archive.stat().st_size),files=files,canonical_member_count=len(members),original_path_count=len(files),contract_aliases=[k for k,v in files.items() if v['member']=='results/contracts-canonical.raw.json.gz'],notes=['Byte-identical full contract raw has one canonical member with eight original-path aliases.','R4e canonical trace and P0 wheel are referenced from prior immutable packages, not duplicated.','Loose ignored files are execution scratch, not additional formal copies.'])
 (results/'packages.json').write_text(json.dumps(index,indent=2)+'\n');print(json.dumps(index['archive']))
if __name__=='__main__':main()
