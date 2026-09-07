# Analysis — UnitRender E2 Cull Per-Candidate Growth

Run: `20260907-125240`  
ZIP SHA256: `c430277f2f98c39367d10d886654fb07a1181d07bf2fc84ffc88b0d543126b6e`

## What E2 closed

The original signal was that Cull cost rose materially from 0% to 100% moving even though candidate volume was nearly unchanged.

E2 confirms candidate volume is stable:

```text
8920.0 -> 8930.3 candidates/frame
~+0.12%
```

It also rejects branch composition as the explanation. Replaying the 0% operation-unit costs against the 100% branch counts predicts only:

```text
+0.00339 ms/frame
~0.4% closure of the prior +0.798 ms/frame signal
```

Warm bulk operation costs are also nearly stable:

```text
record+bounds      +7.2%
fog hit            +7.3% (50% -> 100%)
fog miss          -26.1%
append              +2.6%
full warm replay    +2.6%
```

So E2 does **not** justify changing the spatial-index representation or the Fog membership representation.

## Important measurement boundary discovered

The bulk replay is executed **after** the production Cull has already traversed the same bucket sets, `by_entity` dictionary, records, and `current_vision` set in that frame.

Therefore it is a deliberately useful *warm-repeat* measurement, but it cannot answer whether the first production traversal is slower after Movement/Vision have just mutated those structures.

This matters because churn is large:

```text
50%:
  index revisions/frame                   270.4
  candidate share in changed buckets       39.8%

100%:
  index revisions/frame                   665.7
  candidate share in changed buckets       71.4%
```

A plausible remaining mechanism is therefore:

```text
Movement / Vision mutation
        ↓
spatial/Fog data becomes first-touch cold for renderer
        ↓
production Cull pays locality / cache penalty
        ↓
E2 replay runs immediately afterward
        ↓
replay sees warmed structures and looks stable
```

This is a hypothesis, not yet a conclusion.

## Instrumented Cull section

The absolute E2 `unit_visible_cull` section values are diagnostic only. E2 adds exact revision/changed-bucket accounting inside `_get_visible_units()`, so they are intentionally not used as production cost estimates.

The earlier moving-path attribution left `_get_visible_units()` untouched, so the original movement-dependent Cull signal remains worth investigating.

## Next experiment

E3 should call the **exact production** `_get_visible_units()` and compare its core time under sparse, read-only prewarming:

```text
baseline  no prewarm
context   resolve index/viewport/singletons only
spatial   context + bucket/by_entity touch
fog       context + current_vision touch
both      spatial + fog
```

The prewarm work itself must be excluded from the core metric. If the original baseline growth does not reproduce, close the signal instead of inventing a candidate.
