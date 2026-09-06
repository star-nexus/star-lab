# 10K Vision Geometry Cache-Hit Path

**Status:** ATTRIBUTED — Optimization C1 candidate identified; production A/B pending  
**STAR repository:** `star-nexus/star`  
**Branch at time:** `perf/10k-online`

## Purpose

This case continues Phase-5 10K Core Runtime optimization after Optimization A was retained and Optimization B was rejected/reverted.

The question is deliberately narrow:

> Why does the Vision geometry path still consume material CPU time when the geometry cache already hits about 99.7% of lookups?

The investigation does **not** revisit geometry-cache capacity. The earlier Vision-cache case already established that the 16,384-entry window cache has sufficient headroom and does not evict under this workload.

## Source state

- Current-best production tree after B rollback: `7f72e352f95e20125c29502abd934f0f81a3e0f2`
- C1 measurement-only probe source: `4938a0c81f2155022f5836b12d88294081ae79b2`
- C1 runner / measured HEAD: `ebf2dc5cfb74c16b83272b6e9cf23f29017efe88`

The C1 commits add measurement tools only. Production runtime source remains the retained Optimization-A tree.

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
probe sampling          1 / 16 for hot hit-path micro-operations
```

All recorded driver guards passed in the archived run.

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

Current lookup shape:

```text
terrain bonus lookup
  -> effective range
  -> key(center, effective_range, terrain_revision)
  -> cache get
  -> hit
```

Candidate shape:

```text
key(center, base_range, terrain_revision)
  -> cache get
  -> hit: return immediately
  -> miss: resolve terrain bonus, compute effective range, generate geometry
```

This is semantically valid only because terrain changes already invalidate geometry by incrementing the terrain revision and clearing the cache. The production change still requires focused regression tests and a controlled production A/B before retention.

## Raw evidence

Canonical raw attribution evidence is mirrored directly in:

```text
results/raw/phase5-vision-hit-attribution/chibi-144k-scale-10000/20260906-124920/
```

It contains both 50% and 100% moving points, including `point.json`, `profile.json`, `attribution-summary.json`, logs/configuration, manifest, Git status, and Git diff capture.

Every mirrored file is covered by:

```text
artifacts/RAW_SHA256SUMS
```

Evidence state: **raw attribution evidence complete; exact source provenance recorded; file-level SHA256 covered**.

## Interpretation boundary

The attribution runner adds timing probes, so its aggregate `controlled_work_frame_ms` values are diagnostic and must **not** replace the uninstrumented Optimization-A production baseline. The causal output of this generation is the relative composition of the geometry hit path.

Production performance claims remain pending until Optimization C1 is implemented alone and measured with the normal Phase-5 10K Core runner.
