# Analysis — 10K Vision Geometry Cache-Hit Path

## Observation

Vision remained a dominant dynamic cost after Optimizations A and B. The geometry cache itself was healthy: approximately 99.5-99.7% hit rate and zero evictions under the measured 10K workload.

The residual question was therefore not cache capacity or miss geometry, but work still paid on hits.

## Attribution result

The C1 probe measured four `_visibility_for()` subcosts.

| Density | Terrain bonus | Cache get | LRU touch | Miss geometry | Terrain share |
|---|---:|---:|---:|---:|---:|
| 50% | 0.363 ms | 0.131 ms | 0.071 ms | 0.047 ms | 59.2% |
| 100% | 0.849 ms | 0.310 ms | 0.160 ms | 0.079 ms | 60.8% |

At 100% moving, actual miss geometry was only ~0.079 ms/frame while the terrain-bonus lookup consumed ~0.849 ms/frame before nearly every successful cache hit.

Root cause:

> the cache was effective, but the implementation performed the expensive prerequisite needed to construct the old cache key before asking the cache whether the result already existed.

## Treatment

The window Vision implementation changes the geometry-cache key from effective range to base range for one terrain revision:

```text
before:
(center, effective_range, terrain_revision)

treatment:
(center, base_range, terrain_revision)
```

On a hit, terrain resolution is skipped. On a miss, terrain bonus and effective geometry are computed exactly as before.

No faction union/refcount, set-diff, explored-tile, audit, cache-capacity, LRU, movement, spatial-index, rendering, or GC behavior is changed.

## Semantic audit

The first case draft stated that terrain-changing production operations already call `invalidate_all()`. Source inspection showed a more precise current invariant:

- `MapSystem.initialize()` creates Terrain components;
- production `MapSystem.update()` is idle;
- no live production path was found mutating `Terrain.terrain_type` after initialization.

Thus current runtime terrain is world-lifetime immutable. C1 is safe under that contract.

Any future live LOS-affecting terrain mutation must explicitly call Vision invalidation before C1 remains semantically valid.

## Preregistered closeout

The production A/B kept Optimization B fixed on both sides.

```text
control     7b37f2d0823149042688059715342faf55c4fbb9  (B + C1 OFF)
treatment   4218b5368fbe2815b8512384e2c18b0af443ebfa  (B + C1 ON)
order       A50 -> B50 -> B100 -> A100
```

Acceptance was preregistered before measurement:

- all driver/semantic guards PASS;
- position commits/s, dirty/s, scan/s, geometry calls/s within ±2%;
- geometry hit-rate drop <= 0.5 percentage points;
- zero geometry evictions;
- Vision saving >= 0.5 us/visibility call;
- Vision avg improves at both densities;
- controlled avg no material regression;
- 100% controlled avg improves;
- P99 diagnostic only.

## Closeout result

### 50% moving

| Metric | Control | Treatment | Delta |
|---|---:|---:|---:|
| Controlled avg | 27.248 ms | 26.992 ms | -0.256 ms / -0.94% |
| Controlled P95 | 28.503 ms | 28.455 ms | -0.048 ms |
| Controlled P99 | 30.803 ms | 31.146 ms | +0.342 ms |
| Vision avg | 2.487 ms | 2.158 ms | **-0.329 ms / -13.24%** |
| Vision CPU/call | 8.634 us | 7.555 us | **-1.079 us** |
| Position rate | 10001.3/s | 9997.3/s | -0.040% |
| Dirty rate | 9999.7/s | 10002.3/s | +0.026% |
| Hit rate | 99.531% | 99.527% | -0.005 pp |

### 100% moving

| Metric | Control | Treatment | Delta |
|---|---:|---:|---:|
| Controlled avg | 35.969 ms | 35.185 ms | **-0.783 ms / -2.18%** |
| Controlled P95 | 37.856 ms | 36.887 ms | **-0.969 ms** |
| Controlled P99 | 39.097 ms | 41.805 ms | +2.707 ms |
| Vision avg | 5.629 ms | 4.760 ms | **-0.869 ms / -15.44%** |
| Vision CPU/call | 7.499 us | 6.474 us | **-1.025 us** |
| Position rate | 19977.9/s | 19977.7/s | -0.001% |
| Dirty rate | 19993.8/s | 19986.3/s | -0.037% |
| Hit rate | 99.702% | 99.710% | +0.008 pp |

All preregistered checks pass.

## Attribution-to-production closure

The production result matches the attribution prediction unusually well.

```text
50% attributed terrain cost   ~0.363 ms/frame
50% production Vision saving   0.329 ms/frame

100% attributed terrain cost  ~0.849 ms/frame
100% production Vision saving  0.869 ms/frame
```

Per-call savings are also stable across workloads:

```text
50%   1.079 us / visibility call
100%  1.025 us / visibility call
```

That is the decisive causal signature. Workload transition rates, geometry-call rates, hit rates, and eviction behavior remain effectively unchanged.

## P99 interpretation

Treatment P99 is slightly worse at 50% and materially worse at 100% in this one run. This does not invalidate C1 because P99 was explicitly preregistered as diagnostic rather than the KEEP/REVERT gate, and the local path behaves in the opposite direction:

- Vision avg improves at both densities;
- Vision P99 also improves (`6.716 -> 6.553 ms` at 50%, `8.915 -> 8.376 ms` at 100%);
- controlled P95 improves at 100%;
- known low-rate audit/tail alignment remains present.

Therefore the whole-frame P99 excursion is not causally attributed to C1.

## Root cause classification

C1 is a third class of wrong work after A and B:

```text
A: multiplicity amplification
   stable dependency rediscovered per mover

B: abstraction overreach
   generic lifecycle reconciliation used for position-only movement

C1: cache-ordering inversion
    expensive key prerequisite paid before a cache that almost always hits
```

## Final conclusion

**CAUSALLY CONFIRMED / KEEP / CLOSED.**

C1 removes about 1.0 us of Vision CPU per geometry visibility call and ~0.87 ms/frame at the 10K / 100%-moving workload without changing authoritative transition or visibility workload rates.
