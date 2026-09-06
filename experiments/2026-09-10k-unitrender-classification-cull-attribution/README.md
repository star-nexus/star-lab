# Phase 5 10K UnitRender E — Cull + Animation Classification Attribution

**Status:** RUNNING — preregistered attribution; no production candidate selected  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

The completed moving-path attribution showed that the stable 0%→100% UnitRender growth is not primarily draw cost:

```text
UnitRender total        +2.912 ms/frame
unit_visible_cull       +0.727 ms   25.0%
classification          +1.743 ms   59.8%
render stage            +0.241 ms    8.3%
residual                +0.202 ms    6.9%
```

Exact raster duplicate drawing and committed-hex aggregation collapse were rejected as candidates.

## Source-level question

Current window batch rendering calls animation-position classification for every visible unit. The classification path uses the generic `AnimationSystem.get_unit_render_position(entity)` contract and then independently fetches `HexPosition` and converts the committed hex to pixels again to test whether a real displacement exists.

The generic API itself already checks:

```text
HexPosition
→ AttackAnimation
→ MovementAnimation
→ static hex_to_pixel OR movement interpolation
```

The renderer then performs:

```text
HexPosition again
→ committed hex_to_pixel again
→ displacement compare
→ screen projection
```

This may be abstraction overreach in the high-multiplicity batch path, but it remains a hypothesis until decomposed.

## Measurement design

### Cull

No per-entity timers are added. The probe records:

```text
spatial buckets visited
candidate entries
record misses
exact-bounds rejects
Fog rejects
visible accepts
```

The existing `unit_visible_cull` section remains the CPU clock. The analyzer derives `µs/candidate` and tests whether the +0.727 ms growth is explained by increased candidate volume rather than higher per-candidate cost.

### Animation classification

Sampling period defaults to 192 calls and is divided into three non-overlapping cohorts:

```text
cohort A: full renderer helper total
cohort B: exact production generic API total
cohort C: detailed stage timings
```

Only the detail cohort copies the source-guarded generic body. More than 98% of generic calls remain the exact production function.

Detailed stages:

```text
inner HexPosition get
AttackAnimation get
MovementAnimation get
static hex_to_pixel
movement interpolation
renderer second HexPosition get
renderer second base hex_to_pixel
displacement compare / projection
```

Branch ratios are sampled for static / movement / attack / none.

Aggregate frame latency remains diagnostic only.

## Preregistered decisions

### `SPECIALIZED_ANIMATION_DISPLACEMENT_API_CANDIDATE_JUSTIFIED`

Requires all guards plus:

```text
0%→100% classification growth >= 1.00 ms/frame
100% helper estimated cost       >= 1.50 ms/frame
conservative directly redundant work >= 0.25 ms/frame at any point
```

This only justifies one later specialized candidate; it is not KEEP.

### `CULL_VOLUME_EXPLAINS_GROWTH`

Cull is classified as necessary workload expansion rather than an optimization target if:

```text
0%→100% cull growth >= 0.40 ms/frame
µs/candidate relative change <= 15%
candidate-volume closure of cull growth = 70%..130%
```

### `ANIMATION_LOOKUP_REPRESENTATION_NEEDS_FURTHER_ATTRIBUTION`

If the animation helper is material but directly redundant work is below threshold, do not force a specialized API patch; investigate active-animation representation / lookup cost further.

## Tooling

Branch:

```text
experiment/phase5-unitrender-classification-cull-attribution
```

Head:

```text
0f3159e4694035d5399cc7a8ee151c0253f2d882
```

Files:

```text
tools/phase5_unitrender_classification_cull_attribution.py
tools/phase5_unitrender_classification_cull_analyze.py
tools/run_phase5_unitrender_classification_cull_attribution.sh
```

The branch is based on exact production and has no runtime source diff.

## Methodology

> **先区分必要工作量增长与错误抽象成本，再选择 candidate。**
