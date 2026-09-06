# Phase 5 10K UnitRender Moving-Path Attribution

**Status:** RUNNING — preregistered attribution; no production candidate selected  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

The Vision campaign is formally closed. Post-D1 10K / 100%-moving / 30Hz remains margin-limited:

```text
P99 = 32.926 / 33.348 / 33.764 ms
FRONTIER_NOT_ESTABLISHED
worst headroom = -0.434 ms
```

UnitRender has a stable movement-dependent cost signal across widely separated measurements:

```text
Phase-5 baseline 0% -> 100%:  +2.835 ms
recent diagnostic 0% -> 100%: +2.831 ms
```

This is now the next attribution target.

## Production structure under test

The window batch renderer treats static and animated units differently.

Static visible units:

```text
visible entity
  -> committed HexPosition grouping
  -> _render_unit_group_optimized()
  -> render at most 6 entities per hex group
```

Animated visible units:

```text
visible entity
  -> interpolated animation screen position exists
  -> removed from committed-hex grouping
  -> _render_single_unit_fast() per entity
```

Therefore animation may collapse a bounded aggregation path into per-entity rendering under 10K stress movement.

This is a hypothesis to measure, not an optimization decision.

## Semantic boundary

Units sharing the same committed hex are **not automatically visually mergeable**. Their interpolated screen positions may differ.

The experiment therefore distinguishes:

1. **Committed-hex grouping opportunity** — structural/explanatory only.
2. **Exact pixel duplicate** — same integer screen center.
3. **Exact raster-equivalent duplicate** — same integer screen center plus every `_render_single_unit_fast` input that affects raster output:
   - faction;
   - unit type;
   - texture size;
   - current/max UnitCount.

Only exact raster-equivalent duplicates can justify a draw-dedup candidate from this attribution.

## Frozen runtime

```text
perf/10k-online
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
= A + B + C1 + C2a + D1
```

Vision C2b-1 is not retained; Vision C2c selected no candidate.

## Tooling

STAR branch:

```text
experiment/phase5-unitrender-moving-path-attribution
```

Measurement-only files:

```text
tools/phase5_unitrender_moving_path_attribution.py
tools/phase5_unitrender_moving_path_analyze.py
tools/run_phase5_unitrender_moving_path_attribution.sh
```

The branch is based on exact production and contains no runtime source diff.

## Source guard

The probe refuses to run if exact production or relevant render/animation blobs drift:

```text
unit_render_system.py            7b49027882bd7ba4184a769bae19f7f490cf0a35
fast_render_systems.py           f2c1b819ba44f632aed896e06d1445fd725ec075
window_render_systems_base.py    46e3a75a08666c961fe310763d340c1c6d2d1ee1
optimized_render_systems.py      d554ec9e18dc12d836d475fda6c4ef3bbd17ec62
window_unit_render_system.py     b995df231c5e10d901b129f95716bfb0f30043eb
window_animation_system.py       e529b3cedec85610b32b93d063eef59b17c2f8f3
unit_spatial_index.py            2c2fb26c6ae5f422516a6c3927049d8a78a72b32
```

## Measurement design

The probe monkeypatches only the frozen `_render_units_batch()` implementation and preserves production calls/ordering.

Every batch frame records:

```text
visible units
animated units
static units
static committed-hex groups
static fast-render calls
animated fast-render calls
classification CPU
static-group render CPU
animated-single render CPU
texture-cache hits/misses
```

Every 16th batch frame additionally records structural state:

```text
animated committed-hex groups
static-cap equivalent calls for those groups
committed-group max occupancy
exact integer-pixel duplicates
exact raster-equivalent duplicates
exact duplicate group count/max size
```

Structural sampling intentionally avoids additional per-entity component reads on every frame.

Aggregate frame latency remains diagnostic only.

## Canonical workload

```text
scenario                  chibi-144k-scale-10000
scenario SHA256           e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
resident units            10,000
points                     0% / 50% / 100% moving
seed / phase seed         42 / 42
route steps               12
Fog                       ON
GC                        realtime_defer
MiniMap dynamic units     OFF
render                    uncapped
hub                       offline
```

Fresh ENV + full process-tree cleanup between points.

## Preregistered attribution decisions

### 1. `EXACT_RASTER_DEDUP_CANDIDATE_JUSTIFIED`

Select a later exact-raster dedup candidate only if all guards pass and:

```text
animated render CPU 50%   >= 0.50 ms/frame
animated render CPU 100%  >= 1.00 ms/frame
exact raster duplicate ratio 50%  >= 20%
exact raster duplicate ratio 100% >= 20%
estimated removable CPU 50%  >= 0.15 ms/frame
estimated removable CPU 100% >= 0.50 ms/frame
```

A positive attribution result still requires semantic regression + uninstrumented controlled A/B before KEEP.

### 2. `ANIMATED_SINGLE_PATH_DOMINANT_NEEDS_DECOMPOSITION`

If the animated-single stage is material at both densities but exact raster duplication misses the dedup thresholds, do **not** merge units by committed hex. Instead perform a second attribution inside `_render_single_unit_fast` to identify whether component fetch, texture lookup, command enqueue, or health-bar construction dominates.

Threshold for this outcome:

```text
animated render CPU 50%   >= 0.50 ms/frame
animated render CPU 100%  >= 1.00 ms/frame
```

### 3. `NO_MOVING_PATH_CANDIDATE`

If even the animated-single stage is not material, reject the moving-path hypothesis and rerank remaining UnitRender / render blocks.

## Out of scope

Do not mix into this attribution:

```text
production render semantics changes
committed-hex animation collapsing
texture format changes
RenderEngine submit changes
Vision
Animation simulation changes
GC
native/parallel rewrite
```

## Methodology

> **先证明 movement-dependent cost 是哪条路径造成的，再决定是否存在错误 multiplicity。**
