# Decision — 10K Spatial-Index Movement Specialization

## Decision

**CAUSALLY CONFIRMED / KEEP / CLOSED.**

Retain the specialized spatial-index movement update for ordinary indexed position-only commits.

## Why retained

The final same-session ABBA closeout showed the expected causal signature at both dynamic densities:

```text
50% Animation CPU / commit   13.598121 -> 12.834693 us
                              saving 0.763428 us/commit

100% Animation CPU / commit  11.066122 -> 10.557051 us
                              saving 0.509072 us/commit
```

The directly modified `AnimationSystem` path improved by ~6.3% at both densities.

The workload was preserved:

```text
position commits/s delta   <= 0.04%
Vision dirty/s delta       <= 0.03%
```

All semantic guards passed and 21 targeted regressions passed before the measurement.

The optimization therefore meets STAR's retention rule: measurable local causal win, preserved semantics, and bounded added complexity.

## Superseded rollback

The earlier rollback:

```text
7f72e352f95e20125c29502abd934f0f81a3e0f2
revert: drop non-beneficial spatial index movement specialization
```

was based on an earlier false-negative comparison and is now superseded by stronger evidence.

History was not rewritten. Mainline restored B with:

```text
4218b5368fbe2815b8512384e2c18b0af443ebfa
Revert "revert: drop non-beneficial spatial index movement specialization"
```

This leaves the original rejection and later correction auditable.

## Production invariants

The specialized path must continue to preserve:

- authoritative `HexPosition` as source of truth;
- Vision dirty marking on actual movement;
- cell faction/entity membership;
- cross-bucket membership and revisions;
- `living_counts` invariance for movement;
- generic reconciliation fallback when an index entry is missing.

## What this does not claim

Do not interpret this result as removing the full spatial-index cost attributed in Phase-5.1.

The optimization removes approximately `0.5-0.8 us/commit` of generic lifecycle overhead. Required cell/set/record/bucket maintenance remains.

## Revisit conditions

Revisit only if:

1. spatial-index representation/data layout is redesigned;
2. movement commits become batch-oriented rather than per-entity;
3. faction/liveness can change atomically inside the same movement transition;
4. profiling shows the specialized branches themselves becoming a maintenance or performance liability.

Otherwise, do not route ordinary indexed movement back through the generic lifecycle upsert without new evidence.

## Next direction

Optimization B is closed. Continue Phase-5 Core work on the Vision steady dirty path, keeping spatial-index movement specialization fixed as part of the accepted baseline.
