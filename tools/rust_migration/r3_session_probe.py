"""Owned offline scene: HUD/window lifecycle and exact native replay (no capacity claim)."""
import argparse
from copy import deepcopy
import hashlib
import json
import lzma
import os
from pathlib import Path
import platform
import sys
from unittest.mock import patch
from r3_observations_probe import git


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay_cases(cases, runtime_type):
    for case in cases:
        with runtime_type(case['initial'], threads=case['threads']) as runtime:
            assert runtime.take_presentation_delta() == case['initial_delta']
            for node in case['nodes']:
                params = deepcopy(node['parameters'])
                if node['op'] == 'step':
                    runtime.step(**params)
                    result = None
                else:
                    if 'position' in params:
                        params['position'] = tuple(params['position'])
                    result = runtime.execute_control(**params)
                assert runtime.export_state() == node['state']
                delta = runtime.take_presentation_delta()
                assert delta == node['delta']
                assert (delta['events'] if node['op'] == 'step' else result) == node['result']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--replay', type=Path)
    parser.add_argument('--driver', choices=['cocoa', 'dummy'], default='cocoa')
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.chdir(source); sys.path.insert(0, str(source))
    os.environ['HEADLESS'] = '0'; os.environ['SDL_VIDEODRIVER'] = args.driver
    import pygame
    from framework.engine.game_engine import GameEngine
    from framework.engine import RMS
    from framework.engine.events import EBS
    from rotk_env import components as c
    from rotk_env.prefabs.config import Faction
    from rotk_env.runtime.bootstrap import encode
    from rotk_env.runtime.session import NativeSession
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.runtime.world_presentation import WorldPresentation
    from star_native import API_VERSION, _native

    if args.replay:
        cases = json.loads(lzma.decompress(args.replay.resolve().read_bytes()))
        replay_cases(cases, RustRuntime)
        result = dict(all_passed=True, cases=len(cases), nodes=sum(len(c['nodes']) for c in cases),
                      raw_sha256=digest(args.replay.resolve()), source_sha=git(source, 'rev-parse', 'HEAD'))
        (output / 'replay.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result))
        return
    GameEngine(title='STAR Rust scene/HUD verification', width=1200, height=800, fps=30)
    def listeners():
        return {kind: tuple(items) for kind, items in EBS._listeners.items() if items}
    baseline = listeners()
    cases, pictures = [], []
    original_apply = WorldPresentation.apply
    collected = []
    def capture(self, delta):
        collected.append(deepcopy(delta))
        return original_apply(self, delta)
    try:
        with patch.object(WorldPresentation, 'apply', capture):
            for mode in ('real_time', 'turn_based'):
                for threads in (1, 2, 4):
                    collected.clear()
                    case = dict(mode=mode, threads=threads, nodes=[])
                    with NativeSession(display='window', mode=mode, scenario='chibi-small', seed=42, threads=threads) as scene:
                        case['initial'] = scene.runtime.export_state()
                        case['initial_delta'] = collected.pop()
                        uid = next(uid for uid in scene.world.query().with_component(c.Unit).ordered_entities()
                                   if scene.world.get_component(uid, c.Unit).faction == Faction.WEI)
                        ui = scene.world.get_singleton_component(c.UIState)
                        ui.selected_unit = uid; ui.show_coordinates = True
                        ui.show_stats = True
                        def node(op, parameters):
                            collected.clear()
                            if op == 'step':
                                result = scene.step(**parameters)
                            else:
                                result = scene.controls.execute(**parameters)
                            assert len(collected) == 1
                            delta = collected[0]
                            state = scene.runtime.export_state()
                            assert encode(scene.world.get_singleton_component(c.BattleLog)) == state['singletons']['BattleLog']
                            assert encode(scene.world.get_singleton_component(c.GameStats).faction_stats) == state['singletons']['GameStats']['faction_stats']
                            case['nodes'].append(dict(op=op, parameters=parameters, result=result, delta=delta, state=state))
                            return result
                        result = node('control', dict(kind='move', unit_id=uid, position=(1, 2), wall_time=1720000000.))
                        assert result['success'], result
                        for frame in range(90):
                            if frame == 20:
                                node('control', dict(kind='set_fog', enabled=False, wall_time=1720000000. + frame/30))
                                ui.show_stats = False; ui.show_help = True
                            if frame == 40:
                                node('control', dict(kind='wait', unit_id=uid, wall_time=1720000000. + frame/30))
                                ui.show_help = False
                            node('step', dict(dt=1/30, wall_time=1720000000. + frame/30))
                            state = scene.runtime.export_state()
                            RMS.screen.fill((0, 0, 0)); scene.update_display(1/30)
                            RMS.update(); pygame.display.flip()
                            assert scene.runtime.export_state() == state
                            if threads == 1 and frame in (0, 25, 60):
                                path = output / f'{mode}-{frame:03}.png'
                                pygame.image.save(RMS.screen, path)
                                pictures.append(dict(path=path.name, sha256=digest(path)))
                        position = scene.world.get_component(uid, c.HexPosition)
                        assert (position.col, position.row) == (1, 2)
                        old_controls = scene.controls
                        case['guards'] = dict(move_arrived=True, rendering_read_only=True, hud_matches=True, frames=90)
                    assert listeners() == baseline
                    try:
                        old_controls.execute('set_fog', enabled=True)
                    except RuntimeError:
                        pass
                    else:
                        raise AssertionError('Closed scene accepted input')
                    case['guards']['subscriptions_restored'] = True
                    cases.append(case)
        # Decode the exact serialized form used by the archived raw trace.
        replay_cases(json.loads(json.dumps(cases)), RustRuntime)
        for case in cases:
            case['guards']['independent_replay'] = True
    finally:
        pygame.quit()
    raw = json.dumps(cases, ensure_ascii=False, separators=(',', ':')).encode()
    raw_path = output / 'replay.json.xz'
    raw_path.write_bytes(lzma.compress(raw))
    compact = dict(all_passed=True, cases=[dict(mode=x['mode'], threads=x['threads'], nodes=len(x['nodes']), guards=x['guards']) for x in cases],
        source_sha=git(source, 'rev-parse', 'HEAD'), tool_sha=git(Path(__file__).resolve().parents[2], 'rev-parse', 'HEAD'),
        python=sys.version, platform=platform.platform(), api=API_VERSION, extension_sha256=digest(Path(_native.__file__)),
        source_dirty=git(source, 'status', '--porcelain'),
        tool_dirty=git(Path(__file__).resolve().parents[2], 'status', '--porcelain', '--', str(Path(__file__).resolve())),
        chrome_running=os.system("pgrep -x 'Google Chrome' >/dev/null") == 0,
        driver=args.driver, window=[1200,800], pictures=pictures,
        raw=dict(path=raw_path.name, bytes=raw_path.stat().st_size, sha256=digest(raw_path), decoded_bytes=len(raw), decoded_sha256=hashlib.sha256(raw).hexdigest()),
        capacity_claim=False, game_scene_cli_claim=False, physical_input_claim=False)
    assert not compact['source_dirty'] and not compact['tool_dirty']
    (output / 'compact.json').write_text(json.dumps(compact, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({key: compact[key] for key in ('all_passed','source_sha','tool_sha','raw')}, indent=2))


if __name__ == '__main__':
    main()
