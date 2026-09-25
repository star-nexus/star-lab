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
