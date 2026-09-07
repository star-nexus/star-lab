# Phase 5 10K UnitRender E5-1 — Slotted UnitSpatialRecord

**Status:** CLOSED — `DO_NOT_KEEP`  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`  
**Candidate:** `682fdb3a4c64002b402eb74bdda2331ca7123ab4`

## Trigger

E5 closed with `RECORD_OBJECT_FIRST_TOUCH_DOMINANT`. Formal 100% moving decomposition was:

```text
full spatial first-touch effect  0.757 ms
bucket container                 0.238 ms
by_entity lookup                 0.021 ms
record fields                    0.498 ms
```

E5-1 tested the smallest record-layout change:

```python
@dataclass(frozen=True)
→
@dataclass(frozen=True, slots=True)
```

No Cull, movement, Fog, Vision, or spatial-container semantics changed.

## Formal A/B

```text
run: 20260907-173504
A = 17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
B = 682fdb3a4c64002b402eb74bdda2331ca7123ab4
order = A50 -> B50 -> B100 -> A100
ZIP SHA256 = 355f8877de1e0230b1e62b88f39e72b114df9cbd7d609a966e1b2bab1424d353
```

Validity:

```text
16 targeted regressions PASS
4/4 driver exit = 0
4/4 cleanup exit = 0
all density-point guards PASS
```

### 50% moving

```text
controlled avg   24.385 -> 24.376 ms  (-0.03%)
Cull avg          1.975 -> 1.885 ms   saving 0.090 ms (-4.57%)
Cull p95          2.114 -> 2.011 ms   saving 0.103 ms
Cull p99          2.156 -> 2.050 ms   saving 0.107 ms
UnitRender avg    8.846 -> 8.804 ms   saving 0.042 ms
Animation avg     3.222 -> 3.317 ms   treatment +0.095 ms
```

The frozen Cull gate was `>= 0.10 ms`; observed saving was `0.090 ms`, so this point failed.

### 100% moving

```text
controlled avg   30.913 -> 30.472 ms  (-1.43%)
controlled p99   32.581 -> 32.127 ms
Cull avg          2.280 -> 2.167 ms   saving 0.113 ms (-4.95%)
Cull p95          2.408 -> 2.300 ms   saving 0.108 ms
Cull p99          2.464 -> 2.384 ms   saving 0.080 ms
UnitRender avg    9.599 -> 9.429 ms   saving 0.170 ms
Animation avg     6.845 -> 6.712 ms   saving 0.133 ms
```

The frozen Cull gate was `>= 0.20 ms`; observed saving was `0.113 ms`, so this point failed.

Workload rates were preserved within far less than the preregistered ±2% tolerance.

## Decision

```text
DO_NOT_KEEP
```

`slots=True` is **causally beneficial but insufficient**. The Cull improvement is consistent across mean and tail and is approximately 5% at both densities, so the record-layout hypothesis was directionally correct. It simply does not recover enough margin to justify retention under the frozen gate.

Relative to E5's record-field first-touch magnitude, slots recovered only approximately:

```text
50%:  0.090 / 0.343 ≈ 26%
100%: 0.113 / 0.498 ≈ 23%
```

These ratios are interpretation aids, not additive cost accounting, because E5 prewarm and E5-1 treatment are different interventions.

## Next hypothesis

The remaining record-side cost is more consistent with **fresh-record replacement / object-working-set churn** than with `by_entity` lookup or `__dict__` alone. Production `move_entity()` creates a new `UnitSpatialRecord` on every committed move and replaces `by_entity[entity]`.

Next research should isolate that replacement mechanism before considering SoA or custom containers. A clean design is to compare a slotted fresh-record baseline against a slotted stable-identity/in-place-update treatment while preserving externally frozen semantics, then only compare a successful combined treatment against production.

## Methodology

> **有效但不足也要拒绝；局部因果收益过不了冻结门槛，就不合入 production。**
