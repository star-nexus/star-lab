# Decision — Runtime Visibility-History Retention

**Status:** accepted / closed  
**Decision date:** 2026-09-02  
**Fix commit:** `cc47acb661500787395b2b9b241256edadfed1d4`

## 1. Decision

In scale/window realtime runtime, retain only the latest visibility-transition record per unit. Keep complete historical trajectories out of live ECS runtime state and place them in external logging/evaluation/archive planes when needed. Leave canonical/headless Statistics behavior unchanged unless separately justified.

## 2. Why this option

Current visibility is runtime state; the historical sequence of how visibility changed is telemetry. Treating both as the same live data lifecycle created `O(units × history_length)` retained-object growth without serving a realtime consumer.

The fix preserves the latest transition for compatibility/debug context while removing the unnecessary historical accumulation.

## 3. Alternatives rejected

### Run GC more frequently

Rejected. Full safe-point generation-2 collections already reclaimed zero; the records remained reachable by design.

### Increase the history cap or rely on abundant RAM

Rejected. This would hide the ownership/lifecycle mistake rather than correct it.

### Remove all visibility history everywhere

Rejected. The change was intentionally scoped to scale/window runtime; canonical/headless semantics were not changed without evidence.

## 4. Validation criterion

A healthy repeated soak should show:

```text
visibility history <= 1 record per scale unit
stable ECS counts
bounded Vision cache
no sustained post-warmup tracked-object slope attributable to historical visibility
```

## 5. Revisit when

If a future runtime feature truly requires trajectory history online, design an explicit bounded telemetry/logging interface rather than silently expanding live ECS retention.

## 6. Principle

> Runtime state ≠ historical telemetry.
