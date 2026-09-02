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

## 3. Evidence

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

This keeps the latest transition available while moving the conceptual responsibility for full trajectories to logging/evaluation/archive planes.

## 6. Post-fix validation status

The original final 120-second PASS was terminal-only and is not yet archived as a raw artifact. Historical summary values indicate:

```text
visibility_history_records       5000
max records per unit             1
Vision cache                     4096
entities/components              stable
safe full GC collected           0
tracked objects                  late plateau near 209.7k
RSS                              no monotonic growth
```

These values are useful for locating the transcript, but STAR Lab currently labels them **summary-only** rather than raw evidence. The case should be upgraded once the original terminal transcript is recovered and checksummed.

## 7. Intermediate run policy

`results/intermediate/realtime-gc-soak-600s-incomplete.json` ended with `soak_incomplete`, but it completed eight valid cycles and already showed a retention signal. It is preserved because it materially contributed to the investigation, but it is not used to validate the final conclusion.

This is the intended distinction:

```text
invalid before workload -> discard
valid partial workload + diagnostic value -> keep as intermediate
complete valid workload -> formal evidence
```

## 8. Broader lesson

The strongest diagnostic signal was `collected=0`: the growing objects were not garbage. They were still reachable because application semantics retained them.

> Runtime state is not historical telemetry.
