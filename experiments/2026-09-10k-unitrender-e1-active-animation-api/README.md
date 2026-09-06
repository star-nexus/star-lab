# Phase 5 10K UnitRender E1 — Active-Animation API

**Status:** RUNNING — candidate implemented; uninstrumented A/B preregistered  
**Control production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`  
**Treatment:** `e186135dc25d34f51a77218e2105126be3180b3e`

## Trigger

UnitRender E attribution (`20260907-032059`) formally selected `SPECIALIZED_ANIMATION_DISPLACEMENT_API_CANDIDATE_JUSTIFIED`.

The generic render-position contract returns a committed static pixel position even when no animation is active. The window renderer then independently fetches HexPosition and converts it to pixels again to determine whether any displacement exists. This semantic round trip is amplified across thousands of visible units per frame.

## Candidate

Window AnimationSystem adds an active-only query:

```text
attack active   -> attack world-pixel position
movement active -> movement interpolation
no active animation -> None
```

The existing generic `get_unit_render_position()` remains unchanged.

The window renderer uses the active-only API when available and retains the existing committed-position epsilon comparison. Generic-only animation systems retain the old fallback path.

## Semantic invariants

Must preserve:

- attack precedence over movement;
- movement interpolation formula;
- zero-displacement epsilon behavior;
- static committed-hex grouping;
- batch and rich render positioning;
- shared/headless generic API behavior.

Cull/Fog is explicitly out of scope. The E attribution cull signal remains separately `NOT_CLOSED`.

## Formal A/B

Order:

```text
A50 -> B50 -> B100 -> A100
```

Primary local metric:

```text
UnitRender non-cull
= UnitRenderSystem inclusive_ms - unit_visible_cull inclusive_ms
```

This isolates the candidate path from the separate unresolved cull signal.

## Preregistered KEEP gates

All point guards must pass. Workload rates must remain within ±2%.

```text
50%  non-cull saving >= 0.30 ms/frame
100% non-cull saving >= 0.50 ms/frame
UnitRender avg improves at both densities
Cull section difference <= 10%
50% controlled avg: no material regression (>2%)
100% controlled avg: must improve
P99: diagnostic only
```

A positive attribution result is not enough; only this uninstrumented same-session A/B can authorize KEEP.
