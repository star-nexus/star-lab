"""Pre-registered E7 display input, independent of recorded authority requests.

Fixed viewport in performance replay; real resize has separate Cocoa contracts.
Discrete zooms and pan steps exercise both hot reuse and explicit invalidation.
"""


def apply(session, tick, name):
    if name == 'static':
        return
    from rotk_env import components as c
    from rotk_env.prefabs.config import Faction
    camera = session.world.get_singleton_component(c.Camera)
    ui = session.world.get_singleton_component(c.UIState)
    phase = (tick // 180) % 8
    camera.zoom = (1., .5, 1.25, 1., .75, 1.5, 1., .5)[phase]
    pan = (((tick % 180) // 30) - 2) * 24 if phase in (1, 4) else 0
    camera.offset_x = 1240 + pan
    camera.offset_y = 619 + (24 if phase == 4 else 0)
    ui.view_faction = (Faction.WEI, Faction.WEI, Faction.SHU, Faction.WU,
                       Faction.WEI, Faction.SHU, Faction.WU, Faction.WEI)[phase]
    ids = session.world.query().with_component(c.Unit).ordered_entities()
    ui.selected_unit = ids[(tick // 180) % len(ids)] if ids and phase in (2, 3, 6) else None
    ui.show_stats = phase in (3, 6)
    ui.show_help = phase == 7
    ui.show_coordinates = phase == 4
