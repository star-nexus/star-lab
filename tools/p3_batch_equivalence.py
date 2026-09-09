"""Frozen-world semantic oracle; runs against both pre-change and batch sources."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import sys
import time

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source', required=True)
p.add_argument('--output', required=True)
args = p.parse_args()
sys.path.insert(0, args.source)
with contextlib.redirect_stdout(io.StringIO()):
    from rotk_env.tests.test_selected_observation import setup_world
    from rotk_env.systems.llm_system import LLMSystem
    from rotk_env.components import FogOfWar, GameStats, ActionPoints, UnitCount
    from rotk_env.prefabs.config import Faction
    world, a, b, enemy = setup_world()
    gate = LLMSystem(server_url=None)
    world.add_system(gate)
    world.get_singleton_component(GameStats).agent_id_to_faction['c'] = Faction.SHU
    time.time = lambda: 1234.0
    requests = [
        {'agent_id': aid, 'action_id': i, 'params': params}
        for i, (aid, params) in enumerate([
            ('a', {'faction':'wei'}), ('a', {'faction':'wei','unit_ids':[]}),
            ('a', {'faction':'wei','unit_ids':[a,a,b]}),
            ('b', {'faction':'wei','unit_ids':[a]}),
            ('c', {'faction':'shu','unit_ids':[enemy]}),
            ('a', {'faction':'shu'}), ('a', {'faction':'wei','unit_ids':[enemy]}),
            ('unknown', {'faction':'wei'}), ('a', {'faction':'wei','unit_ids':[True]}),
            ('a', {'faction':'wei','unit_ids':[999999]}),
        ])]
    snapshots = []
    for state in ('fog_on', 'fog_off', 'resources_changed'):
        if state == 'fog_off':
            world.get_singleton_component(FogOfWar).enabled = False
        elif state == 'resources_changed':
            world.get_component(a, ActionPoints).current_ap = 0
            world.get_component(b, UnitCount).current_count = 0
        expected = [gate._process_action_request(r['agent_id'], r['action_id'],
                    'get_faction_state', dict(r['params']), send_response=False)
                    for r in requests]
        if hasattr(gate, 'process_observation_batch'):
            for reuse in (False, True):
                batch = gate.process_observation_batch(requests, budget_ms=1000, reuse=reuse)
                assert batch['consumed'] == len(requests)
                assert [json.loads(r['payload']) for r in batch['responses']] == expected
        snapshots.append({'state': state, 'responses': expected})
Path(args.output).write_text(json.dumps({'requests': requests, 'snapshots': snapshots}, sort_keys=True, indent=2)+'\n')
