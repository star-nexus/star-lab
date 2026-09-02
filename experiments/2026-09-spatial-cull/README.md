# Unit Spatial Cull Hot-Loop Reduction

**Status:** CLOSED  
**STAR repository:** `star-nexus/star`  
**Problem commit:** `0dceb2f92c34bc3f24c746898142ff2e88e8efa2`  
**Fix commit:** `500daa045888310f23fa64eb016e79e0af5e89bf`  
**Regression-complete commit:** `615c3ac27f23f73b38d13b97280861fd1b0c9b72`  
**Scale milestone:** `a24482d438157aa23b371b6e34d49b1c04fec7f7`

## 1. Problem

The large-window renderer already used `UnitSpatialIndex` to discover viewport candidates, but the candidate hot loop still executed legacy per-unit work. For every candidate it called inherited visibility logic that repeatedly fetched `GameState`, `FogOfWar`, `UIState`, `HexPosition`, and `Unit`, resolved the view faction, and recomputed `hex_to_pixel`. A 100-screen-pixel margin also expanded to about 667 world pixels per side at zoom `0.15`.

The structural spatial query was correct; the residual constant work after the query was not.

## 2. Historical signature

Representative pre-fix measurement under the formal 5000-unit Dynamic World workload:

```text
unit_visible_cull ≈ 3.53 ms
resident units    = 5000
moving units      = 5000
Fog               = ON
phase             = staggered
zoom              = 0.15
```

After the fix, repeated formal runs placed `unit_visible_cull` around **1.28–1.33 ms**, roughly a **64% reduction**.

## 3. Reproduce the pre-fix behavior

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout 0dceb2f92c34bc3f24c746898142ff2e88e8efa2
uv sync
```

Start a fresh ENV:

```bash
STAR_SCALE_HARNESS_SOCKET=/tmp/star-scale.sock \
STAR_SCALE_GC_POLICY=realtime_defer \
uv run rotk_env/main.py \
  --skip-start \
  --scenario TestMap-8K-scale-5000 \
  --mode real_time \
  --players human_vs_two_ai \
  --seed 42 \
  --no-hub \
  --profile
```

Keep Fog ON, camera fixed, and zoom at `0.15`.

Run the 100%-moving staggered point:

```bash
uv run tools/scale_driver.py \
  --socket /tmp/star-scale.sock \
  density-point \
  --density 1.0 \
  --seed 42 \
  --target-radius 12 \
  --duration 20 \
  --phase staggered \
  --require-fog on \
  --warmup 5 \
  --sample-after 10 \
  --output results/cull-before.json
```

Expected historical signature: `unit_visible_cull` is around the 3.5 ms class rather than the ~1.3 ms post-fix class. Exact aggregate frame timing can vary by machine/process state; the cull section is the causal metric of interest.

## 4. Validate the fix

Use a fresh process after checking out:

```bash
git checkout 500daa045888310f23fa64eb016e79e0af5e89bf
```

Repeat the same workload. Expected signature:

```text
unit_visible_cull ≈ 1.3 ms
```

For the test-hardened version:

```bash
git checkout 615c3ac27f23f73b38d13b97280861fd1b0c9b72
uv run pytest \
  rotk_env/tests/test_scale_unit_render_spatial_cull.py \
  rotk_env/tests/test_scale_step5_indexed_state.py
```

## 5. What changed

The fix kept the same architecture and removed repeated work:

```text
spatial buckets
  -> exact bounds using cached world coordinates
  -> Fog check using frame-cached state + spatial record
  -> visible units
```

Specifically:

- `UnitSpatialRecord` caches world-space center coordinates when authoritative position state changes;
- frame-global Fog/view state is fetched once rather than once per candidate;
- exact bounds reject edge-bucket false positives before Fog work;
- renderer no longer performs candidate-level ECS component lookups for visibility;
- renderer no longer recomputes `hex_to_pixel` for every candidate every frame;
- overscan uses an explicit world-space semantic margin rather than a zoom-amplified screen-space constant.

## 6. Result

| Metric | Before | After | Change |
|---|---:|---:|---:|
| `unit_visible_cull` | ~3.53 ms | ~1.28–1.33 ms | ~-64% |

This issue is closed. Further bucket-size tuning was deliberately not pursued because the cull path had already moved into the second performance tier; subsequent profiling identified larger costs elsewhere.

## 7. Related records

- [`manifest.yaml`](manifest.yaml)
- [`analysis.md`](analysis.md)
- [`decision.md`](decision.md)
- STAR fix: `500daa045888310f23fa64eb016e79e0af5e89bf`
