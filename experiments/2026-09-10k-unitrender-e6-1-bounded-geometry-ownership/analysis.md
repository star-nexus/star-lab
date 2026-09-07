# Analysis — Phase 5 10K UnitRender E6-1 Bounded Geometry Ownership

## 1. Observation

Validated predecessor evidence:

```text
E5-3:
  world_x/world_y first-touch = 0.201 ms @50%
  world_x/world_y first-touch = 0.375 ms @100%

E6 attribution:
  Cull saving = 0.201 ms @50%
  Cull saving = 0.433 ms @100%
  workload-equivalence guards PASS
```

E6 established that long-lived per-hex derived geometry is materially causal. It did not establish a production-safe ownership model because the attribution cache retained every visited coordinate.

E6-1 replaced that attribution-only representation with a lazy cache whose retained keys are hard-bounded by the current `MapData` board.

## 2. Production hypotheses

### H1 — Board-bounded lazy geometry ownership retains the causal benefit

Why plausible:

- geometry is a pure function of fixed hex projection and `(col,row)`;
- normal skirmish movement is board-bounded;
- stable payload identity, not stable `UnitSpatialRecord` identity, was the validated mechanism;
- a cache limited to current board members gives the same steady-state payload reuse with a hard finite growth bound.

### H2 — Production ownership/lookup overhead erases or moves the benefit

Why plausible:

- every movement refresh adds a board-membership check and dict lookup;
- `_bucket_for_hex()` also enters the shared geometry path;
- a local Cull improvement is insufficient if equivalent cost shifts into Animation or controlled work.

## 3. Instrumentation

No new per-frame profiler instrumentation was added to the production candidate hot path.

Formal discrimination reused Phase-3 metrics:

```text
unit_visible_cull
UnitRenderSystem
AnimationSystem
controlled_work_frame_ms
position commits/s
Vision changed/s
Fog delta tiles/s
```

Structural boundedness was validated by deterministic candidate tests before performance measurement.

## 4. Source isolation / premeasurement validation

Formal run:

```text
run_id = 20260907-213322
control SHA   = 17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
treatment SHA = e7ba18b31870577110b591104ef8fa7b4713e43c
non-test runtime diff:
  rotk_env/utils/unit_spatial_index.py
```

Validation completed before the first density point:

```text
bounded geometry contract:       5 passed
control targeted regressions:   25 passed
treatment targeted regressions: 30 passed
source diff guard:              PASS
scenario/workload guards:       PASS
```

Every formal point also reported all scale-driver guards true, including full rolling-window coverage, Fog fixed ON, realtime-defer GC semantics, production animation, position commits, Vision dirty work, no execution pathfinding, and blocked gameplay input.

## 5. Evidence

### 50% moving

```text
controlled avg: 25.6331477 -> 25.4166656 ms  (-0.8445%)
controlled p99: 26.7667613 -> 26.5637844 ms

Cull avg:       2.1400464 -> 1.9091116 ms
Cull saving:    0.2309347 ms  (10.79%)
Cull p95 save:  0.2609042 ms

UnitRender avg: 9.3941644 -> 9.2237766 ms
saving:         0.1703879 ms

Animation avg:  3.4741726 -> 3.5131502 ms
regression:     +1.1219%

position commits/s delta: +0.0129%
Vision changed/s delta:    +0.0208%
Fog delta tiles/s delta:   +0.1208%
```

All preregistered checks passed.

### 100% moving

```text
controlled avg: 32.5667553 -> 32.1153198 ms  (-1.3862%)
controlled p99: 37.2615414 -> 33.6771260 ms

Cull avg:       2.4062871 -> 1.9830203 ms
Cull saving:    0.4232669 ms  (17.59%)
Cull p95 save:  0.4615656 ms

UnitRender avg: 10.2767846 -> 9.9095364 ms
saving:         0.3672482 ms

Animation avg:  7.2165212 -> 7.2577378 ms
regression:     +0.5711%

position commits/s delta: -0.0154%
Vision changed/s delta:    -0.0085%
Fog delta tiles/s delta:   -0.0348%
```

