# Decision — 10K Vision Geometry Cache-Hit Path

## Decision state

**ATTRIBUTED / OPEN — proceed with isolated Optimization C1 production implementation and controlled A/B.**

Do not mark this optimization retained yet.

## Accepted candidate

Change only the geometry-cache lookup ordering/key semantics so cache hits can bypass terrain-bonus resolution:

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

## Why this candidate is accepted for testing

The attribution run shows, at 10K / 100% moving:

```text
geometry hit rate       99.703%
terrain bonus lookup    0.849 ms/frame
cache get               0.310 ms/frame
LRU touch               0.160 ms/frame
miss geometry           0.079 ms/frame
```

Terrain-bonus lookup is the largest measured `_visibility_for()` subcost and occurs before nearly every successful cache hit.

This is materially different from rejected Optimization B: C1 now has a direct micro-attribution identifying the specific removable work before implementation.

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

Optimization B establishes the precedent:

> no measurable benefit -> no additional production complexity.

## Next action

Implement the key/order change with focused regression tests, then run the standard 0% / 50% / 100% Phase-5 10K Core controlled A/B against the retained Optimization-A production baseline.
