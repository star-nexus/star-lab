# RenderEngine Queue-Drain and Presentation Attribution

**Status:** CLOSED  
**STAR repository:** `star-nexus/star`  
**Problem commit:** `a24482d438157aa23b371b6e34d49b1c04fec7f7`  
**Formal causal-measurement commit:** `6e8c151494de2b37071ecdcd5f1898b7387e057a`  
**Fix commit:** N/A — attribution-only investigation  
**Validated commit:** `6e8c151494de2b37071ecdcd5f1898b7387e057a`  
**Validated tag:** N/A — no separate attribution milestone tag was created

## 1. Problem

At the validated 5000-resident / 5000-moving frontier, `render_engine` consumed roughly 5.5 ms per frame. The top-level timer only wrapped `RenderManager.update()`, while `pygame.display.flip()` was measured separately, so the remaining question was where the queue-drain cost actually lived.

The investigation had to distinguish Python command preparation from actual Surface submission before changing renderer architecture.

## 2. Why it matters

A 5+ ms black box is too large to optimize by intuition. Rewriting queue structures, moving code to native extensions, or changing batching without attribution could easily optimize the wrong layer. The goal was to expose a stable hot boundary and identify the dominant causal workloads.

## 3. Source checkout

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout 6e8c151494de2b37071ecdcd5f1898b7387e057a
uv sync
```

Instrumentation was introduced incrementally at:

```text
b2bda2ffd1f66f2e45816cb1a6d851592cb08852  queue prepare/submit/clear + topology
d25271ffaaebb95b6490d4ccdd2fc06086b5bd7b  submit pack/blits/scalar + optional pixel metrics
6e8c151494de2b37071ecdcd5f1898b7387e057a  Fog/Terrain causal presentation ablations
```

## 4. Environment

```text
Machine: Mac mini
OS: macOS
Python: not captured in the archived run metadata; reproduce with uv at the exact STAR commit
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

## 5. Reproduce the causal baseline

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

### Terminal B — run the formal workload

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
  --output causal-normal.json
```

Use a fresh process for each run.

## 6. Expected problem signature

The final queue-drain decomposition should show approximately:

```text
render_engine                  5.4-5.6 ms
render_queue_submit            ~98% of RenderEngine
render_batch_pack              ~0.2 ms
render_batch_blits             ~3.7-3.8 ms
render_scalar_execute          ~1.4 ms
render queue commands          ~1690-1700
multi-blit batches             4
scalar commands                6
```

The queue topology is important: almost all plain blits form one very large batch, so command fragmentation is not the dominant cost.

## 7. Reproduce the causal ablations

Keep the same workload and change only one presentation variable per fresh process.

Fog presentation suppression:

```bash
STAR_RENDER_ABLATE_FOG_PRESENT=1 \
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

Terrain presentation suppression:

```bash
STAR_RENDER_ABLATE_TERRAIN_PRESENT=1 \
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

Expected causal signature from the archived 3x3x3 runs:

```text
Normal RenderEngine              5.425 ms
Fog-off RenderEngine             2.441 ms
Terrain-off RenderEngine         4.114 ms

Fog-off batch_blits delta       -3.043 ms
Terrain-off scalar delta        -1.366 ms
```

## 8. Result summary

| Finding | Measured evidence |
|---|---:|
| Queue Python packing | ~0.20-0.23 ms; not the dominant target |
| Fog full-window presentation | ~3.0 ms causal cost in `render_batch_blits` |
| Terrain cropped presentation | ~1.37 ms causal cost in `render_scalar_execute` |
| Directly attributable Fog + Terrain | ~4.41 ms, about 81% of normal `render_engine` |

Pixel diagnostics also showed that one 2480x1268 full-window Surface accounted for about 92.7% of submitted plain-blit source pixels, while clipping removed only about 648 pixels. This ruled out off-screen clipping as the explanation for the large batch cost.

## 9. Formal artifacts

Canonical raw evidence is owned by this case:

```text
results/queue-breakdown/
results/submit-breakdown/
results/pixel-diagnostics/
results/causal-ablation/
artifacts/SHA256SUMS
```

## 10. Related records

- [`manifest.yaml`](manifest.yaml)
- [`analysis.md`](analysis.md)
- [`decision.md`](decision.md)
- [`../2026-09-fog-presentation-bounding/`](../2026-09-fog-presentation-bounding/)
- [`../2026-09-terrain-presentation/`](../2026-09-terrain-presentation/)
