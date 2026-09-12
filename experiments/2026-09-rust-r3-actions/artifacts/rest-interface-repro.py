import json,sys,subprocess
from pathlib import Path
source=Path(sys.argv[1]).resolve();sys.path.insert(0,str(source))
from rotk_env.tests.test_native_vision import make_vision_world
from rotk_env.components import MatchRules
from rotk_env.runtime.bootstrap import export_initial_state
from rotk_env.runtime.native import RustRuntime
world,(a,b,c),vision=make_vision_world('none')
world.add_singleton_component(MatchRules(game_actions=('rest',)))
try:
    with RustRuntime(export_initial_state(world)) as native:
        native.execute_action('register_agent_info',dict(faction='wei',provider='synthetic',model_id='fake',base_url='https://host'),agent_id='alpha')
        try: result=native.execute_action('rest',{'unit_id':a},agent_id='alpha')
        except RuntimeError as exc: result={'exception':type(exc).__name__,'message':str(exc)}
        print(json.dumps({'source_sha':subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),'result':result}))
finally:world.reset()
