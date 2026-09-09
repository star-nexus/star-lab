"""The Lab scheduler must not sleep the world or hide an overdue workload."""
from p3_local_agents import LocalAgents
from rotk_env.tests.test_faction_state_affordances import _world, _spawn
from rotk_env.prefabs.config import Faction
from rotk_env.components import FogOfWar, TeamCoordination
from rotk_env.systems.llm_system import LLMSystem


class Clock:
    def __init__(self): self.now = 0.
    def __call__(self): return self.now


def setup(delay=1, **kwargs):
    world = _world()
    for f, col, row in [(Faction.WEI,0,0),(Faction.WEI,-1,0),(Faction.SHU,2,0),(Faction.SHU,2,1)]:
        _spawn(world,faction=f,col=col,row=row)
    fog = world.get_singleton_component(FogOfWar)
    fog.faction_vision = {f:{(c,r) for c in range(-3,4) for r in range(-3,4)} for f in Faction}
    world.add_system(LLMSystem(server_url=None))
    clock = Clock()
    agents = LocalAgents(world,2,delay,scope='selected',clock=clock,policy='move',**kwargs)
    agents.start(synchronized=True)
    return agents, clock


def test_real_registration_multiclaim_and_thinking_never_executes_early():
    agents, clock = setup(60)
    coord = agents.world.get_singleton_component(TeamCoordination)
    assert all(len(s.units)==2 for s in agents.sessions)
    assert all(coord.owner_of(uid)==s.agent_id for s in agents.sessions for uid in s.units)
    agents.pump()
    assert agents.counts['observations']==2 and agents.counts['cycles']==0
    clock.now = 59.99
    agents.pump()
    assert agents.counts['cycles']==0
    clock.now = 60
    agents.pump()
    assert agents.counts['cycles']==2
    assert agents.counts['move_accepted']>0
    assert all(r['snapshot_age_ms']>=60000 for r in agents.records if r['event']=='act')


def test_stall_is_retained_as_queue_latency_and_queue_stays_session_bounded():
    agents, clock = setup()
    agents.pump()
    clock.now = 8
    agents.pump()
    actions = [r for r in agents.records if r['event']=='act']
    assert all(r['queue_ms']==7000 for r in actions)
    # Closed-loop ready time and nominal demand lag are separate, both retained.
    observations = [r for r in agents.records if r['event']=='observe']
    assert observations[-1]['queue_ms']==0
    assert observations[-1]['nominal_cycle_lag_ms']==7000
    assert len(agents.heap)==len(agents.sessions)
    assert all(s.completed == 1 for s in agents.sessions)


def test_selected_probe_really_observes_all_owned_units_and_serializes():
    agents, clock = setup()
    agents.pump()
    assert all(r['returned_units']==2 and r['bytes']>0 for r in agents.records)
    assert all(r['reachable']>0 for r in agents.records)


def test_periodic_observation_continues_during_slow_thinking_without_replacing_snapshot():
    agents, clock = setup(60, observation_hz=5)
    agents.pump()
    actions = [list(s.actions) for s in agents.sessions]
    for i in range(1, 6):
        clock.now = i / 5
        agents.pump()
    assert agents.counts['observations'] == 12
    assert agents.counts['cycles'] == 0
    assert [s.actions for s in agents.sessions] == actions
    assert all(s.observed_at == 0 for s in agents.sessions)
    assert len(agents.heap) == 2 * len(agents.sessions)
    clock.now = 60
    agents.pump()
    assert all(r['snapshot_age_ms'] >= 60000 for r in agents.records if r['event'] == 'act')
    assert agents.counts['cycles'] == 2


def test_periodic_stall_retains_all_due_pulls_and_original_queue_age():
    agents, clock = setup(60, observation_hz=1)
    agents.pump()
    clock.now = 8
    agents.pump()
    pulls = [r for r in agents.records if r['event'] == 'observe']
    assert len(pulls) == 18
    assert pulls[2]['queue_ms'] == 7000
    assert len(agents.heap) == 4


def test_all_modes_preserve_observations_actions_and_rng_trajectory():
    results = []
    for mode in ('single', 'batch-off', 'batch-on'):
        agents, clock = setup(1, observation_hz=1, observation_mode=mode)
        for t in (0, 1, 2, 3):
            clock.now = t
            agents.pump(1000)
        results.append((dict(agents.counts),
            [(r['event'], r['agent'], r.get('actions')) for r in agents.records]))
    assert results[0] == results[1] == results[2]


def test_batch_never_crosses_action_and_keeps_unconsumed_heap_serials(monkeypatch):
    agents, clock = setup(observation_hz=1, observation_mode='batch-on')
    agents.heap.clear()
    agents._push(0, 'observe', 0)
    agents._push(0, 'act', 0)
    agents._push(0, 'observe', 1)
    seen = []
    original = agents.gate.process_observation_batch
    def call(requests, **kwargs):
        seen.append(len(requests))
        return original(requests, **kwargs)
    monkeypatch.setattr(agents.gate, 'process_observation_batch', call)
    agents.pump(1000)
    assert seen == [1, 1]
    assert [r['event'] for r in agents.records[:3]] == ['observe', 'act', 'observe']
    agents, clock = setup(observation_hz=1, observation_mode='batch-on')
    pending = sorted(agents.heap)
    monkeypatch.setattr(agents.gate, 'process_observation_batch',
        lambda *a, **kw: {'consumed':0, 'responses':[], 'cache_metrics':{}})
    agents.pump(1000)
    assert sorted(agents.heap) == pending


def test_overdue_recurrent_reads_keep_heap_order_across_batch_collection():
    traces = []
    for mode in ('single', 'batch-off', 'batch-on'):
        agents, clock = setup(60, observation_hz=1, observation_mode=mode)
        agents.heap.clear()
        agents._push(0, 'observe', 0)
        agents._push(4, 'observe', 1)
        clock.now = 5
        agents.pump(1000)
        traces.append([(r['agent'], r['queue_ms']) for r in agents.records])
    assert traces[0] == traces[1] == traces[2]
