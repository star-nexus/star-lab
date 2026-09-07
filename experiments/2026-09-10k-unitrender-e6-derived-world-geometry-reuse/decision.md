# Decision — Phase 5 10K UnitRender E6 Derived World-Geometry Reuse

## Status

```text
PENDING FORMAL CONTROLLED A/B
```

No production decision has been made.

## Decision question

Does long-lived reuse of pure per-hex derived world geometry:

```text
(world_x, world_y, bucket)
```

materially reduce movement-dependent UnitRender Cull cost when all of the following remain unchanged?

```text
production runtime source
fresh UnitSpatialRecord identity
record dataclass layout
Cull implementation
spatial containers
movement workload
Fog / GC / MiniMap / camera conditions
```

## Preregistered decision rule

Declare:

```text
DERIVED_WORLD_GEOMETRY_REUSE_CANDIDATE_JUSTIFIED
```

only if both 50% and 100% comparisons pass all workload-equivalence guards and:

```text
50% moving:  Cull avg saving >= 0.10 ms
100% moving: Cull avg saving >= 0.20 ms
UnitRender avg improves at both densities
controlled-work avg regression <= 2%
```

Otherwise declare:

```text
DERIVED_WORLD_GEOMETRY_REUSE_NOT_MATERIAL
```

Do not change these thresholds after observing the formal A/B result.

## Production KEEP boundary

Even a positive attribution result is **not** `KEEP`.

The measurement treatment uses an index-local visited-hex geometry cache specifically to isolate reuse. A production candidate must first provide bounded geometry ownership tied to authoritative map/board lifetime (or another demonstrably bounded representation), then pass exact-production controlled A/B and regression validation.

An unbounded visited-coordinate cache must not be retained merely because the attribution experiment is positive.

## Performance Frontier

Do **not** update `records/performance-frontier.md` from this attribution result alone.

A frontier update requires a validated production source state that actually moves or confirms the canonical 10K capability boundary under STAR Lab protocol.

## Revisit conditions

Revisit this decision only if:

- the formal A/B fails source/workload guards and must be rerun;
- new evidence invalidates E5-3 `WORLD_COORD_PAYLOAD_FIRST_TOUCH_DOMINANT`;
- a bounded production representation materially differs from the attribution treatment and requires a new controlled experiment.
