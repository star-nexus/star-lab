# Phase 5 10K UnitRender E3 — Cull First-Touch Locality Attribution

**Status:** RUNNING — preregistered attribution; no production candidate selected  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

E2 closed candidate volume, branch mix, and warm replay unit-cost inflation as explanations for the movement-dependent Cull signal, but its replay happened after the production Cull had already touched the same spatial/Fog data.

At 100% moving E2 observed:

```text
index revisions/frame                  ~665.7
candidate share in changed buckets      ~71.4%
warm full replay unit-cost growth        +2.6%
```

This leaves one specific hypothesis:

> the first renderer traversal may pay a locality/cache penalty on structures just mutated by Movement/Vision, while an immediate second traversal is already warm.

## Measurement design

E3 does not copy or rewrite Cull logic. It wraps and calls the exact production `_get_visible_units()` function.

Most frames are baseline:

```text
baseline: no prewarm -> time exact production Cull core
```

Every 5th Cull call rotates one read-only prewarm mode before timing the exact production call:

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

Prewarm time is excluded from the local core metric. Outer `unit_visible_cull` and aggregate frame latency remain diagnostic only.

## Mandatory reproduction gate

Before attributing locality, E3 must reproduce the original movement-dependent Cull growth using its own **baseline exact-production core** metric:

```text
baseline core 100% - baseline core 0% >= 0.40 ms/frame
```

Candidate volume sampled by E3 must remain within ±2% from 0% to 100%.

If the growth does not reproduce:

```text
ORIGINAL_CULL_GROWTH_NOT_REPRODUCED
```

and the Cull signature should be closed rather than optimized.

## Preregistered locality signals at 100% moving

A prewarm effect is material only if it saves both:

```text
>= 0.20 ms/frame
>= 10% of the comparison baseline
```

`both` uses a slightly stricter combined threshold:

```text
>= 0.25 ms/frame
>= 12%
```

Possible decisions:

```text
CONTEXT_FIRST_TOUCH_LOCALITY_CANDIDATE_JUSTIFIED
SPATIAL_FIRST_TOUCH_LOCALITY_CANDIDATE_JUSTIFIED
FOG_FIRST_TOUCH_LOCALITY_CANDIDATE_JUSTIFIED
MIXED_SPATIAL_FOG_FIRST_TOUCH_CANDIDATE_JUSTIFIED
MIXED_FIRST_TOUCH_LOCALITY_CANDIDATE_JUSTIFIED
CULL_FIRST_TOUCH_NOT_CONFIRMED
ORIGINAL_CULL_GROWTH_NOT_REPRODUCED
```

Positive attribution is **not KEEP**. Any resulting production optimization still requires semantic regressions and uninstrumented controlled A/B.

## Methodology

> **先确认原始 signature 仍可复现，再用只读 prewarm 判断 first-touch locality；不为不稳定信号造 candidate。**
