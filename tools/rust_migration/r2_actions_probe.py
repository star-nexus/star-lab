"""Archive trusted local request parity. No Hub, real LLM or full world loop."""
import argparse
import contextlib
import datetime
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()


def run_case(display, fog, threads):
    import pytest
    from rotk_env.components import Combat, FogOfWar, UnitCount
    from rotk_env.runtime.bootstrap import export_initial_state
    from rotk_env.runtime.native import ActionRequest, RustRuntime
    from rotk_env.systems.llm_system import LLMSystem
    from rotk_env.tests.test_native_vision import make_vision_world
    now = [1720000000.]
    class Frozen(datetime.datetime):
        @classmethod
        def now(cls, tz=None): return cls(2026, 9, 12, 12)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(time, 'time', lambda: now[0])
        patch.setattr(datetime, 'datetime', Frozen)
        world, (a, b, c), vision = make_vision_world(display)
        world.get_singleton_component(FogOfWar).enabled = fog
        world.get_component(a, Combat).attack_range = 5
        world.get_component(c, UnitCount).current_count = 1
        llm = LLMSystem(); world.add_system(llm)
        initial = export_initial_state(world, display=display)
        reg = dict(faction='wei', provider='synthetic', model_id='fake', base_url='https://host/v1/?token=discarded#fragment')
        ops = [
            ('new', None, {}), ('new', 'get_action_list', {}),
            ('new', 'get_faction_state', {'faction':'wei'}),
            ('alpha', 'register_agent_info', {**reg, 'agent_id':'spoof'}),
            ('beta', 'register_agent_info', reg),
            ('enemy', 'register_agent_info', {**reg, 'faction':'shu'}),
            ('alpha', 'register_agent_info', {**reg, 'model_id':'replacement'}),
            ('alpha', 'claim_units', {'unit_ids':[a]}),
            ('alpha', 'list_team', {}),
            ('alpha', 'broadcast_to_team', {'text':'hold position', 'metadata':{'units':[a,b]}}),
            ('beta', 'read_team_messages', {'agent_id':'alpha'}),
            ('enemy', 'read_team_messages', {}),
            ('alpha', 'get_faction_state', {'faction':'wei'}),
            ('enemy', 'get_faction_state', {'faction':'shu'}),
            ('beta', 'get_faction_state', {'faction':'wei', 'unit_ids':[b,a,b], 'agent_id':'alpha'}),
            ('beta', 'get_faction_state', {'faction':'shu'}),
            ('new', 'get_faction_state', {'faction':'wei'}),
            ('beta', 'get_faction_state', {'faction':'wei', 'unit_ids':[]}),
            ('beta', 'get_faction_state', {'faction':'wei', 'unit_ids':[True]}),
            ('beta', 'move', {'unit_id':a, 'target_position':{'col':-2,'row':0}}),
            ('enemy', 'move', {'unit_id':a, 'target_position':{'col':-2,'row':0}}),
            ('alpha', 'move', {'unit_id':a, 'target_position':{'col':-2,'row':0}}),
            ('alpha', 'get_faction_state', {'faction':'wei'}),
            ('beta', 'get_faction_state', {'faction':'wei'}),
            ('beta', 'claim_units', {'unit_ids':[b,a]}),
            ('beta', 'claim_units', {'unit_ids':[b,a], 'exclusive':False}),
            ('alpha', 'get_faction_state', {'faction':'wei', 'unit_ids':[a]}),
            ('beta', 'get_faction_state', {'faction':'wei', 'unit_ids':[a]}),
            ('beta', 'release_units', {'unit_ids':[a,{}]}),
            ('alpha', 'get_faction_state', {'faction':'wei', 'unit_ids':[a]}),
            ('beta', 'get_faction_state', {'faction':'wei', 'unit_ids':[a]}),
            ('beta', 'release_units', {}),
            ('alpha', 'does_not_exist', {}),
            ('alpha', 'rest', {'unit_id':a}),
        ]
        if display == 'none':
            ops += [('alpha','attack',{'unit_id':a,'target_id':c}),
                    ('alpha','get_faction_state',{'faction':'wei'})]
        ops += [('alpha','register_agent_info',{**reg,'faction':'shu'}),
                ('alpha','get_faction_state',{'faction':'shu'}),
                ('alpha','get_faction_state',{'faction':'wei'})]
        requests = [ActionRequest(agent, action, params, now[0]+i, Frozen.now().isoformat())
                    for i,(agent,action,params) in enumerate(ops)]
        case = dict(display=display, fog=fog, threads=threads, initial=initial,
                    operations=[], all_passed=False)
        try:
            with RustRuntime(initial, threads=threads) as single, RustRuntime(initial, threads=threads) as batch:
                expected = []
                for index, request in enumerate(requests):
                    now[0] = request.wall_time
                    result = llm._process_action_request(agent_id=request.agent_id, action_id=index,
                        action=request.action, params=dict(request.parameters), send_response=False)
                    result = json.loads(json.dumps(result)); expected.append(result)
                    actual = single.execute_action(request.action, request.parameters, agent_id=request.agent_id,
                        wall_time=request.wall_time, registration_time=request.registration_time)
                    before = export_initial_state(world, display=display); after = single.export_state()
                    guards = dict(response_equal=result==actual, state_equal=before==after)
                    case['operations'].append(dict(request=request.to_wire(), expected=result, actual=actual,
                        expected_state=before, actual_state=after, guards=guards))
                    if not all(guards.values()): raise AssertionError(f'single request {index} differs')
                report = batch.execute_actions_diagnostic(requests)
                case['batch'] = dict(report=report, expected=expected, state=batch.export_state(),
                    guards=dict(response_equal=report['results']==expected,
                                state_equal=batch.export_state()==single.export_state()))
                shared = next(s for s in report['observation_segments'] if s['start']==12)
                case['guards'] = dict(**case['batch']['guards'], complete_workload=len(case['operations'])==len(requests),
                    census_shared=shared['metrics']['census_builds']==1,
                    factions_shared=shared['metrics']['faction_builds']==2,
                    panels_shared=shared['metrics']['panel_builds']==3,
                    own_permission=report['results'][14]['units'][1]['commandable'] is False,
                    ownership_changed=report['results'][26]['units'][0]['commandable'] is False,
                    partial_release_visible=report['results'][29]['units'][0]['owner'] is None)
                batch.reset(initial)
                reset_result = batch.get_faction_state('wei', agent_id='alpha', wall_time=now[0])
                case['reset'] = dict(result=reset_result, state=batch.export_state())
                case['guards']['reset_invalidates_identity'] = reset_result.get('error_code')==2005
                case['all_passed'] = all(case['guards'].values())
        except Exception:
            case['error'] = traceback.format_exc()
        finally: world.reset()
        return case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); source = args.source.resolve(); output = args.output.resolve()
    os.chdir(source); sys.path.insert(0, str(source))
    from star_native import _native
    cases = []
    for display in ('none','dummy','window'):
        for fog in (False,True):
            for threads in (1,2,4):
                console = io.StringIO()
                with contextlib.redirect_stdout(console), contextlib.redirect_stderr(console):
                    case = run_case(display, fog, threads)
                case['console'] = console.getvalue(); cases.append(case)
    raw = dict(schema='star-r2-trusted-actions-v1', source_sha=git(source,'rev-parse','HEAD'),
        source_dirty=git(source,'status','--porcelain'), tool_sha=git(Path(__file__).parents[2],'rev-parse','HEAD'),
        python=sys.version, platform=platform.platform(),
        extension_sha256=hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest(), cases=cases)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(gzip.compress(json.dumps(raw, sort_keys=True, separators=(',',':')).encode()+b'\n', mtime=0))
    summary = {k:v for k,v in raw.items() if k!='cases'}
    summary['cases'] = [dict(display=c['display'], fog=c['fog'], threads=c['threads'], operations=len(c['operations']),
                            queries=sum(o['request']['action']=='get_faction_state' for o in c['operations']),
                            guards=c.get('guards',{}), all_passed=c['all_passed']) for c in cases]
    summary.update(all_passed=all(c['all_passed'] for c in cases) and not raw['source_dirty'],
        raw_file=output.name, raw_size=output.stat().st_size, raw_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    output.with_name(output.name.removesuffix('.json.gz')+'.summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    if not summary['all_passed']: raise SystemExit(1)

if __name__=='__main__': main()
