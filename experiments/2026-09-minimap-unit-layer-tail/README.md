# MiniMap Unit-Layer Tail Latency and 5K 60Hz Core Stress Boundary

**Status:** DRAFT — causal conclusion accepted; raw-artifact upload and integrity finalization pending  
**STAR repository:** `star-nexus/star`  
**Diagnostic correlation commit:** `def0afaf722a1cd1bf1926a8934c1974a47a9872`  
**Ablation implementation:** `6b7a02c51a869e4c85e63144f2c00cb0128ce880`  
**Measurement / regression-protected commit:** `c5dd895e242b46f193050d8212fcc45b625ad885`  
**Branch at time:** `perf/system-scale-frontier`  
**Validated tag:** N/A — archive finalization pending raw evidence

## 1. Problem

The 5000-unit Phase 4 realtime scale workload appeared to lose a strict 60 Hz controlled-work budget at relatively low moving density. A clean 25%-moving run could show controlled-work P99 in the ~17–18 ms class even though previously closed GC, Vision-cache, culling, Fog-presentation, and movement-continuity signatures were absent.

The investigation asked whether the tail was caused by the number of units crossing hex boundaries, by periodic Vision maintenance, or by another presentation-side workload.

## 2. Why it matters

STAR is an Agent/ENV benchmark. Auxiliary presentation work must not define the realtime capacity of the authoritative environment. A Tier-2 UI feature such as dynamic MiniMap unit dots must not contaminate a 60 Hz engineering stress measurement intended to characterize core runtime scalability.

This case therefore separates:

```text
core realtime workload capacity
from
auxiliary interactive-presentation overhead
```

The literal 60 Hz stress criterion remains:

```text
controlled_work_frame_ms.p99 <= 16.67 ms
```

The final 50%-moving point is recorded separately as a practical `BORDERLINE ACCEPT`: its three-run median P99 is 16.68202856 ms, approximately 0.012 ms / 0.07% above the literal budget. The threshold itself is not moved, and no further 37.5% binary search is required for this investigation.

## 3. Measurement infrastructure

This experiment reuses the production Performance Measurement & Regression Infrastructure introduced in Phase 3; it does not create a separate timing plane.

The reused measurement semantics include:

```text
~5 s wall-clock rolling window
4096-frame hard sample capacity
controlled_work = STAR-controlled work/update/render/vision/input self time
platform_input separated
present separated
uninstrumented residual reported
section inclusive/self timing
frame metrics and tail thresholds
```

Phase 4 adds workload metadata/guards and snapshot-only crossing-cost correlation on top of that profiler.

Related record:

- [`../../records/performance-measurement-regression-infra-2026-09.md`](../../records/performance-measurement-regression-infra-2026-09.md)

## 4. Source checkout

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout c5dd895e242b46f193050d8212fcc45b625ad885
uv sync
```

The controlled ON/OFF ablation intentionally uses the same source state. The independent variable is the explicit scale-only `STAR_SCALE_MINIMAP_UNITS` override.

## 5. Environment

```text
Machine:       Mac mini M4
OS:            macOS (exact version to be completed from run host metadata)
Python:        3.13.12
Display mode:  window, 2480x1268
Scenario:      TestMap-8K-scale-5000
Map:           91x91 / 8281 terrain tiles
Resident:      5000 units
Fog:           ON
Motion:        staggered
GC policy:     realtime_defer
Render:        uncapped
Gameplay input: blocked
Execution pathfinding: disabled
Production animation + position commits: enabled
```

## 6. Reproduce the problem — MiniMap Unit Layer ON

Start a fresh STAR process without the MiniMap override:

```bash
uv run python -m rotk_env.main \
  --skip-start \
  --mode real_time \
  --scenario TestMap-8K-scale-5000 \
  --players human_vs_two_ai \
  --no-hub \
  --seed 42 \
  --uncapped \
  --scale-harness-socket /tmp/star-scale.sock
