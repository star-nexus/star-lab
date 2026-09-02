# Decision — Runtime Visibility-History Retention

**Status:** accepted / closed  
**Decision date:** 2026-09-02  
**Fix commit:** `cc47acb661500787395b2b9b241256edadfed1d4`

## 1. Decision

In scale/window realtime runtime, retain only the latest visibility-transition record per unit. Keep complete historical trajectories out of live ECS runtime state and place them in external logging/evaluation/archive planes when needed. Leave canonical/headless Statistics behavior unchanged unless separately justified.

## 2. Why this option

Current visibility is runtime state; the historical sequence of how visibility changed is telemetry. Treating both as the same live data lifecycle created `O(units × history_length)` retained-object growth without serving a realtime consumer.

The fix preserves the latest transition for compatibility/debug context while removing unnecessary historical accumulation.

## 3. Alternatives rejected

### Run GC more frequently

Rejected. The completed pre-fix 600s soak reports total safe-GC collected = 0 while tracked objects and RSS grow. The retained records are reachable application state, not unreachable cyclic garbage.

### Increase the history cap or rely on abundant RAM

Rejected. This hides an ownership/lifecycle error rather than correcting it.

### Remove all visibility history everywhere

Rejected. The change is intentionally scoped to scale/window runtime; canonical/headless semantics are not changed without evidence.

## 4. Validation result

The recovered 120s post-fix artifact validates the causal invariant directly:

```text
visibility_history_records        5000 throughout
visibility_history_max_per_unit   1 throughout
entities                           13288 throughout
component instances               79852 throughout
Vision cache size                  4096 throughout
total safe GC collected            0
```

The retained-object working set warms into a stable band:

```text
final-five mean                    209690.4
final-five sample SD               104.2
final-five range                   248
final-four slope                   ~ -48 objects/hour
```

RSS is non-monotonic and ends below the primed baseline (`368.812 -> 337.438 MB`).

The artifact's whole-run positive tracked-object slope is not used as the steady-state leak metric because it includes initial bounded working-set population. Leak validation is based on post-warmup retained-state behavior plus the causal visibility-history cardinality.

## 5. Source-provenance caveat

The post-fix JSON is complete and SHA256-verified, but it does not encode its exact STAR checkout SHA. Repository history proves it is from the post-fix/post-diagnostics lineage; the archive records the compatible commit sequence and does not invent an exact measurement SHA.

The closed fix is present in the immutable later milestone:

```text
a24482d438157aa23b371b6e34d49b1c04fec7f7
scale-v1-cull-vision-closed
```

## 6. Revisit when

Revisit this decision if:

- runtime begins retaining new historical per-unit structures;
- a longer post-warmup soak shows sustained tracked-object or RSS growth;
- online runtime behavior genuinely requires more than the latest visibility transition;
- telemetry requirements are moved back into realtime ECS state.

If a future feature requires online trajectory history, design an explicit bounded telemetry/logging interface rather than silently expanding live ECS retention.

## 7. Principle

> Runtime state ≠ historical telemetry.
