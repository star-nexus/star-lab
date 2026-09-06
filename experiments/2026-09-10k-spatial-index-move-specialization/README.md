# 10K Spatial-Index Movement Specialization

**Status:** REJECTED — no measurable causal performance win; implementation reverted  
**STAR repository:** `star-nexus/star`  
**Branch at time:** `perf/10k-online`

## Purpose

This case records Optimization B from Phase-5 10K Core Runtime scaling. The hypothesis was that the generic `UnitSpatialIndex.upsert_from_world()` path performed unnecessary lifecycle bookkeeping during ordinary position-only movement and that a specialized movement path would materially reduce `AnimationSystem` cost.

The implementation was logically valid, regression-covered, and workload-preserving, but controlled production A/B did **not** show a measurable causal speedup. The added production complexity was therefore removed.

This negative result is archived specifically to prevent future engineers from repeating the same optimization based on code appearance alone.

## Source states

- Accepted Optimization-A baseline: `b9e0bb92b546b3283cb5c1d30a9a510d0c006ec2`
- Specialized spatial-index implementation: `5af001817e65869fb3fa782edb9e8284d13e53e7`
- Final measured B state: `73a2f7f33067dfd39e7aaf1c07a4c08eafc021ba`
- Explicit production rollback: `7f72e352f95e20125c29502abd934f0f81a3e0f2`

The rollback commit points to the exact Optimization-A Git tree. Comparing `b9e0bb92...` with `7f72e352...` reports no changed files.

## Candidate optimization

The specialized path attempted to remove work that appeared redundant for position-only movement:

```text
- re-read Unit
- re-read HexPosition
- re-read UnitCount
- living_counts decrement / increment
- same-bucket by_bucket remove / add
```

while retaining required cell occupancy, entity record, bucket, and revision maintenance and preserving a generic self-healing fallback for missing index entries.

## Controlled result

Optimization A was the control; Optimization B was the treatment.

| Density | A controlled avg | B controlled avg | A P99 | B P99 | Direct Animation avg |
|---|---:|---:|---:|---:|---|
| 0% | 16.670 | 17.118 | 20.546 | 20.835 | 0.013 -> 0.015 ms |
| 50% | 25.964 | 26.495 | 29.447 | 30.878 | 3.633 -> 3.664 ms |
| 100% | 34.180 | 34.967 | 38.537 | 37.629 | **7.770 -> 7.749 ms** |

The 100% aggregate P99 happened to fall by ~0.91 ms, but average and P95 became worse and the directly modified `AnimationSystem` path changed by only ~0.021 ms. That is not a causal optimization signature.

Authoritative transition throughput remained essentially unchanged.

## Interpretation

Phase-5.1 had attributed roughly `3.19 ms/frame` at 100% moving to the **entire** generic spatial-index update. Optimization B tested whether the removable generic bookkeeping represented a large fraction of that cost.

It did not.

Most of the spatial-index cost is mandatory movement maintenance: cell/set membership, record reconstruction, pixel/bucket derivation, and revision invalidation. The visually obvious redundant lifecycle bookkeeping was a thin layer below the production noise floor.

## Evidence identity

```text
Optimization-A control:
20260906-041532.zip  45319fef0499383a8888e638d12cc8693ce591c32475b40626012f00abd0c825

Optimization-B treatment:
20260906-120822.zip  ded5cccecec5b157eaff73c2efcbd65d1db7af549f7ee07a69b2cd1edd264c7b
```

Evidence state: **checksum-bound uploaded raw evidence; binary ZIP not mirrored**.
