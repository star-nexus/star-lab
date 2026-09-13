"""Minimal public attack at the API4 and API5 checkpoints (run from STAR root)."""
import json
import subprocess
from rotk_env.tests.test_native_unit_actions import setup
from rotk_env.components import Combat
from rotk_env.runtime.bootstrap import export_initial_state
from rotk_env.runtime.native import RustRuntime
world,(a,b,target),_,llm=setup('dummy')
world.get_component(a,Combat).attack_range=5
try:
    with RustRuntime(export_initial_state(world,display='dummy')) as native:
        assert native.execute_action('register_agent_info',dict(faction='wei',provider='synthetic',model_id='fake',base_url='https://host'),agent_id='alpha')['success']
        result=native.execute_action('attack',dict(unit_id=a,target_id=target),agent_id='alpha')
        delta=native.take_presentation_delta()
        print('RESULT_JSON='+json.dumps(dict(source_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
              result=result,display_keys=sorted(delta),visual_rows=len(delta.get('visuals',{}).get('rows',[])))))
finally:world.reset()