```

Run the 25% staggered density point:

```bash
uv run python tools/scale_driver.py \
  --socket /tmp/star-scale.sock \
  density-point \
  --density 0.25 \
  --phase staggered \
  --seed 42 \
  --phase-seed 42 \
  --route-steps 12 \
  --duration 20 \
  --warmup 5 \
  --sample-after 7 \
  --gc-policy realtime_defer \
  --profile results/phase4/density-025-minimap-units-on-profile.json \
  --output results/phase4/density-025-minimap-units-on.json
```

Expected problem signature from the controlled A/B cohort:

```text
MiniMap unit layer enabled     true
MiniMap refresh pulse P99      ~4.04 ms
controlled-work P99            ~16.81 ms
frames >16.67 ms               6 / 343
```

The earlier correlation diagnostic also showed that every controlled-work over-budget frame in that window coincided with MiniMap unit refresh, while frames without MiniMap refresh did not exceed 16.67 ms.

## 7. Validate the ablation — MiniMap Unit Layer OFF

Start a fresh STAR process with only dynamic MiniMap unit dots disabled:

```bash
STAR_SCALE_MINIMAP_UNITS=off \
uv run python -m rotk_env.main \
  --skip-start \
  --mode real_time \
  --scenario TestMap-8K-scale-5000 \
  --players human_vs_two_ai \
  --no-hub \
  --seed 42 \
  --uncapped \
  --scale-harness-socket /tmp/star-scale.sock
```

Repeat the same 25% density command, changing only output filenames.

Expected fixed/profile signature:

```text
MiniMap visible                 true
MiniMap terrain                 true
MiniMap camera viewport         true
MiniMap clickable               true
MiniMap dynamic unit layer      false
minimap_unit_refreshed          0 throughout measurement window
MiniMapSystem P99               ~0.057 ms
controlled-work P99             ~13.67 ms
frames >16.67 ms               0
```

The regression test `rotk_env/tests/test_window_minimap_ablation.py` protects the rule that the scale override disables only the dynamic unit layer.

## 8. 50% 60Hz core stress point

With MiniMap dynamic units OFF and all other formal conditions held fixed, 2500 of 5000 resident units move continuously.

Three fresh-process run-level controlled-work P99 values are:

```text
Run 1  16.68202856 ms
Run 2  16.13298628 ms
Run 3  16.80107026 ms
Median 16.68202856 ms
```

Literal strict classification:

```text
16.68202856 > 16.67 ms
-> boundary FAIL under the exact stress threshold
```

Accepted engineering disposition:

```text
BORDERLINE ACCEPT
margin above literal threshold ~= 0.012 ms / 0.07%
no evidence of a reopened historical pathology
no 37.5% binary-search follow-up required
```

This disposition does not redefine the 16.67 ms stress threshold and must not be rewritten later as a clear strict PASS.

## 9. Formal artifacts — upload pending

The raw JSON files are still local and will be added before this case is promoted from DRAFT to VALIDATED/CLOSED.

Intended canonical evidence set:

```text
results/density-025-crossing-correlation.json
results/density-025-crossing-correlation-profile.json
results/density-025-minimap-units-on.json
results/density-025-minimap-units-on-profile.json
results/density-025-minimap-units-off.json
results/density-025-minimap-units-off-profile.json
results/density-050-core-60hz-run1.json
results/density-050-core-60hz-run1-profile.json
results/density-050-core-60hz-run2.json
results/density-050-core-60hz-run2-profile.json
results/density-050-core-60hz-run3.json
results/density-050-core-60hz-run3-profile.json
```

After upload:

```bash
cd experiments/2026-09-minimap-unit-layer-tail
shasum -a 256 results/*.json > artifacts/SHA256SUMS
shasum -a 256 -c artifacts/SHA256SUMS
```

Do not create an empty checksum file before raw artifacts exist.

## 10. Related records

- [`manifest.yaml`](manifest.yaml)
- [`analysis.md`](analysis.md)
- [`decision.md`](decision.md)
- [`../2026-09-dynamic-world-scaling/`](../2026-09-dynamic-world-scaling/)
- [`../../records/performance-measurement-regression-infra-2026-09.md`](../../records/performance-measurement-regression-infra-2026-09.md)
- [`../../records/performance-frontier.md`](../../records/performance-frontier.md) — update only after raw evidence + SHA256 are finalized