All preregistered checks passed.

## 6. Interpretation

### H1 is supported

The bounded production representation retained essentially the same Cull recovery seen in E6 attribution:

```text
             E6 attribution   E6-1 production
50% Cull        0.201 ms          0.231 ms
100% Cull       0.433 ms          0.423 ms
```

Do not over-interpret the small run-to-run differences. The important result is that the production-safe representation preserves the same material scale and density dependence as the isolated causal treatment.

### H2 is only partially supported

A small movement-side cost is visible:

```text
Animation avg:
  50%  +1.12%
  100% +0.57%
```

This is consistent with the bounded implementation adding board membership / geometry-cache lookup work during record refresh. However:

- both values remain below the preregistered 2% rejection threshold;
- UnitRender improves at both densities;
- controlled-work avg improves at both densities;
- workload rates are effectively unchanged.

Therefore the bounded ownership overhead does not erase the causal benefit.

## 7. Root cause / mechanism

The complete causal result is now:

> Movement refreshes replace otherwise-pure world-coordinate payload objects; Cull's subsequent first touch of those refreshed payloads is a material moving-density-dependent cost. Canonical per-board-hex geometry preserves those payload objects across movement refreshes. A lazy UnitSpatialIndex-owned cache bounded by current board membership retains the Cull/UnitRender benefit without introducing a material compensating cost or unbounded state.

## 8. Closed causal chain

```text
moving-dependent UnitRender growth
  -> spatial first-touch
  -> record field payload
  -> world_x/world_y dominant
  -> per-hex geometry reuse recovers cost
  -> unbounded attribution cache not production-safe
  -> board-bounded lazy ownership
  -> same Cull recovery retained
  -> small Animation overhead within preregistered tolerance
  -> KEEP production representation
```

## 9. Canonical 30 Hz classification

KEEP is not the same as frontier PASS.

At 10K / 100% moving:

```text
treatment controlled p99 = 33.677126 ms
canonical gate            = 33.33 ms
margin                    = +0.347126 ms
classification            = FAIL
```

The candidate reduced controlled p99 by about `3.584 ms` versus its paired control, but the retained production state remains just outside the strict 30 Hz canonical gate.

Therefore:

```text
production decision  = KEEP
frontier update      = NO
Phase 5 100% boundary = still open
```

## 10. Rejected explanations preserved

Do not reopen without new matching evidence:

- exact duplicate raster draw;
- candidate count growth;
- Fog branch mix;
- by_entity lookup;
- MapRender locality gap;
- `slots=True` as sufficient solution;
- stable `UnitSpatialRecord` identity;
- unbounded visited-coordinate cache as a production design.

## 11. Artifact review

Compact Evidence Package:

```text
20260907-213322-compact.zip
SHA256 0c9db01f29a04dcefc7ba896ab7ab533ec313c31a9e3d974d790b22893cb45a9
size 10616 bytes
```

Its package-local `SHA256SUMS` was independently recomputed and all entries matched. It contains all four decision-grade point payloads, regression logs, source/workload provenance, formal summary, raw profile SHA256/size references, and Raw package identity.

Raw Forensic Package:

```text
20260907-213322-raw.zip
SHA256 4322905154b69ec25688fa0775b0efdd62a7a60bf1366aead9d5e8f73d661c07
size 128760 bytes
```

Raw remains the authoritative forensic substrate. A stable canonical mirror/storage locator is still pending, so this validated KEEP case is not yet marked CLOSED.

## 12. Reporting note

The formal terminal formatter printed `<=` in the human-readable 30 Hz line even when the machine-readable result was FAIL. The summary JSON correctly contained:

```text
controlled_p99_ms = 33.677126
gate_ms            = 33.33
pass               = false
```

The formatter was corrected after the run. This was presentation-only and did not alter any measurement or gate decision.
