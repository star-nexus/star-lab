# Analysis — Phase 5 10K UnitRender E6 Derived World-Geometry Reuse

## 1. Observation

Upstream CLOSED evidence:

```text
E5-3 @ 50% moving:
  full record-field first-touch effect = 0.253 ms
  world_x/world_y contribution        = 0.201 ms (~79.4%)

E5-3 @ 100% moving:
  full record-field first-touch effect = 0.476 ms
  world_x/world_y contribution        = 0.375 ms (~78.8%)
```

Production source semantics establish that:

```text
HexPosition is authoritative.
UnitSpatialIndex is explicitly a derived cache.
_record_for_hex(col,row,faction) recomputes hex_to_pixel(col,row)
and creates fresh world_x/world_y/bucket payload on each refreshed record.
Cull's first exact bounds test reads record.world_x / record.world_y.
```

Formal E6 run `20260907-203733` then measured the effect of reusing only pure per-hex derived geometry while preserving fresh record identity.

## 2. Competing hypotheses

### H1 — Long-lived per-hex derived geometry materially reduces Cull first-touch cost

Why it was plausible:

- E5-3 isolated ~79% of the residual record-field signal to `world_x/world_y` at both 50% and 100% movement.
- `hex_to_pixel(col,row)` is pure for fixed geometry configuration.
- The scale harness uses sustained out-and-back routes, so the same hex geometry is revisited repeatedly.
- Reusing the same derived float/bucket payload objects could improve Cull locality without changing authoritative state or Cull semantics.

Preregistered H1 signature:

```text
Cull avg saving >= 0.10 ms @50%
Cull avg saving >= 0.20 ms @100%
UnitRender avg improves at both densities
workload rates remain within ±2%
controlled-work avg regression <= 2%
```

### H2 — Payload reuse is not the material mechanism

Why it was plausible:

- E5-3 was a first-touch attribution experiment, not direct evidence that stable payload identity would recover the cost.
- The observed signal could have arisen from unavoidable access to movement-refreshed spatial state rather than reuse of the referenced geometry objects.
- A geometry-cache lookup could offset theoretical locality benefit.

H2 would remain viable if one or both preregistered Cull floors failed or UnitRender did not improve consistently under preserved workload rates.

## 3. Instrumentation / diagnostic changes

Exact retained production was both A and B runtime source:

```text
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
```

Formal measurement tooling SHA:

```text
ac68b4e5c50837feb8f978ffe2c2a9dc2caca1df
```

Treatment was delivered only through:

```text
tools/phase5_unitrender_e6_geometry_reuse.py
```

It monkeypatched `UnitSpatialIndex._record_for_hex()` so each `(col,row)` had one long-lived derived geometry tuple:

```text
(world_x, world_y, bucket)
```

Every refresh still created a fresh ordinary production `UnitSpatialRecord`.

Isolation validation before measurement:

```text
E6 identity/isolation contract: 2 passed
control targeted regressions: 25 passed
treatment targeted regressions with patch installed: 25 passed
```

Formal runner order:

```text
A50 -> B50 -> B100 -> A100
```

The retained window was deliberately late (`sample_after=19s`) so first-fill route geometry aged out before measurement.

## 4. Evidence

### Evidence for H1

Formal result:

```text
50% moving
  controlled avg: 25.412 -> 25.267 ms  (-0.57%)
  Cull avg:        2.076 -> 1.875 ms   saving 0.201 ms
  UnitRender avg:  9.268 -> 9.134 ms   saving 0.134 ms
  Animation avg:   3.525 -> 3.518 ms   saving 0.007 ms
  position rate:   +0.733%
  vision changed:  +0.447%
  fog delta:       +0.693%
  all checks:      PASS

100% moving
  controlled avg: 32.880 -> 32.386 ms  (-1.50%)
  Cull avg:        2.404 -> 1.971 ms   saving 0.433 ms
  UnitRender avg: 10.242 -> 10.026 ms   saving 0.217 ms
  Animation avg:   7.320 -> 7.279 ms   saving 0.041 ms
  position rate:   -0.109%
  vision changed:  -0.054%
  fog delta:       +0.319%
  all checks:      PASS
```

