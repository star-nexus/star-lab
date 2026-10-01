"""E5 deterministic Raw + Compact archive; never changes scientific gates."""
import argparse,hashlib,json,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--experiment',type=Path,required=True);p.add_argument('--run',type=Path,required=True);a=p.parse_args()
exp=a.experiment.resolve();run=a.run.resolve();art=exp/'artifacts';art.mkdir(parents=True,exist_ok=True)
def checksum(data):return hashlib.sha256(data).hexdigest()
def archive(path,members):
    lines=[f'{checksum(data)}  {name}' for name,data in sorted(members.items())]
    members=dict(members,SHA256SUMS=('\n'.join(lines)+'\n').encode())
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(members.items()):
            info=zipfile.ZipInfo(name,(2026,10,2,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data)
    return dict(file=str(path.relative_to(exp)),bytes=path.stat().st_size,sha256=checksum(path.read_bytes()),members=len(members)-1)
raw={}
for folder in ['replays','contracts','inputs','validation','wheels']:
    for path in sorted((run/folder).glob('*')):
        if not path.is_file() or (folder=='replays' and path.suffix=='.log'):continue
        if folder=='contracts' and path.name.endswith('.raw.json.gz'):continue
        raw[f'{folder}/{path.name}']=path.read_bytes()
contract_files=sorted((run/'contracts').glob('*.raw.json.gz'))
assert len(contract_files)==13
payload=contract_files[0].read_bytes()
assert all(path.read_bytes()==payload for path in contract_files)
canonical='contracts/contracts-canonical.raw.json.gz'
raw[canonical]=payload
raw['contract-aliases.json']=(json.dumps({f'contracts/{path.name}':dict(member=canonical,sha256=checksum(payload)) for path in contract_files},indent=2)+'\n').encode()
for path in sorted(run.glob('*.json')):raw[path.name]=path.read_bytes()
for name in ['profile_movement_visuals.py','movement_visuals_contracts.py','analyze_movement_visuals.py','run_movement_visuals.py','package_movement_visuals.py','prepare_movement_visuals.py','movement_visuals_cost_bounds.py','movement_visuals_diagnostic_costs.py']:
    path=Path(__file__).with_name(name)
    if path.exists():raw[f'tools/{name}']=path.read_bytes()
builder=run/'final-report-builder.py'
if builder.exists():raw['tools/final-report-builder.py']=builder.read_bytes()
primary=run/'primary-stage-analyzer.py'
if primary.exists():raw['tools/primary-stage-analyzer.py']=primary.read_bytes()
stage=run/'stage-analyzer.py'
if stage.exists():raw['tools/stage-analyzer.py']=stage.read_bytes()
original=run/'original-launcher.py'
if original.exists():raw['tools/original-launcher.py']=original.read_bytes()
raw_info=archive(art/'movement-visuals-raw.zip',raw)
compact={f'results/{p.name}':p.read_bytes() for p in sorted((exp/'results').glob('*')) if p.is_file() and p.name!='artifact-index.json'}
compact['raw-index.json']=(json.dumps(raw_info,indent=2)+'\n').encode()
compact_info=archive(art/'movement-visuals-compact.zip',compact)
index=dict(raw=raw_info,compact=compact_info);(exp/'results/artifact-index.json').write_text(json.dumps(index,indent=2)+'\n');print(json.dumps(index))
