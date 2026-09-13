import json
from rotk_env.components import Vision
from rotk_env.prefabs.config import Faction
from rotk_env.systems.llm_action_handler import LLMActionHandler
from rotk_env.tests.test_faction_state_affordances import _world, _spawn
world = _world()
uid = _spawn(world, faction=Faction.WEI, col=0, row=0)
cells = {(0,1),(-1,0),(1,0),(0,-1),(0,0)}
world.add_component(uid, Vision(range=2, visible_tiles=cells))
handler = LLMActionHandler(world)
for name, data in [('legacy',handler._get_visible_environment(uid,'basic')), ('unit',handler.observation_system._get_visible_terrain(cells))]:
    positions = [(t['position']['col'],t['position']['row']) for t in data]
    print(json.dumps({'interface':name,'positions':positions,'coordinate_order':positions==sorted(cells)}))
