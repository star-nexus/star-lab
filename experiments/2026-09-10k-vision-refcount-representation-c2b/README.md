# 10K Vision C2b — Faction Refcount Representation

**Status:** RUNNING — attribution complete; C2b-1 selected; closeout preregistered  
**STAR repository:** `star-nexus/star`  
**Frozen production runtime:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

Post-D1 formal frontier confirmation remained:

```text
FRONTIER_NOT_ESTABLISHED
100% P99 = 32.926 / 33.348 / 33.764 ms
```

D1 remains `CAUSALLY CONFIRMED / KEEP / CLOSED`; the periodic ~4ms audit pulse is gone. The remaining failure is distributed steady-state margin, so C2b is the first explicit necessary-complexity representation case.

## Attribution run

```text
run_id: 20260906-232805
runtime: 17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
points: 0% / 50% / 100% moving
all guards: PASS
```

The low-overhead probe avoided per-tile timers. Whole `_add_tiles/_remove_tiles` calls were sampled 1/128 and structural refcount snapshots were taken every 120 frames.

### 100%-moving result

```text
refcount ops/frame:                 6588.9
refcount ops/s:                   199916
sampled add/remove path:             1.371 ms/frame
union transition rate:               0.786%
no-transition add/remove:             0.200 / 0.206 us/tile
active entries:                     13820
refcount mass:                      190000
mean refcount:                       13.75
max refcount:                        33
count == 1:                           6.9%
count <= 3:                          14.3%
count >= 16:                       6711 entries
active / faction×bbox slots:         32.0%
outside real map:                   539
outside rectangular bbox:           539
dict-table shallow bytes:            576.2 KiB
```

50% moving independently showed ~100k refcount ops/s and ~0.651 ms/frame sampled path cost, consistent with an approximately linear high-frequency bookkeeping path.

## Interpretation

The overlap refcount itself is necessary: Vision must distinguish `3 -> 2 -> 1 -> 0`. However, ~99.2% of full-motion refcount operations do not create a faction-union transition and therefore primarily maintain overlap multiplicity.

The current representation is:

```python
Dict[Faction, Dict[(col, row), int]]
```

The domain is not strictly map-bounded. Current Vision geometry deliberately emits off-map visibility coordinates, and the attribution observed ~4% of active refcount keys outside the 120x120 map bounding box. Therefore a pure map-only dense array would change semantics and is rejected.

The observed max refcount of 33 is not a semantic upper bound, so fixed-width `uint8/uint16` storage is also not selected.

## Selected candidate — C2b-1

One candidate only:

```text
Window VisionSystem

inside rectangular MapData bbox
    -> per-faction dense list[int]

off-bbox visibility coordinates
    -> per-faction sparse Dict[(col,row), int]
```

Shared/headless `VisionSystem` keeps the original dict representation unchanged. The window specialization overrides only the refcount aggregation path while preserving shared visibility transitions, explored history and fog-journal semantics.

STAR candidate branch:

```text
experiment/phase5-c2b1-dense-core-refcount
implementation commit: 54d7059a0fdddcc8b8e23edb9c7453f7cf2cc044
candidate + tests:     9d70c48f9b7b63ca19314b07f84ee77f79a7952c
```

Candidate diff from production is limited to:

```text
rotk_env/systems/window_vision_system.py
rotk_env/tests/test_window_vision_dense_refcount.py
```

Targeted tests explicitly protect:

```text
in-bbox 2 -> 1 -> 0 overlap
bbox-internal coordinates absent from real MapData.tiles
off-bbox overflow 2 -> 1 -> 0 overlap
explored-history retention
Wei/Shu/Wu separation
no-MapData fallback to shared dict semantics
```

## Preregistered uninstrumented closeout

Branch:

```text
experiment/phase5-c2b1-closeout
```

Formal A/B:

```text
A control   = 17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
B treatment = 9d70c48f9b7b63ca19314b07f84ee77f79a7952c
order       = A50 -> B50 -> B100 -> A100
```

Canonical workload remains the same 10K scenario, seed 42, route 12, Fog ON, MiniMap dynamic units OFF, realtime_defer, uncapped render and offline hub.

### KEEP gates

Both densities must satisfy:

```text
position commits/s       within ±2%
Vision dirty/s           within ±2%
Vision scanned/s         within ±2%
geometry calls/s         within ±2%
faction add/remove       within ±5%
fog delta                within ±5%
geometry hit-rate drop   <= 0.5 pp
geometry evictions       0
Vision avg/frame         improves
Vision CPU/changed unit  saves >= 0.4 us
controlled avg regression <= 2%
```

Additionally, 100%-moving controlled avg must improve.

Whole-frame P99 is diagnostic for C2b-1 retention; a later dedicated frontier confirmation is required before moving the 10K / 100%-moving / 30Hz frontier.

## Out of scope

Do not mix into C2b-1:

```text
set-diff algorithm (C2c)
geometry cache
movement
D1 audit semantics
rendering
GC
native/parallel rewrite
```

## Methodology

> **先消灭错误复杂度，再重构必要复杂度。**

C2b-1 optimizes the representation of necessary overlap information without weakening that information.
