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

This is **not** a production KEEP decision. The next step is a narrow E5-4 treatment that reuses long-lived per-hex derived geometry `(world_x, world_y, bucket)` while preserving fresh `UnitSpatialRecord` creation, so payload reuse is isolated from the E5-2 record-identity hypothesis.

Do not jump to SoA/native/parallel before this narrower candidate is tested.
