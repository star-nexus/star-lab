"""Explicitly enabled VLM: owned state plus legacy display bytes, before/after."""
import argparse
import base64
from copy import deepcopy
import datetime
import hashlib
import io
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
    parser.add_argument('--expect-supported',action='store_true')
    args=parser.parse_args();src=args.source.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    os.chdir(src);sys.path.insert(0,str(src));os.environ['SDL_VIDEODRIVER']='dummy'
    import pygame
    from framework.engine.renders import RenderEngine
    from star_native import API_VERSION,_native
    from rotk_env import components as c
    from rotk_env.prefabs.config import GameMode
    from rotk_env.runtime.bootstrap import export_initial_state
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.tests.test_native_vision import make_vision_world
    from rotk_env.systems.llm_system import LLMSystem
    class Frozen(datetime.datetime):
        @classmethod
        def now(cls,tz=None):return cls(2026,9,12,12)
    cases=[]
    with patch('time.time',return_value=1720000000.),patch('datetime.datetime',Frozen):
        for mode in ['real_time','turn_based']:
            for display in ['none','dummy','window']:
                for threads in [1,2,4]:
                    for size in [None,(1,1),(13,7)]:
                        screen=pygame.Surface(size) if size else None
                        if screen is not None:screen.fill((18,90,147));screen.set_at((0,0),(251,2,67))
                        RenderEngine()._screen=screen
                        world,ids,_=make_vision_world(display)
                        world.get_singleton_component(c.GameTime).current_mode=GameMode(mode)
                        world.get_singleton_component(c.GameModeComponent).mode=GameMode(mode)
                        world.add_singleton_component(c.MatchRules(game_actions=('move','attack','get_faction_state','get_faction_state_vlm')))
                        llm=LLMSystem();world.add_system(llm)
                        initial=export_initial_state(world,display=display);steps=[]
                        try:
                            with RustRuntime(initial,threads=threads) as runtime:
                                for action,params in [('register_agent_info',dict(faction='wei',provider='synthetic',model_id='fake',base_url='http://local')),
                                    ('get_faction_state_vlm',dict(faction='wei',unit_ids=[ids[1],ids[0],ids[1]],agent_id='spoofed'))]:
                                    py=llm._process_action_request(agent_id='a',action_id=0,action=action,params=deepcopy(params),send_response=False)
                                    error=None
                                    try:rs=runtime.execute_action(action,deepcopy(params),agent_id='a')
                                    except RuntimeError as exc:rs=None;error=str(exc)
                                    ps=export_initial_state(world,display=display);ns=runtime.export_state()
                                    steps.append(dict(action=action,parameters=params,python=py,rust=rs,error=error,python_state=ps,rust_state=ns,
                                                      response_equal=rs==json.loads(json.dumps(py)),state_equal=ps==ns))
                                last=steps[-1]
                                if args.expect_supported:assert last['response_equal'] and last['state_equal'],(mode,display,threads,size,last['error'])
                                else:assert last['error']=='native action get_faction_state_vlm is not implemented yet'
                                frame=last['python']['frame_base64'];image=None
                                if frame:
                                    data=base64.b64decode(frame);decoded=pygame.image.load(io.BytesIO(data),'frame.tga')
                                    assert decoded.get_size()==size
                                    assert pygame.image.tobytes(decoded,'RGB')==pygame.image.tobytes(screen,'RGB')
                                    image=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),actual_encoding='TGA',png_magic=data.startswith(b'\x89PNG\r\n\x1a\n'),label=last['python']['frame_format'],size=size)
                                cases.append(dict(mode=mode,display=display,threads=threads,surface_size=size,initial=initial,steps=steps,image=image))
                        finally:world.reset()
    raw=json.dumps(cases,ensure_ascii=False,separators=(',',':')).encode();path=out/'raw.json.xz';path.write_bytes(lzma.compress(raw))
    compact=dict(source_sha=git(src,'rev-parse','HEAD'),source_dirty=git(src,'status','--porcelain'),tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),api=API_VERSION,
                 extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),expected_supported=args.expect_supported,cases=len(cases),
                 response_equal=sum(c['steps'][-1]['response_equal'] for c in cases),state_equal=sum(c['steps'][-1]['state_equal'] for c in cases),
                 all_guards_passed=True,full_migration=False,actual_windows=False,raw=dict(path=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,decoded_sha256=hashlib.sha256(raw).hexdigest(),decoded_bytes=len(raw)))
    assert not compact['source_dirty'];(out/'compact.json').write_text(json.dumps(compact,indent=2)+'\n');print(json.dumps(compact))


if __name__=='__main__':main()
