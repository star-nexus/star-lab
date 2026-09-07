# Phase 5 10K UnitRender E5 — Spatial First-Touch Structure Decomposition

**Status:** RUNNING — preregistered attribution; no production candidate selected  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

E3 established a spatial first-touch locality effect in UnitRender Cull. E4 then rejected the narrower hypothesis that MapRender was the causal eviction boundary:

```text
E4 baseline-late 00% -> 100% growth: +0.735 ms
pre-Map Cull was slower at every density
late-after-early Cull was substantially faster
```

Therefore the next question is not scheduling. It is which layer of the spatial access structure accounts for the first-touch benefit.

Production Cull currently traverses:

```text
by_bucket: Bucket -> Set[entity_id]
                  ↓
            iterate entity_id
                  ↓
by_entity: entity_id -> UnitSpatialRecord
                  ↓
record fields: world_x/world_y/col/row/faction
```

## Measurement design

E5 calls the exact production `_get_visible_units()` function unchanged. Most frames are baseline. Every sixth Cull rotates one read-only cumulative prewarm mode before timing the exact production call:

```text
context
  resolve index / viewport / Fog-view references only

bucket
  context + traverse candidate bucket sets and entity IDs

lookup
  bucket + by_entity.get(entity)

record
  lookup + touch the UnitSpatialRecord fields consumed by Cull
```

Prewarm cost is excluded from the local core metric. The prewarm itself is not a candidate.

This cumulative design estimates the incremental first-touch contribution of:

```text
bucket container      = context_core - bucket_core
by_entity indirection = bucket_core - lookup_core
record object fields  = lookup_core - record_core
```

Aggregate frame latency is diagnostic only.

## Mandatory gates

The original Cull signature must reproduce:

```text
baseline 100% - baseline 0% >= 0.40 ms/frame
```

Sampled candidate count must stay within ±2% from 0% to 100%.

At least 7 samples are required for every mode at every density.

E3's spatial effect must also reproduce at 100%:

```text
context_core - record_core >= 0.25 ms
and >= 12%
```

Otherwise E5 returns `E5_SPATIAL_STRUCTURE_EFFECT_NOT_REPRODUCED` and no representation candidate is selected.

## Dominance rule

A stage is called dominant only if its incremental saving at 100% is both:

```text
>= 0.12 ms
>= 35% of the total context -> record effect
```

Possible decisions:

```text
BUCKET_CONTAINER_FIRST_TOUCH_DOMINANT
BY_ENTITY_INDIRECTION_FIRST_TOUCH_DOMINANT
RECORD_OBJECT_FIRST_TOUCH_DOMINANT
MIXED_SPATIAL_FIRST_TOUCH_STRUCTURE
E5_SPATIAL_STRUCTURE_EFFECT_NOT_REPRODUCED
ORIGINAL_CULL_GROWTH_NOT_REPRODUCED
E5_INCONCLUSIVE_WORKLOAD_SHIFT
E5_INCONCLUSIVE_MEASUREMENT_GUARD
```

Positive attribution is not KEEP. A later representation candidate must still receive semantic regressions and uninstrumented controlled A/B.

## Forbidden during E5

- production Cull changes
- changing `UnitSpatialIndex` representation
- prewarm as an optimization
- native/parallel rewrites
- changing Fog/Vision semantics

## Methodology

> **先把 first-touch 拆到 container / indirection / record 层，再决定是否值得改 spatial representation。**
