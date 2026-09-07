# Summary

E5-3 closed the field-level attribution chain by showing that `world_x/world_y` dominate the movement-dependent record-field first-touch effect seen by UnitRender Cull.

The formal 100% moving result was:

```text
lookup   2.044 ms
world    1.669 ms
faction  1.679 ms
hex      1.568 ms

full field effect = 0.476 ms
world_xy          = 0.375 ms (~78.8%)
```

50% moving produced the same structure (~79.4% world-coordinate share).

The next experiment is E5-4: reuse long-lived per-hex `(world_x, world_y, bucket)` payload while preserving fresh record-container creation, then measure against exact retained production.
