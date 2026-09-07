# Decision — Phase 5 UnitRender E3

## Formal decision

```text
SPATIAL_FIRST_TOUCH_LOCALITY_CANDIDATE_JUSTIFIED
```

E3 is CLOSED as an attribution case.

## Why

All guards passed and the mandatory original-signature reproduction gate passed:

```text
baseline Cull core 00% -> 100%: +0.732 ms
candidate count change: +0.12%
```

At 100% moving, spatial prewarm reduced the exact production Cull core by:

```text
2.372 -> 1.904 ms relative to context
saving = 0.468 ms / 19.7%
```

which exceeds the preregistered single-mode threshold (`>=0.20 ms` and `>=10%`). The effect also grows monotonically from 0% to 50% to 100% moving.

## What is NOT authorized

Do not add a production prewarm pass. The prewarm itself costs more than the Cull saving and exists only as a causal probe.

Do not yet change:

- `UnitSpatialIndex` representation;
- Fog semantics or representation;
- movement semantics;
- native/parallel implementation.

## Next attribution priority

Before any spatial-container redesign, test the lower-blast-radius scheduling hypothesis:

```text
Cull before MapRender
vs
Cull at its normal post-MapRender location
```

If exact production Cull is materially faster before MapRender and the visible-unit result is identical within the frame, then an early frame-local Cull cache is the preferred candidate class.

If not, return to spatial working-set decomposition.

## Production

Production remains exactly:

```text
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
```
