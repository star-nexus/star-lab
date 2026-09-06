# 10K Vision Geometry Cache-Hit Path

**Status:** ATTRIBUTED — C1 implemented; same-session ABBA closeout pre-registered and pending  
**STAR repository:** `star-nexus/star`  
**Branch at time:** `perf/10k-online`

## Purpose

This case continues Phase-5 10K Core Runtime optimization after Optimization A and Optimization B were both causally confirmed and retained.

The question is deliberately narrow:

> Why does the Vision geometry path still consume material CPU time when the geometry cache already hits about 99.7% of lookups?

The investigation does **not** revisit geometry-cache capacity. The earlier Vision-cache case already established that the 16,384-entry window cache has sufficient headroom and does not evict under this workload.

## Source state

At closeout pre-registration:

- Retained B+C1 production tree / treatment: `4218b5368fbe2815b8512384e2c18b0af443ebfa`
- Exact C1-off control derived from that tree: `7b37f2d0823149042688059715342faf55c4fbb9`
- C1 implementation origin: `b39eb592833a3413a002aac294cf4e46481f640a`
- C1 focused regression origin: `b9c63e9d626c9e21a1924121b91cedb116c1f2e1`
- C1 measurement-only probe source: `4938a0c81f2155022f5836b12d88294081ae79b2`
- Attribution runner / measured HEAD: `ebf2dc5cfb74c16b83272b6e9cf23f29017efe88`
- Closeout runner branch HEAD: `9ba2a766f2838570c7ecb77d4fd928ce9dbc5196`

The control is intentionally based on the retained B runtime and differs from the treatment in one runtime file only: `rotk_env/systems/window_vision_system.py`, where the C1 `_visibility_for()` override is removed. This prevents Optimization B from confounding the C1 result.

## Workload

```text
scenario              chibi-144k-scale-10000
resident units        10000
moving points         5000 / 10000
phase                  staggered
seed / phase seed      42 / 42
route steps            12
Fog                    ON
GC                     realtime_defer
MiniMap dynamic units  OFF
render                  uncapped
probe sampling          1 / 16 for attribution only
```

All recorded driver guards passed in the archived attribution run.

## Attribution result

### 50% moving

```text
visibility calls/frame       269.80
geometry hit rate            99.529%
terrain bonus lookup         0.363 ms/frame
cache dictionary get         0.131 ms/frame
LRU touch                    0.071 ms/frame
miss geometry                0.047 ms/frame
measured hit/miss internals  0.613 ms/frame
```

### 100% moving

```text
visibility calls/frame       704.13
geometry hit rate            99.703%
terrain bonus lookup         0.849 ms/frame
cache dictionary get         0.310 ms/frame
LRU touch                    0.160 ms/frame
miss geometry                0.079 ms/frame
measured hit/miss internals  1.397 ms/frame
```

At 100% moving, the terrain-bonus lookup alone is about **60.8%** of the measured `_visibility_for()` internals. Cache lookup is ~22.2%, LRU touch ~11.4%, and actual miss geometry only ~5.6%.

This is the opposite of a cache-capacity problem: almost all calls hit, and the largest measured cost occurs **before the hit can be used**.

## Candidate Optimization C1

Current control lookup shape:

```text
terrain bonus lookup
  -> effective range
  -> key(center, effective_range, terrain_revision)
  -> cache get
  -> hit
```

Treatment shape:

```text
key(center, base_range, terrain_revision)
  -> cache get
  -> hit: return immediately
  -> miss: resolve terrain bonus, compute effective range, generate geometry
```

### Terrain semantic invariant

A source audit before closeout corrected an earlier assumption in this case. The current production runtime does **not** contain live terrain mutation that already calls `VisionSystem.invalidate_all()`; instead, `MapSystem` is a one-shot loader that creates terrain during `initialize()` and performs no terrain mutation during `update()`.

Therefore the actual current invariant is:

```text
terrain type/effects are world-lifetime stable in the production runtime
```

Under that invariant, C1 is semantically safe. If future gameplay introduces live terrain or LOS-rule mutation, that feature must establish an explicit Vision invalidation contract (including `invalidate_all()` / terrain-revision change) before C1's cached result may remain valid across the mutation.

## Pre-registered production closeout

The production closeout is intentionally same-session and counterbalanced:

```text
A50 -> B50 -> B100 -> A100

A = retained Optimization B + C1 OFF
B = retained Optimization B + C1 ON
```

Exact states:

```text
A/control    7b37f2d0823149042688059715342faf55c4fbb9
B/treatment  4218b5368fbe2815b8512384e2c18b0af443ebfa
```

Acceptance criteria were frozen before measurement:

```text
all driver / semantic guards                         PASS
position commits/s A<->B                             within 2%
Vision dirty/s A<->B                                 within 2%
Vision scanned/s A<->B                               within 2%
geometry lookup calls/s A<->B                        within 2%
geometry hit-rate drop                               <= 0.5 percentage points
geometry evictions                                   zero in both variants
Vision inclusive CPU saving                         >= 0.5 us / visibility call
Vision avg/frame                                     B < A at both densities
controlled avg                                       no >2% regression
100% moving controlled avg                           B < A
P99                                                  diagnostic, not sole keep/revert gate
```

The direct normalized metric is `VisionSystem` inclusive CPU per geometry visibility call. Attribution predicts roughly 1.2–1.35 us/call of terrain-bonus work before implementation overhead, so the 0.5 us/call floor deliberately requires a material but conservative causal win.

The closeout runner reuses the process-tree cleanup discipline established during Optimization B, so no subsequent point may start while a captured ENV process remains alive.

## Raw evidence

Canonical raw attribution evidence is mirrored directly in:

```text
results/raw/phase5-vision-hit-attribution/chibi-144k-scale-10000/20260906-124920/
```

It contains both 50% and 100% moving points, including `point.json`, `profile.json`, `attribution-summary.json`, logs/configuration, manifest, Git status, and Git diff capture.

Every mirrored attribution file is covered by:

```text
artifacts/RAW_SHA256SUMS
```

Evidence state: **raw attribution evidence complete; production closeout pre-registered; closeout raw pending**.

## Interpretation boundary

The attribution runner adds timing probes, so its aggregate `controlled_work_frame_ms` values are diagnostic and must **not** be used as the C1 production speedup.

The production decision will come only from the uninstrumented same-session ABBA above. Until that run passes the pre-registered criteria, C1 remains a candidate rather than a causally closed optimization.
