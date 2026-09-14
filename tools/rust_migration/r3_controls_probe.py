"""R3d1 local controls: exact Python/native commands, queries, ticks and replay."""

import argparse
import contextlib
import datetime
import lzma
import hashlib
import io
import itertools
import json
import os
from pathlib import Path
import platform
import sys
import time
import traceback
from r3_observations_probe import git, digest


def run_case(display, mode, kind, dead, critical, threads):
    import pytest
    from framework.engine.events import EBS
    from rotk_env.prefabs.config import GameMode
    from rotk_env.runtime.bootstrap import export_initial_state, encode
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.tests.test_native_combat_presentation import make

    now = [1720000000.0]

    class Frozen(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 9, 12, 12)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(time, "time", lambda: now[0])
        patch.setattr(datetime, "datetime", Frozen)
        world, (a, b, c), llm = make(display, GameMode(mode), kind, dead, critical)
        llm.enabled = False  # Post-game transport/report collection is a later gate.
        from rotk_env.components import TurnManager, Player
        from rotk_env.systems.ui_button_system import UIButtonSystem
        from rotk_env.systems.unit_action_button_system import UnitActionButtonSystem
        from rotk_env.systems.input_system import InputHandlingSystem
        world.add_singleton_component(TurnManager(list(world.query().with_component(Player).ordered_entities())))
        toolbar = UIButtonSystem.__new__(UIButtonSystem); toolbar.world = world
        buttons = UnitActionButtonSystem.__new__(UnitActionButtonSystem); buttons.world = world
        inputs = InputHandlingSystem.__new__(InputHandlingSystem); inputs.world = world
        mover = next(s for s in world.systems if type(s).__name__ == 'MovementSystem')
        combat = next(s for s in world.systems if type(s).__name__ == 'CombatSystem')
        territory = next(s for s in world.systems if type(s).__name__ == 'TerritorySystem')
        events = []
        publish = EBS.publish

        def capture(event):
            events.append(dict(type=type(event).__name__, fields=encode(event)))
            publish(event)

        patch.setattr(EBS, "publish", capture)
        initial = export_initial_state(world, display=display)
        case = dict(
            display=display,
            mode=mode,
            kind=kind,
            dead=dead,
            critical=critical,
            threads=threads,
            initial=initial,
            operations=[],
            all_passed=False,
        )
        try:
            with RustRuntime(initial, threads=threads) as native:
                case["initial_presentation"] = native.take_presentation_delta()

                def record(operation, expected=None, actual=None):
                    expected_state = export_initial_state(world, display=display)
                    expected_state["clock"]["tick"] = native.diagnostics()["clock"][
                        "tick"
                    ]
                    actual_state = native.export_state()
                    delta = native.take_presentation_delta()
                    expected = encode(expected)
                    actual = encode(actual)
                    guards = dict(
                        response_equal=expected == actual,
                        state_equal=expected_state == actual_state,
                        events_equal=events == delta["events"],
                    )
                    node = dict(
                        operation=operation,
                        expected=expected,
                        actual=actual,
                        state=expected_state,
                        actual_state_digest=digest(actual_state),
                        expected_events=list(events),
                        presentation=delta,
                        guards=guards,
                    )
                    if not guards["state_equal"]:
                        node["actual_state"] = actual_state
                    case["operations"].append(node)
                    events.clear()
                    if not all(guards.values()):
                        raise AssertionError(str(operation))

                def request(agent, verb, params):
                    expected = llm._process_action_request(
                        agent_id=agent,
                        action_id=0,
                        action=verb,
                        params=dict(params),
                        send_response=False,
                    )
                    actual = native.execute_action(
                        verb, params, agent_id=agent, wall_time=now[0]
                    )
                    record(
                        dict(
                            kind="request",
                            agent_id=agent,
                            action=verb,
                            parameters=params,
                            wall_time=now[0],
                            registration_time="2026-09-12T12:00:00",
                        ),
                        expected,
                        actual,
                    )

                reg = dict(
                    provider="synthetic", model_id="fake", base_url="https://host"
                )
                for agent, faction in [("alpha", "wei"), ("enemy", "shu")]:
                    request(agent, "register_agent_info", {**reg, "faction": faction})
                request("alpha", "claim_units", {"unit_ids": [a, b]})
                def control(kind, **params):
                    if kind == 'move': expected = mover.move_unit(params['unit_id'], tuple(params['position']))
                    elif kind == 'attack': expected = combat.attack(params['unit_id'], params['target_id'])
                    elif kind in ('wait', 'garrison'): expected = getattr(buttons, f'_execute_{kind}_action')(params['unit_id'])
                    elif kind == 'fortify': expected = territory.build_fortification(params['unit_id'], tuple(params['position']))
                    elif kind == 'set_fog': expected = inputs._set_fog_enabled(None, params['enabled'])
                    elif kind == 'toolbar_end_turn': expected = toolbar._end_turn()
                    else: raise ValueError(kind)
                    actual = native.execute_control(kind, wall_time=now[0], **params)
                    record(dict(kind='control', command=kind, parameters=params, wall_time=now[0]), expected, actual)

                control('move', unit_id=b, position=(-1, 1))
                request('alpha', 'get_faction_state', {'faction': 'wei'})
                control('attack', unit_id=a, target_id=c)
                control('attack', unit_id=a, target_id=b)
                control('wait', unit_id=a)
                control('garrison', unit_id=a)
                control('set_fog', enabled=False)
                request('alpha', 'get_faction_state', {'faction': 'wei'})
                control('set_fog', enabled=True)
                request('alpha', 'get_faction_state', {'faction': 'wei'})
                expected = territory.start_capture(a, (-1, 0))
                actual = native.start_capture(a, (-1, 0), wall_time=now[0])
                record(dict(kind='capture', unit_id=a, position=(-1, 0), wall_time=now[0]), expected, actual)
                for index, dt in enumerate([0.01] * 25 + [0.5, 1.0, 2.0, 12.0]):
                    now[0] += 0.1
                    world.update(dt)
                    native.step(dt, wall_time=now[0])
                    record(dict(kind="step", dt=dt, wall_time=now[0]))
                    if index in (8, 20):
                        native.reset(native.export_state())
                        record(dict(kind="reset-current"))
                control('fortify', unit_id=a, position=(-1, 0))
                control('toolbar_end_turn')
                control('toolbar_end_turn')
                if mode == 'turn_based':
                    next(s for s in world.systems if type(s).__name__ == 'TurnSystem').end_turn()
                    native.finish_human_turn(wall_time=now[0])
                    record(dict(kind='keyboard-turn', wall_time=now[0]))
                request('alpha', 'get_faction_state', {'faction': 'wei'})
                case["all_passed"] = True
                case["trace_digest"] = digest(case["operations"])
        except Exception:
            case["error"] = traceback.format_exc()
        finally:
            world.reset()
    return case


