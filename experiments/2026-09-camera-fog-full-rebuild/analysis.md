# Analysis — Camera Geometry Change -> Fog Full Rebuild

## 1. Observation

The Terrain production camera-stress workload produced repeated long frames whenever the camera jumped between discrete pan/zoom states. The tail appeared in both Terrain presentation modes, including the new opaque path whose own cache rebuild cost remained much smaller.

Across the six canonical camera-stress runs:

```text
camera transitions                    10-11 / run
fog_surface_full_build max            ~25.4-30.3 ms
MapRenderSystem max                    ~39.3-46.1 ms
epoch worst slow frame                ~55.9-67.6 ms
rolling max frame                     ~61.9-73.4 ms
P99                                    ~55.1-62.3 ms
```

## 2. Competing hypotheses

### H1 — Terrain opaque-cache rebuild created the long frames

Plausible because camera changes rebuild Terrain caches and the opaque representation adds extra cache-build work.

### H2 — Fog view-geometry invalidation causes the dominant transition spike

Plausible because `fog_surface_full_build` appears on the large `MapRenderSystem` frames and costs tens of milliseconds.

### H3 — The discrete stress pattern exaggerates a condition that is rare under real smooth camera movement

Plausible because the v1 workload jumps camera state every 0.75 s rather than moving it incrementally every frame.

### H4 — Every small camera change triggers a full Fog rebuild

This is an important but currently unproven possibility. The present workload does not have the resolution required to establish it.

## 3. Instrumentation / diagnostic changes

The existing deterministic camera-stress harness records:

```text
camera start/current state
transition count
step index
Fog state and workload guards
renderer subsystem timers
Terrain cache-build counters/timers
```

The current profiler already exposes `fog_surface_full_build`, `MapRenderSystem`, P95/P99/max frame metrics and slow-frame evidence.

What is still missing is a continuous-camera workload plus explicit Fog rebuild counters/reasons per camera-change frame.

## 4. Evidence

### Evidence against H1 — Terrain opaque cache is not the tail root cause

Opaque stress adds approximately:

```text
max opaque cache build        ~2.5 ms class
max overscan build step       ~4.16 ms mean maximum
```

but its P95/P99/rolling-max are nearly the same as Legacy:

```text
                         Legacy       Opaque
P95                      38.230       38.759 ms
P99                      58.730       59.385 ms
rolling max              67.204       67.464 ms
```

Meanwhile Opaque still improves the renderer-local steady-state path by ~0.645 ms. This separates Terrain's optimization from the large transition-frame tail.

### Evidence for H2 — Fog full rebuild dominates transition work

The largest `MapRenderSystem` frames include `fog_surface_full_build` events in the ~25-30 ms range. These costs are an order of magnitude larger than the additional opaque Terrain cache-build work and align with the long transition-frame signature.

The current evidence therefore supports the statement:

> expensive Fog full rebuilds occur during the discrete camera geometry stress and dominate the observed render tail.

It does not yet justify a stronger statement about the exact invalidation rule.

### Evidence for H3 — workload semantics matter

The user-visible camera motion during the archived stress run was discontinuous: the battlefield jumped, held, then jumped again. This matches the harness design (`step_seconds=0.75`) and confirms the workload is a deliberate boundary/rebuild stress test rather than a realistic smooth camera trace.

### Evidence status for H4

Insufficient. The current experiment does not measure small per-frame camera deltas or count full rebuilds per camera-change frame. H4 remains open.

## 5. Root cause

**Not formally established yet.**

Current working hypothesis:

> Camera view-geometry invalidation can trigger expensive Fog full rebuilds, and those rebuilds dominate the long render frames observed by the discrete stress workload.

The exact trigger condition, invalidation granularity and frequency under realistic continuous motion remain unknown.

## 6. Current causal chain

What is supported:

```text
discrete camera geometry transition
  -> Fog full rebuild observed
  -> ~25-30 ms fog_surface_full_build
  -> ~39-46 ms MapRenderSystem maximum
  -> ~56-68 ms epoch worst slow frame
```

What is **not** yet supported:

```text
every small camera move
  -> full Fog rebuild
```

## 7. Rejected explanations

- **Terrain opaque presentation cache is the dominant new tail source** — rejected because its rebuild cost is ~2.5 ms class and Legacy/Opaque tail metrics are nearly unchanged.
- **The camera workload is smooth motion** — rejected by harness semantics and direct visual observation; it uses discrete state jumps.
- **The exact Fog invalidation root cause is already known** — rejected; the current evidence does not separate pan, zoom, threshold crossing and small continuous movement.

## 8. Limits of the evidence

- Camera stress v1 uses discrete jumps every 0.75 s.
- Pan and zoom are mixed within one pattern rather than orthogonalized.
- No explicit counter yet maps each camera-change frame to Fog rebuild/no-rebuild.
- The exact `view_geometry_changed` invalidation condition still requires source/instrumentation attribution.
- Measurements are from one Mac mini / macOS Pygame environment.
- This case has no locally duplicated raw evidence; it cross-references the canonical Terrain camera-stress artifacts.

## 9. Next attribution design

Add a deterministic continuous-camera workload with independent modes:

```text
P0 fixed camera control
P1 smooth pan, small per-frame delta, no zoom
P2 smooth pan across known geometry/cache boundary
Z1 smooth zoom only
PZ combined smooth pan + zoom
```

Add counters/reasons:

```text
camera_changed_frames
fog_full_rebuild_count
fog_full_rebuild_reason
fog_rebuilds_per_camera_changed_frame
```

Then correlate those counters with:

```text
fog_surface_full_build
MapRenderSystem
P95 / P99 / rolling max
```

Only after that attribution should a production Fog geometry optimization be selected.

## 10. Raw evidence

Canonical evidence is owned by the Terrain case:

- [`../2026-09-terrain-presentation/results/validation/camera-stress/`](../2026-09-terrain-presentation/results/validation/camera-stress/)
- [`../2026-09-terrain-presentation/artifacts/SHA256SUMS`](../2026-09-terrain-presentation/artifacts/SHA256SUMS)
- [`manifest.yaml`](manifest.yaml)
