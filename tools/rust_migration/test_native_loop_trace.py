"""Recorded native requests and presentation drains are independently replayable."""
import json,subprocess,sys
from pathlib import Path
from types import SimpleNamespace
from native_loop_trace import NativeLoopTrace
from rotk_env.runtime.bootstrap import export_initial_state
from rotk_env.runtime.native import RustRuntime
from rotk_env.tests.test_native_observation import setup
import rotk_env
import star_native


def test_native_input_capture_replays_on_other_worker_count(tmp_path):
    import hashlib
    from star_native import _native
    src=Path(rotk_env.__file__).resolve().parents[1]
    identity={'sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip()}
    extension={'api':star_native.API_VERSION,'sha256':hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest()}
    world,(a,_,_),_=setup('window')
    try:
        with RustRuntime(export_initial_state(world,display='window')) as n:
            n.take_presentation_delta()
            recorder=NativeLoopTrace(n,tmp_path/'small.json',identity,extension,1)
            owner=SimpleNamespace(agent_id='alpha')
            for i in range(3):
                response=recorder.call(owner,'get_faction_state',dict(faction='wei',unit_ids=[a]))
                recorder.payload(json.dumps(response,separators=(',',':'),ensure_ascii=False).encode())
                if i==0:recorder.call(owner,'move',dict(unit_id=a,target_position=dict(col=-2,row=0)))
                n.step(1/30,wall_time=1720000000.+i/30);n.take_presentation_delta()
            saved=recorder.finish()
        subprocess.run([sys.executable,str(Path(__file__).with_name('replay_rendered_loop.py')),'--source',str(src),'--trace',str(tmp_path/saved['trace']['file']),'--output',str(tmp_path/'replayed.json'),'--threads','4'],check=True)
        assert json.loads((tmp_path/'replayed.json').read_text())['all_passed']
    finally:world.reset()


def test_trace_replays_nondefault_numeric_conversion_environment(tmp_path):
    import hashlib
    from star_native import _native
    src=Path(rotk_env.__file__).resolve().parents[1]
    identity={'sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip()}
    extension={'api':star_native.API_VERSION,'sha256':hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest()}
    world,_,_=setup('window');previous=sys.get_int_max_str_digits()
    try:
        with RustRuntime(export_initial_state(world,display='window')) as n:
            n.take_presentation_delta()
            recorder=NativeLoopTrace(n,tmp_path/'numeric.json',identity,extension,1)
            owner=SimpleNamespace(agent_id='alpha')
            recorder.call(owner,'register_agent_info',dict(faction='wei',provider='fake',model_id='m',base_url='http://local'))
            sys.set_int_max_str_digits(640)
            for value in ('0'*640+'1',2):
                recorder.call(owner,'report_llm_stats',dict(faction='wei',api_stats=dict(prompt_tokens=value)))
            assert n.export_state()['singletons']['GameStats']['llm_api_stats']['wei']['prompt_tokens']==2
            saved=recorder.finish()
        sys.set_int_max_str_digits(previous)
        subprocess.run([sys.executable,str(Path(__file__).with_name('replay_rendered_loop.py')),'--source',str(src),'--trace',str(tmp_path/saved['trace']['file']),'--output',str(tmp_path/'numeric-replay.json'),'--threads','4'],check=True)
        assert json.loads((tmp_path/'numeric-replay.json').read_text())['all_passed']
    finally:
        sys.set_int_max_str_digits(previous);world.reset()
