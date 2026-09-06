# Decision — 10K Vision Geometry Cache-Hit Path

## Decision state

**CANDIDATE IMPLEMENTED — local regression and uninstrumented production A/B pending.**

Do not mark this optimization retained yet.

## Accepted candidate

The isolated Optimization C1 treatment has now been implemented in the window Vision path:

```text
before:
terrain bonus
  -> effective range
  -> key(center, effective_range, terrain_revision)
  -> cache get

after candidate:
key(center, base_range, terrain_revision)
  -> cache get
  -> hit: return
  -> miss: terrain bonus -> effective range -> geometry
```

Source identity:

```text
attribution runtime HEAD   ebf2dc5cfb74c16b83272b6e9cf23f29017efe88
candidate implementation  b39eb592833a3413a002aac294cf4e46481f640a
candidate + regressions   b9c63e9d626c9e21a1924121b91cedb116c1f2e1
```

The production change is intentionally scoped to `window_vision_system.py`, the exact runtime path used by the Phase-5 10K window workload. Shared union/refcount, audit scheduling, cache capacity, LRU policy, Animation, movement, spatial-index, rendering and GC code are unchanged.

## Why this candidate was accepted for implementation

The attribution run shows, at 10K / 100% moving:

```text
geometry hit rate       99.703%
terrain bonus lookup    0.849 ms/frame
cache get               0.310 ms/frame
LRU touch               0.160 ms/frame
miss geometry           0.079 ms/frame
```

Terrain-bonus lookup is the largest measured `_visibility_for()` subcost and occurs before nearly every successful cache hit.

Optimization B provides the relevant process precedent: its first cross-generation comparison produced a false negative, but a later same-session pre-registered ABBA closeout causally confirmed a `0.5-0.8 us/commit` benefit. C1 therefore also requires a direct local causal metric plus controlled production validation before retention.

## Semantic contract

For one `_terrain_revision`, terrain bonus is a deterministic function of `center`. Therefore `(center, base_range, terrain_revision)` uniquely determines the effective visibility geometry.

The treatment relies on the existing terrain invalidation contract:

```text
terrain changes
  -> VisionSystem.invalidate_all()
  -> _terrain_revision += 1
  -> geometry cache cleared
  -> affected observers dirty
  -> next cache miss re-reads terrain bonus
```

Focused regression tests now require:

1. a second same-key cache hit performs zero additional terrain-bonus lookups;
2. `invalidate_all()` changes revision, clears the cache, and forces the next lookup to re-read terrain bonus and recompute geometry.

## Constraints

Optimization C1 must not include:

- faction-union/refcount changes;
- set-diff changes;
- explored-tile changes;
- audit scheduling changes;
- cache-capacity changes;
- LRU-policy changes;
- Animation, movement, spatial-index, render, or GC changes.

One optimization only.

## Production acceptance criteria

Retain C1 only if the uninstrumented production A/B shows the expected causal signature:

```text
0% moving             approximately unchanged
50% / 100% moving     Vision local cost decreases
geometry hit rate     semantically comparable
movement commits/s    preserved
Vision dirty/s        preserved
all semantic guards   PASS
```

The normal Phase-5 10K Core runner is the canonical production measurement. Instrumented C1 aggregate frame metrics are not the acceptance baseline.

## Rejection rule

If the direct Vision-path improvement is below noise or aggregate improvement has no supporting local causal reduction, revert the implementation rather than carrying extra cache semantics.

Optimization B refines the rule:

> no measured causal benefit -> no added production complexity; if machine drift can plausibly mask a small per-transition effect, close the question with same-session counterbalanced A/B before making the decision durable.

## Next action

Run focused Vision regressions at `b9c63e9d...`, then execute the standard 0% / 50% / 100% uninstrumented Phase-5 10K Core controlled run. Compare treatment against the accepted A+B baseline, not against a state that has spatial-index specialization reverted.
