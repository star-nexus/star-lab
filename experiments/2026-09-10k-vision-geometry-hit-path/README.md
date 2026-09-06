# 10K Vision Geometry Cache-Hit Path

**Status:** CLOSED — CAUSALLY CONFIRMED / KEEP; raw evidence complete  
**STAR repository:** `star-nexus/star`  
**Production treatment:** `4218b5368fbe2815b8512384e2c18b0af443ebfa`

## Question

Why does Vision still spend material CPU in `_visibility_for()` when the geometry cache already hits about 99.7% of lookups?

## Attribution

The measurement-only C1 probe isolated the geometry hit path.

At 50% moving:

```text
visibility calls/frame       269.80
geometry hit rate            99.529%
terrain bonus lookup         0.363 ms/frame
cache dictionary get         0.131 ms/frame
LRU touch                    0.071 ms/frame
miss geometry                0.047 ms/frame
```

At 100% moving:

```text
visibility calls/frame       704.13
geometry hit rate            99.703%
terrain bonus lookup         0.849 ms/frame
cache dictionary get         0.310 ms/frame
LRU touch                    0.160 ms/frame
miss geometry                0.079 ms/frame
```

Terrain-bonus resolution was ~60.8% of the measured `_visibility_for()` internals at 100% moving even though almost every call hit the geometry cache.

## Optimization C1

Before:

```text
terrain bonus
  -> effective range
  -> key(center, effective_range, terrain_revision)
  -> cache lookup
  -> hit
```

After:

```text
key(center, base_range, terrain_revision)
  -> cache lookup
  -> hit: return cached geometry immediately
  -> miss: terrain bonus -> effective range -> geometry
```

Implementation:

```text
b39eb592833a3413a002aac294cf4e46481f640a
test: b9c63e9d626c9e21a1924121b91cedb116c1f2e1
```

The current retained production tree also includes Optimization B and resolves to:

```text
4218b5368fbe2815b8512384e2c18b0af443ebfa
```

## Semantic contract

A later source audit corrected the original wording around terrain invalidation.

Current production STAR has no live terrain mutation after `MapSystem.initialize()`. Terrain is therefore world-lifetime immutable for this runtime. Under that current contract, `(center, base_range, terrain_revision)` safely identifies the already-computed geometry.

If live LOS-affecting terrain mutation is introduced later, it must establish the explicit contract:

```text
terrain mutation
  -> VisionSystem.invalidate_all()
  -> terrain_revision++
  -> geometry cache clear
  -> dirty observers recompute
```

C1 must be revisited if that contract changes.

## Same-session closeout

Run:

```text
20260906-183456
control SHA    7b37f2d0823149042688059715342faf55c4fbb9
treatment SHA  4218b5368fbe2815b8512384e2c18b0af443ebfa
order          A50 -> B50 -> B100 -> A100
scenario SHA   e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
```

All four driver guards passed, all four ENV cleanup exit codes were zero, and the treatment's focused regressions reported `15 passed in 0.05s`.

### 50% moving

```text
controlled avg              27.248 -> 26.992 ms   (-0.94%)
controlled p95              28.503 -> 28.455 ms
controlled p99              30.803 -> 31.146 ms   diagnostic tail only

Vision avg                   2.487 -> 2.158 ms     (-13.24%)
Vision CPU / visibility      8.634 -> 7.555 us
saved / visibility call                        1.079 us

position commits/s delta                        -0.040%
Vision dirty/s delta                            +0.026%
Vision scan/s delta                             +0.026%
geometry-call/s delta                           +0.026%
hit-rate delta                                  -0.005 pp
evictions                                       0 -> 0
```

### 100% moving

```text
controlled avg              35.969 -> 35.185 ms   (-2.18%)
controlled p95              37.856 -> 36.887 ms
controlled p99              39.097 -> 41.805 ms   diagnostic tail only

Vision avg                   5.629 -> 4.760 ms     (-15.44%)
Vision CPU / visibility      7.499 -> 6.474 us
saved / visibility call                        1.025 us

position commits/s delta                        -0.001%
Vision dirty/s delta                            -0.037%
Vision scan/s delta                             -0.037%
geometry-call/s delta                           -0.037%
hit-rate delta                                  +0.008 pp
evictions                                       0 -> 0
```

The direct local saving is almost exactly the expected scale from attribution. The 100% Vision reduction (`0.869 ms/frame`) matches the attributed terrain-bonus cost (`~0.849 ms/frame`) particularly closely.

The 100% controlled-work P99 worsened in this one ABBA sample, but P99 was preregistered as diagnostic rather than a KEEP/REVERT gate. The treatment improves controlled average and P95, and Vision's own average and P99 both improve; workload rates and cache semantics remain unchanged. The isolated whole-frame tail therefore does not contradict the local causal result.

## Decision

```text
Optimization C1
Vision geometry cache-hit terrain bypass

CAUSALLY CONFIRMED
KEEP
CLOSED
```

This optimization does not establish a new 10K / 100%-moving 30Hz frontier point because the canonical P99 gate remains above 33.33 ms.

## Evidence

Canonical attribution evidence and the final closeout generation are mirrored under this case:

```text
results/raw/phase5-vision-hit-attribution/chibi-144k-scale-10000/20260906-124920/
results/raw/phase5-c1-closeout/chibi-144k-scale-10000/20260906-183456/
```

The final same-session closeout ZIP independently inspected before mirroring had SHA256:

```text
edb940801a95d78b3f059190bb8ae62d75c5a3f9ce3778547c39156e09513c46
```

A machine-readable independently recomputed summary is archived at:

```text
artifacts/CLOSEOUT_SUMMARY_20260906-183456.json
```

`artifacts/RAW_SHA256SUMS` covers all **54** case-owned raw files: 17 attribution files plus 37 closeout files. Evidence state: **raw complete, exact source provenance recorded, file-level SHA256 covered**.
