# Analysis — 10K Vision Geometry Cache-Hit Path

## Observation

After the retained movement optimizations, Vision remains one of the dominant dynamic costs at 10K / 100% moving. The existing geometry cache is healthy: hit rate is about 99.7%, capacity is 16,384 entries, and the C1 attribution run recorded zero evictions.

The remaining question is therefore not cache size or miss geometry. It is the CPU work paid on cache hits.

## Hypothesis

The shared `VisionSystem._visibility_for()` resolves terrain vision bonus before constructing the cache key:

```text
center + base range
  -> terrain lookup
  -> effective range
  -> cache key
  -> cache lookup
```

If cache hits dominate, the terrain lookup may be repeated work whose result is already implicit in an existing cached entry for the same center/base-range/terrain state.

Competing explanations were:

1. terrain-bonus resolution dominates the hit path;
2. dictionary lookup dominates;
3. LRU `move_to_end()` dominates;
4. rare actual geometry misses still dominate despite high hit rate.

## Instrumentation

Measurement-only probe at STAR commit:

```text
ebf2dc5cfb74c16b83272b6e9cf23f29017efe88
```

The probe wraps `_visibility_for()` internals without replacing the production Vision dirty loop or Animation movement loop. Hot micro-operations are sampled 1/16; actual geometry misses are timed directly because they are rare.

Measured sections:

```text
terrain bonus lookup
cache dictionary get
LRU touch
miss geometry calculation
```

The attribution commits add tools only. They do not modify production runtime source.

## Evidence

### 50% moving

| Section | Avg estimated ms/frame | Share of measured internals |
|---|---:|---:|
| terrain bonus lookup | **0.3631** | **59.2%** |
| cache get | 0.1314 | 21.4% |
| LRU touch | 0.0713 | 11.6% |
| miss geometry | 0.0475 | 7.7% |
| **sum** | **0.6132** | 100% |

Supporting workload values:

```text
visibility calls/frame  269.80
geometry hit rate       99.529%
geometry evictions      0
```

The attributed terrain lookup is approximately `1.346 us` per visibility call.

### 100% moving

| Section | Avg estimated ms/frame | Share of measured internals |
|---|---:|---:|
| terrain bonus lookup | **0.8490** | **60.8%** |
| cache get | 0.3098 | 22.2% |
| LRU touch | 0.1599 | 11.4% |
| miss geometry | 0.0785 | 5.6% |
| **sum** | **1.3972** | 100% |

Supporting workload values:

```text
visibility calls/frame  704.13
geometry hit rate       99.703%
geometry misses/frame   2.10
geometry evictions      0
```

The attributed terrain lookup is approximately `1.206 us` per visibility call.

The 100% point is the decisive signal: actual geometry computation is only ~0.079 ms/frame while terrain-bonus resolution consumes ~0.849 ms/frame.

## Attribution conclusion

The primary geometry cache-hit overhead is **terrain-bonus resolution performed before cache lookup**.

This is not evidence that the entire historical Vision geometry cost can disappear. It isolates one removable component of the steady hit path.

The measured candidate opportunity is on the order of ~0.85 ms/frame at the 100% attribution workload before accounting for implementation overhead and realtime feedback effects.

## Semantic audit before closeout

The original candidate reasoning assumed that production terrain-changing operations already call `VisionSystem.invalidate_all()`. A source audit before formal A/B found that this wording was inaccurate: current production does not expose a live terrain-mutation path at all.

`MapSystem` is a one-shot loader:

```text
initialize()
  -> load map
  -> create Terrain components

update()
  -> no-op
```

Repository inspection found no production path that mutates `Terrain.terrain_type` or replaces map Terrain components after initialization.

Therefore the actual current semantic invariant is stronger and simpler:

```text
terrain type/effects are stable for the lifetime of the running world
```

Under current STAR semantics, a fixed `(center, base_range)` maps to a fixed terrain bonus for that world, so C1 may safely reuse the cached effective geometry.

`invalidate_all()` still provides the correct mechanism for an explicit future terrain revision, but it is not currently called by a live mutation path because no such path exists. If future gameplay introduces terrain destruction, construction, weather/LOS rule changes, or any other live mutation that changes effective visibility geometry, that feature must establish the invalidation contract before cached results can span the mutation.

This semantic correction is part of the C1 record; do not silently rely on a nonexistent mutation caller.

## Candidate

Control key/path:

```text
terrain bonus
  -> effective_range
  -> (center, effective_range, terrain_revision)
  -> cache lookup
```

Treatment key/path:

```text
(center, base_range, terrain_revision)
  -> cache lookup
  -> hit: return immediately
  -> miss: terrain bonus -> effective_range -> geometry
```

The treatment exists in Window Vision only. Shared/headless Vision remains unchanged.

Focused tests already prove the central contracts:

1. a repeated Window cache hit does not re-query terrain bonus;
2. `invalidate_all()` clears the entry, bumps revision, and forces bonus re-query/recompute;
3. the accepted 16,384-entry Window cache capacity remains independently protected;
4. existing terrain tests continue to protect hill/mountain bonus behavior.

## Production closeout design

Do not compare C1 against the old Optimization-A-only baseline. Optimization B is now retained and must be fixed in both variants.

Exact states:

```text
Control A
7b37f2d0823149042688059715342faf55c4fbb9
= retained B runtime + C1 override removed

Treatment B
4218b5368fbe2815b8512384e2c18b0af443ebfa
= retained B runtime + C1 enabled
```

A Git comparison confirms the control differs from treatment in only:

```text
rotk_env/systems/window_vision_system.py
```

where the C1 override is removed.

The runner uses same-session counterbalancing:

```text
A50 -> B50 -> B100 -> A100
```

and the process-tree cleanup discipline established by the Optimization-B closeout.

## Pre-registered causal metrics and retention gate

The directly modified operation occurs once per geometry visibility lookup. To reduce sensitivity to realtime feedback and FPS redistribution, the primary normalized metric is:

```text
VisionSystem inclusive CPU / geometry visibility call
```

This metric deliberately includes the rest of Vision work; therefore the treatment must still produce a material reduction despite that dilution.

Acceptance criteria frozen before the production run:

```text
all driver / semantic guards                         PASS
position commits/s                                   within +/-2%
Vision dirty/s                                       within +/-2%
Vision scanned/s                                     within +/-2%
geometry calls/s                                     within +/-2%
geometry hit-rate drop                               <= 0.5 pp
geometry evictions                                   0 in A and B
Vision CPU saving                                    >= 0.5 us / visibility call
Vision avg/frame                                     B < A at 50% and 100%
controlled avg                                       no >2% regression
100% moving controlled avg                           B < A
P99                                                  diagnostic only
```

The `0.5 us/call` floor is conservative relative to attribution (~1.21–1.35 us/call of terrain lookup) while still requiring a clear causal local win.

## Interpretation boundary

The instrumented attribution run's aggregate frame timing is diagnostic only. Probe overhead changes the frame body, so C1 must not claim a production speedup from that generation.

The current `perf/10k-online` tree contains the C1 candidate, but C1 is not considered causally retained until the uninstrumented same-session ABBA satisfies the frozen closeout criteria. The production closeout must decide the case without changing those criteria after seeing the data.
