# Analysis — Unit Spatial Cull Hot-Loop Reduction

## 1. Observation

The scale/window renderer already queried a maintained `UnitSpatialIndex`, yet `unit_visible_cull` remained around the **3.5 ms** class under the formal 5000-unit, 100%-moving workload.

This contradicted the initial simplified story that the renderer was still scanning all 5000 resident units every frame: the first-stage spatial architecture was already present.

## 2. Competing hypotheses

### H1 — The spatial index itself is too coarse

The default bucket size could be returning too many false-positive candidates, making candidate discovery expensive.

### H2 — Legacy work remains inside the candidate loop

Even after spatial candidate discovery, every candidate may still pay repeated singleton/ECS/coordinate costs.

### H3 — Actual visible-unit rendering, not culling, dominates the measured cull section

The profiler attribution might combine culling with downstream draw preparation.

## 3. Code inspection / instrumentation

Inspection of the scale renderer showed that candidate discovery already used `candidates_in_world_rect`, but every candidate then called inherited `_is_unit_visible(entity)`. That method repeatedly fetched:

```text
GameState singleton
FogOfWar singleton
UIState singleton
HexPosition component
Unit component
```

The scale cull then separately recomputed `hex_to_pixel(record.col, record.row)`.

The filter order was also:

```text
coarse bucket
 -> expensive visibility/ECS work
 -> exact viewport bounds
```

instead of rejecting cheap edge false positives first.

Finally, the margin was expressed as 100 screen pixels and divided by zoom. At zoom 0.15:

```text
100 / 0.15 ≈ 667 world pixels per side
```

which materially expanded the coarse query.

## 4. Evidence

The fix commit `500daa045888310f23fa64eb016e79e0af5e89bf` changed only the residual cull path rather than replacing the spatial architecture.

It introduced cached world-space center coordinates in `UnitSpatialRecord` and changed the renderer to use frame-cached Fog/view state and record fields directly.

Representative measurements:

```text
before: unit_visible_cull ≈ 3.53 ms
after:  unit_visible_cull ≈ 1.28-1.33 ms
```

The roughly 64% reduction occurred without introducing a new renderer architecture or a different visibility model.

## 5. Root cause

> The spatial prefilter was correct, but legacy per-unit ECS/singleton lookups, repeated coordinate conversion, suboptimal filter order, and a zoom-amplified screen-space margin remained in the post-filter hot loop.

## 6. Causal chain

```text
spatial candidate
 -> repeated singleton/component lookup + hex_to_pixel
 -> thousands of avoidable Python operations per frame
 -> ~3.5 ms cull section

state-change cached record + frame-global state + cheap bounds first
 -> much lower candidate constant cost
 -> ~1.3 ms cull section
```

## 7. Rejected explanations

- **"Scale rendering still performs a full 5000-unit scan."** Rejected: `scale_unit_render_system.py` already used `UnitSpatialIndex` candidate discovery before the fix.
- **"A new rendering architecture is required."** Rejected for this stage: cleaning the existing hot loop removed most of the cull cost.
- **"Bucket-size tuning must be the first optimization."** Rejected as premature: after hot-loop cleanup the cull cost fell enough that bucket ablation no longer had first-order value.

## 8. Limits of the evidence

This experiment establishes the 5K low-zoom workload improvement. It does not prove that the current bucket size is globally optimal for much larger maps or 50K resident worlds.

Future scaling should inspect candidate/visible ratio and index-update cost before changing bucket size.
