# Analysis — 10K Vision Geometry Cache-Hit Path

## Observation

After Optimization A, Vision remains one of the dominant dynamic costs at 10K / 100% moving. The existing geometry cache is healthy: hit rate is about 99.7%, capacity is 16,384 entries, and the C1 attribution run recorded zero evictions.

The remaining question is therefore not cache size or miss geometry. It is the CPU work paid on cache hits.

## Hypothesis

`VisionSystem._visibility_for()` currently resolves terrain vision bonus before constructing the cache key:

```text
center + base range
  -> terrain lookup
  -> effective range
  -> cache key
  -> cache lookup
```

If cache hits dominate, the terrain lookup may be repeated work whose result is already implicit in an existing cached entry for the same center/base-range/terrain-revision state.

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

The 100% point is the decisive signal: actual geometry computation is only ~0.079 ms/frame while terrain-bonus resolution consumes ~0.849 ms/frame.

## Attribution conclusion

The primary geometry cache-hit overhead is **terrain-bonus resolution performed before cache lookup**.

This is not evidence that the entire historical Vision geometry cost can disappear. It isolates one removable component of the steady hit path.

The measured candidate opportunity is on the order of ~0.85 ms/frame at the 100% attribution workload before accounting for implementation overhead and realtime feedback effects.

## Semantic reasoning for the candidate

Current key:

```text
(center, effective_range, terrain_revision)
```

Candidate key:

```text
(center, base_range, terrain_revision)
```

For a fixed `center`, `base_range`, and `terrain_revision`, terrain bonus is deterministic. Terrain-changing operations already call `invalidate_all()`, which increments `_terrain_revision` and clears the geometry cache.

Therefore a cache entry keyed by `(center, base_range, terrain_revision)` can safely return the already-computed effective geometry without repeating terrain-bonus lookup on hits.

On a miss, the system still resolves terrain bonus and computes the exact same effective visibility geometry as before.

## Required correctness tests before production A/B

The implementation should prove:

1. repeated hit at the same `(center, base_range, terrain_revision)` does not call `_get_vision_terrain_bonus()` again;
2. first miss still applies terrain bonus exactly;
3. `invalidate_all()` forces a new terrain-bonus lookup and recomputation;
4. different base ranges at the same center do not alias;
5. LRU capacity/eviction behavior remains correct;
6. resulting visible tiles, faction refcounts, explored tiles, and fog journal semantics remain unchanged.

## Interpretation boundary

The instrumented run's aggregate frame timing is diagnostic only. Probe overhead changes the frame body, so C1 must not claim a production speedup from the attribution run itself.

The accepted current-best production baseline remains Optimization A. C1 becomes a retained optimization only after an isolated production implementation and normal uninstrumented Phase-5 controlled A/B.
