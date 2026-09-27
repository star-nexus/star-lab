"""Boundary attribution must preserve actual responses, events and world state."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import subprocess
import sys

from native_loop_trace import NativeLoopTrace
from rotk_env.runtime.bootstrap import export_initial_state
from rotk_env.runtime.native import RustRuntime
from rotk_env.tests.test_native_observation import setup
import rotk_env
import star_native
from star_native import _native


def test_both_boundary_modes_preserve_recorded_stream(tmp_path):
    src=Path(rotk_env.__file__).resolve().parents[1]
    identity={'sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip()}
    extension={'api':star_native.API_VERSION,'sha256':hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest()}
    world,(uid,_,_),_=setup('window')
    try:
        with RustRuntime(export_initial_state(world,display='window')) as n:
            n.take_presentation_delta()
            recorder=NativeLoopTrace(n,tmp_path/'input.json',identity,extension,1)
            owner=SimpleNamespace(agent_id='alpha')
            for i in range(3):
                response=recorder.call(owner,'get_faction_state',dict(faction='wei',unit_ids=[uid]))
                recorder.payload(json.dumps(response,separators=(',',':'),ensure_ascii=False).encode())
                if i==0:recorder.call(owner,'move',dict(unit_id=uid,target_position=dict(col=-2,row=0)))
                n.step(1/30,wall_time=1720000000.+i/30);n.take_presentation_delta()
            saved=recorder.finish()
        for mode,threads in [('legacy','1'),('direct','4')]:
            out=tmp_path/(mode+'.json')
            subprocess.run([sys.executable,str(Path(__file__).with_name('profile_native_boundary.py')),'--source',str(src),'--trace',str(tmp_path/saved['trace']['file']),'--output',str(out),'--mode',mode,'--threads',threads],check=True)
            result=json.loads(out.read_text())
            assert result['all_responses_events_and_final_state_match']
            assert result['observations']==3 and result['admitted_observations']==0
            assert result['final_state_sha256']==saved['final_state_sha256']
    finally:world.reset()
