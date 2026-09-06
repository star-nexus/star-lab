# Post-D1 10K / 100%-Moving 30Hz Frontier Confirmation

**Status:** RUNNING — preregistered, measurement pending  
**STAR repository:** `star-nexus/star`  
**Frozen production runtime:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

Vision D1 is already:

```text
CAUSALLY CONFIRMED / KEEP / CLOSED
```

Its controlled A/B removed the periodic 10K Vision audit pulse:

```text
100% control P99      33.931 ms
100% treatment P99    32.497 ms
audit max             4.233 -> 0.001 ms
>33.33ms frames       2 -> 0
```

That P99 is supporting evidence only because the D1 optimization closeout preregistered P99 as diagnostic. This separate case decides whether the production capacity frontier can formally move.

## Frozen runtime

```text
perf/10k-online
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
= A + B + C1 + C2a + D1
```

No runtime optimization change is allowed during confirmation.

## Canonical workload

```text
scenario                  chibi-144k-scale-10000
scenario SHA256           e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
resident units            10000
seed / phase seed         42 / 42
route steps               12
phase                     staggered
Fog                       ON
GC                        realtime_defer
MiniMap dynamic units     OFF
render                    uncapped
hub                       offline
mock_ai                    off
```

## Execution sequence

```text
00pct-moving
50pct-moving
100pct-moving-r1
100pct-moving-r2
100pct-moving-r3
```

The first three points are a complete canonical sweep. The final two are fresh-process full-motion replications with full process-tree cleanup between points.

## Preregistered frontier rule

Canonical gate:

```text
controlled_work_frame_ms.p99 <= 33.33 ms
```

Formal establishment requires:

1. all five points pass all runtime/workload guards;
2. `00 / 50 / 100-r1` all pass the P99 gate;
3. **all three** 100%-moving runs independently pass the gate.

No median-only or majority-only reinterpretation is permitted.

Decision values:

```text
FRONTIER_ESTABLISHED_10K_100PCT_30HZ
FRONTIER_NOT_ESTABLISHED
```

## Tooling

STAR branch:

```text
experiment/phase5-10k-frontier-confirmation-d1
```

The branch is based on exact production `17ced8d...` and adds only:

```text
tools/phase5_10k_frontier_confirmation_d1.py
tools/run_phase5_10k_frontier_confirmation_d1.sh
```

The runner executes exact production from a detached worktree, copies only the intentionally untracked 10K map, runs targeted semantic regressions, launches a fresh ENV process for each point and verifies process-tree cleanup before the next point.

## Interpretation

D1 validity and capacity-frontier status remain separate:

```text
D1 KEEP
    !=
10K / 100%-moving / Fog ON / 30Hz frontier established
```

The frontier moves only from this dedicated confirmation evidence.
