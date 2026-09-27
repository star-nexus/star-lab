"""Package R4d evidence after measurement; retain one canonical raw ZIP."""
from pathlib import Path
import argparse,hashlib,json,zipfile
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,required=True);root=parser.parse_args().root.resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rawfiles=[p for p in (root/'results').rglob('*') if p.is_file() and (p.name.endswith(('.raw.json','.json.gz','.png','.log')))]
raw=root/'artifacts/r4d-5000-agents-raw.zip'
with zipfile.ZipFile(raw,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(rawfiles):z.write(p,str(p.relative_to(root)))
index={'raw':dict(file=str(raw.relative_to(root)),bytes=raw.stat().st_size,sha256=sha(raw)), 'members':{str(p.relative_to(root)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(rawfiles)}}
(root/'results/artifact-index.json').write_text(json.dumps(index,indent=2)+'\n')
ignored='\n'.join('/'+str(p.relative_to(root)) for p in sorted(rawfiles))+'\n'
(root/'.gitignore').write_text(ignored)
compactfiles=[p for p in (root/'results').glob('*.json') if p not in rawfiles and p.name!='packages.json']
compactfiles += [root/name for name in ['README.md','manifest.yaml','analysis.md','decision.md']]
compact=root/'artifacts/r4d-5000-agents-compact.zip'
with zipfile.ZipFile(compact,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(compactfiles):z.write(p,str(p.relative_to(root)))
 z.writestr('SHA256SUMS',''.join(f'{sha(p)}  {p.relative_to(root)}\n' for p in sorted(compactfiles)))
index2={name:dict(file=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p)) for name,p in [('raw',raw),('compact',compact)]}
(root/'results/packages.json').write_text(json.dumps(index2,indent=2)+'\n')
allfiles=compactfiles+[root/'results/packages.json',raw,compact]
(root/'artifacts/SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(root)}\n' for p in sorted(allfiles)))
with zipfile.ZipFile(raw) as z:
 for name,item in index['members'].items():assert hashlib.sha256(z.read(name)).hexdigest()==item['sha256']
print(json.dumps(index2,indent=2));print('raw members verified',len(index['members']))
