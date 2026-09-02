# Terrain Opaque Presentation Cache

**Status:** VALIDATED  
**STAR repository:** `star-nexus/star`  
**Problem commit:** `6a61115ab29a0c4aeb39fa8b74c7cbcded314180`  
**Diagnostic commit:** `b2dd5d03c09bae46ba8b0d92e78559bcc7d0d836`  
**Orthogonal attribution commit:** `0f9368c942ad3a75fd872ec9e1e0cd979e23cae1`  
**Fix commit:** `89f667985810fca8bb2756058e34f6b4d3663a5a`  
**Validated commit:** `54d17745098fb3fc4c43861d839e8dc40164c030`  
**Validated tag:** N/A — no separate Terrain-presentation milestone tag has been created  
**Formal closure gap:** regression-test stdout is not archived in this case yet

## 1. Problem

After Fog presentation was bounded, Terrain remained a large scalar RenderEngine cost. The verified overscan renderer built a large `pygame.SRCALPHA` staging Surface and presented a cropped region using `RMS.draw(..., area=source)`. The causal Terrain-off ablation had already shown that this single presentation command accounted for roughly 1.37 ms of `render_scalar_execute`.

The investigation needed to distinguish four plausible causes:

```text
pixel-format conversion
large backing-surface pitch / locality
actual non-opaque alpha values
Pygame/SDL SRCALPHA Surface semantics
```

## 2. Why it matters

The optimization target was already content-bounded, so repeating the Fog strategy would not help. A production change had to preserve the proven overscan build semantics and modify only the final presentation representation if the evidence justified it.

## 3. Source checkout

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout 0f9368c942ad3a75fd872ec9e1e0cd979e23cae1
uv sync
```

The investigation chain is:

```text
6a61115  Fog fixed; Terrain remains
b2dd5d0  alpha/format diagnostics + first opaque attempt
0f9368c  A-B-C-D orthogonal attribution
89f6679  production opaque compact presentation cache
54d1774  same-commit Legacy/Opaque A/B + deterministic camera stress
```

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
Fixed camera: offset_x=1240, offset_y=634
Zoom: 0.15
GC policy: realtime_defer
Vision geometry-cache capacity: 16384
```

## 5. Diagnostic signature

Run once with:

```bash
STAR_RENDER_TERRAIN_ALPHA_DIAGNOSTICS=1 \
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

The archived diagnostic showed:

```text
Terrain submitted pixels         1,224,348
opaque pixels                    1,176,918  (96.126%)
partial-alpha pixels                 5,221  (0.426%)
transparent pixels                  42,209  (3.447%)
source/screen RGB format match        true
source SRCALPHA                       true
```

This largely ruled out format conversion and showed that most pixels were already opaque in value.

## 6. Invalid-but-informative first opaque experiment

The first attempt used conceptually:

```python
pygame.Surface(content.size).convert(screen)
```

The intended independent variable was `SRCALPHA -> false`, but the resulting Surface still reported `SRCALPHA=true` because the display Surface itself carried that format/flag combination on this platform.

The three runs in `results/intermediate/` therefore **must not** be used as proof that disabling alpha blending helps. They remain archived because they revealed the experimental flaw and motivated the orthogonal A-B-C-D design.

## 7. Orthogonal A-B-C-D attribution

At `0f9368c...`, use a fresh process for each variant:

```text
A original
  large 2992x1780 backing Surface
  pitch ~11968 bytes
  SRCALPHA=true
  mixed alpha

B compact_alpha
  compact ~1028x1191 Surface
  pitch 4112 bytes
  SRCALPHA=true
  original RGBA preserved

C compact_flat_srcalpha
  same compact geometry/pitch
  SRCALPHA=true
  pixels precomposed, alpha=255

D compact_opaque_rgb
  same compact geometry/pitch
  SRCALPHA=false
  alpha mask=0
  RGB masks aligned with display
```

Set one of:

```bash
STAR_RENDER_TERRAIN_PRESENT_VARIANT=original
STAR_RENDER_TERRAIN_PRESENT_VARIANT=compact_alpha
STAR_RENDER_TERRAIN_PRESENT_VARIANT=compact_flat_srcalpha
STAR_RENDER_TERRAIN_PRESENT_VARIANT=compact_opaque_rgb
```

and use the standard 5K formal driver:

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
  --output terrain-abcd.json
```

The causal interpretation is:

```text
A -> B  backing-surface pitch/locality
B -> C  alpha-value flattening while SRCALPHA remains enabled
C -> D  disabling the SRCALPHA software-blit path
```

