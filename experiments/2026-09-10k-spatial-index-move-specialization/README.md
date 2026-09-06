# 10K Spatial-Index Movement Specialization

**Status:** CLOSED — causally confirmed KEEP; raw evidence complete  
**STAR repository:** `star-nexus/star`  
**Branch at time:** `perf/10k-online`

## Purpose

This case records Optimization B from Phase-5 10K Core Runtime scaling. The generic `UnitSpatialIndex.upsert_from_world()` path treated ordinary position-only movement like lifecycle reconciliation: it re-read ECS components, touched liveness accounting, and performed generic bucket maintenance even when faction and liveness could not have changed.

The first production comparison incorrectly suggested that the specialization had no measurable benefit and the implementation was reverted. A later treatment run contradicted that conclusion. The case was therefore reopened and closed with a same-session, pre-registered ABBA experiment.

Final result: **Optimization B is causally beneficial and retained.**

## Source states

- Optimization-A control: `b9e0bb92b546b3283cb5c1d30a9a510d0c006ec2`
- Specialized implementation: `5af001817e65869fb3fa782edb9e8284d13e53e7`
- Final measured B candidate: `73a2f7f33067dfd39e7aaf1c07a4c08eafc021ba`
- Historical false-negative rollback: `7f72e352f95e20125c29502abd934f0f81a3e0f2`
- Closeout runner fix: `aa612ecfa2c31c61d942689999e2e8d7352b2d4b`
- Mainline restore after closeout: `4218b5368fbe2815b8512384e2c18b0af443ebfa`

## Candidate optimization

For indexed position-only movement, reuse the cached spatial-index record and update only movement-dependent derived state.

Removed from the normal movement fast path:

```text
- re-read Unit
- re-read HexPosition
- re-read UnitCount
- living_counts decrement / increment
- same-bucket by_bucket remove / add
- generic lifecycle reconciliation branches
```

Preserved:

```text
- authoritative HexPosition commit
- Vision dirty semantics
- old/new cell faction counts
- old/new cell entity membership
- entity record update
- required cross-bucket membership changes
- bucket/global revisions
- generic upsert fallback if the cache entry is missing
```

## Why the first result was superseded

The earlier candidate generation `20260906-120822` showed essentially no direct Animation benefit and led to rollback. That was a valid run, but it was not a same-session counterbalanced A/B and the machine-level drift was large enough to make the conclusion fragile.

A later uninstrumented B-only reproduction `20260906-154003` showed a clear local-path improvement at 100% moving, so the negative conclusion was reopened rather than treated as settled.

The final closeout used one session and an ABBA order:

```text
A50 -> B50 -> B100 -> A100
```

This prevents a monotonic machine drift from favoring B at both densities merely because B always ran later.

## Pre-registered closeout criteria

Before the final run, the analyzer required:

```text
all driver/semantic guards                     PASS
position commits/s A<->B                       within 2%
Vision dirty/s A<->B                           within 2%
Animation CPU saving                           >= 0.5 us / position commit
controlled avg                                 no >2% regression
100% moving controlled avg                     B < A
P99                                             diagnostic, not sole keep/revert gate
```

## Final same-session closeout — `20260906-172143`

All 21 targeted regressions passed before measurement. All four driver points passed semantic guards and ENV cleanup checks.

| Density | Metric | Opt A | Opt B | Delta |
|---|---|---:|---:|---:|
| 50% | Animation avg/frame | 3.874383 ms | 3.628230 ms | **-6.35%** |
| 50% | Animation CPU / position commit | 13.598121 us | 12.834693 us | **-0.763428 us** |
| 50% | controlled avg | 26.960328 ms | 26.740870 ms | -0.219458 ms |
| 50% | controlled P99 | 30.834542 ms | 30.697517 ms | -0.137025 ms |
| 100% | Animation avg/frame | 8.200243 ms | 7.685533 ms | **-6.28%** |
| 100% | Animation CPU / position commit | 11.066122 us | 10.557051 us | **-0.509072 us** |
| 100% | controlled avg | 35.499686 ms | 34.873006 ms | **-0.626680 ms** |
| 100% | controlled P99 | 40.409518 ms | 39.315061 ms | **-1.094458 ms** |

Independent CPU-per-second normalization gives almost identical savings:

```text
50%   0.760820 us / commit
100%  0.513289 us / commit
```

## Workload preservation

The optimization did not reduce authoritative world evolution.

```text
50% position commits/s   A 9992.66   B 9994.63   delta +0.020%
50% Vision dirty/s       A 9995.05   B 9996.03   delta +0.010%

100% position commits/s  A 19992.42  B 19984.62  delta -0.039%
100% Vision dirty/s      A 19996.81  B 19991.58  delta -0.026%
```

These are far inside the pre-registered +/-2% tolerance.

## Root cause

The original generic spatial-index update was semantically correct but used the wrong abstraction granularity for a high-frequency state transition.

```text
generic abstraction: entity/lifecycle reconciliation
actual hot transition: position-only movement
```

The removable layer is much smaller than the full `~3.19 ms/frame` spatial-index cost attributed earlier, because cell/set/record/bucket maintenance remains mandatory. But the removable work is real and stable: approximately **0.5-0.8 us per authoritative position commit**.

At 10K and ~20K commits/s, that is enough to measurably reduce `AnimationSystem` and controlled frame work.

## Historical correction

The rollback:

```text
7f72e352f95e20125c29502abd934f0f81a3e0f2
revert: drop non-beneficial spatial index movement specialization
```

is now a superseded historical decision, not the current engineering conclusion.

After closeout, mainline restored B without rewriting history:

```text
4218b5368fbe2815b8512384e2c18b0af443ebfa
Revert "revert: drop non-beneficial spatial index movement specialization"
```

This keeps the false-negative decision and its later correction auditable.

## Raw evidence

STAR Lab now mirrors all three B-owned valid evidence generations:

```text
results/raw/phase5-10k-core/chibi-144k-scale-10000/20260906-120822/
results/raw/phase5-10k-core/chibi-144k-scale-10000/20260906-154003/
results/raw/phase5-opt-b-closeout/chibi-144k-scale-10000/20260906-172143/
```

Canonical Optimization-A raw control remains owned by the A case and is cross-referenced rather than duplicated:

```text
../2026-09-10k-movement-system-lookup/
  results/raw/phase5-10k-core/chibi-144k-scale-10000/20260906-041532/
```

The B case owns **89 mirrored raw files** in total:

```text
20260906-120822   26 files   superseded false-negative generation
20260906-154003   26 files   corroborating treatment generation
20260906-172143   37 files   final same-session ABBA closeout
```

Every mirrored B-owned raw file is covered by:

```text
artifacts/RAW_SHA256SUMS
```

Source ZIP identities are preserved for the later generations:

```text
20260906-154003.zip  ae5e923c242b69144693d58efc843912ca8dff57ab795630913a7f95619ed167
20260906-172143.zip  e6d4e7d3beebf5880a13e30b59ab6e795afe9e1c4e268de394778b6b2b1acc8c
```

The interrupted closeout generation `20260906-162730` is explicitly **excluded from formal evidence** because ENV child processes leaked between points and contaminated later measurements. Independent repository-tree verification confirmed that this generation is absent from the STAR Lab archive.

Evidence state: **raw evidence complete; exact source provenance recorded; 89 B-owned raw files covered by file-level SHA256**.
