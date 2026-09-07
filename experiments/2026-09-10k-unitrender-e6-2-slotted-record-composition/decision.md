# Decision — Phase 5 10K UnitRender E6-2 Slotted Spatial Record Composition

**Status:** VALIDATED NEGATIVE — RAW FORENSIC MIRROR PENDING

## Baseline

Retained E6-1 production:

```text
e7ba18b31870577110b591104ef8fa7b4713e43c
```

## Formal decision

```text
SLOTTED_RECORD_COMPOSITION_NOT_MATERIAL
```

The preregistered candidate-justification rule was not satisfied at both densities.

### 50% moving

```text
Cull saving              0.074 ms  PASS >= 0.05
controlled avg delta    +1.29%     FAIL > +1.00%
UnitRender avg delta    -0.05%     PASS
Animation avg delta     +1.64%     PASS <= +2%
workload rates                         PASS
```

### 100% moving

```text
Cull saving              0.053 ms  FAIL < 0.07
controlled avg delta    +0.84%     PASS
UnitRender avg delta    -0.70%     PASS
Animation avg delta     +1.21%     PASS <= +2%
workload rates                         PASS
```

The 100%-moving treatment P99 was also worse:

```text
33.506 -> 34.365 ms
```

and remained above the 33.33 ms canonical gate.

## Interpretation

The earlier E5-1 causal signal was not spurious. A residual Cull saving remains after E6-1, but it is no longer reliably material in the frontier workload:

```text
50% signal retention  ~82% of E5-1
100% signal retention ~47% of E5-1
```

This is best read as partial subsumption by E6-1 rather than contradiction of E5-1.

## Production disposition

Do **not** create or retain the one-line `slots=True` production candidate.

Retained production remains:

```text
e7ba18b31870577110b591104ef8fa7b4713e43c
```

No Performance Frontier update is authorized.

The slotted-record composition path is closed unless a future runtime representation change creates a new matching causal signature.

## Artifact rule

Compact Evidence Package:

```text
20260907-231532-compact.zip
SHA256 682a02741be2c4002fe815418254f5ac056c06c27e1e8f4dd10130aa40c74bbc
```

Raw Forensic Package:

```text
20260907-231532-raw.zip
SHA256 e6aeee218bd21332819b881f904524ca15c3b3942c5eb4dd0bf867b42023e2c4
```

Compact remains the default review artifact. Raw remains authoritative for forensic re-audit and still needs a stable canonical mirror before the case is marked fully CLOSED.
