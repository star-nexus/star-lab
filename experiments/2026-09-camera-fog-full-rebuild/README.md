# Camera Geometry Change -> Fog Full Rebuild

**Status:** REPRODUCED  
**STAR repository:** `star-nexus/star`  
**Problem / measurement commit:** `54d17745098fb3fc4c43861d839e8dc40164c030`  
**Fix commit:** N/A — investigation remains open  
**Validated commit:** N/A  
**Validated tag:** N/A

## 1. Problem

The deterministic camera-stress validation for the Terrain opaque presentation cache exposed a separate tail-latency problem. Camera geometry transitions correlate with expensive `fog_surface_full_build` events and large `MapRenderSystem` spikes even though the Terrain opaque cache itself does not introduce a new tail pathology.

The current evidence reproduces the problem, but does **not** yet establish how frequently it occurs under realistic smooth camera motion or which specific geometry changes require a full Fog rebuild.

## 2. Why it matters

Under the stress workload, steady-state renderer improvements are overwhelmed on transition frames by Fog full rebuild work in the ~25-30 ms class. This creates 50-70+ ms frame tails even though normal fixed-camera frames remain much lower.

If small continuous camera movements trigger the same rebuild frequently, this would be a major interactive-rendering bottleneck. If rebuilds occur only on threshold crossings or zoom changes, the engineering response should be different.

## 3. Source checkout

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout 54d17745098fb3fc4c43861d839e8dc40164c030
uv sync
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
Initial camera: offset_x=1240, offset_y=634
Initial zoom: 0.15
GC policy: realtime_defer
Vision geometry-cache capacity: 16384
```

## 5. Reproduce the problem

Start STAR in either Terrain presentation mode. The Fog rebuild signature appears in both, so Terrain mode is not the independent variable for this case.

Example:

```bash
STAR_SCALE_HARNESS_SOCKET=/tmp/star-scale.sock \
STAR_SCALE_GC_POLICY=realtime_defer \
STAR_SCALE_VISION_GEOMETRY_CACHE_MAX_ENTRIES=16384 \
STAR_TERRAIN_PRESENTATION_MODE=opaque_compact \
uv run rotk_env/main.py \
  --skip-start \
  --scenario TestMap-8K-scale-5000 \
  --mode real_time \
  --players human_vs_two_ai \
  --seed 42 \
  --no-hub \
  --profile
```

Then run:

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

## 6. Important workload semantics

`terrain_camera_stress.py` v1 is intentionally a **discrete rebuild-stress workload**. Approximately every 0.75 s it jumps to a new camera state, including pan distances larger than the 256-pixel Terrain overscan margin and explicit zoom changes.

Visual behavior therefore looks like:

```text
jump -> hold -> jump -> hold -> zoom jump -> hold
```

It is **not** a smooth per-frame pan/zoom simulation. This distinction is part of the evidence boundary.

## 7. Expected reproduced signature

Across the six canonical camera-stress runs archived by the Terrain case, representative ranges are:

```text
camera transitions                    10-11 per run
fog_surface_full_build max            ~25.4-30.3 ms
MapRenderSystem max                    ~39.3-46.1 ms
epoch worst slow frame                ~55.9-67.6 ms
rolling max frame                     ~61.9-73.4 ms
P99                                    ~55.1-62.3 ms
```

The same runs show that switching Terrain from Legacy to Opaque still reduces steady-state RenderEngine cost, while tail metrics remain nearly unchanged. This separates the new Fog-rebuild problem from the Terrain optimization.

## 8. Current interpretation

The evidence supports:

```text
camera geometry transition
  -> Fog view geometry becomes invalid
  -> fog_surface_full_build occurs
  -> MapRenderSystem transition frame becomes expensive
  -> long frame tail
```

However, the following are still unknown:

```text
Does every small camera offset trigger a full rebuild?
Are pan and zoom equivalent invalidation causes?
Do only threshold crossings rebuild?
Can the Fog presentation/semantic geometry be translated instead of rebuilt?
Can rebuild work be incrementally or asynchronously bounded?
```

## 9. Next experiment required

Before changing Fog architecture, build a deterministic **continuous-camera attribution workload** that changes camera state in small per-frame increments and separately controls:

```text
pan only
zoom only
pan within cache/geometry tolerance
pan crossing geometry boundary
combined pan + zoom
```

Measure at least:

```text
number of camera-change frames
number of fog full rebuilds
rebuilds / camera-change frame
fog_surface_full_build inclusive/max
MapRenderSystem inclusive/max
P95 / P99 / rolling max
reason / invalidation counters
```

The next engineering step is therefore instrumentation, not optimization.

## 10. Canonical evidence

This case owns no duplicate raw JSON. The six canonical artifacts live in:

```text
../2026-09-terrain-presentation/results/validation/camera-stress/
```

Their checksums are recorded in that case's `artifacts/SHA256SUMS` and repeated as cross-references in this case's `manifest.yaml`.

Per `PROTOCOL.md`, this cross-reference-only case intentionally has no empty `artifacts/SHA256SUMS`.

## 11. Related records

- [`manifest.yaml`](manifest.yaml)
- [`analysis.md`](analysis.md)
- [`decision.md`](decision.md)
- [`../2026-09-terrain-presentation/`](../2026-09-terrain-presentation/)
- [`../2026-09-fog-presentation-bounding/`](../2026-09-fog-presentation-bounding/)
