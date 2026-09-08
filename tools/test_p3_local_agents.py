"""The Lab scheduler must not sleep the world or hide an overdue workload."""
from p3_local_agents import LocalAgents
from rotk_env.tests.test_faction_state_affordances import _world, _spawn
from rotk_env.prefabs.config import Faction
from rotk_env.components import FogOfWar, TeamCoordination
from rotk_env.systems.llm_system import LLMSystem


class Clock:
    def __init__(self): self.now = 0.
    def __call__(self): return self.now


def setup(delay=1):
    world = _world()
    for f, col, row in [(Faction.WEI,0,0),(Faction.WEI,-1,0),(Faction.SHU,2,0),(Faction.SHU,2,1)]:
        _spawn(world,faction=f,col=col,row=row)
    fog = world.get_singleton_component(FogOfWar)
    fog.faction_vision = {f:{(c,r) for c in range(-3,4) for r in range(-3,4)} for f in Faction}
    world.add_system(LLMSystem(server_url=None))
    clock = Clock()
    agents = LocalAgents(world,2,delay,scope='selected',clock=clock,policy='move')
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
