# Summary — UnitRender E5-2 Stable Record Identity

E5-2 tested whether preserving the same slotted `UnitSpatialRecord` object across pure movement commits materially reduces the remaining UnitRender Cull first-touch cost.

It does not.

```text
50% moving   Cull saving 0.007 ms
100% moving  Cull saving 0.044 ms
```

Both miss the preregistered floors (`0.08 / 0.15 ms`). Workload and semantic guards all passed, so the result is a valid negative attribution.

The investigation therefore moves below record-container identity to the field payload consumed by Cull, beginning with `world_x/world_y`, then `faction`, then `col/row`.
