# Decision

```text
WORLD_COORD_PAYLOAD_FIRST_TOUCH_DOMINANT
```

E5-3 formally reproduced the slotted-base Cull growth and isolated the residual record-field first-touch effect to `world_x/world_y`.

At 100% moving:

```text
full field effect = 0.476 ms
world_x/world_y   = 0.375 ms  (~78.8%)
faction           = -0.011 ms
col/row           = 0.111 ms
```

At 50% moving, `world_x/world_y` similarly account for ~79.4% of the full field effect. This consistency across densities is strong structural evidence.

This is **not** a production KEEP decision.

The next investigation is named **E6 — Derived World-Geometry Reuse**, rather than E5-4. E5 is considered complete as a spatial-structure/field-payload attribution stage; E6 starts a new treatment layer focused narrowly on whether Cull can reuse or avoid movement-refreshed derived world geometry.

The first E6 candidate should reuse long-lived per-hex derived geometry `(world_x, world_y, bucket)` while preserving fresh `UnitSpatialRecord` creation, so payload reuse remains isolated from the E5-2 record-identity hypothesis.

This naming change does not alter the E5-3 evidence or decision. Do not jump to SoA/native/parallel before this narrower candidate is tested.
