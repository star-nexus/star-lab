# Analysis — UnitRender E1 Active-Animation API

## Validity

Formal same-session order was `A50 -> B50 -> B100 -> A100` using control `17ced8d2...` and treatment `e186135d...`.

- 20 targeted regressions passed in 0.42s.
- All four drivers exited 0.
- All four ENV cleanups exited 0.
- All point guards passed.
- Workload rates were preserved to far inside the preregistered ±2% tolerance.

The result is therefore suitable for a production KEEP/REJECT decision.

## Result

The candidate strongly improves the mixed 50%-moving workload but has essentially no effect at 100%-moving:

```text
50% moving
UnitRender non-cull  6.806 -> 6.191 ms   saving 0.615 ms
controlled avg      24.196 -> 23.586 ms  -2.52%

100% moving
UnitRender non-cull  7.281 -> 7.247 ms   saving 0.034 ms
controlled avg      30.529 -> 30.471 ms  -0.19%
```

The 100% preregistered non-cull saving floor was 0.50 ms/frame. Observed saving was only 0.0338 ms/frame, about 6.8% of the required floor.

## Why the benefit collapses at 100% moving

E1 changes the window classification contract from a generic position API to an active-animation-only API.

For a static unit, treatment can return `None` immediately after checking attack/movement state. It therefore removes the complete static semantic round trip:

```text
generic inner HexPosition lookup
static hex_to_pixel
renderer second HexPosition lookup
renderer base hex_to_pixel
compare/project
```

At 50% moving, roughly half the visible units are static, so this fast-return opportunity is material and production A/B confirms a ~0.615 ms/frame non-cull saving.

At 100% moving, every visible unit has an active movement animation. The active-only API must still perform attack/movement lookup and interpolation, and the renderer must still recover the committed position, compute its base pixel position, and compare displacement. The only material operation eliminated from the movement branch is the generic API's first `HexPosition` lookup.

Production A/B shows that removing that lookup is worth only ~0.034 ms/frame in the full-motion workload.

## Correction to E attribution estimates

The prior E attribution reported a detailed 100%-moving `inner HexPosition` estimate near 1.3 ms/frame. The uninstrumented A/B falsifies interpreting that estimate as removable production cost.

The fine-grained stage probe placed `perf_counter_ns()` around extremely small Python operations. Timer overhead and local perturbation therefore materially inflated those sub-stage estimates. The aggregate attribution was still useful for identifying semantic structure, but the detailed operation-level timings must not be used as production savings estimates.

This is precisely why the methodology requires an uninstrumented controlled A/B before KEEP.

## Interpretation

E1 is a real optimization for static/mixed visibility classification, but it does not solve the current Phase-5 10K full-motion frontier. Retaining it would add a second window animation-position API and compatibility fallback while delivering effectively zero full-motion margin.

Therefore the correct production decision is `DO_NOT_KEEP`.

The separate UnitRender E cull signal remains open: candidate volume stayed essentially constant while cull CPU per candidate increased strongly with movement. That question is not affected by E1 and should be investigated independently as E2.
