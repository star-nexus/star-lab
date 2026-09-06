# 10K Vision C2b — Faction Refcount Representation

**Status:** CLOSED — C2b-1 rejected / DO_NOT_KEEP  
**STAR repository:** `star-nexus/star`  
**Production runtime remains:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

Post-D1 formal frontier confirmation remained:

```text
FRONTIER_NOT_ESTABLISHED
100% P99 = 32.926 / 33.348 / 33.764 ms
```

D1 remains `CAUSALLY CONFIRMED / KEEP / CLOSED`; the periodic ~4ms audit pulse is gone. The remaining failure is distributed steady-state margin, so C2b was the first explicit necessary-complexity representation case.

## Attribution run

```text
run_id: 20260906-232805
runtime: 17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
points: 0% / 50% / 100% moving
all guards: PASS
```

The low-overhead probe avoided per-tile timers. Whole `_add_tiles/_remove_tiles` calls were sampled 1/128 and structural refcount snapshots were taken every 120 frames.

### 100%-moving attribution

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

## Candidate selected from attribution — C2b-1

Pure map-only dense storage was rejected because current Vision semantics include real off-bbox visibility keys. Fixed-width integer storage was also rejected because the observed max refcount is not a semantic upper bound.

The single candidate was therefore:

```text
Window VisionSystem

inside rectangular MapData bbox
    -> per-faction dense list[int]

off-bbox visibility coordinates
    -> per-faction sparse Dict[(col,row), int]
```

Shared/headless `VisionSystem` retained the original dict representation.

Candidate identity:

```text
branch:                    experiment/phase5-c2b1-dense-core-refcount
implementation commit:     54d7059a0fdddcc8b8e23edb9c7453f7cf2cc044
candidate + tests:         9d70c48f9b7b63ca19314b07f84ee77f79a7952c
closeout branch:           experiment/phase5-c2b1-closeout
closeout runner:           dac76b95940a74463f1a8132bd9f57894886dee3
```

Targeted tests protected in-bbox and off-bbox `2 -> 1 -> 0` overlap, bbox-internal non-map coordinates, explored history, faction separation and no-MapData fallback.

## Formal uninstrumented closeout

Run:

```text
20260907-000444
A control   = 17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
B treatment = 9d70c48f9b7b63ca19314b07f84ee77f79a7952c
order       = A50 -> B50 -> B100 -> A100
```

Targeted regression:

```text
100 passed in 0.47s
```

All four driver and ENV cleanup exit codes were zero and all runtime/workload guards passed.

### 50%-moving

```text
controlled avg:       24.355 -> 24.395 ms   (+0.16%)
controlled P99:       25.842 -> 25.544 ms
Vision avg:            1.494 -> 1.424 ms
Vision CPU/changed:     5.797 -> 5.516 us
saved/changed:          0.281 us
position rate:         -0.017%
dirty rate:            -0.025%
geometry rate:         -0.025%
faction add/remove:    +0.050% / +0.030%
```

### 100%-moving

```text
controlled avg:       30.719 -> 30.522 ms   (-0.64%)
controlled P99:       32.306 -> 31.957 ms
Vision avg:            3.318 -> 3.256 ms
Vision CPU/changed:     5.163 -> 5.098 us
saved/changed:          0.064 us
position rate:         -0.021%
dirty rate:            -0.017%
geometry rate:         -0.017%
faction add/remove:    -0.434% / +0.272%
```

The preregistered local causal floor was `>= 0.4 us` saved per changed unit at both densities. C2b-1 failed that gate at both 50% and 100%, so the formal decision is:

```text
DO_NOT_KEEP
```

Whole-frame P99 improved, but P99 was explicitly diagnostic and cannot override the failed local gate.

## Interpretation

C2b attribution correctly identified a real ~200k ops/s necessary overlap-bookkeeping path, but C2b-1 showed that the tuple-keyed dict representation itself is only a small fraction of that path's production cost.

Relative to the attribution sampled path estimate:

```text
50%:  Vision saving ~0.070 ms/frame vs ~0.651 ms/frame path  -> ~10.8%
100%: Vision saving ~0.062 ms/frame vs ~1.371 ms/frame path  -> ~4.5%
```

The dense fast path removes tuple-dict lookup for most keys, but replaces it with Python-level tuple unpacking, four bounds comparisons, a branch, coordinate arithmetic and list indexing on every tile. CPython's existing tuple/dict lookup executes much of its work in optimized C, so the expected representation win did not materialize at production scale.

The 100%-moving treatment also ran before the final A100 control in the ABBA order, so any gradual machine slowdown would tend to exaggerate rather than hide the treatment advantage. The already-small `0.064 us/changed` result is therefore not a plausible false negative worth retaining.

Do not merge C2b-1 into `perf/10k-online`. Production remains `17ced8d...`.

## Decision on the C2b direction

Do not pursue a C2b-2 micro-optimization of bounds checks or list indexing. The current evidence says that would optimize a small representation fraction while adding custom Python control flow.

A materially larger refcount win would likely require changing the tile identity representation upstream, which has a much larger semantic blast radius and is not justified from this case alone.

## Recommended next case — C2c

Return to the remaining Vision residual and attribute **visibility-delta multiplicity**, not just raw set-diff CPU.

The earlier C2 attribution measured set difference at about `1.03 ms/frame` at 100% moving. Geometry cache hits are ~99.7%, so many units may share canonical cached visibility frozensets. The next useful question is:

> How many changed units repeat the exact same `(old visibility object -> new visibility object)` transition within or across frames?

If transition reuse is high, cache the resulting `(removed_tiles, added_tiles)` delta instead of recomputing the same two `difference()` operations per unit. This preserves set-diff semantics while attacking multiplicity rather than trying to out-micro-optimize CPython's set implementation.

## Raw evidence

Attribution raw mirror and C2b-1 closeout raw mirror remain pending until copied from the local STAR result directories and checksum-verified in STAR Lab.

## Methodology

> **先消灭错误复杂度，再重构必要复杂度。**

C2b-1 is a useful negative result: a necessary path was correctly identified, but the selected representation layer did not contribute enough of the cost to justify production complexity.
