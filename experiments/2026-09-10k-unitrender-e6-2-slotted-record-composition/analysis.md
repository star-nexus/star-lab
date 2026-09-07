# Analysis — Phase 5 10K UnitRender E6-2 Slotted Spatial Record Composition

## 1. Observation

Earlier E5-1 evidence showed a small positive Cull signal from `slots=True` on `UnitSpatialRecord`:

```text
50% moving:  ~0.090 ms Cull saving
100% moving: ~0.113 ms Cull saving
```

E6-1 later removed the dominant `world_x/world_y/bucket` payload first-touch mechanism and became retained production.

E6-2 formally tested whether the older representation signal remained independently material on top of E6-1.

## 2. Formal evidence

Run:

```text
run_id: 20260907-231532
control/treatment runtime: e7ba18b31870577110b591104ef8fa7b4713e43c
order: A50 -> B50 -> B100 -> A100
```

Validation:

```text
treatment contract: 4 passed
control targeted regressions: 30 passed
treatment targeted regressions: 30 passed
all scale-driver guards: PASS
```

### 50% moving

```text
controlled avg: 24.923 -> 25.245 ms (+1.29%)
controlled p99: 30.921 -> 26.466 ms
Cull avg:       1.848 -> 1.774 ms  saving 0.074 ms
Cull p95 save:  0.078 ms
UnitRender avg: 9.005 -> 9.000 ms (-0.05%)
Animation avg:  3.397 -> 3.452 ms (+1.64%)
position rate:  -0.035%
Vision rate:    -0.045%
Fog delta:      +0.214%
```

The local Cull floor passed, but controlled average exceeded the preregistered +1% ceiling.

The apparently large P99 improvement is not treated as causal evidence. Control had p50 24.819 ms and p95 25.877 ms, both lower than treatment p50 25.267 ms and p95 26.137 ms; only a small number of control tail frames raised p99 to 30.921 ms. This is exactly the type of run-level tail shape for which local metrics and preregistered average guards take precedence.

### 100% moving

```text
controlled avg: 31.930 -> 32.199 ms (+0.84%)
controlled p99: 33.506 -> 34.365 ms
Cull avg:       1.942 -> 1.889 ms  saving 0.053 ms
Cull p95 save:  0.032 ms
UnitRender avg: 9.783 -> 9.714 ms (-0.70%)
Animation avg:  7.211 -> 7.298 ms (+1.21%)
position rate:  -0.022%
Vision rate:    -0.009%
Fog delta:      -0.421%
```

The frontier workload failed the preregistered Cull materiality floor of 0.07 ms and its P99 moved in the wrong direction.

## 3. Interpretation

The old E5-1 signal was genuine but is now partially subsumed by E6-1.

Signal retention relative to E5-1:

```text
50%:  0.074 / 0.090 ~= 82%
100%: 0.053 / 0.113 ~= 47%
```

This density-dependent attenuation matters. The relevant Phase-5 boundary is 100% moving, where the remaining slotted-record Cull benefit is below the preregistered materiality floor.

The repeated Animation increase (+1.64% @50%, +1.21% @100%) is also directionally consistent with a small movement-side representation/construction cost. It remains below the formal 2% rejection ceiling, so it does not alone reject the candidate, but it reinforces that slots are not a free composition win.

Do not over-attribute the exact Animation mechanism from this run alone. The safe conclusion is that any remaining Cull benefit is small enough that compensating work and run-level variation prevent a reliable end-to-end gain.

## 4. Causal conclusion

```text
E5-1 positive record-representation signal
        +
E6-1 canonical world-geometry payload reuse
        ↓
small residual Cull benefit remains
        ↓
benefit attenuates at 100% moving
        +
no stable controlled-work / tail improvement
        ↓
SLOTTED_RECORD_COMPOSITION_NOT_MATERIAL
```

This does not invalidate E5-1. It updates its engineering relevance in the new retained runtime state.

## 5. Production consequence

No one-line `slots=True` source candidate is justified. Production remains:

```text
e7ba18b31870577110b591104ef8fa7b4713e43c
```

Do not combine additional previously rejected UnitSpatialRecord representation tweaks into a bundle; that would lose attribution. Any next Phase-5 work should start from the retained E6-1 production state and inspect the current 100%-moving tail/system composition.

## 6. Canonical 30 Hz result

E6-2 treatment at 100% moving:

```text
controlled p99 = 34.364929 ms
threshold      = 33.33 ms
classification = FAIL
```

No Performance Frontier update.

## 7. Artifact integrity

Compact package SHA256:

```text
682a02741be2c4002fe815418254f5ac056c06c27e1e8f4dd10130aa40c74bbc
```

Raw package SHA256:

```text
e6aeee218bd21332819b881f904524ca15c3b3942c5eb4dd0bf867b42023e2c4
```

The uploaded Compact package's internal `SHA256SUMS` was independently rechecked and all retained members matched. Raw remains the final forensic substrate and is not replaced by Compact.
