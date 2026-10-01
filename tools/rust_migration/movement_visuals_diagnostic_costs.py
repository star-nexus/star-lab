"""E5 four-mode diagnostic cost table from canonical raw only; not net gain."""
import argparse,gzip,hashlib,json,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();matched=[]
with zipfile.ZipFile(a.raw) as z:
    for line in z.read('SHA256SUMS').decode().splitlines():
        checksum,name=line.split('  ',1);assert hashlib.sha256(z.read(name)).hexdigest()==checksum,name
    for t in [2,4]:
        def load(mode):return json.loads(gzip.decompress(z.read(f'replays/diagnostic-{mode}-t{t}.timings.json.gz')))
        mask={x['seq'] for x in load('parallel') if x['phases_ns'].get('e5_eligible')};assert len(mask)==3772
        for mode in ['baseline','empty_fork','split_serial','parallel']:
            rows=[x for x in load(mode) if x['seq'] in mask];assert len(rows)==3772
            fields={key:sum(x['phases_ns'].get(key,0) for x in rows)/len(rows) for key in ['e5_prepare','movement','visuals','e5_compute','e5_publish','e5_region']}
            matched.append(dict(threads=t,mode=mode,matched_ticks=len(rows),actual_selected_ticks=sum(x['phases_ns'].get('e5_eligible',0) for x in rows),means_ns=fields))
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(dict(results=matched,scope='same recorded tick mask, different diagnostic runs; includes nested clocks, not an untimed speedup'),indent=2)+'\n')
