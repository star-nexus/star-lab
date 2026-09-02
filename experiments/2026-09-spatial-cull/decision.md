# Decision — Unit Spatial Cull Hot Loop

**Status:** accepted / closed  
**Decision date:** 2026-09-02  
**Validated STAR commit:** `615c3ac27f23f73b38d13b97280861fd1b0c9b72`  
**Later scale milestone:** `a24482d438157aa23b371b6e34d49b1c04fec7f7`

## 1. Decision

Keep the existing `UnitSpatialIndex` architecture and remove the remaining legacy per-candidate work. Cache deterministic world-space coordinates when authoritative position state changes, read Fog/view state once per frame, perform exact bounds rejection before Fog filtering, and express overscan in world-space units.

## 2. Decision drivers

- preserve authoritative ECS state and existing visibility semantics;
- reduce hot-loop cost without coupling Vision state into the spatial index;
- move deterministic repeat work from per-frame execution to state-change paths;
- avoid a more complex viewport-membership architecture unless profiling later proves it necessary.

## 3. Alternatives

| Option | Evidence | Decision |
|---|---|---|
| Clean existing spatial hot loop | ~3.53 ms -> ~1.28-1.33 ms | **Chosen** |
| Tune bucket size first | No evidence it was the dominant residual cost | Deferred |
| Incremental viewport membership | More state/invalidations for a cost already reduced to second tier | Rejected for now |
| Rust/GPU rewrite | No stable native boundary justified by this cull cost | Rejected for now |

## 4. Why this option

The improvement came from removing demonstrably repeated Python work while keeping architecture and semantics stable. This is exactly the preferred STAR optimization pattern: eliminate wrong complexity before adding new infrastructure.

## 5. Revisit when

Re-open this decision if:

- cull again becomes a top-tier frame cost;
- maps become large enough that candidate false-positive ratios dominate;
- camera motion/zoom becomes the dominant invalidation source;
- measured bucket query + index update cost supports a different spatial partition.

Until then, `unit_visible_cull` is considered CLOSED and further effort should follow the current profiler ranking.
