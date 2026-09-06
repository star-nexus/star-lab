# 10K Vision C2b — Faction Refcount Representation Attribution

**Status:** RUNNING — attribution prepared; no production candidate selected  
**STAR repository:** `star-nexus/star`  
**Frozen production runtime:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

Post-D1 formal frontier confirmation remained:

```text
FRONTIER_NOT_ESTABLISHED
100% P99 = 32.926 / 33.348 / 33.764 ms
```

D1 remains `CAUSALLY CONFIRMED / KEEP / CLOSED`; the periodic ~4ms audit pulse is gone. The remaining failure is distributed steady-state margin, not a new isolated pathology. The system needs roughly `0.5 ms` minimum and preferably about `1 ms` of engineering margin.

This marks the transition from removing clearly wrong complexity to optimizing **necessary complexity**.

## Question

Vision faction visibility must know when observer overlap changes:

```text
3 -> 2 -> 1 -> 0
```

so the overlap refcount bookkeeping itself cannot simply be deleted. Current production represents it as:

```python
Dict[Faction, Dict[(col, row), int]]
```

C2b asks:

> Is Python tuple-keyed sparse-dict representation unnecessarily expensive for this bounded 120x120 world, and what representation constraints must a safer candidate satisfy?

## Frozen runtime

```text
perf/10k-online
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
= A + B + C1 + C2a + D1
```

STAR experiment branch:

```text
experiment/phase5-c2b-refcount-representation
```

The branch is based on exact production and adds measurement tooling only:

```text
tools/phase5_vision_c2b_refcount_representation.py
tools/phase5_vision_c2b_refcount_representation_analyze.py
tools/run_phase5_vision_c2b_refcount_representation.sh
```

Tool commits:

```text
probe     03616c220e02bb33ecdf5b5f5dcbd85ff06d8bf5
analyzer  a92fb0829c9beac09d2486a19297dacfe1b5a606
runner    a1a308e1742e374a85873b6d84e0fe03585272ab
```

No production source file is modified on the experiment branch.

## Why this probe is different from the old C2 probe

The previous C2 attribution used per-tile microtiming to decompose dict/set work. That instrumentation was intentionally useful for ranking sub-operations, but it inflated the enclosing union-call time and cannot be treated as production CPU.

C2b therefore avoids per-tile timers. It uses:

```text
whole _add_tiles/_remove_tiles timing sample: 1 / 128 calls
structural refcount snapshot:                1 / 120 frames
```

All exact operation counts remain cheap counters. Aggregate instrumented frame latency is diagnostic only.

## Canonical workload

```text
scenario                  chibi-144k-scale-10000
scenario SHA256           e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
map                       120x120 / 14,400 real tiles
resident units            10,000
points                     0% / 50% / 100% moving
seed / phase seed         42 / 42
route steps               12
phase                     staggered
Fog                       ON
GC                        realtime_defer
MiniMap dynamic units     OFF
render                    uncapped
hub                       offline
```

## Measurements

Exact per-frame counters:

```text
add/remove calls
add/remove tiles
refcount ops
0<->1 union transitions
transition-call counts
active refcount entries
faction containers
```

Low-rate whole-call samples estimate existing `_add_tiles/_remove_tiles` cost per tile, split into calls with and without faction-union transitions.

Structural snapshots measure:

```text
active refcount entries
sum of observer multiplicities
refcount histogram: 1 / 2 / 3 / 4-7 / 8-15 / 16+
max refcount
entries inside/outside real map
entries inside/outside rectangular map bounding box
active density vs per-faction dense map/bbox slots
per-faction entry spread
Python dict-table shallow bytes
candidate dense u8/u16 footprint
```

The outside-map/bounding-box measurements are semantic constraints, not just memory statistics: a dense candidate must not silently drop currently represented visibility coordinates.

## Interpretation — frozen before measurement

This attribution does **not** retain a representation candidate automatically.

Evidence favoring a bounded dense/tile-indexed candidate includes:

- essentially all active refcount keys lie inside a stable bounded domain;
- maximum refcount fits a compact integer width;
- active entry density is high enough that sparse tuple hashing buys little;
- non-transition refcount calls dominate operation volume;
- low-rate whole-call sampling shows a material CPU opportunity relative to the `~0.5-1.0 ms` margin requirement.

If the domain is sparse or contains meaningful out-of-bounds semantic keys, do not force a dense array. Consider a map-tile-id indexed representation or another bounded/sparse hybrid instead.

Any selected candidate must preserve exact `0->1` and `1->0` faction-union transitions, explored history, fog journal deltas, faction changes, lifecycle cleanup and current observation semantics.

## Out of scope

Do not mix into C2b attribution:

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

C2b is the first explicit necessary-complexity representation case in this campaign.
