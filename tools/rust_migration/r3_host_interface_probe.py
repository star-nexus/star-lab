"""Offline host capability A/B or bounded real CLI loop; no network/capacity claim."""
import argparse
from contextlib import redirect_stderr
import hashlib
import io
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch
from r3_observations_probe import git


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--entry',choices=('capability','headless','skip-start'),default='capability')
    parser.add_argument('--mode',choices=('real_time','turn_based'),default='real_time')
    args=parser.parse_args();source=args.source.resolve();output=args.output.resolve()
    os.chdir(source);sys.path.insert(0,str(source))
    os.environ['HEADLESS']='1' if args.entry=='headless' else '0'
    os.environ['SDL_VIDEODRIVER']='dummy' if args.entry in ('headless','capability') else 'cocoa'
    from star_native import API_VERSION,_native
    from rotk_env import main as entry
    from rotk_env.runtime.bootstrap import prepare_scene
    from rotk_env.runtime.native import RustRuntime
    result=dict(source_sha=git(source,'rev-parse','HEAD'),source_dirty=git(source,'status','--porcelain'),
        tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'),api=API_VERSION,
        extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(),entry=args.entry,mode=args.mode,
        network=False,capacity=False)
    assert not result['source_dirty']
    if args.entry=='capability':
        with patch.object(sys,'argv',['star','--backend','rust','--no-hub']),redirect_stderr(io.StringIO()):
            try:result['cli_backend']=entry.parse_arguments().backend
            except SystemExit as exc:result['cli_error_exit']=exc.code
        initial=prepare_scene(mode=args.mode,scenario='chibi-small',seed=42,display='none')
        result['report_context']=initial.get('interface',{}).get('report_context')
        with RustRuntime(initial) as runtime:
            registration=runtime.execute_action('register_agent_info',dict(faction='wei',provider='synthetic',model_id='fake',base_url='http://local'),agent_id='a',wall_time=1720000000.,registration_time='2024-07-03T09:46:40')
            assert registration['success']
            requests=[('strategy_ping',dict(faction='wei',score=.75,evidence='probe')),('report_llm_stats',dict(faction='wei',api_stats=dict(total_calls=2,successful_calls=1))),('retrieve_game_status',{})]
            result['responses']={name:runtime.execute_action(name,params,agent_id='a',wall_time=1720000001.) for name,params in requests}
            result['prepare_game_end_available']=hasattr(runtime,'prepare_game_end')
        if API_VERSION>=8:
            assert result['cli_backend']=='rust' and result['report_context'] and result['prepare_game_end_available']
            assert all(r['success'] for r in result['responses'].values())
        else:
            assert result['cli_error_exit']==2 and not result['prepare_game_end_available']
            assert all(not r['success'] for r in result['responses'].values())
    else:
        import pygame
        from framework.engine.game_engine import GameEngine
        from rotk_env.prefabs.config import GameConfig
        sessions=[];dts=[];original=GameEngine._update
        def update(engine):
            original(engine)
            scene=engine.scene_manager._current_scene
            session=getattr(scene,'native_session',None)
            if session is not None and session not in sessions:sessions.append(session)
            dts.append(engine.delta_time)
            if len(dts)==12:pygame.event.post(pygame.event.Event(pygame.QUIT))
            assert len(dts)<20,'SDL quit did not stop loop'
        argv=['star','--backend','rust','--no-hub','--'+args.entry,'--mode',args.mode,'--scenario','chibi-small','--seed','42']
        with patch.object(sys,'argv',argv),patch.object(GameEngine,'_update',update),patch.object(GameConfig,'FPS',30):
            entry.main()
        assert len(sessions)==1 and sessions[0].closed and sessions[0].failure is None
        assert len(dts)>=12 and all(dt==1/30 for dt in dts)
        result.update(argv=argv,frames=len(dts),fixed_dt=1/30,native_worlds=len(sessions),closed=True,quit='synthetic SDL',driver=os.environ['SDL_VIDEODRIVER'],pygame_closed=not pygame.get_init())
        assert result['pygame_closed']
    result['all_passed']=True;output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(all_passed=True,entry=args.entry,api=API_VERSION)))


if __name__=='__main__':main()
