"""VLM reads actual Cocoa framebuffer; does not introduce per-Agent rendering."""
import argparse
import base64
from copy import deepcopy
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
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    src=a.source.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);os.chdir(src);sys.path.insert(0,str(src));os.environ.update(HEADLESS='0',SDL_VIDEODRIVER='cocoa')
    import pygame
    from star_native import API_VERSION,_native
    from framework.engine.game_engine import GameEngine
    from rotk_env import components as c
    from rotk_env.prefabs.config import GameConfig,Faction,PlayerType
    from rotk_env.runtime import session as session_module
    from rotk_env.scenes import GameScene
    from rotk_env.systems.llm_action_handler import LLMActionHandler
    engine=GameEngine(title='STAR native VLM compatibility',width=1200,height=800,fps=30)
    engine.runtime_backend='rust';engine.native_threads=1;engine.scene_manager.register_scene('game',GameScene)
    GameConfig.WINDOW_WIDTH=1200;GameConfig.WINDOW_HEIGHT=800
    original=session_module.prepare_display_world
    def prepare(**kwargs):
        world,initial=original(**kwargs)
        names=tuple(initial['singletons']['MatchRules']['game_actions'])+('get_faction_state_vlm',)
        world.add_singleton_component(c.MatchRules(game_actions=names));initial['singletons']['MatchRules']['game_actions']=list(names)
        return world,initial
    now=[1720000000.];cases=[]
    try:
        with patch.object(session_module,'prepare_display_world',prepare),patch('time.time',lambda:now[0]):
            for mode in ['real_time','turn_based']:
                engine.scene_manager.switch_to('game',mode=mode,scenario='chibi-small',seed=42,hub_url=None,players={Faction.WEI:PlayerType.HUMAN,Faction.SHU:PlayerType.HUMAN})
                scene=engine.scene_manager._current_scene;runtime=scene.native_session.runtime
                reg=runtime.execute_action('register_agent_info',dict(faction='wei',provider='synthetic',model_id='vlm-probe',base_url='http://local'),agent_id='a');assert reg['success']
                for view in [Faction.WEI,Faction.SHU]:
                    ui=scene.world.get_singleton_component(c.UIState);ui.view_faction=view
                    for _ in range(3):now[0]+=1/30;engine.delta_time=1/30;engine._update()
                    before=runtime.export_state();rgb=pygame.image.tobytes(engine.screen,'RGB')
                    reference,error=LLMActionHandler._capture_frame_base64(None);assert error is None
                    plain=runtime.get_faction_state('wei',agent_id='a')
                    result=runtime.execute_action('get_faction_state_vlm',dict(faction='wei'),agent_id='a')
                    assert result['frame_base64']==reference and result['frame_format']=='png'
                    assert {k:v for k,v in result.items() if not k.startswith('frame_')}==plain
                    data=base64.b64decode(result['frame_base64']);image=pygame.image.load(io.BytesIO(data),'frame.tga')
                    decoded_rgb=pygame.image.tobytes(image,'RGB')
                    if decoded_rgb != rgb:
                        name=mode+'-'+view.value
                        pygame.image.save(engine.screen,out/(name+'-screen.png'))
                        pygame.image.save(image,out/(name+'-decoded.png'))
                        (out/(name+'-frame.tga')).write_bytes(data)
                        different=[i for i,(x,y) in enumerate(zip(rgb,decoded_rgb)) if x!=y]
                        mismatch=dict(source_sha=git(src,'rev-parse','HEAD'),tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),
                            legacy_and_native_bytes_equal=result['frame_base64']==reference,name=name,size=engine.screen.get_size(),decoded_size=image.get_size(),
                            masks=engine.screen.get_masks(),decoded_masks=image.get_masks(),rgb_bytes=len(rgb),decoded_bytes=len(decoded_rgb),
                            changed_channels=len(different),first_difference=different[0] if different else None,
                            screen_now_equal=pygame.image.tobytes(engine.screen,'RGB')==rgb)
                        (out/'pixel-mismatch.json').write_text(json.dumps(mismatch,indent=2)+'\n')
                        raise AssertionError(mismatch)
                    assert ui.view_faction==view and pygame.image.tobytes(engine.screen,'RGB')==rgb
                    after=runtime.export_state();comparison=deepcopy(after)
                    for key in ['action_counts_by_agent','action_counts_by_faction']:
                        comparison['singletons']['GameStats'][key]=before['singletons']['GameStats'][key]
                    assert comparison==before
                    name=mode+'-'+view.value;pygame.image.save(engine.screen,out/(name+'.png'));(out/(name+'.tga')).write_bytes(data)
                    cases.append(dict(name=name,mode=mode,requested_faction='wei',display_view=view.value,before=before,result=result,plain=plain,after=after,frame=dict(size=image.get_size(),png_magic=data.startswith(b'\x89PNG\r\n\x1a\n'),actual_encoding='TGA',sha256=hashlib.sha256(data).hexdigest(),rgb_sha256=hashlib.sha256(rgb).hexdigest())))
                scene.exit();engine.scene_manager._current_scene=None
    finally:
        if engine.scene_manager._current_scene is not None:engine.scene_manager._current_scene.exit()
        pygame.quit()
    raw=json.dumps(cases,ensure_ascii=False,separators=(',',':')).encode();path=out/'raw.json.xz';path.write_bytes(lzma.compress(raw))
    result=dict(source_sha=git(src,'rev-parse','HEAD'),source_dirty=git(src,'status','--porcelain'),tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),api=API_VERSION,extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),driver='cocoa',cases=len(cases),all_guards_passed=True,owner_thread=True,network=False,capacity=False,raw=dict(path=path.name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),decoded_bytes=len(raw),decoded_sha256=hashlib.sha256(raw).hexdigest()))
    assert not result['source_dirty'];(out/'compact.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
