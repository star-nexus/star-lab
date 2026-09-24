"""Isolated faction-query broad phase; no Agent/network/frame-capacity claim."""
import argparse
import contextlib
import hashlib
import io
import json
import lzma
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from unittest.mock import patch


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();src=args.source.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    os.chdir(src);sys.path.insert(0,str(src));os.environ['SDL_VIDEODRIVER']='dummy'
    from star_native import NativeRuntime,API_VERSION,_native
    from rotk_env import components as c
    from rotk_env.prefabs.config import Faction
    from rotk_env.runtime.bootstrap import export_initial_state
    from rotk_env.systems.llm_action_handler import LLMActionHandler
    from rotk_env.tests.test_faction_state_affordances import _world,_spawn,_disc
    def git(root,*cmd):return subprocess.check_output(['git',*cmd],cwd=root,text=True).strip()
    raw=[];rows=[]
    with patch('time.time',return_value=1720000000.),contextlib.redirect_stdout(io.StringIO()):
        for n in [500,5000]:
            for radius,ap in [(1,2),(3,2),(80,2),(3,0)]:
                world=_world();world.add_singleton_component(c.GameTime());world.add_singleton_component(c.RngService(seed=42))
                for entity in list(world.get_singleton_component(c.MapData).tiles.values()):world.destroy_entity(entity)
                board=_disc(world,math.ceil(math.sqrt(n/3))+2)
                cells=sorted(board.tiles)
                assert len(cells)>=n
                ids=[]
                for i,(col,row) in enumerate(cells[:n]):
                    ids.append(_spawn(world,faction=Faction.WEI if i<n//2 else Faction.SHU,col=col,row=row,mp=0,ap=ap,attack_range=radius))
                world.get_singleton_component(c.FogOfWar).enabled=False
                selected=ids[max(0,n//2-100):n//2]
                params={'faction':'wei','unit_ids':selected};wire=json.dumps([params])
                initial=export_initial_state(world);native=NativeRuntime(json.dumps(initial))
                try:
                    report=json.loads(native._observation_probe_json(wire));expected=report['results']
                    python_equal=None
                    if n==500:
                        python_equal=expected==[LLMActionHandler(world).handle_faction_state(params)]
                        assert python_equal
                    samples=[]
                    for _ in range(5):
                        start=time.perf_counter();encoded=native._observation_probe_json(wire);end=time.perf_counter()
                        current=json.loads(encoded);assert current['results']==expected
                        samples.append((end-start)*1000)
                    final=json.loads(native.export_state_json());assert final==initial
                    result=expected[0];visible=len(result['visible_enemy_units'])
                    row=dict(units=n,selected_units=len(selected),visible_enemies=visible,radius=radius,ap=ap,
                        initial_sha256=digest(initial),response_sha256=digest(expected),state_unchanged=True,python_equal=python_equal,
                        response_bytes=len(json.dumps(expected,separators=(',',':')).encode()),attackable_targets=sum(len(u['attackable']) for u in result['units']),
                        legacy_enemy_visits=len(selected)*visible,metrics=report['metrics'],samples_ms=samples,median_ms=sorted(samples)[len(samples)//2])
                    rows.append(row);raw.append(dict(summary=row,initial=initial,parameters=params,response=expected))
                finally:native.close();world.reset()
    rawbytes=json.dumps(raw,separators=(',',':')).encode();path=out/'raw.json.xz';path.write_bytes(lzma.compress(rawbytes))
    report=dict(source_sha=git(src,'rev-parse','HEAD'),source_dirty=git(src,'status','--porcelain'),tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),
        api=API_VERSION,extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),platform=platform.platform(),python=sys.version,
        clock='injected world metadata; perf_counter timing',rows=rows,raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        timing_scope='single read-only native faction query including JSON encoding; Python decoding excluded; 1 warmup, 5 samples',
        capacity_claim=False,parallel_claim=False,all_guards_passed=True)
    assert not report['source_dirty'];(out/'compact.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'}));print(json.dumps(rows))


if __name__=='__main__':main()
