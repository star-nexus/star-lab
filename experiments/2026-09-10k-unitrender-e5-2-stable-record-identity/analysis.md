# Analysis — UnitRender E5-2 Stable Record Identity

E5-2 isolated one hypothesis on top of the rejected-but-causally-beneficial E5-1 slotted layout:

```text
A: slots=True + fresh UnitSpatialRecord replacement on every pure movement commit
B: slots=True + same UnitSpatialRecord identity, internal in-place field refresh
```

Both control and treatment ran the exact same runtime commit `682fdb3a4c64002b402eb74bdda2331ca7123ab4`; treatment was injected only at startup and preserved external frozen semantics. Generic `upsert_from_world()` was unchanged.

## Result

The additional Cull improvement from stable identity was small:

```text
50% moving   1.894 -> 1.887 ms   saving 0.007 ms
100% moving  2.202 -> 2.158 ms   saving 0.044 ms
```

Both are far below the preregistered floors (`0.08 / 0.15 ms`). UnitRender also regressed slightly at 50% and improved only `0.033 ms` at 100%.

The 100% controlled-work improvement (`-0.406 ms`) is not used to override the local gate. AnimationSystem moved by `-0.208 ms` at 100% while the direct Cull treatment effect was only `-0.044 ms`; this is exactly the kind of neighboring-system/runtime drift for which aggregate metrics are diagnostic only.

## What this rules out

E5-2 substantially weakens the hypothesis that the dominant residual E5 first-touch signal comes from replacing the `UnitSpatialRecord` container object itself on each movement commit.

This is especially informative combined with E5-1:

```text
E5 formal record-field first-touch @100%      ~0.498 ms
E5-1 slots production Cull saving @100%       ~0.113 ms
E5-2 stable identity additional saving @100%  ~0.044 ms
```

These interventions are not strictly additive, so the arithmetic is not a formal decomposition. Directionally, however, record-layout and record-identity churn explain only a minority of the original record-field first-touch effect.

## Next hypothesis

Pure movement still refreshes the record's field payload even when identity is preserved. In particular, `_record_for_hex()` computes new `world_x/world_y` Python float values and a new bucket tuple for each commit. Cull reads `world_x/world_y` first for exact bounds, then reads `faction`, then `col/row` for Fog membership.

Therefore the next experiment should decompose the remaining Cull field-payload first-touch effect cumulatively:

```text
lookup-only
+ world_x/world_y
+ faction
+ col/row
```

This is preferable to immediately introducing SoA or a parallel packed index. If world-coordinate payload dominates, a smaller candidate may reuse/cache derived per-hex render geometry rather than redesign the whole spatial index.
