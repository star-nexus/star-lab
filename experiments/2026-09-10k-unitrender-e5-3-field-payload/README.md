# Phase 5 10K UnitRender E5-3 — Cull Field-Payload Attribution

**Status:** CLOSED — `WORLD_COORD_PAYLOAD_FIRST_TOUCH_DOMINANT`  
**Experimental base:** `682fdb3a4c64002b402eb74bdda2331ca7123ab4` (E5-1 slotted record; not production-retained)  
**Production remains:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

The UnitRender Cull chain had narrowed to record-field first-touch:

```text
E5   record-field first-touch dominant (~0.498 ms @100%)
E5-1 slots=True beneficial but insufficient (0.113 ms @100%)
E5-2 stable record identity not material (0.044 ms additional @100%)
```

E5-3 decomposed the fields actually consumed by Cull:

```text
lookup   = bucket traversal + by_entity.get only
world    = lookup + world_x/world_y
faction  = world + faction
hex      = faction + col/row
```

Prewarm work was read-only and excluded from the timed core. The exact runtime `_get_visible_units()` remained the timed operation.

## Formal result

Run: `20260907-182654`  
ZIP SHA256: `c34be3a60c970bba514c7d39b44be82447aae93f83d08022f4a5982368502156`

Validation:

```text
10 targeted regressions PASS
3/3 driver exit = 0
3/3 cleanup exit = 0
all guards PASS
8s rolling-window target/coverage satisfied at all densities
100% samples: lookup=10 world=10 faction=10 hex=10
```

Results:

```text
00%:
  baseline 1.505 ms
  lookup   1.350 ms
  world    1.284 ms
  faction  1.279 ms
  hex      1.297 ms
  field effect 0.053 ms
  world_xy    0.066 ms

50%:
  baseline 1.933 ms
  lookup   1.714 ms
  world    1.513 ms
  faction  1.518 ms
  hex      1.461 ms
  field effect 0.253 ms
  world_xy    0.201 ms
  faction    -0.005 ms
  col_row     0.057 ms

100%:
  baseline 2.204 ms
  lookup   2.044 ms
  world    1.669 ms
  faction  1.679 ms
  hex      1.568 ms
  field effect 0.476 ms
  world_xy    0.375 ms
  faction    -0.011 ms
  col_row     0.111 ms
```

At 100% moving, `world_x/world_y` account for approximately `78.8%` of the full field-payload first-touch effect. At 50%, the share is approximately `79.4%`. The same dominant ratio at both movement densities is strong evidence that the signal is structural rather than a sample artifact.

Baseline Cull growth also reproduced:

```text
0% -> 100% = +0.699 ms
candidate count change = +0.14%
```

## Decision

```text
WORLD_COORD_PAYLOAD_FIRST_TOUCH_DOMINANT
```

This is an attribution decision, not a production KEEP decision.

The result rejects `faction` as a meaningful source of the residual record-field effect and places `col/row` as a secondary component. The dominant remaining target is the movement-refreshed derived world-coordinate payload consumed first by Cull's exact bounds test.

## Next stage — E6 Derived World-Geometry Reuse

Do **not** continue this chain as E5-4. E5 is now considered complete: it decomposed spatial first-touch from structure to record fields and finally to the dominant `world_x/world_y` payload. E6 starts a separate treatment stage.

The E6 question is:

> Can Cull reuse or avoid movement-refreshed derived world geometry without changing authoritative `HexPosition` semantics or broadening into a spatial-index rewrite?

The smallest evidence-aligned first candidate is reuse of long-lived per-hex derived geometry:

```text
(col,row)
   -> cached/stable (world_x, world_y, bucket)
   -> UnitSpatialRecord references those stable payload objects
```

This deliberately preserves fresh `UnitSpatialRecord` creation so geometry reuse remains isolated from the E5-2 record-identity hypothesis.

A candidate must be tested against exact production, because the slotted experimental base was rejected for production.

Do not jump to SoA, native code, broad spatial-index redesign, or parallelism before this narrower candidate is tested.

## Methodology lesson

> **连续 negative results 的价值，是把一个“UnitRender moving 时变慢”的模糊问题，收敛成一个具体、可验证、低侵入的 data-representation target。**
