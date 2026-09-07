# Decision — Phase 5 10K UnitRender E6-1 Bounded Geometry Ownership

**Status:** PENDING FORMAL CONTROLLED A/B

## Candidate

Frozen treatment source:

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

Choose:

```text
KEEP_BOUNDED_DERIVED_WORLD_GEOMETRY_REUSE
```

only if all formal source/workload guards and regressions pass, and at both tested densities:

```text
position / Vision / Fog rates remain within ±2%
Cull saving >= 0.10 ms @50%
Cull saving >= 0.20 ms @100%
UnitRender avg improves
Animation avg regression <= 2%
controlled-work avg regression <= 2%
```

Otherwise choose:

```text
DO_NOT_KEEP_BOUNDED_DERIVED_WORLD_GEOMETRY_REUSE
```

Do not relax these thresholds after observing formal results.

## 30 Hz capacity rule

The production KEEP decision and the Phase-5 canonical capacity gate are intentionally separate.

At 10K / 100% moving:

```text
controlled_work_frame_ms.p99 <= 33.33 ms
```

is required before treating the run as a 30 Hz canonical PASS or considering a Performance Frontier update.

A KEEP result with `p99 > 33.33 ms` means:

```text
candidate is retained
Phase 5 100%-moving frontier remains unresolved / FAIL
continue causal profiling from the new retained production state
```

## Production retention

Until formal A/B closes this record:

```text
production retained baseline = 17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
candidate                     = experimental only
```

No merge/tag/frontier update is authorized by this preregistration alone.

## Artifact rule

Formal result must produce and preserve both:

```text
Compact Evidence Package
Raw Forensic Package
```

Compact is the default review artifact. Raw remains the final audit substrate and cannot be replaced by Compact.
