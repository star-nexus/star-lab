"""Exact observation catalog scaling with mostly hidden terrain; not a frame gate."""
import argparse
import contextlib
import hashlib
import io
import json
import lzma
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from unittest.mock import patch
from kernel_attack_candidates_probe import digest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();src=args.source.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    os.chdir(src);sys.path.insert(0,str(src));os.environ['SDL_VIDEODRIVER']='dummy'
    from star_native import NativeRuntime,API_VERSION,_native
    from rotk_env import components as c
    from rotk_env.prefabs.config import Faction,GameMode
    from rotk_env.runtime.bootstrap import export_initial_state
    from rotk_env.systems.llm_action_handler import LLMActionHandler
    from rotk_env.utils.hex_utils import HexMath
    from rotk_env.tests.test_faction_state_affordances import _world,_spawn,_disc
    def git(root,*cmd):return subprocess.check_output(['git',*cmd],cwd=root,text=True).strip()
    rows=[];raw=[]
    with patch('time.time',return_value=1720000000.),contextlib.redirect_stdout(io.StringIO()):
        for radius in [45,142]:
            for mode in ['local','empty','disabled']:
                world=_world();world.add_singleton_component(c.GameTime(current_mode=GameMode.REAL_TIME,game_start_time=1720000000.,turn_start_time=1720000000.,last_update_time=1720000000.));world.add_singleton_component(c.RngService(seed=42))
                for entity in list(world.get_singleton_component(c.MapData).tiles.values()):world.destroy_entity(entity)
                board=_disc(world,radius)
                cells=sorted(board.tiles,key=lambda p:(HexMath.hex_distance((0,0),p),p))
                own=[]
                for i,(col,row) in enumerate(cells[:100]):
                    uid=_spawn(world,faction=Faction.WEI if i%2==0 else Faction.SHU,col=col,row=row,mp=0)
                    if i%2==0:own.append(uid)
                fog=world.get_singleton_component(c.FogOfWar);fog.enabled=mode!='disabled';fog.faction_vision={Faction.WEI:set(cells[:7]) if mode=='local' else set()}
                params={'faction':'wei','unit_ids':own[:5]};wire=json.dumps([params]);initial=export_initial_state(world)
                native=NativeRuntime(json.dumps(initial))
                try:
                    report=json.loads(native._observation_probe_json(wire));expected=report['results'];python_equal=None
                    if radius==45:
                        python_equal=expected==[LLMActionHandler(world).handle_faction_state(params)];assert python_equal
                    samples=[]
                    for _ in range(5):
                        start=time.perf_counter();encoded=native._observation_probe_json(wire);end=time.perf_counter()
                        assert json.loads(encoded)['results']==expected;samples.append((end-start)*1000)
                    assert json.loads(native.export_state_json())==initial
                    row=dict(radius=radius,tiles=len(board.tiles),units=100,selected_units=5,fog=mode,
                        initial_sha256=digest(initial),response_sha256=digest(expected),state_unchanged=True,python_equal=python_equal,
                        legacy_census_entities=len(initial['entities']),legacy_enemy_entities=len(initial['entities']),legacy_terrain_cells=len(board.tiles),
                        response_bytes=len(encoded.encode()),visible_terrain=len(expected[0]['visible_terrain']),metrics=report['metrics'],samples_ms=samples,median_ms=sorted(samples)[2])
                    rows.append(row);raw.append(dict(summary=row,initial=initial,parameters=params,response=expected))
                finally:native.close();world.reset()
    payload=json.dumps(raw,separators=(',',':')).encode();path=out/'raw.json.xz';path.write_bytes(lzma.compress(payload))
    result=dict(source_sha=git(src,'rev-parse','HEAD'),source_dirty=git(src,'status','--porcelain'),tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),api=API_VERSION,
        extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),platform=platform.platform(),python=sys.version,rows=rows,
        raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),timing='native query plus JSON encode; 1 warmup, 5 samples; import/decode excluded',capacity_claim=False,all_guards_passed=True)
    assert not result['source_dirty'];(out/'compact.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
