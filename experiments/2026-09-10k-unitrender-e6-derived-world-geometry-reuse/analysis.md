# Analysis — Phase 5 10K UnitRender E6 Derived World-Geometry Reuse

## 1. Observation

Upstream CLOSED evidence only:

```text
E5-3 @ 50% moving:
  full record-field first-touch effect = 0.253 ms
  world_x/world_y contribution        = 0.201 ms (~79.4%)

E5-3 @ 100% moving:
  full record-field first-touch effect = 0.476 ms
  world_x/world_y contribution        = 0.375 ms (~78.8%)
```

Production source semantics also establish that:

```text
HexPosition is authoritative.
UnitSpatialIndex is explicitly a derived cache.
_record_for_hex(col,row,faction) recomputes hex_to_pixel(col,row)
and creates fresh world_x/world_y/bucket payload on each refreshed record.
Cull first exact bounds test reads record.world_x / record.world_y.
```

No E6 treatment measurement has been observed yet.

## 2. Competing hypotheses

### H1 — Long-lived per-hex derived geometry materially reduces Cull first-touch cost

Why it is plausible:

- E5-3 isolated ~79% of the residual record-field signal to `world_x/world_y` at both 50% and 100% movement.
- `hex_to_pixel(col,row)` is pure for fixed geometry configuration.
- The scale harness uses sustained out-and-back routes, so the same hex geometry is revisited repeatedly.
- Reusing the same derived float payload objects may improve Cull locality without changing authoritative state or Cull semantics.

Expected H1 signature:

```text
Cull avg saving >= 0.10 ms @50%
Cull avg saving >= 0.20 ms @100%
UnitRender avg improves at both densities
workload rates remain within ±2%
```

### H2 — Payload identity/reuse is not the material mechanism

Why it is plausible:

- E5-3 is a first-touch attribution experiment, not direct evidence that stable object payload identity will recover the cost.
- The observed signal may arise from unavoidable access to movement-refreshed spatial state rather than from allocation/reuse of the referenced float objects themselves.
- A cache lookup may offset some or all theoretical locality benefit.

Expected H2 signature:

```text
Cull saving fails one or both preregistered floors,
or UnitRender does not improve consistently despite preserved workload rates.
```

## 3. Instrumentation / diagnostic changes

E6 uses exact retained production as both A and B runtime source:

```text
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
```

Treatment is delivered only through:

```text
tools/phase5_unitrender_e6_geometry_reuse.py
```

It monkeypatches `UnitSpatialIndex._record_for_hex()` so each `(col,row)` has one long-lived derived geometry tuple:

```text
(world_x, world_y, bucket)
```

Every refresh still creates a fresh ordinary production `UnitSpatialRecord`.

Isolation contract test:

```text
tools/test_phase5_unitrender_e6_geometry_reuse.py
```

The test requires:

```text
fresh record identity remains true
same-hex world_x object identity is reused
same-hex world_y object identity is reused
same-hex bucket tuple identity is reused
faction remains record-specific
move_entity/upsert methods are unchanged
movement occupancy/living-count semantics remain intact
```

Formal runner:

```text
tools/run_phase5_unitrender_e6_attribution.sh
```

Counterbalanced order:

```text
A50 -> B50 -> B100 -> A100
```

The retained window is deliberately late (`sample_after=19s`) so first-fill route geometry ages out before measurement.

## 4. Evidence

### Evidence for / against H1

**PENDING FORMAL RUN.**

Required evidence fields after execution:

```text
control/treatment Cull avg + p95
control/treatment UnitRender avg
control/treatment Animation avg
controlled-work avg + diagnostic p99
position commits/s
Vision changed/s
Fog delta tiles/s
all scale-driver guards
source/treatment metadata guards
```

### Evidence for / against H2

**PENDING FORMAL RUN.**

Do not infer H2 merely from aggregate frame noise. The local Cull metric and workload-equivalence guards decide this experiment.

## 5. Root cause

**PENDING E6 EVIDENCE.**

E5-3 already established `WORLD_COORD_PAYLOAD_FIRST_TOUCH_DOMINANT`; E6 does not reopen that CLOSED attribution. E6 tests whether *reuse* of that isolated payload is an effective treatment.

## 6. Causal chain under test

```text
movement commit
  -> fresh UnitSpatialRecord refresh
  -> derived world_x/world_y payload regenerated
  -> Cull first touches movement-refreshed world geometry
  -> movement-dependent Cull cost

E6 treatment:
(col,row) stable semantic key
  -> long-lived derived geometry payload
  -> fresh record references reused geometry
  -> test whether Cull first-touch cost falls materially
```

## 7. Rejected explanations preserved from upstream cases

Do not reopen these without a new matching signature:

- exact raster duplicate draw — insufficient duplicate rate / savings;
- active-animation API — rejected at full-motion frontier;
- Cull candidate-volume growth — candidates essentially unchanged;
- Fog branch-mix explanation — branch closure insufficient;
- generic dict/set per-op slowdown — bulk replay did not explain observed growth;
- MapRender eviction/locality-gap — early pre-Map Cull was slower, second same-frame Cull was fast;
- `by_entity` lookup cost — E5 structure decomposition showed negligible contribution;
- stable `UnitSpatialRecord` identity — E5-2 additional saving was not material;
- `slots=True` as full answer — E5-1 recovered only a small fraction and was not kept.

## 8. Limits of the evidence

Before execution:

- no E6 performance result exists;
- the treatment uses an attribution-only visited-hex cache and does not establish acceptable production ownership/lifetime;
- a positive result will justify a production candidate, not production KEEP;
- only the existing Mac 10K workload is planned for this causal test;
- P99 remains diagnostic for this mechanism experiment because run-level tail noise can exceed the local causal signal.

## 9. Raw evidence

Pending formal execution. No empty checksum file is created before artifacts exist.

- [`manifest.yaml`](manifest.yaml)
- [`decision.md`](decision.md)
