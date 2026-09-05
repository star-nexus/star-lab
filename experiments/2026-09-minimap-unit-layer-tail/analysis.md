# Analysis — MiniMap Unit-Layer Tail Latency and 5K 60Hz Core Stress Boundary

## 1. Observation

The Phase 4 5000-unit stress workload showed a mismatch between average throughput and strict 60 Hz tail behavior.

At 25% moving density, with Fog ON, staggered motion, `realtime_defer`, and the full interactive MiniMap unit layer enabled, controlled-work P99 could enter the ~17–18 ms range even though average throughput remained above 60 FPS.

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

Observed evidence:

```text
normal frames had more commits on average than over-budget frames in the diagnostic window
maintenance-off controlled-work correlation with commit count was weak
Pearson r approximately +0.14
R^2 approximately 0.02
slope approximately 0.0084 ms / commit
```

A frame bucket with more than 50 commits and no periodic MiniMap/Vision maintenance remained comfortably below the 16.67 ms budget.

Interpretation:

> Hex crossing contributes to the steady dynamic baseline, but commit count does not explain the 25% tail failure.

This rejects reopening the historical movement-continuity case: the old issue was visual interpolation/overshoot/deadzone behavior; the current scale tail is a different mechanism.

### Evidence against H2 as the primary 25% cause

Vision audit increased Vision cost by roughly 2 ms, but audit-only frames in the decisive 25% diagnostic remained below 16.67 ms.

Interpretation:

> Vision audit consumes tail headroom, but it was not the primary mechanism producing the 25% failure.

At the later 50% stress boundary, occasional Vision-audit frames can become the last contributor that pushes an otherwise normal heavy frame over 16.67 ms. This is treated as normal work composition near the boundary, not as a reopened Vision-cache or Vision-audit pathology.

### Evidence for H3 — MiniMap refresh is the dominant 25% tail mechanism

Conditioning the 25% correlation window by maintenance state produced a strong separation:

```text
no MiniMap refresh:
  controlled-work average approximately 13.06 ms
  zero over-budget frames in the main no-refresh group

MiniMap refresh:
  MiniMapSystem rises from approximately 0.08 ms to approximately 4.09 ms
  controlled-work rises by approximately the same ~4.0 ms
  all observed over-budget frames in the decisive correlation window coincided with MiniMap unit refresh
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

The formal 25% A/B uses the same STAR measurement source and fresh processes.

Representative result:

| Metric | MiniMap Units ON | MiniMap Units OFF |
|---|---:|---:|
| Controlled avg | ~12.998 ms | ~11.975 ms |
| Controlled P95 | ~16.417 ms | ~12.632 ms |
| Controlled P99 | ~16.808 ms | ~13.666 ms |
| Controlled max | ~19.438 ms | ~14.083 ms |
| Frames >16.67 ms | 6 / 343 | 0 / 369 |
| MiniMapSystem P99 | ~4.042 ms | ~0.057 ms |
| MiniMap unit refreshes in measured window | present | 0 |

The observed position-commit rate per second remained effectively unchanged. The lower commits-per-frame in the faster OFF run is explained by the same world motion being distributed across more uncapped frames; it is not a reduced dynamic workload.

Interpretation:

> Removing only the auxiliary dynamic MiniMap unit-dot work eliminates the 25% 60 Hz tail failure while preserving the authoritative world workload.

### 50% Core 60Hz stress point

With MiniMap units OFF, 2500 of 5000 units move continuously.

Three fresh-process P99 results:

```text
Run 1  16.68202856 ms
Run 2  16.13298628 ms
Run 3  16.80107026 ms
Median 16.68202856 ms
```

All formal workload/GC/input/Fog/production-animation guards passed in the preserved run summaries.

The steady shape is repeatable:

```text
controlled-work average  ~14.1–14.24 ms
P50                      ~14.0–14.18 ms
P95                      ~15.0–15.23 ms
```

Subsystem scale is also repeatable:

```text
AnimationSystem  ~2.64–2.68 ms
VisionSystem     ~0.79 ms average
UnitRenderSystem ~4.3–4.4 ms
MapRenderSystem  ~2.1–2.2 ms
MiniMapSystem    ~0.047 ms with unit layer OFF
```

The 50% workload produces approximately 5000 position commits per second, matching the expected 2500 movers × ~2 hex/s scale.

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
  -> 25% controlled P99 drops to ~13.67 ms
  -> over-budget frames drop to zero in the A/B window
```

## 7. Rejected explanations

- **Hex crossing count as the primary 25% tail cause** — rejected by weak conditioned correlation and by high-commit frames that remain within budget when periodic maintenance is absent.
- **Historical movement-continuity bug reopened** — rejected because the old issue was animation/render interpolation at segment boundaries; current evidence identifies an auxiliary MiniMap full redraw.
- **Realtime GC reopened** — rejected because `realtime_defer` guards pass and the old 15–30 ms UnitRender GC-pause signature is absent.
- **Vision geometry-cache thrashing** — rejected because the 16,384 cache remains bounded with zero evictions and normal low miss counts.
- **Vision audit as the primary 25% cause** — rejected because audit-only frames remained within budget in the decisive 25% diagnostic. At 50%, audit can consume remaining headroom but does not establish a new pathological case.
- **MiniMap should simply be excluded from accounting while still executing** — rejected because removing a metric from `controlled_work` would not remove the real main-thread delay. The work must either not execute in the Core stress profile or be redesigned off the critical path.

## 8. Limits of the evidence

- The measured host is one Mac mini M4 configuration.
- The formal scenario is the 91x91 / 5000-resident large-window map.
- This case validates profile isolation of the dynamic MiniMap unit layer; it does not implement or validate a dirty-cell incremental MiniMap renderer.
- It does not validate asynchronous MiniMap execution or ECS multi-core scheduling.
- The 50% result is intentionally retained as `BORDERLINE ACCEPT`, not as a literal strict PASS; its median P99 remains 0.012 ms above the unchanged 16.67 ms stress criterion.
- The exact maximum 60 Hz moving-density frontier is intentionally not binary-searched further.
- The planned distinction between canonical 30 Hz benchmark semantics and 60 Hz engineering stress mode is an architectural/runtime policy discussion outside the causal proof of this case unless separately implemented and validated.

## 9. Raw evidence

Raw evidence upload is pending. See [`manifest.yaml`](manifest.yaml) and [`README.md`](README.md) for the intended canonical filenames.

Do not promote this package to `VALIDATED` / `CLOSED`, and do not add a new Performance Frontier row, until the raw JSON artifacts are committed and covered by experiment-relative `artifacts/SHA256SUMS`.
