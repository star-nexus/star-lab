# Phase 5 10K UnitRender E2 — Cull Per-Candidate Growth Attribution

**Status:** RUNNING — preregistered attribution; no production candidate selected  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

UnitRender E showed that the spatial cull candidate volume is essentially unchanged from 0% to 100% moving, while cull CPU rises materially:

```text
candidates/frame     8920.0 -> 8930.4   (+0.12%)
cull CPU             1.715  -> 2.513 ms (+46.5%)
us/candidate         0.192  -> 0.281     (+46.3%)
```

Candidate-volume closure was only ~0.2%, so the cull signal remains `NOT_CLOSED`.

## Question

Does the movement-dependent cull growth come from:

1. **branch composition** — more candidates taking expensive Fog-visible / accept paths even though total candidates are stable; or
2. **same-stage cost inflation** — spatial record / bounds / Fog membership operations themselves becoming more expensive under continuous index churn?

## Measurement rules

This attribution deliberately avoids per-candidate timers. Exact counters run every cull; bulk replay timing runs only on sparse sampled frames so timer overhead is amortized across hundreds or thousands of operations.

Exact per-frame counters:

```text
nonempty buckets
candidate entries
record misses
bounds rejects / bounds passes
friendly bounds-pass candidates
enemy bounds-pass candidates
Fog membership checks
Fog visible hits / Fog reject misses
visible friendly / visible enemy
current vision tile count
index revision delta
```

Sparse bulk samples decompose:

```text
by_entity.get batch
bounds-field batch
Fog positive-membership batch
Fog negative-membership batch
visible append batch
full warm replay of the same cull state
```

Aggregate frame latency and instrumented cull totals are diagnostic only.

## Preregistered interpretations

### `BRANCH_MIX_EXPLAINS_GROWTH`

Select if operation-unit costs remain stable while the observed 0%→100% branch-count shift explains 70%..130% of the prior +0.798 ms/frame cull growth.

This is an attribution result, not automatically an optimization candidate.

### `SPATIAL_ACCESS_CHURN_CANDIDATE_JUSTIFIED`

Select if candidate count stays within ±2%, branch-mix modeled closure is <50%, and bulk `by_entity + bounds` unit cost rises by >=20% at 100% moving together with substantial index revision churn.

A later candidate must be separately designed and A/B tested.

### `FOG_MEMBERSHIP_COST_CANDIDATE_JUSTIFIED`

Select if candidate count stays within ±2%, branch-mix modeled closure is <50%, and bulk Fog membership unit cost rises by >=20% at 100% moving in a way not explained by hit/miss composition alone.

A later candidate must be separately designed and A/B tested.

### `CULL_REQUIRES_FURTHER_ATTRIBUTION`

Use if none of the above close the signal.

## Forbidden during E2

- production cull changes
- E1 active-animation API
- Vision changes
- Fog semantic changes
- spatial-index representation changes
- native/parallel rewrites

## Methodology

> **先用批量、低扰动测量把 branch mix 与同阶段成本变化分开，再决定是否存在可优化的错误复杂度。**
