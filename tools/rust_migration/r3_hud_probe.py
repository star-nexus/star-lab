"""Before/after HUD availability and history-independent payload structure."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
from r3_observations_probe import git


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve(); output = args.output.resolve()
    os.chdir(source); sys.path.insert(0, str(source))
    from rotk_env.runtime.bootstrap import prepare_scene
    from rotk_env.runtime.native import RustRuntime
    from star_native import API_VERSION, _native
    cases = []
    for history in (0, 10000):
        initial = prepare_scene(mode='real_time', scenario='chibi-small', seed=42, display='none')
        stats = initial['singletons']['GameStats']
        stats['battle_history'] = [{'marker':'retained history', 'n':n} for n in range(history)]
        stats['unit_observation_history'] = [{'marker':'retained observations', 'n':n} for n in range(history)]
        with RustRuntime(initial) as runtime:
            first = runtime.take_presentation_delta()
            idle = runtime.take_presentation_delta()
            assert runtime.export_state() == initial
        cases.append(dict(history_entries=history, hud_present='hud' in first,
            first_hud=first.get('hud'), idle_hud=idle.get('hud'),
            first_hud_bytes=len(json.dumps(first.get('hud'), sort_keys=True).encode()),
            idle_hud_bytes=len(json.dumps(idle.get('hud'), sort_keys=True).encode()), authority_unchanged=True))
    if API_VERSION >= 7:
        assert cases[0]['first_hud'] == cases[1]['first_hud']
        assert cases[0]['idle_hud'] == cases[1]['idle_hud']
        assert cases[0]['idle_hud']['battle_log']['entries'] == []
    result = dict(source_sha=git(source,'rev-parse','HEAD'), source_dirty=git(source,'status','--porcelain'),
        tool_sha=git(Path(__file__).resolve().parents[2],'rev-parse','HEAD'), api=API_VERSION,
        extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(), python=sys.version, platform=platform.platform(),
        session_available=importlib.util.find_spec('rotk_env.runtime.session') is not None,
        cases=cases, all_passed=True, performance_claim=False)
    assert not result['source_dirty']
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(api=API_VERSION,session_available=result['session_available'],hud_present=cases[0]['hud_present'])))


if __name__ == '__main__':
    main()