Cull relative savings:

```text
50%  ≈ 9.7%
100% ≈ 18.0%
```

Both density points exceeded the preregistered materiality floors and preserved workload-equivalence rates within ±2%.

A strong causal consistency check is the 50% result:

```text
E5-3 world_x/world_y attribution = 0.201 ms
E6 geometry-reuse Cull recovery  = 0.201 ms
```

At 100%:

```text
E5-3 world_x/world_y attribution = 0.375 ms
E6 geometry-reuse Cull recovery  = 0.433 ms
```

The `0.058 ms` excess must not be interpreted as >100% recovery of the earlier world-coordinate estimate. E6 jointly canonicalized `(world_x, world_y, bucket)`, and normal run-level measurement variation is comparable to this small excess. The preregistered conclusion only requires material recovery, which is clearly established.

### Evidence against H2

H2 predicted that stable per-hex payload reuse would fail the local Cull floors or fail to improve UnitRender consistently.

Observed evidence contradicts that prediction:

```text
Cull floor @50% required >= 0.10 ms; observed 0.201 ms
Cull floor @100% required >= 0.20 ms; observed 0.433 ms
UnitRender improved at both densities
controlled-work avg improved at both densities
all workload-rate guards passed
```

Therefore H2 is rejected for this workload.

## 5. Root cause / treatment conclusion

E5-3 already established the root attribution:

> **Movement-dependent Cull growth is dominated by first-touch of regenerated derived world-coordinate payload.**

E6 adds the treatment conclusion:

> **Long-lived reuse of pure per-hex derived world geometry materially recovers that Cull cost even when `UnitSpatialRecord` identity remains fresh.**

This demonstrates that the material mechanism is not stable record identity; it is the lifecycle/locality of the derived geometry payload referenced by those records.

## 6. Causal chain

```text
movement commit
  -> fresh UnitSpatialRecord refresh
  -> world_x/world_y/bucket payload regenerated
  -> Cull first touches movement-refreshed derived geometry
  -> movement-dependent Cull cost

E6 treatment
(col,row) stable semantic key
  -> long-lived derived geometry payload
  -> fresh records reference reused geometry
  -> Cull avg -0.201 ms @50%
  -> Cull avg -0.433 ms @100%
  -> UnitRender improves with workload rates preserved
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

E6 also rejects:

- **geometry reuse is not material** — rejected because both preregistered Cull floors passed with preserved workload rates.

## 8. Limits of the evidence

- The treatment uses an attribution-only visited-hex cache and does **not** establish acceptable production ownership/lifetime.
- A positive E6 result justifies a bounded production candidate; it is not production KEEP.
- Only the existing Mac 10K formal workload was used for this causal test.
- P99 remains diagnostic for this mechanism experiment; local Cull/UnitRender metrics and workload-equivalence guards are the causal evidence.
- E6 does not prove that a particular bounded representation will preserve the full attribution-treatment benefit; that requires a new production controlled A/B.

## 9. Raw evidence and integrity

Raw forensic package from formal run:

```text
file: 20260907-203733.zip
sha256: d4f7bab293ced78ab11231fe0e370fe51a257e1cb95b12666340a7a628819bc4
```

Raw profile SHA256 values:

```text
control/50pct-moving/profile.json
  5adf77262ee556fe872cd3d1665b340a4a6d18fd9b2d54492a87560fcec51be8
control/100pct-moving/profile.json
  ec108d107702e961a76717462ddc3daeb59d66e8059f49aa744a13bc51b7647b
treatment/50pct-moving/profile.json
  5fea892fc789b86142de8413904e8530bc8c3f2a4a02c98b53def817d17abdb3
treatment/100pct-moving/profile.json
  95f89a0f8560cbdf632a46ce1b0a5f59732f75529049855291f387394bd521ba
```

The raw package checksum is frozen, but its durable STAR Lab storage/mirror locator is still pending. Per `PROTOCOL.md` v1.2, the scientific attribution is validated while the case remains not fully CLOSED until that raw forensic artifact has stable canonical storage.

- [`manifest.yaml`](manifest.yaml)
- [`decision.md`](decision.md)
