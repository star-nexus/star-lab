# Phase 5 10K UnitRender E3 — Cull First-Touch Locality Attribution

**Status:** CLOSED — `SPATIAL_FIRST_TOUCH_LOCALITY_CANDIDATE_JUSTIFIED`  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`  
**Run:** `20260907-132252`

## Trigger

E2 closed candidate volume, branch mix, and warm replay unit-cost inflation as explanations for the movement-dependent Cull signal, but its replay happened after the production Cull had already touched the same spatial/Fog data.

At 100% moving E2 observed:

```text
index revisions/frame                  ~665.7
candidate share in changed buckets      ~71.4%
warm full replay unit-cost growth        +2.6%
```

This left one specific hypothesis:

> the first renderer traversal may pay a locality/cache penalty on structures just mutated by Movement/Vision, while an immediate second traversal is already warm.

## Measurement design

E3 did not copy or rewrite Cull logic. It wrapped and called the exact production `_get_visible_units()` function.

Most frames were baseline:

```text
baseline: no prewarm -> time exact production Cull core
```

Every 5th Cull call rotated one read-only prewarm mode before timing the exact production call:

```text
context:
  resolve index + viewport + singleton/Fog/current_vision references

spatial:
  context + traverse candidate bucket sets + by_entity lookups

fog:
  context + touch/hash all current_vision entries

both:
  spatial + fog
```

Prewarm time was excluded from the local core metric. Outer `unit_visible_cull` and aggregate frame latency remained diagnostic only.

## Result

The original Cull signature reproduced cleanly:

```text
baseline core:
00%   1.544 ms
50%   1.993 ms
100%  2.276 ms

00% -> 100% growth = +0.732 ms
candidate count change = +0.12%
```

Spatial prewarm produced a density-monotonic reduction:

```text
spatial vs context:
00%   0.141 ms   (9.2%)
50%   0.275 ms  (13.8%)
100%  0.468 ms  (19.7%)
```

At 50% moving the sampled core ranges were fully separated:

```text
context  1.899 .. 2.111 ms
spatial  1.614 .. 1.840 ms
```

At 100% they were almost disjoint:

```text
context  2.066 .. 3.043 ms
spatial  1.801 .. 2.061 ms
```

Fog-only prewarm did not clear its preregistered materiality gate. The dominant locality signal is spatial.

Artifact SHA256:

```text
ae9fdc8412c58cb597cb7c9a521656892df2bcd9cc4c398a63f55f1b1e1e0735
```

Targeted regressions:

```text
9 passed in 0.43s
```

All point guards passed.

## Important boundary: prewarm is not the optimization

At 100% moving, spatial prewarm itself cost about `1.780 ms/frame`, while it reduced the following Cull by `0.468 ms/frame`.

Therefore a production prewarm pass would be net negative. E3 only proves that the first Cull touch of the spatial working set is expensive.

## Host caveat

The operator reported Chrome and other desktop activity during the experiment, so the host was not isolated. This weakens aggregate frame/FPS interpretation, but the primary metric is interleaved same-session whole-call Cull timing. The large sample separation and density-monotonic effect make background activity an implausible explanation for the spatial signal.

## Decision

```text
SPATIAL_FIRST_TOUCH_LOCALITY_CANDIDATE_JUSTIFIED
```

Positive attribution is **not KEEP**. Production remains unchanged.

## Next

Before changing the spatial-index representation, test the smaller scheduling hypothesis implied by the window system order:

```text
Movement / spatial-index mutation
    -> MapRenderSystem
    -> UnitRenderSystem Cull
```

E4 should compare exact production Cull before MapRender versus at its normal post-MapRender position. If the earlier call is materially faster and returns the identical visible-unit list, an early frame-local Cull cache becomes the preferred candidate class.

> **先证明是不是调度把热数据变冷，再考虑改数据结构。**
