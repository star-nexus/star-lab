"""Cocoa SDL input -> Python adapters -> Rust authority -> existing rendering.

Synthetic SDL events exercise the real input dispatcher; no manual-play, full
GameScene, Protocol, HUD/settlement or capacity acceptance is claimed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
from r3_observations_probe import git, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--driver', choices=['cocoa', 'dummy'], default='cocoa')
    args = parser.parse_args()
    source = args.source.resolve(); output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.chdir(source); sys.path.insert(0, str(source))
    os.environ['HEADLESS'] = '0'; os.environ['SDL_VIDEODRIVER'] = args.driver
    import pygame
    from framework.engine.game_engine import GameEngine
    from framework.engine.inputs import InputSystem
    from framework.engine import RMS
    from rotk_env import components as c
    from rotk_env.prefabs.config import GameMode, Faction, PlayerType
    from rotk_env.runtime.bootstrap import export_initial_state
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.runtime.local_controls import LocalControls
    from rotk_env.runtime import native_input as ni
    from rotk_env.runtime.world_presentation import WorldPresentation
    from rotk_env.runtime.window_presentation import attach_battlefield_renderers
    from rotk_env.systems.window_input_system import InputHandlingSystem as LegacyInput
    from rotk_env.systems.unit_action_button_system import UnitActionButtonSystem as LegacyPanel
    from rotk_env.systems.ui_button_system import UIButtonSystem as LegacyToolbar
    from rotk_env.systems.window_vision_system import VisionSystem
    from rotk_env.tests.test_native_combat_presentation import make
    from rotk_env.tests.test_native_world_presentation import detached_world
    from star_native import _native, API_VERSION

    GameEngine(title='STAR Rust local input verification', width=1200, height=800, fps=30)
    cases = []; screenshots = []
    try:
        for mode in (GameMode.REAL_TIME, GameMode.TURN_BASED):
            for kind in ('melee', 'ranged'):
                w, (a, b, target), llm = make('window', mode, kind, critical=True)
                llm.enabled = False
                players = list(w.query().with_component(c.Player).ordered_entities())
                for pid in players:
                    if w.get_component(pid, c.Player).faction == Faction.SHU:
                        w.get_component(pid, c.Player).player_type = PlayerType.AI
                w.add_singleton_component(c.TurnManager(players))
                for uid in (a, b, target): w.add_component(uid, c.Vision(range=4))
                vision = VisionSystem(); w.add_system(vision); vision.update(0.)
                w.add_system(LegacyInput()); w.add_system(LegacyPanel()); w.add_system(LegacyToolbar())
                camera = w.get_singleton_component(c.Camera)
                camera.zoom = 1.; camera.offset_x = 500; camera.offset_y = 400
                initial = export_initial_state(w, display='window')
                display = detached_world(w)
                events = []; inputs_log = []; frames = []
                presentation = WorldPresentation(display)
                with RustRuntime(initial) as native:
                    w.reset()  # In particular, unsubscribe the old input callbacks.
                    controls = LocalControls(native, presentation, initial, on_events=events.extend)
                    controls.refresh()
                    attach_battlefield_renderers(presentation)
                    inputs = ni.InputHandlingSystem(controls)
                    buttons = ni.UnitActionButtonSystem(controls)
                    toolbar = ni.UIButtonSystem(controls)
                    counter = display.entity_counter
                    for system in (inputs, buttons, toolbar): display.add_system(system)
                    assert display.entity_counter == counter == initial['entity_counter']
                    ticker = pygame.time.Clock()
                    def key(code, frame):
                        inputs_log.append(dict(frame=frame, kind='SDL_KEYDOWN', key=code))
                        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=code))
                    def click(pos, frame, label):
                        pos = tuple(round(v) for v in pos)
                        inputs_log.append(dict(frame=frame, kind='SDL_MOUSEBUTTONDOWN', pos=pos, label=label))
                        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
                    for frame in range(120):
                        if frame == 0:
                            key(pygame.K_v, frame)
                            click(inputs._hex_to_screen((0, 0)), frame, 'select moving unit')
                        if frame == 1: click(inputs._hex_to_screen((-1, 1)), frame, 'move destination')
                        if frame == 6:
                            key(pygame.K_ESCAPE, frame)
                            click(inputs._hex_to_screen((-1, 0)), frame, 'select attacker')
                        if frame == 8:
                            panel = display.get_singleton_component(c.UnitActionPanel)
                            index = next(i for i, action in enumerate(panel.available_actions) if action.action_type.value == 'attack' and action.enabled)
                            click((panel.x + 30, panel.y + 45 + index * 40 + 15), frame, 'attack panel button')
                        if frame == 9:
                            assert inputs._targeting_action == 'attack'
                            click(inputs._hex_to_screen((1, 1)), frame, 'attack target')
                        if frame == 14: key(pygame.K_ESCAPE, frame)
                        if frame == 15: display.get_singleton_component(c.Camera).zoom = .5
                        if frame == 20: key(pygame.K_1, frame)
                        if frame == 21: key(pygame.K_3, frame)
                        if frame == 22: key(pygame.K_2, frame)
                        if frame == 30: display.get_singleton_component(c.Camera).offset_x = 580
                        if frame == 40: display.get_singleton_component(c.Camera).zoom = 1.25
                        if frame == 80:
                            toolbar._end_turn()
                            inputs_log.append(dict(frame=frame, kind='toolbar_command', label='separate local toolbar contract'))
                        if frame == 81: key(pygame.K_SPACE, frame)
                        InputSystem().update()
                        if frame == 0: assert display.get_singleton_component(c.UIState).selected_unit == b
                        if frame == 9:
                            assert inputs._targeting_action is None
                            assert display.get_component(target, c.UnitCount).current_count < 10000
                        native.step(1 / 30); controls.refresh()
                        before = native.export_state()
                        RMS.screen.fill((0, 0, 0)); display.update(1 / 30); RMS.update(); pygame.display.flip()
                        assert native.export_state() == before
                        frames.append(dict(frame=frame, state_digest=digest(before), units=len(display.query().with_component(c.Unit).entities()),
                            damage=len(display.query().with_component(c.DamageNumber).entities()), projectiles=len(display.query().with_component(c.ProjectileAnimation).entities())))
                        if frame in (0, 10, 16, 55):
                            path = output / f'{mode.value}-{kind}-{frame:03d}.png'
                            pygame.image.save(RMS.screen, path)
                            screenshots.append(dict(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
                        ticker.tick(30)
                    pos = display.get_component(b, c.HexPosition)
                    assert (pos.col, pos.row) == (-1, 1)
                    assert any(row['damage'] >= 2 for row in frames)
                    if kind == 'ranged': assert any(row['projectiles'] for row in frames)
                    assert all(not rows for rows in native.export_state()['systems']['VisualLifecycle'].values())
                    cases.append(dict(mode=mode.value, kind=kind, inputs=inputs_log, frames=frames, events=events, all_passed=True))
                display.reset()
        raw = dict(source_sha=git(source, 'rev-parse', 'HEAD'), source_dirty=git(source, 'status', '--porcelain'),
            tool_sha=git(Path(__file__).resolve().parents[2], 'rev-parse', 'HEAD'), tool_dirty=git(Path(__file__).resolve().parents[2], 'status', '--porcelain', '--', str(Path(__file__).resolve())),
            extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(), api=API_VERSION,
            python=sys.version, platform=platform.platform(), driver=pygame.display.get_driver(), window=list(RMS.screen.get_size()),
            chrome_running=os.system("pgrep -x 'Google Chrome' >/dev/null") == 0, cases=cases, screenshots=screenshots,
            all_passed=True, capacity_claim=False, full_scene_claim=False, input_source='synthetic SDL events; toolbar command separately invoked')
        assert not raw['source_dirty'] and not raw['tool_dirty']
        (output / 'render.json').write_text(json.dumps(raw, indent=2) + '\n')
        print(json.dumps(dict(all_passed=True, frames=sum(len(c['frames']) for c in cases), driver=raw['driver'])))
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()
