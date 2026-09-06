# Phase 5 10K UnitRender E1 — Active-Animation API

**Status:** CLOSED — `DO_NOT_KEEP`  
**Control production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`  
**Rejected treatment:** `e186135dc25d34f51a77218e2105126be3180b3e`

## Trigger

UnitRender E attribution (`20260907-032059`) formally selected `SPECIALIZED_ANIMATION_DISPLACEMENT_API_CANDIDATE_JUSTIFIED`.

The generic render-position contract returns a committed static pixel position even when no animation is active. The window renderer then independently fetches HexPosition and converts it to pixels again to determine whether any displacement exists.

## Candidate

Window AnimationSystem added an active-only query:

```text
attack active        -> attack world-pixel position
movement active      -> movement interpolation
no active animation  -> None
```

The existing generic `get_unit_render_position()` remained unchanged. Cull/Fog was explicitly out of scope.

## Formal closeout

Run:

```text
20260907-034626
A50 -> B50 -> B100 -> A100
```

ZIP SHA256:

```text
df141f6e643b6d251e187bd711c1cb9cb079d7ee621b3dce06211bce9b08a8ea
```

Validity:

```text
20 targeted regressions passed in 0.42s
all driver exits = 0
all cleanup exits = 0
all point guards PASS
```

Results:

```text
50% moving
controlled avg       24.196 -> 23.586 ms  (-2.52%)
UnitRender            8.780 -> 8.161 ms
Cull                  1.974 -> 1.970 ms
UnitRender non-cull   6.806 -> 6.191 ms
saving                0.615 ms   PASS

100% moving
controlled avg       30.529 -> 30.471 ms  (-0.19%)
UnitRender            9.530 -> 9.511 ms
Cull                  2.249 -> 2.264 ms
UnitRender non-cull   7.281 -> 7.247 ms
saving                0.034 ms   FAIL
```

Preregistered 100%-moving non-cull saving floor was `0.50 ms/frame`. The treatment delivered only `0.0338 ms/frame`.

## Why 50% improves but 100% does not

The active-only API is genuinely useful for static units: when no attack or movement animation is active, it returns `None` before the renderer performs the static semantic round trip.

At 50% moving, about half of visible units take that fast return, so the candidate saves ~0.615 ms/frame outside cull.

At 100% moving, every visible unit still needs attack/movement lookup, interpolation, committed-position recovery, base-pixel conversion, and displacement comparison. The treatment only removes the generic API's initial HexPosition lookup from that branch. Production A/B shows that operation is worth only ~0.034 ms/frame.

## Measurement correction

The previous fine-grained E attribution estimated the inner HexPosition stage at a much larger cost. That estimate was instrumentation-inflated because `perf_counter_ns()` was wrapped around extremely short operations. It is useful for structural attribution, not as a removable-production-cost prediction.

The uninstrumented A/B is authoritative.

## Decision

```text
DO_NOT_KEEP
production remains 17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
```

Do not retain a second window animation-position API for a candidate that provides effectively no full-motion frontier margin.

The UnitRender cull signal from E remains separately `NOT_CLOSED` and is the next attribution target.

Raw physical artifact mirroring remains pending.
