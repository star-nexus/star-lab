# Phase 5 10K UnitRender E5 — Spatial First-Touch Structure Decomposition

**Status:** RUNNING — two sample-guard-inconclusive attempts; profiler-window correction preregistered  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

E3 established a spatial first-touch locality effect in UnitRender Cull. E4 rejected MapRender as the causal eviction boundary. E5 asks which spatial-access layer accounts for the first-touch benefit.

Production Cull currently traverses:

```text
by_bucket: Bucket -> Set[entity_id]
                  ↓
by_entity: entity_id -> UnitSpatialRecord
                  ↓
record fields: world_x/world_y/col/row/faction
```

## Measurement design

Exact production `_get_visible_units()` remains the timed operation. Every sixth Cull rotates one read-only cumulative prewarm mode:

```text
context -> bucket -> lookup -> record
```

The inferred incremental effects are:

```text
bucket container      = context_core - bucket_core
by_entity indirection = bucket_core - lookup_core
record object fields  = lookup_core - record_core
```

Prewarm cost is excluded and prewarm itself is not an optimization candidate.

## Frozen gates

```text
baseline 100% - baseline 0% >= 0.40 ms
candidate count change <= ±2%
>= 7 samples for every mode at every density
100% context -> record >= 0.25 ms and >= 12%
```

A stage is dominant only if at 100% it contributes both:

```text
>= 0.12 ms
>= 35% of full context -> record effect
```

Thresholds and sampling cadence remain unchanged throughout E5.

## Attempt 1 — `20260907-143507`

Formal result:

```text
E5_INCONCLUSIVE_MEASUREMENT_GUARD
```

The Cull signature and spatial effect reproduced. Directional 100% decomposition:

```text
full spatial           0.666 ms
bucket container       0.163 ms   ~24%
by_entity lookup       0.023 ms    ~3%
record fields          0.480 ms   ~72%
```

100% samples were `context=6 bucket=6 lookup=7 record=7`, below the frozen minimum of 7 for every mode.

Artifact SHA256:

```text
66839700b528f8e3aef44a4154b1a16f7a620089f5b1648f7114a09f2ad064d0
```

## Attempt 2 — `20260907-154710`

The duration-only retry used `DURATION=25` exactly as preregistered. Formal result again:

```text
E5_INCONCLUSIVE_MEASUREMENT_GUARD
```

All workload/semantic guards passed. The main signal reproduced almost identically:

```text
baseline 0% -> 100% growth     0.727490 ms
full spatial effect @100%      0.678333 ms  (30.40%)

bucket container               0.177101 ms
by_entity lookup               0.019375 ms
record fields                  0.481857 ms
```

`record_fields` again directionally exceeds both dominance thresholds. However 100% samples were:

```text
baseline 129
context    7
bucket     6
lookup     6
record     7
```

so no formal dominance decision is permitted.

Artifact SHA256:

```text
be6614da8923dc9e29a6c16c75abb99790e11e7f0e1400215da088f19ace853c
```

## Measurement-design diagnosis

Attempt 2 exposed that extending run duration cannot solve the sample guard because the profiler retains a wall-clock rolling window of only 5 seconds.

At 100% moving the raw profile reported:

```text
window_target_s       5.0
window_coverage_s     5.0048
window_throughput_fps 30.9703
sample_count          155
```

With `PREWARM_PERIOD=6` and four rotating modes, the retained budget is only:

```text
155 / 6 / 4 ~= 6.46 samples per mode
```

Therefore 6/7 mode counts are structurally expected. The previous duration-only retry was valid but incapable of reliably satisfying the frozen >=7-sample gate.

## Preregistered measurement-window correction

Do **not** lower the prewarm period because that would increase instrumentation density and change locality perturbation. Instead retain the exact `1/6` cadence and widen only the profiler's rolling statistical horizon:

```text
profiler rolling horizon: 5.0s -> 8.0s
PREWARM_PERIOD:           6 unchanged
thresholds:               unchanged
production runtime:       unchanged
```

At ~31 FPS, 8 seconds retains roughly 248 frames, giving approximately `248 / 6 / 4 ~= 10.3` samples per mode.

This is classified as a **measurement-window correction**, not a candidate/runtime change. E5 tooling records the configured profile horizon in profiler metadata. The retry should keep `DURATION=25` so the only new change relative to attempt 2 is the retained measurement horizon.

## Interpretation boundary

The two inconclusive attempts provide strong replicated directional evidence:

```text
record_fields @100%
attempt 1: 0.480292 ms
attempt 2: 0.481857 ms
```

But E5 remains formally open until the frozen sample-count guard passes. Do not select a spatial representation candidate before that.

## Forbidden during E5

- production Cull changes
- changing `UnitSpatialIndex` representation
- prewarm as an optimization
- lowering prewarm period to manufacture sample count
- changing the dominance thresholds
- native/parallel rewrites
- changing Fog/Vision semantics

## Methodology

> **先把 first-touch 拆到 container / indirection / record 层；测量窗口必须足以满足预注册样本预算，但不能靠提高 probe 密度来制造证据。**
