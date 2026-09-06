# 10K / 100%-Moving 30Hz Frontier Confirmation

**Status:** RUNNING — preregistered, measurement pending  
**STAR repository:** `star-nexus/star`  
**Frozen production runtime:** `6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b`

## Question

After Optimization C2a produced the first observed 10K / 100%-moving controlled-work P99 below the canonical 30Hz gate, is that crossing stable enough to establish a new Performance Frontier point?

The C2a closeout observed:

```text
100% moving treatment
controlled_work_frame_ms.p99 = 33.199 ms
canonical gate                 = 33.330 ms
headroom                       = 0.131 ms
```

That closeout preregistered P99 as diagnostic, so it cannot retrospectively establish the capacity frontier. This case is a separate boundary-confirmation experiment where P99 is the primary gate by design.

## Frozen runtime

```text
perf/10k-online
6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b
```

Retained production optimizations:

```text
A   MovementSystem dependency lookup elimination
B   position-specialized spatial-index movement transition
C1  Vision geometry cache-hit terrain bypass
C2a explored history on faction visibility 0 -> 1
```

No additional runtime optimization is allowed in this experiment.

## Canonical workload

```text
scenario                  chibi-144k-scale-10000
scenario SHA256           e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
resident units            10000
seed / phase seed         42 / 42
route steps               12
motion phase              staggered
Fog                       ON
GC                        realtime_defer
MiniMap dynamic units     OFF
render                    uncapped
hub                       offline
mock_ai                   off
```

## Execution sequence

```text
00pct-moving
50pct-moving
100pct-moving-r1
100pct-moving-r2
100pct-moving-r3
```

The first three points are one complete canonical 0/50/100 sweep. The final two points are independent full-motion repeats, each launched in a fresh ENV process after complete process-tree cleanup.

## Preregistered frontier rule

Canonical 30Hz gate:

```text
controlled_work_frame_ms.p99 <= 33.33 ms
```

The frontier is formally established only if:

1. all five points pass all driver / workload guards;
2. the full canonical `0/50/100-r1` sweep passes the 30Hz P99 gate;
3. **all three** `100pct-moving` runs independently satisfy `P99 <= 33.33 ms`.

No median-only or majority-pass reinterpretation is allowed after measurement.

Decision values:

```text
FRONTIER_ESTABLISHED_10K_100PCT_30HZ
FRONTIER_NOT_ESTABLISHED
```

If one or more full-motion repeats fail, C2a remains a retained causal optimization; only the formal capacity-frontier claim remains unestablished.

## Tooling

STAR branch:

```text
experiment/phase5-10k-frontier-confirmation
```

The branch is based on exact production `6896cdc0...` and adds measurement tooling only:

```text
tools/phase5_10k_frontier_confirmation.py
tools/run_phase5_10k_frontier_confirmation.sh
```

The runner executes the runtime itself from a detached worktree at exact production SHA, copies only the intentionally untracked 10K scenario, performs targeted semantic regressions before measurement, and terminates the complete ENV process tree between points.

## Interpretation

This case exists specifically to keep two conclusions separate:

```text
Optimization C2a validity
    !=
10K / 100%-moving 30Hz capacity frontier
```

C2a is already `CAUSALLY CONFIRMED / KEEP / CLOSED`. This experiment answers only whether the production runtime has enough repeatable P99 margin to advance the formal Performance Frontier.
