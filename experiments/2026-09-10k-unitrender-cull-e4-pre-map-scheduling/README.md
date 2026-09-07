# Phase 5 10K UnitRender E4 — Pre-Map Cull Scheduling Attribution

**Status:** RUNNING — preregistered attribution; no production candidate selected  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

E3 reproduced the Cull growth and isolated a strong spatial first-touch locality effect:

```text
baseline Cull core 00% -> 100%: +0.732 ms
spatial prewarm saving vs context:
00%   0.141 ms
50%   0.275 ms
100%  0.468 ms
```

However, the prewarm itself costs more than the saving and is not a production candidate.

The window system order provides a lower-blast-radius hypothesis:

```text
... -> MapRenderSystem -> UnitRenderSystem -> ...
```

UnitRender performs its visibility Cull at the start of `UnitRenderSystem.update()`. Therefore MapRender/Fog presentation may evict the spatial working set between Movement/index updates and Cull.

## Question

Is exact production Cull materially faster when executed immediately **before MapRender** than at its normal **post-MapRender** position?

If yes, the preferred candidate class is not a prewarm pass and not a spatial-index rewrite. It is:

```text
compute visible units once before MapRender
-> keep a frame-local immutable/result cache
-> UnitRender consumes that same result after MapRender
```

## Measurement design

E4 is measurement-only and runs exact production `UnitRenderSystem._get_visible_units()`.

Most frames:

```text
baseline:
MapRender -> time normal UnitRender Cull
```

Every 4th frame:

```text
time exact Cull before MapRender   [early probe, read-only]
-> run normal MapRender unchanged
-> time normal UnitRender Cull again
-> compare early and late visible-unit lists
```

The early result is **not consumed by rendering**. Production rendering still uses the normal late Cull result.

Exact early/late list equality is mandatory, including order, not only set membership.

Aggregate frame latency is diagnostic only because sampled frames intentionally do one extra Cull.

## Preregistered gates

The original baseline signature must reproduce again:

```text
baseline late 100% - baseline late 0% >= 0.40 ms
```

At least 10 early samples per density are required.

Semantic gate:

```text
early visible list == late visible list
for every sampled frame
```

Scheduling locality is material only if both hold:

```text
50% moving:
  early saving >= 0.15 ms
  early saving >= 8%

100% moving:
  early saving >= 0.25 ms
  early saving >= 12%
```

Possible decisions:

```text
PRE_MAP_CULL_SCHEDULING_CANDIDATE_JUSTIFIED
MAP_RENDER_LOCALITY_GAP_NOT_CONFIRMED
ORIGINAL_CULL_GROWTH_NOT_REPRODUCED
E4_INCONCLUSIVE_EARLY_LATE_SEMANTIC_MISMATCH
E4_INCONCLUSIVE_MEASUREMENT_GUARD
```

Positive attribution is not KEEP. Any frame-local early-cull cache still requires semantic regressions and an uninstrumented controlled A/B.

## Methodology

> **先测试执行时机能否自然保住 locality；只有调度解释不成立，才升级到 spatial representation 重构。**
