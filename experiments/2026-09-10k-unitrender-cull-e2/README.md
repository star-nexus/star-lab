# Phase 5 10K UnitRender E2 — Cull Per-Candidate Growth Attribution

**Status:** CLOSED — `CULL_REQUIRES_FURTHER_ATTRIBUTION`  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`  
**Run:** `20260907-125240`  
**ZIP SHA256:** `c430277f2f98c39367d10d886654fb07a1181d07bf2fc84ffc88b0d543126b6e`

## Result

E2 tested whether the movement-dependent Cull growth came from candidate volume, branch composition, or same-stage warm operation-cost inflation.

It closed all three simple explanations.

```text
candidates/frame
00%   8920.0
100%  8930.3
change ~+0.12%

branch-mix modeled delta
+0.00339 ms/frame
~0.4% closure of prior +0.798 ms/frame

warm bulk unit-cost growth
record+bounds    +7.2%
fog hit          +7.3% (50% -> 100%)
fog miss        -26.1%
append            +2.6%
full replay       +2.6%
```

Therefore E2 does **not** justify changing the spatial-index representation or Fog membership representation.

## Important remaining gap

The bulk replay happens after the production Cull has already traversed the same data in that frame. It is therefore a **warm repeated-access** measurement.

Meanwhile movement churn is substantial:

```text
50% moving:
  index revisions/frame                270.4
  candidates in changed buckets         39.8%

100% moving:
  index revisions/frame                665.7
  candidates in changed buckets         71.4%
```

So E2 cannot rule out this remaining mechanism:

```text
same-frame Movement / Vision mutation
        ↓
first production Cull touches cold / recently rewritten data
        ↓
first pass is expensive
        ↓
E2 replay immediately repeats the same traversal
        ↓
second pass is warm and looks stable
```

This is only a hypothesis.

## Decision

```text
CULL_REQUIRES_FURTHER_ATTRIBUTION
production unchanged
```

Rejected explanations:

- candidate-volume growth;
- branch-mix growth;
- material warm spatial-access inflation;
- material warm Fog-membership inflation.

## Next

Proceed to:

```text
UnitRender E3 — Cull first-touch locality attribution
```

E3 must call the exact production `_get_visible_units()` and compare its core time under sparse, read-only prewarming of context, spatial state, Fog state, and both. It must first require the original baseline Cull growth to reproduce; otherwise the Cull signature should be closed instead of optimized.

Raw artifact mirroring remains pending.
