# Phase 5 10K UnitRender Investigation Synthesis

**Status:** CLOSED SYNTHESIS — evidence chain archived  
**Production baseline:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Why this case matters

This case records a performance-engineering result that is easy to undervalue: a long sequence of rejected hypotheses progressively removed the wrong abstraction layers until one narrow, testable data-representation target remained.

The starting symptom was broad:

```text
UnitRender moving-dependent growth ~= +2.8 to +3.0 ms/frame
```

The tempting responses would have been to batch more aggressively, rewrite the spatial index, introduce dense arrays/SoA, or move code native/parallel.

Instead the investigation followed:

```text
Instrument -> Attribute -> Optimize candidate -> Controlled A/B -> Reject/Keep -> Repeat
```

The final causal narrowing was:

```text
moving-dependent UnitRender growth
  -> not duplicate draw / aggregation collapse
  -> classification + Cull
  -> classification optimization not material at 100% moving
  -> Cull not explained by candidate volume
  -> not explained by branch mix
  -> not explained by warm dict/set per-op cost
  -> spatial first-touch confirmed
  -> not caused by MapRender scheduling/eviction
  -> record fields dominate first-touch
  -> by_entity lookup is negligible
  -> slots helps only modestly
  -> stable record identity is not material
  -> world_x/world_y payload dominates residual field first-touch
```

## Investigation ledger

| Step | Hypothesis / question | Formal result | Engineering consequence |
|---|---|---|---|
| Moving-path attribution | animated units may lose static aggregation and duplicate draw | exact raster duplicates only ~0.6% / 1.1%; removable draw ~0.009 / 0.035 ms | reject duplicate-draw redesign |
| E | classification and Cull decomposition | classification +1.949 ms; Cull +0.798 ms from 0%->100% | split the problem |
| E1 | active-animation-only API removes semantic round trip | 50% strong, 100% only ~0.034 ms non-cull saving | reject; static/mixed optimization, not full-motion frontier |
| E2 | Cull growth from candidates/branches/basic lookup cost | candidate +0.1%; branch closure 0.4%; warm replay +2.6% | reject volume/branch/basic-op stories |
| E3 | spatial first-touch locality | spatial prewarm saves 0.468 ms at 100% | confirm first-touch direction; prewarm not a candidate |
| E4 | MapRender evicts spatial working set | pre-Map Cull is slower; second-touch Cull is much faster | reject scheduling/MapRender locality-gap hypothesis |
| E5 | bucket vs by_entity vs record fields | record fields ~0.498 ms dominate; by_entity ~0.021 ms | do not rewrite hash/index indirection |
| E5-1 | dataclass instance layout / __dict__ | slots saves ~0.113 ms Cull at 100%, below KEEP gate | layout is real but insufficient; reject candidate |
| E5-2 | fresh record-container replacement | stable identity adds only ~0.044 ms Cull saving at 100% | reject mutable/in-place record redesign |
| E5-3 | which field payload dominates | world_x/world_y = 0.375 / 0.476 ms full field effect at 100% (~78.8%) | target derived world-coordinate representation only |

## Core outcome

The investigation did **not** retain a new UnitRender production optimization yet. That is not failure.

It removed multiple plausible but incorrect redesign paths:

```text
duplicate draw
animation API as full-motion fix
candidate-volume scaling
Fog/branch composition
by_entity dict lookup
MapRender scheduling
record-container identity churn
```

Each rejection reduced the solution space and prevented unnecessary complexity.

The current target is no longer:

```text
"UnitRender is ~3 ms slower while moving"
```

It is:

```text
movement repeatedly refreshes derived world-coordinate payload;
Cull's first touch of record.world_x / record.world_y dominates the residual field-locality effect.
```

## Methodology lesson

> **Negative results are not dead ends when they eliminate a tempting abstraction layer. A performance campaign succeeds when it converts a broad symptom into a narrow causal target, even before the final KEEP appears.**

STAR-specific phrasing:

> **先消灭错误复杂度，再重构必要复杂度。连续被拒绝的 candidate 不是弯路，而是在购买因果确定性。**

## Next step

E5-4 should test the smallest representation change aligned with E5-3:

```text
long-lived per-hex derived geometry
(col,row) -> stable (world_x, world_y, bucket)
```

Do not jump directly to SoA or native code. The candidate must start from exact retained production and prove real Cull savings in an uninstrumented controlled A/B.