def replay(raw, output):
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.runtime.bootstrap import encode

    count = 0
    groups = {}
    for case in raw["cases"]:
        assert case["all_passed"], case.get("error")
        assert digest(case["operations"]) == case["trace_digest"]
        key = tuple(case[k] for k in ("display", "mode", "kind", "dead", "critical"))
        groups.setdefault(key, set()).add(case["trace_digest"])
        with RustRuntime(case["initial"], threads=case["threads"]) as native:
            assert native.take_presentation_delta() == case["initial_presentation"]
            for node in case["operations"]:
                assert all(node["guards"].values())
                assert digest(node["state"]) == node["actual_state_digest"]
                assert node["expected"] == node["actual"]
                assert node["expected_events"] == node["presentation"]["events"]
                op = node["operation"]
                result = None
                if op["kind"] == "step":
                    native.step(op["dt"], wall_time=op["wall_time"])
                elif op["kind"] == "reset-current":
                    native.reset(native.export_state())
                elif op['kind'] == 'control':
                    result = native.execute_control(op['command'], wall_time=op['wall_time'], **op['parameters'])
                elif op['kind'] == 'capture':
                    result = native.start_capture(op['unit_id'], tuple(op['position']), wall_time=op['wall_time'])
                elif op['kind'] == 'keyboard-turn':
                    native.finish_human_turn(wall_time=op['wall_time'])
                else:
                    result = native.execute_action(
                        op["action"],
                        op["parameters"],
                        agent_id=op["agent_id"],
                        wall_time=op["wall_time"],
                        registration_time=op["registration_time"],
                    )
                assert encode(result) == node["expected"]
                assert native.export_state() == node["state"]
                assert native.take_presentation_delta() == node["presentation"]
                count += 1
    assert all(len(v) == 1 for v in groups.values())
    result = dict(
        all_passed=True,
        cases=len(raw["cases"]),
        operations=count,
        thread_settings_equal=True,
        source_sha=raw["source_sha"],
        extension_sha256=raw["extension_sha256"],
    )
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--replay", type=Path)
    args = p.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    os.chdir(source)
    sys.path.insert(0, str(source))
    from star_native import _native, API_VERSION

    extension = hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest()
    if args.replay:
        data = args.replay.resolve().read_bytes()
        raw = json.loads(lzma.decompress(data))
        assert git(source, "rev-parse", "HEAD") == raw["source_sha"]
        assert extension == raw["extension_sha256"]
        replay(raw, output)
        return
    cases = []
    for options in itertools.product(
        ("none", "dummy", "window"),
        ("real_time", "turn_based"),
        ("melee", "ranged"),
        (False, True),
        (False, True),
        (1, 2, 4),
    ):
        console = io.StringIO()
        with contextlib.redirect_stdout(console), contextlib.redirect_stderr(console):
            case = run_case(*options)
        case["console"] = console.getvalue()
        cases.append(case)
    lab = Path(__file__).resolve().parents[2]
    raw = dict(
        schema="star-r3-controls-v1",
        source_sha=git(source, "rev-parse", "HEAD"),
        source_dirty=git(source, "status", "--porcelain"),
        tool_sha=git(lab, "rev-parse", "HEAD"),
        tool_dirty=git(
            lab, "status", "--porcelain", "--", str(Path(__file__).resolve())
        ),
        python=sys.version,
        platform=platform.platform(),
        native_api_version=API_VERSION,
        extension_sha256=extension,
        cases=cases,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(
        lzma.compress(
            json.dumps(raw, sort_keys=True, separators=(",", ":")).encode() + b"\n",
            preset=6,
        )
    )
    summary = {k: v for k, v in raw.items() if k != "cases"}
    summary["cases"] = [
        {
            **{
                k: c[k]
                for k in (
                    "display",
                    "mode",
                    "kind",
                    "dead",
                    "critical",
                    "threads",
                    "all_passed",
                )
            },
            "operations": len(c["operations"]),
            "ticks": sum(n["operation"]["kind"] == "step" for n in c["operations"]),
            "trace_digest": c.get("trace_digest"),
        }
        for c in cases
    ]
    groups = {}
    for c in cases:
        groups.setdefault(
            tuple(c[k] for k in ("display", "mode", "kind", "dead", "critical")), set()
        ).add(c.get("trace_digest"))
    equal = all(len(v) == 1 and None not in v for v in groups.values())
    summary.update(
        all_passed=all(c["all_passed"] for c in cases)
        and equal
        and not raw["source_dirty"]
        and not raw["tool_dirty"],
        thread_settings_equal=equal,
        raw_file=output.name,
        raw_size=output.stat().st_size,
        raw_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
    )
    output.with_name(output.name.removesuffix(".json.xz") + ".summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(
        json.dumps(
            dict(
                all_passed=summary["all_passed"],
                cases=len(cases),
                operations=sum(len(c["operations"]) for c in cases),
            )
        )
    )
    if not summary["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