Observed 3-run means:

```text
                         scalar_execute   queue_submit   render_engine
A original                   2.440 ms       3.433 ms       3.529 ms
B compact alpha              2.223 ms       3.177 ms       3.261 ms
C flat SRCALPHA              2.206 ms       3.130 ms       3.206 ms
D opaque RGB                 1.375 ms       2.346 ms       2.435 ms
```

Key deltas:

```text
A -> B   ~-0.22 ms scalar    secondary locality/pitch signal
B -> C   ~-0.02 ms scalar    effectively noise
C -> D   ~-0.83 ms scalar    dominant causal effect
```

## 8. Production design

The production fix deliberately keeps two representations:

```text
oversized SRCALPHA overscan raster
  -> remains the semantic/build representation

cache-install boundary
  -> crop actual terrain content
  -> precompose once against frame clear color
  -> build compact 32-bit RGB Surface with alpha mask=0

steady state
  -> present from compact opaque Surface
```

This changes presentation representation without rewriting the verified overscan builder.

## 9. Fixed-camera production validation

At `54d1774...`, use the same source state for both sides:

```bash
STAR_TERRAIN_PRESENTATION_MODE=legacy_alpha
```

versus:

```bash
STAR_TERRAIN_PRESENTATION_MODE=opaque_compact
```

Three fresh-process runs per side produced:

```text
                         Legacy       Opaque       Change
scalar_execute            2.346        1.383 ms    -0.963 ms (-41.1%)
queue_submit              3.255        2.354 ms    -0.901 ms (-27.7%)
render_engine             3.333        2.444 ms    -0.889 ms (-26.7%)
batch_blits               0.696        0.736 ms    essentially unchanged
```

Aggregate frame time drifted in the opposite direction across process groups, so the local renderer timers are the primary causal evidence.

## 10. Camera-stress validation

The deterministic stress driver intentionally uses discrete camera state jumps every 0.75 s, including pan distances larger than the 256-pixel overscan margin and explicit zoom changes. It is a rebuild-stress workload, not a smooth camera-motion simulation.

Run:

```bash
uv run tools/terrain_camera_stress.py \
  --socket /tmp/star-scale.sock \
  --density 1.0 \
  --seed 42 \
  --target-radius 12 \
  --warmup 5 \
  --stress-duration 10 \
  --step-seconds 0.75 \
  --sustained-duration 20 \
  --output terrain-camera.json
```

3-run means:

```text
                         Legacy       Opaque       Change
scalar_execute            1.872        1.209 ms    -0.663 ms (-35.4%)
queue_submit              3.594        2.946 ms    -0.648 ms (-18.0%)
render_engine             3.717        3.073 ms    -0.645 ms (-17.3%)
P95                      38.230       38.759 ms    +0.529 ms
P99                      58.730       59.385 ms    +0.655 ms
rolling max              67.204       67.464 ms    +0.260 ms
```

Opaque cache rebuilds occurred about 9-10 times per run. Their observed maximum build cost averaged ~2.51 ms, while `map_overscan_build_step` maximum averaged ~4.16 ms versus ~1.53 ms in Legacy. Despite that extra rebuild work, P95/P99/max did not develop a new tail pathology.

## 11. Regression-test command

```bash
uv run pytest \
  rotk_env/tests/test_terrain_presentation_cache.py \
  rotk_env/tests/test_scale_camera_stress.py \
  rotk_env/tests/test_scale_map_overscan.py \
  rotk_env/tests/test_render_presentation_ablation.py \
  framework/tests/test_render_blit_batching.py \
  framework/tests/test_render_engine_profile_breakdown.py \
  -q
```

The exact stdout is not currently archived, so the case remains **VALIDATED** rather than formally CLOSED under `PROTOCOL.md`.

## 12. Formal artifacts

```text
results/diagnostics/       format/alpha diagnostic
results/intermediate/      valid workload, invalid intended opaque variable
results/abcd/              formal orthogonal attribution
results/validation/fixed-camera/
results/validation/camera-stress/
artifacts/SHA256SUMS
```

## 13. Related records

- [`manifest.yaml`](manifest.yaml)
- [`analysis.md`](analysis.md)
- [`decision.md`](decision.md)
- [`../2026-09-render-engine-attribution/`](../2026-09-render-engine-attribution/)
- [`../2026-09-camera-fog-full-rebuild/`](../2026-09-camera-fog-full-rebuild/)
