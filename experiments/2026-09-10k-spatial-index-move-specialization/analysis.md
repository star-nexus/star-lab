# Analysis — 10K Spatial-Index Movement Specialization

## Observation

After Optimization A, the 10K / 100%-moving point still showed substantial dynamic Core cost:

```text
controlled avg  34.180 ms
controlled P99  38.537 ms
Animation avg    7.770 ms
Vision avg       5.130 ms
```

Phase-5.1 attribution measured the full generic spatial-index update at roughly `3.19 ms/frame` under the instrumented 100% workload.

## Hypothesis

`UnitSpatialIndex.upsert_from_world()` is a generic cache-reconciliation path. Ordinary movement changes position but cannot change faction or liveness. Yet the generic path re-read ECS components and performed lifecycle bookkeeping that had no semantic value for a position-only transition.

Hypothesis:

> Specializing the movement update will reduce per-position-commit Animation CPU cost while preserving authoritative transition rate and all spatial-index semantics.

## Candidate

A specialized `move_entity()` path reused the cached record/faction and updated only movement-dependent derived index state. It preserved:

- cell faction counts;
- cell entity membership;
- cross-bucket membership changes;
- bucket revisions;
- global revision;
- generic `upsert_from_world()` fallback if the cache entry is missing.

Regression coverage included stacked cells, true same-bucket movement, cross-bucket movement, no ECS component reads on the indexed fast path, and fallback self-healing.

## First controlled result — false negative

Generation `20260906-120822` compared B against the earlier accepted A generation and showed almost no direct-path improvement:

```text
50% Animation avg   3.633 -> 3.664 ms
100% Animation avg  7.770 -> 7.749 ms
```

Aggregate average/P95 also did not improve. Under the STAR rule "no measured win, no extra production complexity", B was reverted at `7f72e352...`.

That decision was reasonable given the evidence then available, but the comparison was cross-generation rather than a same-session counterbalanced experiment. The 0%-moving point also showed broad machine drift.

## Reopening evidence

A later uninstrumented run at the exact B candidate SHA, `20260906-154003`, produced the opposite local signature:

```text
100% Animation avg   7.770 ms (prior A reference)
                    -> 6.900 ms (B treatment)
```

Authoritative position/dirty throughput remained ~20K/s. Because the directly modified path now showed a substantial benefit, the prior rejection could no longer be considered closed.

This triggered a dedicated closeout rather than simply restoring B from one cross-session result.

## Final instrumentation / experiment design

The closeout runner created detached worktrees at the exact historical source states:

```text
A = b9e0bb92b546b3283cb5c1d30a9a510d0c006ec2
B = 73a2f7f33067dfd39e7aaf1c07a4c08eafc021ba
```

It ran one session in counterbalanced order:

```text
A50 -> B50 -> B100 -> A100
```

The runner also enforced full ENV process-tree cleanup between points. An earlier attempt, `20260906-162730`, failed this requirement because Pygame child processes survived between points; that generation is invalid and excluded from formal evidence.

Pre-registered decision criteria were encoded before the valid run:

```text
rate tolerance                         2%
minimum Animation saving               0.5 us / position commit
maximum controlled-avg regression      2%
100% controlled avg                    must improve
P99                                    diagnostic only
```

## Final evidence — `20260906-172143`

### 50% moving

```text
Animation avg/frame
A 3.874383 ms
B 3.628230 ms
Delta -0.246153 ms (-6.35%)

Animation CPU / position commit
A 13.598121 us
B 12.834693 us
Saving 0.763428 us/commit

controlled avg
26.960328 -> 26.740870 ms

controlled P99
30.834542 -> 30.697517 ms
```

### 100% moving

```text
Animation avg/frame
A 8.200243 ms
B 7.685533 ms
Delta -0.514710 ms (-6.28%)

Animation CPU / position commit
A 11.066122 us
B 10.557051 us
Saving 0.509072 us/commit

controlled avg
35.499686 -> 34.873006 ms

controlled P99
40.409518 -> 39.315061 ms
```

### Independent normalization

Using Animation CPU milliseconds per wall-clock second divided by authoritative commits/s gives:

```text
50%  saved 0.760820 us/commit
100% saved 0.513289 us/commit
```

This independently reproduces the direct per-commit calculation.

## Workload preservation

The performance gain did not come from reducing world evolution:

```text
50% position commits/s   +0.0197%
50% Vision dirty/s       +0.0098%
100% position commits/s  -0.0390%
100% Vision dirty/s      -0.0262%
```

All are effectively unchanged and far inside the pre-registered +/-2% bound.

All semantic guards passed; 21 targeted regressions passed in `0.14s` before measurement.

## Root cause

The earlier `~3.19 ms/frame` attribution represented the **entire** spatial-index update. Most of that work is mandatory:

- render-space/bucket derivation;
- old/new cell counts;
- old/new cell entity sets;
- entity record update;
- cross-bucket maintenance;
- revision invalidation.

The initial mistake was not that the full 3.19 ms should disappear. The actual removable layer is the generic lifecycle/reconciliation overhead applied to a position-only transition.

That layer costs approximately:

```text
0.5-0.8 us / authoritative position commit
```

and is therefore material at 10K / ~20K commits per second.

## Why the first rejection was wrong

The first result was not fabricated or guard-invalid; it was simply insufficiently controlled for a small per-transition effect in the presence of machine drift.

The decisive evidence is stronger because it combines:

1. exact historical A/B source states;
2. same-session counterbalancing;
3. pre-registered acceptance criteria;
4. direct modified-path metrics;
5. per-authoritative-commit normalization;
6. workload preservation;
7. semantic/regression guards.

## Rejected explanations

- **Reduced movement workload:** rejected by unchanged commits/s.
- **Reduced Vision workload:** rejected by unchanged dirty/s.
- **P99 luck:** rejected because Animation avg/frame and CPU/commit both improve at both densities.
- **Monotonic machine drift:** mitigated by ABBA order; B cannot be favored at both densities merely by always running later.
- **Entire spatial index was removable:** rejected; most indexed movement maintenance remains necessary.

## Engineering lesson

Optimization A was a wrong-complexity bug: a stable dependency lookup was repeated per mover.

Optimization B is a wrong-abstraction-granularity bug: a generic lifecycle reconciliation path was used for a high-frequency position-only transition.

A visually large generic function may contain mostly mandatory work, but a sub-microsecond removable layer can still matter when multiplied by tens of thousands of authoritative transitions per second.

The case also establishes a process lesson: when a candidate effect is small relative to machine drift, close the question with same-session counterbalanced A/B and a normalized local causal metric, not cross-session aggregate FPS alone.
