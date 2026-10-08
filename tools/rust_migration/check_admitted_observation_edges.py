"""Small E8 edge checks on installed candidate versus independent old binary.

These tests exercise real exported entry points; no product patch or rebuild.
They do not replace canonical full-state or accepted-host trajectory checks.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from threading import RLock
from unittest.mock import patch

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--extension-dir',type=Path,required=True)
    p.add_argument('--baseline-extension',type=Path,required=True)
    p.add_argument('--runs',type=Path,required=True)
    a=p.parse_args();a.runs.mkdir(parents=True,exist_ok=True)
    assert not (a.runs/'edges.json').exists()
    sys.path.insert(0,str(a.source));sys.path.insert(0,str(a.extension_dir))
    from star_native import _native
    from rotk_env.runtime.native import RustRuntime
    from rotk_env.runtime.bootstrap import export_initial_state
    from rotk_env.tests.test_native_observation import setup
    assert sha(_native.__file__)=='9bb2fa4412bc810fbd751c42f525614f8cddb42e8c136612a51495fa0679f0d9'
    assert sha(a.baseline_extension)=='838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544'
    spec=importlib.util.spec_from_file_location('e8_frozen_reference._native',a.baseline_extension)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    w,(unit,other,enemy),_=setup('window')
    try: initial=export_initial_state(w,display='window')
    finally: w.reset()
    (a.runs/'initial.json').write_text(json.dumps(initial,indent=2)+'\n')
    checks=[];failure=None
    def old_runtime(state,threads):
        old=RustRuntime.__new__(RustRuntime);old._admission_lock=RLock()
        old._native=module.NativeRuntime(json.dumps(state,allow_nan=False),threads)
        return old
    def same(a,b):
        assert a.export_state()==b.export_state()
        assert a.take_presentation_delta()==b.take_presentation_delta()
    try:
        for threads in (1,4):
            for case in ('cold_stats','game_over','clock_barrier','vlm_barrier','invalid_stats','panic_poison'):
                state=deepcopy(initial)
                if case=='cold_stats':state['singletons'].pop('GameStats')
                if case=='game_over':state['singletons']['GameState'].update(game_over=True,winner='wei')
                if case=='vlm_barrier':state['singletons']['MatchRules']={'game_actions':['get_faction_state','get_faction_state_vlm','move','attack']}
                if case=='invalid_stats':state['singletons']['GameStats']=42
                if case=='panic_poison':state['singletons']['GameStats']['action_counts_by_agent']=[]
                old=old_runtime(state,threads);new=RustRuntime(state,threads=threads)
                scope=None;owned=[];errors=[]
                try:
                    assert old.take_presentation_delta()==new.take_presentation_delta()
                    if case in ('invalid_stats','panic_poison'):
                        try:old.get_faction_state_json('wei',agent_id='alpha',wall_time=123.)
                        except BaseException as e:errors.append((type(e).__name__,str(e)))
                        try:
                            with new._admitted_observation_segment('segment_encoded') as scope:
                                scope.get_faction_state_json('wei',agent_id='alpha',wall_time=123.)
                        except BaseException as e:errors.append((type(e).__name__,str(e)))
                        assert len(errors)==2 and errors[0]==errors[1]
                        assert not scope.entered and scope.token is None and not new._admission_lock._is_owned()
                        if case=='invalid_stats':
                            assert 'invalid GameStats' in errors[0][1]
                            assert scope.report is None
                            same(old,new)
                            with new._admitted_observation_segment('segment_encoded'):pass
                        else:
                            assert errors[0][0]=='PanicException'
                            for r in (old,new):
                                try:r.diagnostics()
                                except RuntimeError as e:assert 'poisoned' in str(e)
                                else:raise AssertionError('Poisoned runtime unexpectedly resumed')
                            with RustRuntime(initial,threads=threads) as fresh:
                                with fresh._admitted_observation_segment('segment_encoded') as clean:
                                    assert json.loads(clean.get_faction_state_json('wei',agent_id='alpha',wall_time=124.))['success']
                    else:
                        with new._admitted_observation_segment('segment_encoded',diagnostics=True) as scope:
                            for i in range(4):
                                if case=='clock_barrier' and i in (1,2):
                                    for r in (old,new):
                                        r.set_clock(paused=i==1,time_scale=2.5)
                                        r.step(1/30,wall_time=124.+i)
                                if case=='vlm_barrier' and i==1:
                                    with patch('framework.engine.frame_capture.capture_rendered_frame',return_value=('OWNED_FAKE_FRAME',None)):
                                        x=old.execute_action('get_faction_state_vlm',{'faction':'wei'},agent_id='alpha',wall_time=125.)
                                        y=new.execute_action('get_faction_state_vlm',{'faction':'wei'},agent_id='alpha',wall_time=125.)
                                    assert x==y and x['success'] and x['frame_base64']=='OWNED_FAKE_FRAME'
                                q=dict(faction='wei',agent_id='alpha',unit_ids=[unit,other,unit],wall_time=130.+i)
                                x=old.get_faction_state_json(**q);y=scope.get_faction_state_json(**q)
                                assert x==y;owned.append(y)
                        same(old,new)
                        if case in ('clock_barrier','vlm_barrier'):assert scope.report is None
                        else:assert scope.report['requests']==4
                        new.reset(initial);new.close()
                        assert all(isinstance(json.loads(wire),dict) for wire in owned)
                    checks.append(dict(case=case,threads=threads,passed=True,errors=errors,owned_responses=len(owned)))
                finally:
                    for r in (old,new):
                        try:r.close()
                        except RuntimeError as e:assert 'poisoned' in str(e)
    except BaseException as e:
        failure=repr(e);raise
    finally:
        (a.runs/'edges.json').write_text(json.dumps(dict(passed=failure is None,checks=checks,failure=failure,
            source_extension_sha256=sha(_native.__file__),baseline_extension_sha256=sha(a.baseline_extension),
            tool_sha256=sha(__file__),initial_sha256=sha(a.runs/'initial.json'),
            deferred=['revision exhaustion injection','synthetic final encoder fault injection','bounded retained cache lifecycle'],
            scope='12 small exported-entry checks; no performance or general leak claim'),indent=2)+'\n')
        print(json.dumps(dict(passed=failure is None,checks=len(checks),failure=failure)),flush=True)

if __name__=='__main__':main()
