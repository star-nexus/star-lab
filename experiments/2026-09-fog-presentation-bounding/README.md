# Fog Presentation Bounding

**Status:** CLOSED  
**STAR repository:** `star-nexus/star`  
**Problem commit:** `6e8c151494de2b37071ecdcd5f1898b7387e057a`  
**Fix commit:** `6a61115ab29a0c4aeb39fa8b74c7cbcded314180`  
**Validated performance commit:** `6a61115ab29a0c4aeb39fa8b74c7cbcded314180`  
**Regression / integration validation commit:** `54d17745098fb3fc4c43861d839e8dc40164c030`  
**Validated tag:** N/A — no separate Fog-presentation milestone tag has been created

## 1. Problem

Fog semantic updates had already been converted to incremental dirty patches, but the final presentation path still submitted a viewport-sized `SRCALPHA` Surface every frame:

```text
2480 * 1268 = 3,144,640 pixels/frame
```

The RenderEngine attribution case causally showed that suppressing only Fog presentation removed about 3.04 ms from `render_batch_blits`, while the scalar path stayed effectively unchanged.

The remaining question was whether presentation could be bounded to the actual map-content screen rectangle without changing Fog semantics.

## 2. Why it matters

The existing implementation had already removed repeated semantic recomputation, yet presentation still paid for the entire framebuffer-sized alpha Surface. That left a large amount of unnecessary software pixel composition in the realtime render loop.

The optimization had to preserve:

- the viewport-sized semantic Fog Surface;
- stable screen-space patch coordinates;
- incremental Fog update semantics;
- later clear-to-fog transitions for tiles currently transparent;
- existing camera/zoom/faction invalidation behavior.

## 3. Source checkout

Problem state:

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout 6e8c151494de2b37071ecdcd5f1898b7387e057a
uv sync
```

Validated performance fix:

```bash
git checkout 6a61115ab29a0c4aeb39fa8b74c7cbcded314180
```

Regression/integration validation was later run at:

```bash
git checkout 54d17745098fb3fc4c43861d839e8dc40164c030
```

No Fog production presenter file changed between the performance fix commit and this regression commit; the intervening changes were Terrain/testing/stress-harness work.

## 4. Environment

```text
Machine: Mac mini
OS: macOS
Python: not captured in archived run metadata; reproduce with uv at the exact STAR commit
Display: 2480x1268 window
Scenario: TestMap-8K-scale-5000
Map: 91x91
Resident units: 5000
Moving units: 5000
Seed: 42
Fog: ON
Camera: offset_x=1240, offset_y=634
Zoom: 0.15
GC policy: realtime_defer
Vision geometry-cache capacity: 16384
```

## 5. Reproduce the problem

The canonical pre-fix baseline is owned by the RenderEngine attribution case:

```text
../2026-09-render-engine-attribution/results/causal-ablation/causal-normal-run1.json
../2026-09-render-engine-attribution/results/causal-ablation/causal-normal-run2.json
../2026-09-render-engine-attribution/results/causal-ablation/causal-normal-run3.json
```

### Terminal A — start STAR

```bash
STAR_SCALE_HARNESS_SOCKET=/tmp/star-scale.sock \
STAR_SCALE_GC_POLICY=realtime_defer \
STAR_SCALE_VISION_GEOMETRY_CACHE_MAX_ENTRIES=16384 \
uv run rotk_env/main.py \
  --skip-start \
  --scenario TestMap-8K-scale-5000 \
  --mode real_time \
  --players human_vs_two_ai \
  --seed 42 \
  --no-hub \
  --profile
```

### Terminal B — run the workload

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
  --output fog-result.json
```

Use a fresh process for each run.

## 6. Expected problem signature

At the pre-fix causal baseline, the 3-run mean was approximately:

```text
Fog presentation source pixels      3,144,640
render_engine                           5.425 ms
render_queue_submit                     5.344 ms
render_batch_blits                      3.748 ms
render_scalar_execute                   1.383 ms
avg frame                              21.331 ms
P99                                    25.114 ms
```

A separate causal suppression showed:

```text
Fog present OFF
render_batch_blits delta               -3.043 ms
render_engine delta                    -2.984 ms
```

This established that the full-window presentation, not Fog semantic patching, was the dominant Fog-side RenderEngine cost.

## 7. Validate the fix

At `6a61115...`, use the same commands and guards. The implementation keeps the viewport-sized semantic Fog Surface but computes a map-content presentation rectangle during `_full_rebuild`, reuses that cached rectangle during steady state, and submits only the bounded area.

The fixed geometry should report:

```text
full viewport pixels                   3,144,640
bounded source rect                    [726, 36, 1029, 1190]
bounded source pixels                  1,224,510
saved pixels                           1,920,130
saved ratio                            61.06%
```

The 3-run production mean was:

```text
render_engine                           3.433 ms
render_queue_submit                     3.343 ms
render_batch_blits                      0.726 ms
render_scalar_execute                   2.382 ms
avg frame                              20.690 ms
P99                                    25.005 ms
```

The queue topology changes by exactly one command class: Fog moves from one full-window plain/batchable blit to one bounded `area=` scalar blit. This produces the expected causal migration:

```text
batch_blits       -3.022 ms
scalar_execute    +0.999 ms
queue_submit      -2.001 ms
render_engine     -1.992 ms
```

## 8. Regression validation

The final combined renderer regression suite was executed at integration commit `54d17745098fb3fc4c43861d839e8dc40164c030`:

```bash
uv run pytest \
  rotk_env/tests/test_incremental_fog_presenter.py \
  rotk_env/tests/test_terrain_presentation_cache.py \
  rotk_env/tests/test_scale_camera_stress.py \
  rotk_env/tests/test_scale_map_overscan.py \
  rotk_env/tests/test_render_presentation_ablation.py \
  framework/tests/test_render_blit_batching.py \
  framework/tests/test_render_engine_profile_breakdown.py \
  framework/tests/test_performance_profiler_v2.py \
  rotk_env/tests/test_render_engine_profile_export.py \
  rotk_env/tests/test_scale_experiment_measurement.py \
  -q
```

Observed result:

```text
43 passed in 1.12s
```

This closes the regression-test requirement in `PROTOCOL.md`. The canonical raw JSON artifacts were separately SHA256-verified after archival and remained byte-identical.

## 9. Formal artifacts

This case canonically owns only the three fixed runs:

- [`results/fog-bounded-run1.json`](results/fog-bounded-run1.json)
- [`results/fog-bounded-run2.json`](results/fog-bounded-run2.json)
- [`results/fog-bounded-run3.json`](results/fog-bounded-run3.json)
- [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

The pre-fix causal baseline remains canonical in the RenderEngine attribution case and is cross-referenced rather than duplicated.

## 10. Related records

- [`manifest.yaml`](manifest.yaml)
- [`analysis.md`](analysis.md)
- [`decision.md`](decision.md)
- [`../2026-09-render-engine-attribution/`](../2026-09-render-engine-attribution/)
