"""Independent-binary full-state/delta/error matrix for the E2 Statistics split."""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def sha(data):
    return hashlib.sha256(data).hexdigest()


def generate(source, output):
    sys.path.insert(0, str(source))
    from rotk_env.tests.test_native_statistics_compute import initial_statistics
    cases = []
    for display in ['none', 'dummy', 'window']:
        for mode in ['real_time', 'turn_based']:
            initial, ids = initial_statistics(display)
            initial['mode'] = mode
            initial['clock']['realtime'] = mode == 'real_time'
            initial['singletons']['GameTime']['current_mode'] = mode
            # The trace owns these exact bootstrap bytes, including injected wall metadata.
            steps = [0., .25, .75, .25, 2., 0., 1., .1]
            cases.append(dict(name=f'{display}-{mode}-cycle', initial=initial, steps=steps, reset_after=[1, 5]))
        initial, ids = initial_statistics(display)
        for fault in range(3):
            state = copy.deepcopy(initial)
            units = {e['id']: e['components'] for e in state['entities']}
            units[ids[fault]]['UnitCount']['max_count'] = 0
            n = 10 if display == 'window' else 10000
            state['singletons']['GameStats']['unit_observation_history'] = [{'prior': i} for i in range(n)]
            cases.append(dict(name=f'{display}-first-error-{fault}', initial=state, steps=[.25, .25], reset_after=[0]))
        for variant in ['disabled', 'absent', 'no-stats-singleton', 'no-fog', 'no-tracker', 'zero-batch']:
            state = copy.deepcopy(initial)
            if variant == 'disabled':
                state['systems']['StatisticsSystem']['enabled'] = False
            elif variant == 'absent':
                del state['systems']['StatisticsSystem']
            elif variant == 'no-stats-singleton':
                del state['singletons']['GameStats']
            elif variant == 'no-fog':
                del state['singletons']['FogOfWar']
            elif variant == 'no-tracker':
                del state['singletons']['VisibilityTracker']
            else:
                state['systems']['StatisticsSystem']['batch_size'] = 0
            cases.append(dict(name=f'{display}-{variant}', initial=state, steps=[.25, 1., 1., 1.], reset_after=[1]))
    initial, (a, b, c) = initial_statistics('window')
    units = {e['id']: e['components'] for e in initial['entities']}
    del units[b]['MovementPoints']
    del units[c]['UnitCount']
    units[b]['UnitObservation'] = dict(current_position=[99,99], previous_position=[98,98],
        health_percentage=77., movement_remaining=77, has_acted_this_turn=True,
        is_visible_to={'$set':['legacy']}, last_seen_time=1710000000., current_terrain_type='forest',
        terrain_bonus_active=True, movement_path=[[i,i] for i in range(50)], total_distance_moved=42)
    initial['systems']['StatisticsSystem']['history_limit'] = 100
    initial['systems']['StatisticsSystem']['cycle'] = dict(phase='observations', index=0,
        observation_entities=[a,a,b,b,c,999999], visibility_entities=[a,a,b,b,c,999999],
        faction_counts={}, visibility_cleared=False, fog_disabled_visible_to=None)
    cases.append(dict(name='window-imported-duplicate-sparse-no-mp', initial=initial,
                      steps=[0., .1, .1, 0.], reset_after=[1]))
    for fog_enabled in [True, False]:
        initial, ids = initial_statistics('window')
        template = copy.deepcopy(next(e for e in initial['entities'] if e['id'] == ids[0]))
        for i in range(256):
            entity = copy.deepcopy(template)
            entity['id'] = initial['entity_counter'] + i
            initial['entities'].append(entity)
        initial['entity_counter'] += 256
        initial['singletons']['FogOfWar']['enabled'] = fog_enabled
        initial['systems']['StatisticsSystem']['history_limit'] = 10000
        cases.append(dict(name=f'window-259-resident-fog-{fog_enabled}', initial=initial,
                          steps=[.1]*16, reset_after=[2, 10]))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(gzip.compress(json.dumps(cases, separators=(',', ':')).encode(), mtime=0))
    print(json.dumps(dict(cases=len(cases), input_sha256=sha(output.read_bytes()))))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path)
    p.add_argument('--generate', action='store_true')
    p.add_argument('--extension-sha256')
    p.add_argument('--native-package', type=Path)
    p.add_argument('--threads', type=int, choices=[1,2,4], default=1)
    p.add_argument('--min-rows', type=int, help='force experimental compute policy through private advancing probe')
    a = p.parse_args()
    source = a.source.resolve()
    if a.generate:
        generate(source, a.input)
        return
    sys.path.insert(0, str(source))
    if a.native_package:
        sys.path.insert(0, str(a.native_package.resolve()))
    from star_native import NativeRuntime, _native
    assert sha(Path(_native.__file__).read_bytes()) == a.extension_sha256
    cases = json.loads(gzip.decompress(a.input.read_bytes()))
    reports = []
    for case in cases:
        original = json.dumps(case['initial'])
        runtime = NativeRuntime(original, a.threads)
        rows = [dict(state=json.loads(runtime.export_state_json()),
                     delta=json.loads(runtime.take_presentation_delta_json()))]
        for index, dt in enumerate(case['steps']):
            error = None
            try:
                wall = 1720000000. + index
                if a.min_rows is None:
                    runtime.step(dt, wall)
                else:
                    runtime._statistics_step_json(dt, wall, a.min_rows, False)
            except RuntimeError as e:
                error = str(e)
            row = dict(error=error, state=json.loads(runtime.export_state_json()),
                       delta=json.loads(runtime.take_presentation_delta_json()))
            if index in case['reset_after']:
                before = runtime.export_state_json()
                try:
                    runtime.reset('{}')
                except RuntimeError:
                    pass
                else:
                    raise AssertionError('invalid reset accepted')
                assert runtime.export_state_json() == before
                runtime.reset(before)
                row['reset_state'] = json.loads(runtime.export_state_json())
                row['reset_delta'] = json.loads(runtime.take_presentation_delta_json())
            rows.append(row)
        runtime.close()
        runtime.close()
        try:
            runtime.step(0., 0.)
        except RuntimeError as e:
            assert 'closed' in str(e)
        else:
            raise AssertionError('closed world advanced')
        reports.append(dict(name=case['name'], rows=rows))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    raw = a.output.with_suffix('.raw.json.gz')
    raw.write_bytes(gzip.compress(json.dumps(reports, sort_keys=True, separators=(',', ':')).encode(), mtime=0))
    result = dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),
                  extension_sha256=a.extension_sha256, tool_sha256=sha(Path(__file__).read_bytes()),
                  input_sha256=sha(a.input.read_bytes()), threads=a.threads, min_rows=a.min_rows,
                  cases=len(cases), steps=sum(len(c['steps']) for c in cases), all_passed=True,
                  raw=dict(file=raw.name, sha256=sha(raw.read_bytes()), bytes=raw.stat().st_size),
                  scope='synthetic full exports, one-shot deltas, errors and reset/close; not capacity')
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
