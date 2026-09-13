import json
from rotk_env.components import MatchRules
from rotk_env.prefabs.action_catalog import GAME_ACTIONS
from rotk_env.runtime.bootstrap import export_initial_state
from rotk_env.runtime.native import RustRuntime
from rotk_env.tests.test_native_unit_actions import setup
w,(a,b,c),_,llm=setup()
w.get_singleton_component(MatchRules).game_actions=tuple(s.name for s in GAME_ACTIONS)
try:
    with RustRuntime(export_initial_state(w)) as native:
        native.execute_action('register_agent_info',dict(faction='wei',provider='synthetic',model_id='fake',base_url='https://host'),agent_id='alpha')
        for name,params in [('observation',{'unit_id':a}),('unit_observation',{'unit_id':a}),('faction_observation',{'faction':'wei'}),('limited_observation',{'faction':'wei'}),('godview_observation',{})]:
            try:
                response=native.execute_action(name,params,agent_id='alpha')
                print(json.dumps({'action':name,'success':response.get('success'),'result_keys':sorted(response)}))
            except Exception as exc:print(json.dumps({'action':name,'exception':type(exc).__name__,'message':str(exc)}))
finally:w.reset()
