"""Real scene/menu/offline settlement lifecycle; injected wall time, no capacity claim."""
import argparse
from contextlib import ExitStack, chdir
from copy import deepcopy
import datetime
import hashlib
import json
import lzma
import os
from pathlib import Path
import platform
import sys
import time
from unittest.mock import patch
from r3_observations_probe import git


def file_sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def replay(cases, Runtime):
    count=0
    for case in cases:
        with Runtime(case['initial'],threads=case['threads']) as runtime:
            for node in case['nodes']:
                kwargs=deepcopy(node['kwargs']);args=deepcopy(node['args'])
                if node['method']=='execute_control' and 'position' in kwargs:
                    kwargs['position']=tuple(kwargs['position'])
                result=getattr(runtime,node['method'])(*args,**kwargs)
                assert result==node['result'],(case['entry'],node['method'])
                assert runtime.export_state()==node['state']
                count+=1
    return count


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--replay',type=Path)
    args=parser.parse_args()
    source=args.source.resolve();output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    os.chdir(source);sys.path.insert(0,str(source));os.environ['HEADLESS']='0';os.environ['SDL_VIDEODRIVER']='cocoa'
    import pygame
    from star_native import _native,API_VERSION
    from framework.engine.game_engine import GameEngine
    from framework.engine.events import EBS
    from rotk_env import components as c
    from rotk_env.components.start_menu import StartMenuConfig,CONTROLLER_NONE
    from rotk_env.components.settlement_report import SettlementReport
    from rotk_env.prefabs.config import GameConfig,GameMode,Faction,PlayerType
    from rotk_env.scenes import StartScene,GameScene,GameOverScene
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.runtime.session import NativeSession
    from rotk_env.runtime.settlement import NativeSettlementFormatter
    if args.replay:
        cases=json.loads(lzma.decompress(args.replay.resolve().read_bytes()))
        count=replay(cases,RustRuntime)
        result=dict(all_passed=True,cases=len(cases),nodes=count,raw_sha256=file_sha(args.replay.resolve()),source_sha=git(source,'rev-parse','HEAD'))
        (output/'replay.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return
    engine=GameEngine(title='STAR Rust offline scene validation',width=1200,height=800,fps=30)
    engine.runtime_backend='rust';engine.native_threads=1
    GameConfig.WINDOW_WIDTH=1200;GameConfig.WINDOW_HEIGHT=800
    manager=engine.scene_manager
    for name,cls in [('start',StartScene),('game',GameScene),('game_over',GameOverScene)]:manager.register_scene(name,cls)
    def listeners():return {k:tuple(v) for k,v in EBS._listeners.items() if v}
    baseline=listeners();cases=[];active=[None];now=[1720000000.]
    original_export=RustRuntime.export_state;original_init=RustRuntime.__init__
    def initialize(self,initial_state,*,threads=1):
        original_init(self,initial_state,threads=threads)
        active[0]['initial']=deepcopy(initial_state);active[0]['threads']=threads
    def recorded(method):
        original=getattr(RustRuntime,method)
        def invoke(self,*args,**kwargs):
            if method!='take_presentation_delta':kwargs.setdefault('wall_time',now[0])
            result=original(self,*args,**kwargs)
            active[0]['nodes'].append(dict(method=method,args=deepcopy(args),kwargs=deepcopy(kwargs),result=deepcopy(result),state=original_export(self)))
            return result
        return invoke
    original_display=NativeSession.update_display
    def display(self,*args,**kwargs):
        before=original_export(self.runtime);result=original_display(self,*args,**kwargs)
        assert original_export(self.runtime)==before
        active[0]['rendered_frames']+=1
        return result
    original_save=NativeSettlementFormatter._save_report_to_files
    def save(self,data):
        active[0]['report_generated']=True
        folder=output/active[0]['name'];folder.mkdir(exist_ok=True)
        with chdir(folder):original_save(self,data)
    real_datetime=datetime.datetime
    class Frozen(real_datetime):
        @classmethod
        def now(cls,tz=None):return cls.fromtimestamp(now[0],tz)
    try:
        with ExitStack() as stack:
            stack.enter_context(patch('time.time',lambda:now[0]));stack.enter_context(patch('datetime.datetime',Frozen))
            stack.enter_context(patch.object(RustRuntime,'__init__',initialize))
            for method in ('step','execute_control','finish_human_turn','prepare_game_end','take_presentation_delta'):
                stack.enter_context(patch.object(RustRuntime,method,recorded(method)))
            stack.enter_context(patch.object(NativeSession,'update_display',display))
            stack.enter_context(patch.object(NativeSettlementFormatter,'_save_report_to_files',save))
            stack.enter_context(patch.object(GameConfig,'MAX_REALTIME_SECONDS',1.0))
            stack.enter_context(patch.object(GameConfig,'MAX_TURNS',1))
            for mode in ('real_time','turn_based'):
                for entry in ('headless','skip-start','menu'):
                    case=dict(name=f'{mode}-{entry}',mode=mode,entry=entry,nodes=[],rendered_frames=0,report_generated=False)
                    active[0]=case;now[0]+=1000
                    options=dict(mode=mode,players={Faction.WEI:PlayerType.HUMAN,Faction.SHU:PlayerType.HUMAN},scenario='chibi-small',hub_url=None,seed=42)
                    if entry=='headless':manager.switch_to('game',headless=True,**options)
                    elif entry=='skip-start':manager.switch_to('start',auto_start_config=options)
                    else:
                        manager.switch_to('start')
                        menu=manager._current_scene
                        config=menu.world.get_singleton_component(StartMenuConfig)
                        config.selected_mode=GameMode(mode);config.selected_scenario='chibi-small'
                        config.selected_players=options['players'];config.selected_controller_backend=CONTROLLER_NONE
                        menu._start_game()
                    if manager._current_scene.name=='start':
                        engine.delta_time=1/30;engine._update()
                    scene=manager._current_scene
                    assert scene.name=='game' and scene.backend=='rust'
                    old_session=scene.native_session
                    uid=next(uid for uid in scene.world.query().with_component(c.Unit).ordered_entities() if scene.world.get_component(uid,c.Unit).faction==Faction.WEI)
                    scene.world.get_singleton_component(c.UIState).selected_unit=uid
                    assert old_session.controls.execute('move',unit_id=uid,position=(1,2))['success']
                    jumped=False
                    for frame in range(120):
                        now[0]+=1/30
                        if mode=='turn_based' and frame in (25,45):
                            pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE))
                        if frame==5:
                            pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_v))
                        engine.delta_time=1/30;engine._update()
                        if entry!='headless' and frame==15:
                            pygame.image.save(engine.screen,output/(case['name']+'.png'))
                        if case['report_generated']:break
                        if scene.native_host.game_end_time is not None and not jumped:
                            now[0]+=61;jumped=True
                    assert case['report_generated'] and jumped
                    assert scene._headless_exit_triggered if entry=='headless' else manager._current_scene.name=='game_over'
                    if entry=='headless':scene.exit()
                    else:
                        # Real GameOver -> menu path, then close its subscriptions.
                        manager._current_scene._restart_game()
                        assert manager._current_scene.name=='start'
                        manager._current_scene.exit()
                    assert old_session.closed
                    assert listeners()==baseline
                    manager._current_scene=None
                    case['guards']=dict(report=True,exit=True,subscriptions_restored=True,rendering_read_only=True,backend_preserved=True)
                    cases.append(case)
        count=replay(json.loads(json.dumps(cases)),RustRuntime)
    finally:pygame.quit()
    raw=json.dumps(cases,ensure_ascii=False,separators=(',',':')).encode();path=output/'trace.json.xz';path.write_bytes(lzma.compress(raw))
    compact=dict(all_passed=True,source_sha=git(source,'rev-parse','HEAD'),tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),
        source_dirty=git(source,'status','--porcelain'),api=API_VERSION,extension_sha256=file_sha(Path(_native.__file__)),python=sys.version,platform=platform.platform(),
        driver='cocoa',chrome_running=os.system("pgrep -x 'Google Chrome' >/dev/null")==0,cases=[{k:v for k,v in c.items() if k not in ('nodes','initial')} for c in cases],
        replay_nodes=count,raw=dict(path=path.name,bytes=path.stat().st_size,sha256=file_sha(path),decoded_bytes=len(raw),decoded_sha256=hashlib.sha256(raw).hexdigest()),
        wall_clock='injected; 61 second jump for settlement',capacity_claim=False,network_claim=False,
        controls='direct local move; synthetic SDL V and SPACE; menu callbacks invoked directly')
    assert not compact['source_dirty']
    (output/'compact.json').write_text(json.dumps(compact,indent=2)+'\n');print(json.dumps(dict(all_passed=True,nodes=count)))


if __name__=='__main__':main()
