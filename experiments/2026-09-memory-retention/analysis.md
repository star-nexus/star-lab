# Analysis — Scale Visibility-History Retention

## 1. Observation

After Vision geometry caching itself was bounded, a long repeated realtime soak still showed material RSS/tracked-object growth.

At the same time:

```text
safe generation-2 GC collections repeatedly collected 0
Vision geometry cache remained at its configured bound
ECS entity count remained flat
ECS component-instance count remained flat
```

Therefore the remaining growth did not have the shape of unreachable cyclic garbage or entity leakage.

## 2. Competing hypotheses

### H1 — Python cyclic garbage is accumulating

If true, explicit full GC at safe points should reclaim objects.

### H2 — Vision geometry cache is still effectively unbounded

If true, cache size should continue growing rather than remain at 4096.

### H3 — ECS entities/components leak across movement cycles

If true, world entity/component counts should rise.

### H4 — Application-owned historical state is intentionally retaining live objects

If true, GC would collect nothing because the objects remain reachable, while selected bounded history structures would grow toward their own caps.

## 3. Instrumentation

The soak tooling exposed at safe/control points:

```text
RSS
tracked Python objects
GC collection result
entity count
component-instance count
Vision cache size/capacity/evictions
Statistics retained history counts
UnitObservation movement-path entries
```

This was deliberately sampled outside the realtime hot loop.

## 4. Evidence

The long-soak summary showed roughly:

```text
RSS growth               +51.953 MB
tracked-object growth    +149,950
full GC collected        0 repeatedly
Vision cache             4096 / 4096
entity growth            0
component growth         0
```

Inspection of `scale_statistics_system.py` then found:

```text
VisibilityTracker.visibility_history: Dict[int, List[Dict]]
VISIBILITY_HISTORY_LIMIT = 100
```

At 5000 units this allows as many as:

```text
5000 × 100 = 500,000
```

live historical transition records.

No realtime consumer required the full per-unit trajectory. Current visibility semantics already lived in current-state structures such as `faction_visible_units` and `UnitObservation.is_visible_to`.

The fix commit `cc47acb...` changed scale/window retention from 100 records to 1 and explicitly documented that historical trajectories are telemetry rather than realtime state.

The later 120s soak held:

```text
visibility_history_records       5000 exactly
max records per unit             1 exactly
Vision cache                     4096 exactly
entities/components              stable
safe full GC collected           0
```

while late tracked-object values plateaued tightly around 209.7k rather than continuing a monotonic rise.

## 5. Root cause

> The runtime was not leaking unreachable objects; it was intentionally retaining too much historical visibility telemetry inside live ECS state.

## 6. Causal chain

```text
visibility change events
 -> append reachable history dicts
 -> up to 100 records per unit
 -> up to 500k live records at 5K units
 -> tracked-object / RSS growth despite GC collecting 0

retain latest transition only in scale runtime
 -> bounded 1 record/unit
 -> 5000 total visibility records
 -> post-warmup memory plateau
```

## 7. Rejected explanations

- **Cyclic GC leak:** rejected because explicit generation-2 collections repeatedly collected zero.
- **Vision cache leak:** rejected because cache size stayed exactly at its configured cap.
- **ECS entity/component leak:** rejected because counts stayed flat.

## 8. Broader lesson

The strongest diagnostic signal was `collected=0`: the objects were not garbage. They were still reachable because application semantics retained them.

This distinction prevents an incorrect response such as "run GC more often" and directs investigation toward ownership and data-lifecycle design.
