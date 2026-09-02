# Analysis — Scale Visibility-History Retention

## 1. Observation

The completed pre-fix 600-second soak (`results/realtime-gc-soak-v2-600s.json`) showed:

```text
cycles completed                 40 / 40
RSS growth                       +51.953 MB
tracked-object growth            +149,950
total safe-GC collected          0
entity growth                    0
component-instance growth        0
Vision geometry-cache size       4096 (bounded)
```

Therefore the remaining growth did not have the shape of unreachable cyclic garbage, an ECS entity leak, or an unbounded Vision cache.

## 2. Competing hypotheses

### H1 — Python cyclic garbage is accumulating
If true, explicit full GC at safe points should reclaim objects.

### H2 — Vision geometry cache is still unbounded
If true, cache cardinality should continue growing rather than remain at 4096.

### H3 — ECS entities/components leak across cycles
If true, world entity/component counts should rise.

### H4 — Application-owned historical state retains reachable objects
If true, GC can collect zero while selected history structures grow toward their own caps.

## 3. Pre-fix evidence

The formal soak strongly rejected H1-H3:

- safe Gen2 collections reclaimed zero in aggregate;
- entity and component-instance growth were zero;
- the Vision geometry cache stayed bounded at 4096.

Inspection then found:

```text
VisibilityTracker.visibility_history: Dict[int, List[Dict]]
VISIBILITY_HISTORY_LIMIT = 100
```

At 5000 units:

```text
5000 × 100 = 500,000 potential live history records
```

Those records remain reachable by design, explaining why GC does not reclaim them.

## 4. Root cause

> The runtime was not leaking unreachable objects; it was intentionally retaining too much historical visibility telemetry inside live scale runtime state.

No realtime consumer required the full per-unit visibility trajectory. Current visibility semantics already lived in current-state structures.

## 5. Fix

The scale/window policy changed to:

```text
VISIBILITY_HISTORY_LIMIT = 1
```

This keeps the latest transition available while moving full trajectories to logging/evaluation/archive planes.

The fix commit is `cc47acb661500787395b2b9b241256edadfed1d4`. Follow-up diagnostics exposed retained-statistics cardinalities in the soak output.

## 6. Post-fix raw validation

Recovered artifact:

```text
results/realtime-gc-soak-v3-120s.json
SHA256 7db3c6fe035bf56a800d021dabaea4c33c465e01c7d4ecb351d0f98907145de3
```

It reports:

```text
top-level ok                      true
cycles completed                  8 / 8
realtime seconds completed        120
```

Every cycle's `start`, density check, cycle result, stop, and safe post-collection path is valid. The one 4999-mover cycle is within the explicit `max_missing_moving_units=10` guard.

Across all post-safe-GC samples:

```text
visibility_history_records        5000 exactly
visibility_history_max_per_unit   1 exactly
world entities                    13288 exactly
component instances               79852 exactly
Vision geometry-cache size        4096 exactly
safe GC collected                 0 in total
```

The retained-object sequence is:

```text
priming  198808
15s      202693
30s      206762
45s      209291
60s      209508
75s      209741
90s      209747
105s     209700
120s     209756
```

This has two phases:

```text
cold / state-population warm-up
        -> retained working set fills
        -> steady plateau near 209.7k
```

The final five post-GC samples are:

```text
209508, 209741, 209747, 209700, 209756
mean      209690.4
sample SD 104.2
range     248
```

The final four samples (75–120 s) have a linear slope of approximately:

```text
-48 objects/hour
```

which is effectively flat relative to a ~209.7k retained working set.

RSS is likewise non-monotonic and lower at the end than after priming:

```text
priming RSS                    368.812 MB
15s                            349.656 MB
30s                            334.438 MB
45s                            325.984 MB
60s                            341.703 MB
75s                            330.281 MB
90s                            334.297 MB
105s                           337.453 MB
120s                           337.438 MB
post-collect growth            -31.374 MB
```

## 7. Interpreting the whole-run slope correctly

The raw JSON summary contains a large positive `post_collect_tracked_objects_slope_per_hour`. That statistic spans the initial transition from the primed baseline (`198808`) into the ~`209.7k` steady working set.

It is therefore a **whole-run warm-up slope**, not a steady-state leak slope.

For a retention/leak conclusion, the causal metric is whether the retained set continues to expand after the workload has populated its stable state. The late-window evidence says no:

```text
visibility history cardinality fixed at 5000
max history per unit fixed at 1
ECS cardinality fixed
Vision cache cardinality fixed
late tracked-object range only 248
final-four tracked slope ~ -48 objects/hour
RSS not monotonic
```

This distinction matters: a system may legitimately allocate/populate a bounded working set during warm-up without leaking in steady state.

## 8. Source-provenance limit

The recovered JSON itself does not contain a Git commit SHA. Git history establishes the relevant sequence:

```text
cc47acb6  fix visibility-history retention to 1
5382834a  expose retained statistics in memory soak
0c65bfc4  test bounded visibility-history retention
04c58ad5  test retained-statistics soak snapshots
```

The artifact's fields prove it is from the post-fix/post-diagnostics lineage, but they do not uniquely identify which of those compatible checkouts was used. The archive records this uncertainty instead of guessing a SHA.

The later immutable milestone containing the closed fix is:

```text
a24482d438157aa23b371b6e34d49b1c04fec7f7
scale-v1-cull-vision-closed
```

## 9. Intermediate run policy

`results/intermediate/realtime-gc-soak-600s-incomplete.json` ended with `soak_incomplete`, but it completed eight valid cycles and materially contributed to the investigation. It remains diagnostic evidence, not formal validation evidence.

```text
invalid before workload -> discard
valid partial workload + diagnostic value -> keep as intermediate
complete valid workload -> formal evidence
```

## 10. Broader lesson

The strongest pre-fix diagnostic signal was `collected=0`: the growing objects were not garbage. They were still reachable because application semantics retained them.

The strongest post-fix validation signal is not merely lower RSS. It is that the **causal retained structure itself is now fixed at one record per unit** and the broader live-state cardinalities remain bounded.

> Runtime state is not historical telemetry.
