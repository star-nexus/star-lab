"""Compare authoritative/legacy Player membership with native presentation after death."""
import argparse
from copy import deepcopy
import datetime
import hashlib
import json
import lzma
import os
from pathlib import Path
import sys
from unittest.mock import patch
from r3_observations_probe import git


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();source=args.source.resolve();output=args.output.resolve()
    os.chdir(source);sys.path.insert(0,str(source));os.environ['SDL_VIDEODRIVER']='dummy'
    from star_native import API_VERSION,_native
    from rotk_env.components import Player
    from rotk_env.prefabs.config import GameMode
    from rotk_env.runtime.bootstrap import export_initial_state,encode
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.runtime.world_presentation import WorldPresentation
    from rotk_env.tests.test_native_combat_presentation import make,request
    from rotk_env.tests.test_native_world_presentation import detached_world
    from rotk_env.tests.test_native_unit_actions import register
    class Frozen(datetime.datetime):
        @classmethod
        def now(cls,tz=None):return cls(2026,9,12,12)
    cases=[]
    with patch('time.time',return_value=1720000000.),patch('datetime.datetime',Frozen):
        for display in ('none','dummy','window'):
            for mode in (GameMode.REAL_TIME,GameMode.TURN_BASED):
                for threads in (1,2,4):
                    for drain_before in (False,True):
                        world,(a,b,target),llm=make(display,mode,'melee',dead=True)
                        derived=detached_world(world);projection=WorldPresentation(derived)
                        try:
                            initial=export_initial_state(world,display=display)
                            with RustRuntime(initial,threads=threads) as runtime:
                                if drain_before:projection.apply(runtime.take_presentation_delta())
                                register(world,runtime,llm,display)
                                response=request(world,runtime,llm,'attack',dict(unit_id=a,target_id=target),display)
                                assert response['success'] and response['battle_summary']['battle_result']['target_destroyed']
                                state=runtime.export_state();delta=runtime.take_presentation_delta();projection.apply(delta)
                                assert runtime.export_state()==state==export_initial_state(world,display=display)
                                expected={str(uid):encode(world.get_component(uid,Player)) for uid in world.query().with_component(Player).ordered_entities()}
                                actual={str(uid):encode(derived.get_component(uid,Player)) for uid in derived.query().with_component(Player).ordered_entities()}
                                equal=actual==expected
                                assert equal==(API_VERSION>=9)
                                if API_VERSION>=9:
                                    idle=runtime.take_presentation_delta()['players']
                                    assert idle==dict(full=False,rows=[],units_removed=[])
                                cases.append(dict(display=display,mode=mode.value,threads=threads,drain_before=drain_before,initial=initial,response=response,state=state,delta=delta,expected_players=expected,actual_players=actual,authority_equal=True,presentation_equal=equal))
                        finally:world.reset();derived.reset()
    output.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(cases,ensure_ascii=False,separators=(',',':')).encode();path=output/'raw.json.xz';path.write_bytes(lzma.compress(raw))
    summary=dict(source_sha=git(source,'rev-parse','HEAD'),source_dirty=git(source,'status','--porcelain'),tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),api=API_VERSION,extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),cases=len(cases),authority_equal=sum(c['authority_equal'] for c in cases),presentation_equal=sum(c['presentation_equal'] for c in cases),all_guards_passed=True,capacity=False,raw=dict(path=path.name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),decoded_bytes=len(raw),decoded_sha256=hashlib.sha256(raw).hexdigest()))
    assert not summary['source_dirty']
    (output/'compact.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))


if __name__=='__main__':main()
