"""Recompute E3 optimistic E5 bounds; no dispatch/prepare/publish deducted."""
import argparse,gzip,hashlib,json,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--e3-raw',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
assert hashlib.sha256(a.e3_raw.read_bytes()).hexdigest()=='c3e347b145fcc5edfda304bb35030d3d3d9320861f116a5507d2b92cbd9b6abd'
result=[]
with zipfile.ZipFile(a.e3_raw) as z:
    for line in z.read('SHA256SUMS').decode().splitlines():
        checksum,name=line.split('  ',1);assert hashlib.sha256(z.read(name)).hexdigest()==checksum,name
    for threads in [1,2,4]:
        member=f'replays/candidate-t{threads}.timings.json.gz';raw=z.read(member);rows=json.loads(gzip.decompress(raw));assert len(rows)==9880
        def bound(selected,narrow):
            values=[]
            for row in selected:
                v=row['candidates']['visuals']
                visual=sum(v[k] for k in ['attack_ns','projectile_ns','effect_ns','damage_ns']) if narrow else row['phases_ns']['visuals']
                values.append(min(row['phases_ns']['movement'],visual))
            ordered=sorted(values)
            return dict(ticks=len(values),conditional_mean_ns=sum(values)/len(values),p99_ns=ordered[int(len(values)*.99)],max_ns=max(values),all_tick_weighted_mean_ns=sum(values)/9880)
        active=[r for r in rows if r['moving_before']>0]
        cuts={str(cut):bound([r for r in active if r['candidates']['visuals']['damage_rows']>=cut],True) for cut in [0,1,4,8,16,24]}
        result.append(dict(threads=threads,raw_member=member,member_sha256=hashlib.sha256(raw).hexdigest(),full_phase=bound(active,False),narrow_loop=bound(active,True),damage_thresholds=cuts))
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(dict(tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),e3_raw_sha256=hashlib.sha256(a.e3_raw.read_bytes()).hexdigest(),results=result,scope='diagnostic optimistic bound including timers; no cost deducted; not a net speedup'),indent=2)+'\n')
