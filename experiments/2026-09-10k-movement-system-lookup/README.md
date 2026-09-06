# 10K MovementSystem Lookup Elimination

**Status:** CLOSED — causal optimization retained; raw evidence complete  
**STAR repository:** `star-nexus/star`  
**Branch at time:** `perf/10k-online`

## Purpose

This case records the Phase-5 10K Core Runtime bottleneck where `AnimationSystem` resolved `MovementSystem` inside the per-moving-entity loop. At 10,000 moving units this turned a semantically constant dependency lookup into roughly 10,000 `world.systems` scans per frame.

The case is important because the code looked trivial, but the repeated lookup accounted for a large fraction of dynamic scaling cost.

## Source states

- Problem / production baseline: `82054c554d359516fe3d9cf0fa80cfd81bc222a3`
- Attribution harness: `497ca6ce7113cb4883359fb0821b4022538255a6`
- Fix: `b9e0bb92b546b3283cb5c1d30a9a510d0c006ec2`
- Historical Optimization-B rollback state: `7f72e352f95e20125c29502abd934f0f81a3e0f2`
- Current `perf/10k-online` state restoring confirmed Optimization B while retaining A: `4218b5368fbe2815b8512384e2c18b0af443ebfa`

`b9e0bb92...` and `7f72e352...` have no production file diff; the latter is retained only as historical provenance for the temporary Optimization-B rollback. Optimization B was later re-evaluated with a same-session ABBA closeout, confirmed beneficial, and restored at `4218b536...`. Optimization A remained retained throughout.

## Workload

```text
scenario              chibi-144k-scale-10000
scenario SHA256       e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
resident units        10000
moving points         0 / 5000 / 10000
phase                  staggered
seed / phase seed      42 / 42
route steps            12
Fog                    ON
GC                     realtime_defer
MiniMap dynamic units  OFF
render                  uncapped
execution pathfinding  OFF
production animation   ON
canonical gate         controlled_work_frame_ms.p99 <= 33.33 ms
```

Hardware: Mac mini ARM64, macOS 26.5.2.

## Reproduction

Checkout the problem or fix SHA, provide the local test-only `rotk_env/maps/chibi-144k-scale-10000.json` with the scenario SHA above, then run:

```bash
./tools/run_phase5_10k_core.sh
```

The map is intentionally test-only and is not part of the STAR release tree.

For the attribution generation, checkout `497ca6ce...` and use the archived Phase-5.1 attribution tooling represented by run `20260906-033723`.

## Canonical result

| Density | Baseline controlled avg | Fixed avg | Baseline P99 | Fixed P99 | 30 Hz |
|---|---:|---:|---:|---:|---|
| 0% | 16.871 ms | 16.670 ms | 20.595 ms | 20.546 ms | PASS -> PASS |
| 50% | 30.239 ms | 25.964 ms | 36.581 ms | 29.447 ms | **FAIL -> PASS** |
| 100% | 41.589 ms | 34.180 ms | 46.191 ms | 38.537 ms | FAIL -> FAIL |

Direct causal metric at 100% moving:

```text
AnimationSystem avg
13.5409 ms -> 7.7701 ms
Delta = -5.7708 ms (-42.6%)
```

Phase-5.1 attribution predicted approximately `5.55 ms/frame` for the repeated lookup at 100% moving, closely matching the production A/B reduction.

Authoritative movement throughput remained approximately 20K committed transitions/s; the improvement did not come from reducing world evolution.

## Root cause

A stable system dependency was resolved at the wrong complexity level:

```text
semantic requirement: one MovementSystem dependency per synchronous update
implementation:       one world.systems scan per moving entity
complexity:           O(Nmoving * Nsystems)
```

At 10K movers, a semantically worthless Python lookup became a first-class runtime bottleneck.

## Raw evidence

Canonical raw evidence is mirrored in this case:

```text
results/raw/phase5-10k-core/chibi-144k-scale-10000/20260906-030632/
results/raw/phase5-10k-attribution/chibi-144k-scale-10000/20260906-033723/
results/raw/phase5-10k-core/chibi-144k-scale-10000/20260906-041532/
```

Together they contain the problem baseline, causal attribution generation, and fixed production A/B. Every mirrored raw file is covered by `artifacts/RAW_SHA256SUMS`; source-package identities are retained in `artifacts/SHA256SUMS`.

Evidence state: **raw evidence complete; exact source provenance recorded; file-level SHA256 covered**.

## Engineering lesson

A tiny operation can dominate scale when architectural multiplicity is wrong. Cost must be evaluated as:

```text
cost per call * calls at target scale
```

not by visual code size or intuition about one invocation.
