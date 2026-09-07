# Phase 5 10K UnitRender E5-1 — Slotted UnitSpatialRecord

**Status:** RUNNING — candidate implemented; formal A/B preregistered  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

E5 closed with:

```text
RECORD_OBJECT_FIRST_TOUCH_DOMINANT
```

Formal 100% moving decomposition:

```text
full spatial first-touch effect  0.757 ms
bucket container                 0.238 ms
by_entity lookup                 0.021 ms
record fields                    0.498 ms
```

The record-field contribution was also directionally replicated in the two prior inconclusive E5 attempts at approximately `0.480 ms` and `0.482 ms`.

Production `UnitSpatialRecord` is a frozen dataclass whose fields are read repeatedly by UnitRender Cull. E5-1 tests the smallest representation change that removes per-instance attribute dictionaries without changing index semantics:

```python
@dataclass(frozen=True)
```

becomes:

```python
@dataclass(frozen=True, slots=True)
```

## Candidate boundary

No field, algorithm, or API semantics change.

Unchanged:

- record fields and constructor order
- frozen/value equality semantics
- `by_entity`, `by_bucket`, `by_cell`, and revisions
- movement commit semantics
- Cull bounds/Fog logic
- Vision and occupancy behavior

The candidate branch includes one layout contract test asserting no instance `__dict__`, preserved value equality/field reads, and frozen behavior.

## Formal A/B

```text
A = 17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
B = 682fdb3a4c64002b402eb74bdda2331ca7123ab4
order = A50 -> B50 -> B100 -> A100
```

Canonical workload remains unchanged: 10K resident units, seed/phase-seed 42, 12-step staggered routes, Fog ON, realtime_defer GC, MiniMap dynamic units OFF, uncapped render, hub offline.

Aggregate P99 is diagnostic only.

## Frozen KEEP gates

Workload preservation:

```text
position commits/s   within ±2%
vision changed/s     within ±2%
fog delta/s          within ±2%
```

Primary local causal metric:

```text
50%  unit_visible_cull saving >= 0.10 ms/frame
100% unit_visible_cull saving >= 0.20 ms/frame
```

Additional requirements:

```text
UnitRenderSystem avg improves at both densities
50% controlled avg does not materially regress (>2%)
100% controlled avg improves
```

If all pass:

```text
CAUSALLY_CONFIRMED_KEEP
```

Otherwise:

```text
DO_NOT_KEEP
```

A positive E5 attribution does not override this A/B gate. If slots produces only negligible production savings, E5-1 is rejected and the next hypothesis may examine fresh-record churn/in-place or tighter read representation.

## Interpretation boundary

Do not expect the full E5 `~0.5 ms` record-field prewarm effect to map one-for-one to `slots=True`. E5 warmed the complete record/object working set, whereas slots only changes Python object/attribute layout.

## Methodology

> **先试最小对象布局修正；拿不到真实 production margin，就不为漂亮的 attribution 强留 candidate。**
