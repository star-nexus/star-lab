# Analysis — MiniMap Unit-Layer Tail Latency and 5K 60Hz Core Stress Boundary

## 1. Observation

The Phase 4 5000-unit stress workload showed a mismatch between average throughput and strict 60 Hz tail behavior.

At 25% moving density, with Fog ON, staggered motion, `realtime_defer`, and the full interactive MiniMap unit layer enabled, controlled-work P99 entered the ~17–18 ms range even though average throughput remained above 60 FPS.

The already-closed historical signatures were absent:

```text
no realtime Gen2-GC UnitRender spike
no Vision geometry-cache eviction/thrashing
no old spatial-cull ~3.5 ms signature
no Camera->Fog full rebuild
no movement-continuity deadzone signature
no platform-input event-pump tail inside controlled-work classification
```

The initial 25% workload also showed roughly 35–40 position commits per frame, motivating a hypothesis that hex-boundary crossings themselves were driving the tail.

All formal raw artifacts are now archived and covered by experiment-relative SHA256 metadata.

## 2. Competing hypotheses

### H1 — Hex crossing / position-commit count drives the 25% P99 failure

Why it was plausible:

- a unit crossing a hex boundary creates a discrete authoritative state transition;
- the position commit fans out into the spatial index, Vision dirty invalidation, Fog delta generation, and other derived state;
- the earlier single-unit visual movement-continuity case also involved the segment/hex boundary, although its causal mechanism was different and already CLOSED.

### H2 — Periodic Vision safety audit drives the tail

Why it was plausible:

- normal Vision work is K-driven, but the safety audit periodically scans the full resident set;
- an audit can add roughly 2 ms of Vision cost and therefore could matter near a 16.67 ms frame budget.

### H3 — MiniMap dynamic-unit refresh drives the tail

Why it was plausible:

- the window MiniMap uses a 15 Hz dynamic unit layer;
- its invalidation is driven by `UnitSpatialIndex.revision`;
- code inspection showed that a refresh clears the unit surface and calls the inherited `_render_units()` path, which traverses all entities with `HexPosition` and `Unit` and redraws every dot.

This means the current implementation is:

```text
incremental invalidation
+
full O(Nresident) redraw on refresh
```

rather than true dirty-unit/cell incremental redraw.

## 3. Instrumentation / diagnostic changes

The investigation deliberately reused the Phase-3 production profiler instead of introducing a second measurement plane.

The existing profiler already retained per-frame samples for:

```text
controlled_work_ms
effect_position_index_changes
Vision / Animation / UnitRender / MapRender / MiniMap section timing
```

A snapshot-only crossing-cost correlation diagnostic was added at:

```text
def0afaf722a1cd1bf1926a8934c1974a47a9872
```

It computed, after the measurement window:

```text
commit-count buckets
controlled-work distributions by bucket
Vision-audit condition groups
MiniMap-refresh condition groups
over-budget vs within-budget groups
Pearson correlation / linear fit
```

No new per-frame timing workload was added for the correlation analysis.

An explicit scale-only MiniMap unit-layer override was then added at:

```text
6b7a02c51a869e4c85e63144f2c00cb0128ce880
```

and protected by regression tests at:

```text
c5dd895e242b46f193050d8212fcc45b625ad885
```

The override changes only `MiniMap.show_units`; terrain, camera viewport, MiniMap visibility, border/composite, and clickability remain enabled.

## 4. Evidence

### Evidence against H1 — crossing count is not the P99 driver

The 25% correlation window did not show the expected monotonic relation between commit count and tail latency.

The formal diagnostic artifact preserves:

```text
controlled-work P99       18.51077221 ms
position commits avg       38.8447 / frame
Vision dirty avg           38.8882 / frame
```

Conditioned correlation from the same profile showed that maintenance-off commit count explained very little frame-time variance; high-commit frames could remain comfortably within budget when periodic maintenance was absent.

Interpretation:

> Hex crossing contributes to the steady dynamic baseline, but commit count does not explain the 25% tail failure.

This rejects reopening the historical movement-continuity case: the old issue was visual interpolation/overshoot/deadzone behavior; the current scale tail is a different mechanism.

### Evidence against H2 as the primary 25% cause

Vision audit increased Vision cost, but audit-only frames in the decisive 25% diagnostic remained below 16.67 ms.

Interpretation:

> Vision audit consumes tail headroom, but it was not the primary mechanism producing the 25% failure.

At the later 50% stress boundary, occasional Vision-audit frames can become the last contributor that pushes an otherwise normal heavy frame over 16.67 ms. This is treated as normal work composition near the boundary, not as a reopened Vision-cache or Vision-audit pathology.

### Evidence for H3 — MiniMap refresh is the dominant 25% tail mechanism

Conditioning the 25% correlation window by maintenance state produced a strong separation:

```text
no MiniMap refresh:
  controlled-work average approximately 13.06 ms
  no over-budget frames in the main no-refresh group

MiniMap refresh:
  MiniMapSystem rises from approximately 0.08 ms to approximately 4.09 ms
  controlled-work rises by approximately the same ~4.0 ms
  all observed over-budget frames in the decisive correlation window coincide with MiniMap unit refresh
```

The code path explains the fixed pulse:

```text
any relevant spatial revision
  -> wait until 15 Hz refresh is due
  -> clear cached unit surface
  -> query all resident Unit + HexPosition entities
  -> convert all positions
  -> redraw all unit dots
  -> ~4 ms periodic main-thread pulse at Nresident = 5000
```

This is O(Nresident) presentation work triggered by incremental invalidation.

### Controlled A/B — same source, same workload, only MiniMap unit layer changes

