# Decision — Phase 5 10K UnitRender E6-1 Bounded Geometry Ownership

**Status:** VALIDATED / KEEP — raw forensic mirror pending

## Candidate

Validated treatment source:

```text
e7ba18b31870577110b591104ef8fa7b4713e43c
```

Control:

```text
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
```

The candidate changes only the production `UnitSpatialIndex` derived-geometry ownership mechanism:

```text
lazy per-board-hex canonical (world_x, world_y, bucket)
```

while preserving fresh `UnitSpatialRecord` creation and all authoritative semantics.

## Preregistered decision rule

KEEP required all formal source/workload guards and regressions to pass, plus at both tested densities:

```text
position / Vision / Fog rates remain within ±2%
Cull saving >= 0.10 ms @50%
Cull saving >= 0.20 ms @100%
UnitRender avg improves
Animation avg regression <= 2%
controlled-work avg regression <= 2%
```

No threshold was changed after measurement.

## Formal decision

Run:

```text
20260907-213322
```

All checks passed.

Observed local causal savings:

```text
50% moving:
  Cull saving       0.231 ms
  UnitRender saving 0.170 ms
  Animation         +1.12%
  controlled avg    -0.84%

100% moving:
  Cull saving       0.423 ms
  UnitRender saving 0.367 ms
  Animation         +0.57%
  controlled avg    -1.39%
```

Workload-rate drift was negligible and well inside the preregistered ±2% equivalence gate.

Therefore choose:

```text
KEEP_BOUNDED_DERIVED_WORLD_GEOMETRY_REUSE
```

The candidate commit becomes the retained production state for subsequent Phase-5 profiling:

```text
retained production = e7ba18b31870577110b591104ef8fa7b4713e43c
```

## 30 Hz capacity decision

The production KEEP decision and the Phase-5 canonical capacity gate remain separate.

At 10K / 100% moving:

```text
controlled_work_frame_ms.p99 = 33.677126 ms
canonical threshold          = 33.33 ms
margin                       = +0.347126 ms
```

Therefore:

```text
30Hz canonical @100% = FAIL
Performance Frontier update = NO
```

This is close to the boundary, but the threshold is not moved and the result is not rounded into a PASS.

## Interpretation of the slight Animation regression

The bounded production design adds board-membership / geometry-cache lookup work during spatial record refresh. A small compensating Animation-side increase is visible (`+1.12%` at 50%, `+0.57%` at 100%).

This does not invalidate the KEEP because:

- the preregistered rejection threshold was `>2%`;
- Cull and UnitRender improve materially;
- controlled-work avg improves at both densities;
- workload equivalence is preserved.

The decision therefore reflects the full controlled-work tradeoff rather than only the local Cull metric.

## Retained / rejected designs

Retain:

```text
UnitSpatialIndex-owned
lazy
board-bounded
per-hex derived geometry reuse
fresh UnitSpatialRecord identity
```

Reject as production design:

```text
unbounded visited-coordinate geometry cache
```

Do not reopen without a new matching signature:

```text
stable record identity
slots-only representation
by_entity lookup
candidate count / branch mix
MapRender scheduling
exact raster duplicate draw
```

## Artifact decision

Compact Evidence Package is accepted as sufficient for normal review:

```text
20260907-213322-compact.zip
SHA256 0c9db01f29a04dcefc7ba896ab7ab533ec313c31a9e3d974d790b22893cb45a9
size 10616 bytes
```

Raw Forensic Package remains authoritative for low-level re-audit:

```text
20260907-213322-raw.zip
SHA256 4322905154b69ec25688fa0775b0efdd62a7a60bf1366aead9d5e8f73d661c07
size 128760 bytes
```

The case remains **validated but not CLOSED** until the Raw package has a stable canonical mirror/storage locator.

## Reporting correction

The formal terminal line displayed `FAIL (33.677 ms <= 33.33 ms)` because the formatter printed `<=` unconditionally. The machine-readable gate result was correctly `false`, so no experiment decision was affected. The formatter was corrected in STAR after the run.
