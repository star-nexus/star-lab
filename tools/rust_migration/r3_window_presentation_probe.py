"""Rendered battlefield integration check; no capacity or frame-time acceptance."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
from r3_observations_probe import git


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--driver", choices=("cocoa", "dummy"), default="cocoa")
    p.add_argument(
        "--selection",
        action="store_true",
        help="Show the legacy selection/range overlays",
    )
    args = p.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.chdir(source)
    sys.path.insert(0, str(source))
    os.environ["HEADLESS"] = "0"
    os.environ["SDL_VIDEODRIVER"] = args.driver
    import pygame
    from framework.engine.game_engine import GameEngine
    from framework.engine import RMS
    from rotk_env import components as c
    from rotk_env.prefabs.config import GameMode, GameConfig, Faction
    from rotk_env.runtime.bootstrap import export_initial_state
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.runtime.world_presentation import WorldPresentation
    from rotk_env.runtime.window_presentation import attach_battlefield_renderers
    from rotk_env.tests.test_native_combat_presentation import make
    from rotk_env.tests.test_native_world_presentation import detached_world
    from rotk_env.systems.window_vision_system import VisionSystem
    from star_native import _native

    engine = GameEngine(
        title="STAR Rust battlefield verification", width=1200, height=800, fps=30
    )
    cases = []
    screenshots = []
    try:
        for mode in (GameMode.REAL_TIME, GameMode.TURN_BASED):
            for kind in ("melee", "ranged"):
                source_world, (a, b, target), llm = make(
                    "window", mode, kind, critical=True
                )
                for uid in (a, b, target):
                    source_world.add_component(uid, c.Vision(range=4))
                vision = VisionSystem()
                source_world.add_system(vision)
                vision.update(0.0)
                source_world.add_singleton_component(
                    c.UIState(
                        view_faction=Faction.WEI, show_coordinates=True, selected_unit=a
                    )
                )
                camera = source_world.get_singleton_component(c.Camera)
                camera.zoom = 1.0
                camera.offset_x = 600
                camera.offset_y = 400
                display = detached_world(source_world)
                presentation = WorldPresentation(display)
                attach_battlefield_renderers(presentation)
                counts = []
                events = []
                try:
                    with RustRuntime(
                        export_initial_state(source_world, display="window")
                    ) as native:
                        presentation.apply(native.take_presentation_delta())
                        assert native.execute_action(
                            "register_agent_info",
                            dict(
                                faction="wei",
                                provider="synthetic",
                                model_id="fake",
                                base_url="https://host",
                            ),
                            agent_id="alpha",
                        )["success"]
                        assert native.execute_action(
                            "move",
                            {"unit_id": b, "target_position": {"col": -1, "row": 1}},
                            agent_id="alpha",
                        )["success"]
                        attack = native.execute_action(
                            "attack",
                            {"unit_id": a, "target_id": target},
                            agent_id="alpha",
                        )
                        assert (
                            attack["success"]
                            and attack["battle_summary"]["battle_result"]["is_critical"]
                        )
                        for frame in range(120):
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    raise RuntimeError(
                                        "Window closed before completion"
                                    )
                            if frame == 12:
                                display.get_singleton_component(c.Camera).zoom = 0.5
                            if frame == 30:
                                display.get_singleton_component(c.Camera).offset_x = 680
                            if frame == 60:
                                display.get_singleton_component(c.Camera).zoom = 1.25
                            if frame == 90:
                                display.get_singleton_component(
                                    c.UIState
                                ).show_coordinates = False
                            native.step(1 / 30)
                            delta = native.take_presentation_delta()
                            events.extend(presentation.apply(delta))
                            # Rendering may mutate only the Python presentation cache.
                            before = native.export_state()
                            RMS.screen.fill((0, 0, 0))
                            display.update(1 / 30)
                            RMS.update()
                            pygame.display.flip()
                            assert native.export_state() == before
                            counts.append(
                                dict(
                                    frame=frame,
                                    units=len(
                                        display.query().with_all(c.Unit).entities()
                                    ),
                                    damage=len(
                                        display.query()
                                        .with_all(c.DamageNumber)
                                        .entities()
                                    ),
                                    projectile=len(
                                        display.query()
                                        .with_all(c.ProjectileAnimation)
                                        .entities()
                                    ),
                                    effects=len(
                                        display.query()
                                        .with_all(c.EffectAnimation)
                                        .entities()
                                    ),
                                )
                            )
                            if frame in (2, 14, 61):
                                path = output / f"{mode.value}-{kind}-{frame:03d}.png"
                                pygame.image.save(RMS.screen, path)
                                screenshots.append(
                                    dict(
                                        file=path.name,
                                        sha256=hashlib.sha256(
                                            path.read_bytes()
                                        ).hexdigest(),
                                    )
                                )
                            pygame.time.Clock().tick(30)
                        assert all(
                            not rows
                            for rows in native.export_state()["systems"][
                                "VisualLifecycle"
                            ].values()
                        )
                        assert (
                            counts[-1]["damage"]
                            == counts[-1]["projectile"]
                            == counts[-1]["effects"]
                            == 0
                        )
                        assert any(row["damage"] >= 2 for row in counts)
                        if kind == "ranged":
                            assert any(row["projectile"] for row in counts)
                        cases.append(
                            dict(
                                mode=mode.value,
                                kind=kind,
                                frames=120,
                                counts=counts,
                                events=events,
                                all_passed=True,
                            )
                        )
                finally:
                    source_world.reset()
                    display.reset()
        raw = dict(
            source_sha=git(source, "rev-parse", "HEAD"),
            source_dirty=git(source, "status", "--porcelain"),
            tool_sha=git(Path(__file__).resolve().parents[2], "rev-parse", "HEAD"),
            tool_dirty=git(
                Path(__file__).resolve().parents[2],
                "status",
                "--porcelain",
                "--",
                str(Path(__file__).resolve()),
            ),
            extension_sha256=hashlib.sha256(
                Path(_native.__file__).read_bytes()
            ).hexdigest(),
            python=sys.version,
            platform=platform.platform(),
            driver=pygame.display.get_driver(),
            window=list(RMS.screen.get_size()),
            chrome_running=os.system("pgrep -x 'Google Chrome' >/dev/null") == 0,
            cases=cases,
            screenshots=screenshots,
            all_passed=True,
            capacity_claim=False,
            selected_overlay=args.selection,
        )
        assert not raw["source_dirty"] and not raw["tool_dirty"]
        (output / "render.json").write_text(json.dumps(raw, indent=2) + "\n")
        print(
            json.dumps(
                dict(
                    all_passed=True,
                    frames=sum(c["frames"] for c in cases),
                    driver=raw["driver"],
                )
            )
        )
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
