# Phase 5 10K UnitRender E5-4 — Derived Geometry Reuse Attribution

**Status:** PREREGISTERED — measurement-only treatment, no production source diff  
**Production runtime:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

E5-3 closed with:

```text
WORLD_COORD_PAYLOAD_FIRST_TOUCH_DOMINANT
```

At 100% moving, `world_x/world_y` contributed `0.375 ms` of the `0.476 ms` full field-payload first-touch effect (~78.8%). E5-2 already showed that preserving record-container identity is not material.

## Hypothesis

Pure movement currently recomputes derived geometry every commit:

```text
(col,row)
  -> hex_to_pixel
  -> fresh world_x/world_y payload
  -> fresh bucket tuple
  -> fresh UnitSpatialRecord
```

E5-4 isolates reuse of the **derived per-hex payload** while preserving fresh `UnitSpatialRecord` creation:

```text
first visit to hex:
  compute and retain (world_x, world_y, bucket)

subsequent record construction for same hex:
  reuse the exact cached payload objects
  still construct a new UnitSpatialRecord
```

Thus E5-4 does not test record identity (already rejected by E5-2); it tests whether stable per-hex world-coordinate payload materially reduces Cull first-touch cost.

## Experimental design

A/B both run exact retained production SHA. Treatment injects a startup monkeypatch for `UnitSpatialIndex._record_for_hex()` only.

```text
A = exact production behavior
B = exact production + per-hex derived-geometry cache monkeypatch
order = A50 -> B50 -> B100 -> A100
```

No production file is modified on the branch.

Treatment invariants:

- fresh `UnitSpatialRecord` object still created on cache hit;
- `col`, `row`, `faction`, `world_x`, `world_y`, and `bucket` values are identical to production;
- repeated construction for the same hex reuses identical `world_x`, `world_y`, and `bucket` payload objects;
- different factions at the same hex reuse geometry but keep faction semantics;
- movement/index/Fog/Cull algorithms are unchanged.

## Frozen decision gates

Workload preservation:

```text
position commits/s   within ±2%
vision changed/s     within ±2%
fog delta/s          within ±2%
```

Primary local causal metric:

```text
50%  unit_visible_cull saving >= 0.08 ms/frame
100% unit_visible_cull saving >= 0.15 ms/frame
```

Additional requirements:

```text
UnitRenderSystem avg improves at 100%
controlled avg must not regress >2% at either density
```

Positive attribution:

```text
DERIVED_GEOMETRY_REUSE_CANDIDATE_JUSTIFIED
```

Otherwise:

```text
DERIVED_GEOMETRY_REUSE_NOT_MATERIAL
```

This is still not a production KEEP. A positive result only justifies implementing the smallest runtime candidate on exact production and doing a separate uninstrumented closeout A/B.

## Methodology

> **E5-3 已经把问题收敛到 world-coordinate payload；E5-4 只验证 payload reuse，不扩大到 SoA、mutable record 或 spatial-index 重写。**