Formal 25% ON artifact:

```text
controlled avg       12.997793137 ms
controlled P95       16.416786800 ms
controlled P99       16.808029340 ms
controlled max       19.437584000 ms
frames >16.67 ms      6 / 343
```

Formal 25% OFF artifact:

```text
controlled avg       11.974982583 ms
controlled P95       12.631831800 ms
controlled P99       13.666346920 ms
controlled max       14.082585000 ms
frames >16.67 ms      0 / 369
```

The observed position-commit rate per second remained effectively unchanged. The lower commits-per-frame in the faster OFF run is explained by the same world motion being distributed across more uncapped frames; it is not a reduced dynamic workload.

Interpretation:

> Removing only the auxiliary dynamic MiniMap unit-dot work eliminates the 25% 60 Hz tail failure while preserving the authoritative world workload.

### 50% Core 60Hz stress point

With MiniMap units OFF, 2500 of 5000 units move continuously.

Three fresh-process controlled-work results:

| Run | Avg | P50 | P95 | P99 | Max |
|---|---:|---:|---:|---:|---:|
| 1 | 14.095536 | 14.002666 | 14.990516 | 16.682029 | 17.534501 |
| 2 | 14.190961 | 14.113835 | 15.009150 | 16.132986 | 16.468418 |
| 3 | 14.243056 | 14.180208 | 15.228605 | 16.801070 | 16.991708 |
| **Run-level median** | **14.190961** | — | — | **16.682029** | — |

All preserved summary artifacts report `ok:true`, and the formal workload/GC/input/Fog/production-animation guards are true.

Position-change and Vision-dirty work are internally consistent:

```text
Run 1 position changes avg  78.5486/frame
Run 1 Vision dirty avg      78.5737/frame
Run 2 position changes avg  79.0221/frame
Run 2 Vision dirty avg      79.0189/frame
Run 3 position changes avg  79.3333/frame
Run 3 Vision dirty avg      79.3714/frame
```

At the observed frame rates this is approximately 5000 position commits/s, matching the expected 2500 movers × ~2 hex/s workload.

## 5. Root cause

> The 25% apparent 60 Hz scale failure was dominated by the auxiliary MiniMap dynamic-unit layer. The layer used `UnitSpatialIndex.revision` only for invalidation/refresh scheduling; each 15 Hz refresh still cleared and rebuilt all 5000 unit dots through a full resident-unit traversal, creating an approximately 4 ms periodic O(Nresident) main-thread pulse that pushed otherwise acceptable core frames over 16.67 ms.

This was a presentation-boundary contamination of the core stress measurement, not evidence that 1250 moving units exceeded STAR's authoritative realtime capacity.

## 6. Causal chain

```text
5000 resident units + continuous movement
  -> spatial revision changes continuously
  -> 15 Hz MiniMap refresh becomes due
  -> clear dynamic MiniMap unit surface
  -> full query/redraw of all resident unit dots
  -> ~4 ms periodic main-thread pulse
  -> controlled-work tail crosses 16.67 ms
```

Ablation chain:

```text
STAR_SCALE_MINIMAP_UNITS=off
  -> dynamic MiniMap unit redraw does not execute
  -> MiniMapSystem remains ~0.05 ms
  -> same world motion / Vision / Fog / render workload continues
  -> 25% controlled P99 drops to 13.66634692 ms
  -> over-budget frames drop to zero in the A/B window
```

## 7. Rejected explanations

- **Hex crossing count as the primary 25% tail cause** — rejected by weak conditioned correlation and by high-commit frames that remain within budget when periodic maintenance is absent.
- **Historical movement-continuity bug reopened** — rejected because the old issue was animation/render interpolation at segment boundaries; current evidence identifies an auxiliary MiniMap full redraw.
- **Realtime GC reopened** — rejected because `realtime_defer` guards pass and the old 15–30 ms UnitRender GC-pause signature is absent.
- **Vision geometry-cache thrashing** — rejected because the 16,384 cache remains bounded without the old eviction signature.
- **Vision audit as the primary 25% cause** — rejected because audit-only frames remained within budget in the decisive 25% diagnostic. At 50%, audit can consume remaining headroom but does not establish a new pathological case.
- **MiniMap should simply be excluded from accounting while still executing** — rejected because removing a metric from `controlled_work` would not remove the real main-thread delay. The work must either not execute in the Core stress profile or be redesigned off the critical path.

## 8. Limits of the evidence

- The measured host is one Mac mini M4 configuration.
- Exact macOS minor version and installed memory were not captured in the canonical artifacts and are intentionally not reconstructed.
- The formal scenario is the 91x91 / 5000-resident large-window map.
- This case validates profile isolation of the dynamic MiniMap unit layer; it does not implement or validate a dirty-cell incremental MiniMap renderer.
- It does not validate asynchronous MiniMap execution or ECS multi-core scheduling.
- The 50% result is intentionally retained as `BORDERLINE ACCEPT`, not as a literal strict PASS; its median P99 remains 0.01202856 ms above the unchanged 16.67 ms stress criterion.
- The exact maximum 60 Hz moving-density frontier is intentionally not binary-searched further.
- The planned distinction between canonical 30 Hz benchmark semantics and 60 Hz engineering stress mode is outside the causal proof of this case unless separately implemented and validated.

## 9. Raw evidence

Canonical evidence is preserved under [`results/`](results/) and all 12 formal JSON artifacts are listed in [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS).

Verify from the experiment root:

```bash
shasum -a 256 -c artifacts/SHA256SUMS
```

All 12 entries were verified `OK` before this case was marked CLOSED.
