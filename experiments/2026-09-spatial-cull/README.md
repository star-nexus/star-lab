# Unit Spatial Cull Hot-Loop Reduction

**Status:** CLOSED — canonical cross-case evidence  
**STAR repository:** `star-nexus/star`  
**Problem commit:** `0dceb2f92c34bc3f24c746898142ff2e88e8efa2`  
**Fix commit:** `500daa045888310f23fa64eb016e79e0af5e89bf`  
**Regression-complete commit:** `615c3ac27f23f73b38d13b97280861fd1b0c9b72`  
**Milestone tag:** `scale-v1-cull-vision-closed`

## 1. Problem

The large-window renderer already used `UnitSpatialIndex` to discover viewport candidates, but the candidate hot loop still executed legacy per-unit work: repeated singleton/ECS lookups, repeated view-faction resolution, repeated `hex_to_pixel`, Fog work before cheap exact bounds, and a screen-space overscan margin that expanded heavily at zoom `0.15`.

The spatial architecture was already present. The residual constant work after spatial prefiltering was the actual bottleneck.

## 2. Canonical before/after evidence

This case deliberately owns **no duplicate raw JSON**.

### Before

Canonical artifact:

[`../2026-09-realtime-gc/results/density-100-realtime-gc.json`](../2026-09-realtime-gc/results/density-100-realtime-gc.json)

SHA256:

```text
2cd93685852aebffd3fffd8893fc7106f047494f6df24556f1e47328300a4561
```

Valid 5K / 100%-moving / Fog ON / staggered / `realtime_defer` result:

```text
unit_visible_cull = 3.527383733 ms
```

### After

Canonical artifact:

[`../2026-09-vision-cache/results/capacity-16384.json`](../2026-09-vision-cache/results/capacity-16384.json)

SHA256:

```text
f9ea376497c8c0f39a343ec99965dc2b27800c509b2bef89eb578df108daaa32
```

Later valid 5K / 100%-moving formal result:

```text
unit_visible_cull ≈ 1.329 ms
```

The causal metric therefore fell by roughly 62–63% in these canonical runs. Other nearby post-fix runs were in the ~1.28–1.33 ms class.

## 3. Reproduce the pre-fix behavior

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout 0dceb2f92c34bc3f24c746898142ff2e88e8efa2
uv sync
```

Run the formal 5000-unit 100%-moving staggered workload with Fog ON, fixed camera, zoom `0.15`, and `realtime_defer`.

Expected signature:

```text
unit_visible_cull ~3.5 ms class
```

## 4. Validate the fix

```bash
git checkout 500daa045888310f23fa64eb016e79e0af5e89bf
```

Repeat the comparable workload. Expected signature:

```text
unit_visible_cull ~1.3 ms class
```

For the regression-hardened state:

```bash
git checkout 615c3ac27f23f73b38d13b97280861fd1b0c9b72
uv run pytest \
  rotk_env/tests/test_scale_unit_render_spatial_cull.py \
  rotk_env/tests/test_scale_step5_indexed_state.py
```

## 5. What changed

```text
spatial buckets
  -> exact bounds using cached world coordinates
  -> Fog check using frame-cached state + spatial record
  -> visible units
```

Specifically:

- `UnitSpatialRecord` caches world-space center coordinates on authoritative position change;
- frame-global Fog/view state is fetched once;
- cheap exact bounds reject edge-bucket false positives before Fog work;
- candidate-level ECS component lookups are removed from the cull hot loop;
- `hex_to_pixel` is not recomputed per candidate every frame;
- overscan uses a world-space semantic margin rather than a zoom-amplified screen-space constant.

## 6. Archive integrity model

There is intentionally no local `results/` evidence copy and no local `artifacts/SHA256SUMS` for this case. The canonical checksums live with the owning GC and Vision cases.

This follows the STAR Lab rule:

> one raw artifact -> one canonical location -> cross-case references
