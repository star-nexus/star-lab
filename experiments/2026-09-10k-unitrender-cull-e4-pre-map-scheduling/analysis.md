# Analysis — UnitRender E4 Pre-Map Cull Scheduling

## Formal result

`MAP_RENDER_LOCALITY_GAP_NOT_CONFIRMED`

The original movement-dependent Cull signature reproduced again:

```text
baseline late Cull core
00%   1.543 ms
50%   1.995 ms
100%  2.278 ms

00% -> 100% = +0.735 ms
```

However, moving the exact production Cull earlier did not improve it. It made the call consistently slower:

```text
early-pre-map minus baseline-late
00%   +0.127 ms
50%   +0.195 ms
100%  +0.230 ms
```

At the same time, the second exact Cull on sampled frames was much faster:

```text
late-after-early
00%   1.317 ms
50%   1.493 ms
100%  1.659 ms
```

At 100% moving the three local timing distributions were well separated:

```text
baseline-late      p50 2.274 / p95 2.416 / max 2.505 ms
early-pre-map      p50 2.492 / p95 2.638 / max 2.918 ms
late-after-early   p50 1.668 / p95 1.757 / max 1.818 ms
```

Every sampled early/late visible list matched exactly, including order.

## What E4 rejects

E3 suggested that Cull pays a spatial first-touch locality penalty. E4 tested the narrower hypothesis that `MapRenderSystem`, which executes immediately before `UnitRenderSystem`, evicts the spatial working set and causes that penalty.

That hypothesis is rejected. If MapRender were the main eviction gap, the pre-Map Cull should have been materially faster than the normal post-Map Cull. The opposite occurred at every movement density.

Therefore do not implement an early frame-local Cull cache merely to move the work before MapRender.

## What E4 strengthens

The strong `late-after-early` speedup shows that the first complete Cull traversal itself warms data/code needed by a second traversal. This is consistent with E3's spatial-prewarm result but localizes the phenomenon differently:

> the important boundary is first complete spatial traversal, not the MapRender scheduling boundary.

The next attribution should decompose the cumulative spatial prewarm itself:

```text
context
-> bucket container touch
-> by_entity lookup touch
-> UnitSpatialRecord field touch
```

This can distinguish whether the first-touch penalty is dominated by:

1. `by_bucket` set/container traversal,
2. the two-level `bucket entity-id -> by_entity record` indirection, or
3. the scattered `UnitSpatialRecord` objects and their fields.

Only after that evidence should a representation candidate such as bucket-local direct records be considered.

## Measurement caveat

The benchmark host was not an isolated lab machine; desktop applications may have been running. This weakens aggregate frame/FPS interpretation. It does not invalidate the formal E4 result because the primary evidence is same-session, interleaved local core timing, the effect is large and directionally consistent across 0/50/100%, and semantic/workload guards all passed.
