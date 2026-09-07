# Phase 5 10K UnitRender E6-2 — Slotted Spatial Record Composition

**Status:** VALIDATED NEGATIVE — RAW FORENSIC MIRROR PENDING  
**STAR repository:** `star-nexus/star`  
**Retained production:** `e7ba18b31870577110b591104ef8fa7b4713e43c`  
**Experiment branch:** `experiment/phase5-unitrender-e6-2-slotted-composition`  
**Frozen tooling commit:** `f1bf1c4f8e921287a9fc3c1b76c685f6f551a5e2`

## Question

E5-1 previously found a small positive Cull signal from `UnitSpatialRecord slots=True` (~0.090 ms @50%, ~0.113 ms @100%). E6-1 later removed the dominant world-coordinate payload first-touch mechanism and became retained production.

E6-2 asked whether the earlier slotted-record signal remained independently material after composing it with retained E6-1 bounded geometry reuse. This did not reopen E5 root-cause attribution.

## Treatment isolation

Both control and treatment ran exact retained E6-1 source:

```text
e7ba18b31870577110b591104ef8fa7b4713e43c
```

Treatment changed only the representation before world creation:

```python
@dataclass(frozen=True, slots=True)
class UnitSpatialRecord:
    ...same fields...
```

E6-1 bounded geometry ownership, fresh record identity, record fields, Cull, spatial containers, HexPosition authority, movement, Vision and Fog semantics were preserved.

## Formal run

```text
run_id: 20260907-231532
order: A50 -> B50 -> B100 -> A100
contract: 4 passed
control targeted regressions: 30 passed
treatment targeted regressions: 30 passed
all workload guards: PASS
```

Formal result:

```text
50% moving
  controlled avg: 24.923 -> 25.245 ms (+1.29%)
  controlled p99: 30.921 -> 26.466 ms
  Cull avg:       1.848 -> 1.774 ms  saving 0.074 ms
  UnitRender avg: 9.005 -> 9.000 ms (-0.05%)
  Animation avg:  3.397 -> 3.452 ms (+1.64%)
  decision check: FAIL controlled avg > preregistered +1% ceiling

100% moving
  controlled avg: 31.930 -> 32.199 ms (+0.84%)
  controlled p99: 33.506 -> 34.365 ms
  Cull avg:       1.942 -> 1.889 ms  saving 0.053 ms
  UnitRender avg: 9.783 -> 9.714 ms (-0.70%)
  Animation avg:  7.211 -> 7.298 ms (+1.21%)
  decision check: FAIL Cull saving < preregistered 0.07 ms floor
```

Decision:

```text
SLOTTED_RECORD_COMPOSITION_NOT_MATERIAL
```

The old E5-1 signal was not false: at 50% moving E6-2 still recovered 0.074 ms, about 82% of the prior 0.090 ms signal. At 100% moving it recovered only 0.053 ms, about 47% of the prior 0.113 ms signal. The residual representation benefit is therefore real but no longer reliably material at the frontier workload after E6-1.

The large 50% P99 decrease is not used as evidence for slots: control p50/p95 were lower than treatment while only a few tail frames raised control p99. The preregistered local/average gates correctly prevent treating this run-level tail shape as causal improvement.

## Production disposition

No source candidate is created. Retained production remains:

```text
e7ba18b31870577110b591104ef8fa7b4713e43c
```

The slotted-record composition path is closed unless a future runtime representation change creates a new matching signature.

## Canonical 30 Hz diagnostic

At 100% moving the treatment P99 was:

```text
34.364929 ms > 33.33 ms
```

so E6-2 does not move the Performance Frontier.

## Two-tier artifacts

Compact Evidence Package:

```text
20260907-231532-compact.zip
SHA256 682a02741be2c4002fe815418254f5ac056c06c27e1e8f4dd10130aa40c74bbc
size 11796 bytes
```

Raw Forensic Package:

```text
20260907-231532-raw.zip
SHA256 e6aeee218bd21332819b881f904524ca15c3b3942c5eb4dd0bf867b42023e2c4
size 131085 bytes
```

Compact is the default review artifact. Raw remains the authoritative forensic substrate and still needs a stable canonical mirror before the case can be marked fully CLOSED.
