# Analysis — 10K Spatial-Index Movement Specialization

## Observation

After Optimization A, 10K / 100%-moving still had:

```text
controlled avg  34.180 ms
controlled P99  38.537 ms
Animation avg    7.770 ms
Vision avg       5.130 ms
```

Phase-5.1 attribution had measured the full generic spatial-index update at roughly `3.19 ms/frame` under the instrumented 100% workload.

## Hypothesis

`UnitSpatialIndex.upsert_from_world()` is a generic authoritative-cache reconciliation path. For ordinary movement, faction and liveness do not change, yet the generic path:

```text
re-reads Unit
re-reads HexPosition
re-reads UnitCount
removes the old record
re-indexes the new record
decrements living_counts
increments living_counts
removes/adds bucket membership even for same-bucket moves
```

Hypothesis: removing this unnecessary lifecycle work will materially reduce `AnimationSystem` cost.

## Candidate

A specialized `move_entity()` path reused the cached faction/record and updated only position-derived index state. It preserved:

- cell faction counts;
- cell entity membership;
- cross-bucket membership changes;
- bucket revisions;
- global revision;
- generic `upsert_from_world()` fallback if the cache entry is missing.

Regression coverage included stacked cells, same-bucket movement, cross-bucket movement, no ECS component reads on the fast path, and fallback self-healing.

## Controlled evidence

### 50% moving

```text
Optimization A control:
controlled avg   25.964 ms
P95              27.392 ms
P99              29.447 ms
Animation avg     3.633 ms
Animation P99     4.106 ms

Optimization B:
controlled avg   26.495 ms
P95              27.995 ms
P99              30.878 ms
Animation avg     3.664 ms
Animation P99     4.149 ms
```

Direct path delta:

```text
Animation avg +0.031 ms
```

### 100% moving

```text
Optimization A control:
controlled avg   34.180 ms
P95              35.686 ms
P99              38.537 ms
Animation avg     7.770 ms
Animation P99     8.481 ms

Optimization B:
controlled avg   34.967 ms
P95              36.949 ms
P99              37.629 ms
Animation avg     7.749 ms
Animation P99     8.333 ms
```

Direct path delta:

```text
Animation avg -0.021 ms
```

The isolated P99 improvement is contradicted by worse average/P95 and by the essentially unchanged direct causal metric. It is therefore treated as tail-distribution / run noise, not as candidate benefit.

## Workload preservation

Transition throughput remained effectively equal. At 100%:

```text
A: 27.9768 fps * 713.914 index changes/frame ~= 19.97K/s
B: 27.3597 fps * 730.263 index changes/frame ~= 19.98K/s
```

Vision dirty throughput likewise remained approximately 20K/s.

The B run's 0%-moving point was globally slower than A (`controlled avg 16.670 -> 17.118 ms`) with unrelated rendering sections also somewhat higher, further supporting the use of local causal metrics rather than aggregate P99 alone.

## Root conclusion

The earlier `~3.19 ms/frame` attribution represented the **entire spatial-index update**, not the subset removable by specialization.

Most of that work is required even on a position-only movement:

- derive render-space position / bucket;
- maintain old/new cell faction counts;
- maintain old/new cell entity sets;
- update entity record;
- maintain bucket membership when crossing buckets;
- invalidate revisions.

The apparently redundant lifecycle layer was too small to measure in production.

## Rejected interpretation

Do not conclude that spatial indexing itself is free or that the 3.19 ms attribution was wrong. The experiment only rejects this specific optimization:

> replacing generic upsert with a hand-specialized movement upsert while keeping the same index data model and required maintenance.

A future spatial-index optimization would need to attack mandatory representation/data-structure work, not merely remove the generic wrapper bookkeeping.

## Engineering lesson

The visual complexity of code is not a performance measurement. Optimization A showed that a tiny lookup can be huge because of multiplicity; Optimization B showed that a large-looking generic function can contain mostly necessary work and almost no removable cost.
