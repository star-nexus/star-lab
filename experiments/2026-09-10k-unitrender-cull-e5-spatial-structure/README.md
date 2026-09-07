# Phase 5 10K UnitRender E5 — Spatial First-Touch Structure Decomposition

**Status:** CLOSED — `RECORD_OBJECT_FIRST_TOUCH_DOMINANT`  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Question

E3 established a spatial first-touch locality effect in UnitRender Cull. E4 rejected MapRender as the causal eviction boundary. E5 decomposed the spatial working set cumulatively:

```text
context -> bucket containers -> by_entity lookup -> record fields
```

The exact production `_get_visible_units()` remained the timed operation. All prewarm work was read-only, excluded from the local core metric, and never considered a production optimization.

## Frozen attribution rules

The original Cull growth had to reproduce:

```text
baseline 100% - baseline 0% >= 0.40 ms/frame
candidate count change <= ±2%
>= 7 samples for every mode at every density
```

The full spatial first-touch effect at 100% had to satisfy:

```text
context_core - record_core >= 0.25 ms
and >= 12%
```

A stage was dominant only if it contributed both:

```text
>= 0.12 ms
>= 35% of the full context -> record effect
```

## Earlier attempts

Attempt 1 (`20260907-143507`) and Attempt 2 (`20260907-154710`) both returned `E5_INCONCLUSIVE_MEASUREMENT_GUARD` because the original 5-second rolling profiler window retained only ~6–7 samples/mode at the 100% point.

Despite being formally inconclusive, both attempts independently pointed to record fields:

```text
Attempt 1 record_fields @100% = 0.480292 ms
Attempt 2 record_fields @100% = 0.481857 ms
```

A duration-only retry could not fix the sample budget because only the final 5-second rolling window was retained. The measurement design was therefore corrected without changing probe cadence: profiler horizon `5s -> 8s`, `PREWARM_PERIOD=6` unchanged. The first corrected attempt was aborted because `sample_after=7s` no longer aged startup work outside an 8-second rolling window. The runner was fixed to restore the original 2-second aging margin:

```text
profile window = 8s
sample_after   = 10s
```

That aborted attempt produced no valid attribution result.

## Formal run — `20260907-163736`

Artifact SHA256:

```text
02755e116f83653dd2c845735c7f94ed2a7318b3dc5b517d1ec376f28f0f50a7
```

Validation:

```text
runtime SHA exact:       PASS
scenario SHA exact:      PASS
9 targeted regressions:  PASS
3/3 driver exit:         0
3/3 cleanup exit:        0
all workload guards:     PASS
profile horizon:         8s at all three densities
sample guard:            PASS
```

Retained profile windows:

```text
00%:  coverage 8.010s, 440 frames
50%:  coverage 8.008s, 292 frames
100%: coverage 8.028s, 238 frames
```

Mode samples:

```text
             baseline context bucket lookup record
00%             367      18     19     18     18
50%             243      12     12     12     13
100%            198      10     10     10     10
```

### Formal 100% decomposition

```text
baseline core          2.339 ms
context core           2.388 ms
bucket core            2.150 ms
lookup core            2.129 ms
record core            1.631 ms

full spatial effect    0.757 ms
bucket container       0.238 ms   31.5%
by_entity lookup       0.021 ms    2.8%
record fields          0.498 ms   65.8%
```

The original movement-dependent Cull signature reproduced:

```text
baseline 00% -> 100% growth = +0.728 ms
candidate change              = +0.12%
```

The record-mode distribution was also strongly separated from lookup at 100%:

```text
lookup: min 2.035 / p50 2.127 / max 2.259 ms
record: min 1.536 / p50 1.636 / max 1.754 ms
```

`record max < lookup min`, so the dominant result is not caused by a few lucky samples.

## Replication across three attempts

```text
                           Attempt 1   Attempt 2   Formal
full spatial @100%           0.666       0.678       0.757 ms
by_entity lookup             0.023       0.019       0.021 ms
record fields                0.480       0.482       0.498 ms
```

The three record-field estimates span only ~0.017 ms. This is the most stable component of the decomposition.

## Decision

```text
RECORD_OBJECT_FIRST_TOUCH_DOMINANT
```

Interpretation boundary:

- This does **not** mean prewarming records is an optimization. Record prewarm itself costs far more than the Cull time it saves.
- This does **not** establish that `by_entity` hashing is expensive; E5 measured only ~0.021 ms attributable to that indirection at 100%.
- The evidence points to the storage/access layout after obtaining `UnitSpatialRecord`: repeated first access to Python record fields is the dominant locality penalty.

Current production `UnitSpatialRecord` is a frozen dataclass without slots. Movement creates a new record on every committed position update, while Cull reads `world_x`, `world_y`, `faction`, `col`, and `row` for thousands of candidates per frame.

## Next candidate

The lowest-blast-radius candidate is **E5-1: slotted UnitSpatialRecord**:

```python
@dataclass(frozen=True, slots=True)
class UnitSpatialRecord:
    ...
```

Rationale: remove the per-instance `__dict__` and store fields directly in slots while preserving the same fields, equality semantics, immutability, `by_entity`, `by_bucket`, movement semantics, Fog semantics, and Cull algorithm.

Do not jump directly to SoA arrays, custom hash tables, bucket-direct records, native code, or parallelism until this minimal representation treatment receives semantic regressions and an uninstrumented controlled A/B.

## Methodology

> **先验证最小 representation treatment 是否能把稳定的 record-field first-touch signal 转成真实 production saving；不要因为 attribution 指向 memory locality 就直接重写整个 spatial index。**
