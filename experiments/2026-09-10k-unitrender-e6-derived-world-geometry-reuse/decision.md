# Decision — Phase 5 10K UnitRender E6 Derived World-Geometry Reuse

## Status

```text
VALIDATED ATTRIBUTION
DERIVED_WORLD_GEOMETRY_REUSE_CANDIDATE_JUSTIFIED
```

The scientific treatment decision is complete. The case is **not yet fully CLOSED** only because the raw forensic ZIP still needs a stable canonical STAR Lab storage/mirror locator under `PROTOCOL.md` v1.2.

No production KEEP has been made.

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

These thresholds were frozen before the formal A/B result.

## Formal result

Run:

```text
20260907-203733
```

Observed:

```text
50% moving
  Cull:       2.076 -> 1.875 ms  saving 0.201 ms
  UnitRender: 9.268 -> 9.134 ms  saving 0.134 ms
  controlled avg: -0.57%
  position rate drift: +0.733%
  Vision rate drift:   +0.447%
  Fog delta drift:     +0.693%
  checks: PASS

100% moving
  Cull:       2.404 -> 1.971 ms  saving 0.433 ms
  UnitRender: 10.242 -> 10.026 ms saving 0.217 ms
  controlled avg: -1.50%
  position rate drift: -0.109%
  Vision rate drift:   -0.054%
  Fog delta drift:     +0.319%
  checks: PASS
```

All preregistered gates passed.

Decision:

```text
DERIVED_WORLD_GEOMETRY_REUSE_CANDIDATE_JUSTIFIED
```

## Engineering interpretation

E5-2 already showed that stable `UnitSpatialRecord` identity is not material. E6 kept record identity fresh and changed only the lifetime/reuse of pure per-hex derived geometry.

Therefore the next production hypothesis is not:

```text
reuse records
```

but:

```text
provide bounded, long-lived derived world geometry
```

The preferred design space should stay as narrow as possible around that conclusion.

## Production KEEP boundary

This positive attribution result is **not** `KEEP`.

The measurement treatment uses an index-local visited-hex geometry cache specifically to isolate reuse. A production candidate must provide bounded geometry ownership tied to authoritative map/board lifetime, or another demonstrably bounded representation, then pass exact-production controlled A/B and regression validation.

An unbounded visited-coordinate cache must not be retained merely because the attribution experiment is positive.

Required next validation:

```text
bounded production geometry owner
  -> exact production-derived experiment branch
  -> semantic/regression tests
  -> controlled A/B vs 17ced8d2...
  -> verify Cull / UnitRender recovery
  -> re-check 10K canonical 30 Hz gate
```

## Artifact policy

This case adopts the `PROTOCOL.md` v1.2 two-tier artifact rule:

```text
Compact Evidence Package = default review / Agent / LLM artifact
Raw Forensic Package      = authoritative low-level audit substrate
```

Formal raw artifact checksum:

```text
d4f7bab293ced78ab11231fe0e370fe51a257e1cb95b12666340a7a628819bc4
```

The raw artifact must remain available independently of compact evidence.

## Performance Frontier

Do **not** update `records/performance-frontier.md` from E6 attribution alone.

A frontier update requires a validated production source state that actually moves or confirms the canonical 10K capability boundary under STAR Lab protocol.

## Revisit conditions

Revisit this decision only if:

- new evidence invalidates E5-3 `WORLD_COORD_PAYLOAD_FIRST_TOUCH_DOMINANT`;
- a bounded production representation materially differs from the E6 treatment and fails to reproduce its benefit;
- workload structure changes so per-hex derived geometry reuse behavior is materially different;
- raw forensic re-audit finds a source/workload guard violation in the formal run.
