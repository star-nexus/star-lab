# Analysis — UnitRender E

Run `20260907-032059` is valid for attribution. Exact production runtime and scenario guards match; 14 targeted regressions passed; all point guards, driver exits, and cleanup exits passed.

## Classification result

Classification grows from `3.004` to `4.953 ms/frame` (`+1.949 ms/frame`) between 0% and 100% moving. At 100%, the renderer helper is estimated at `5.206 ms/frame`, comfortably above the preregistered materiality threshold.

The generic path contains a semantic round trip:

```text
get_unit_render_position(entity)
  -> HexPosition
  -> AttackAnimation
  -> MovementAnimation
  -> static hex_to_pixel or interpolation
renderer
  -> HexPosition again
  -> committed hex_to_pixel again
  -> compare displacement
```

At 0% moving, the generic API computes a static world-pixel position for every visible entity even though the batch renderer ultimately needs only the committed HexPosition for grouping. The renderer then recomputes that static pixel position to discover there was no animation displacement.

At 100% moving, the path remains material; the detailed sample estimates `inner HexPosition get ~=1.300 ms/frame` before the renderer performs its own position lookup. This is a high-multiplicity abstraction cost, not animation simulation cost.

The preregistered specialized-API gates all pass:

- classification growth >= 1.00 ms/frame: PASS (`1.949`)
- 100% helper estimated cost >= 1.50 ms/frame: PASS (`5.206`)
- conservative directly redundant work >= 0.25 ms/frame at any point: PASS (`1.375 / 1.037 / 0.379`)

Therefore exactly one candidate is justified: an active-animation-only position API for the window batch renderer. This attribution does **not** justify changing movement interpolation, attack precedence, animation state, or render equivalence.

## Cull result

Cull growth is `+0.798 ms/frame`, but candidate count is essentially unchanged:

```text
8920.0 -> 8930.4 candidates/frame
ratio = 1.00116
```

Candidate-volume closure is only `0.25%`, while cost per candidate rises:

```text
0.192 -> 0.281 us/candidate
+46.3%
```

Thus `CULL_VOLUME_EXPLAINS_GROWTH` is rejected. The current experiment does not identify the cause of the per-candidate rise. Branch mix changes substantially (Fog rejects fall, visible accepts rise), so this signal must remain a separate attribution problem; it must not be folded into the animation candidate.

## Diagnostic field issue

The analyzer emitted `controlled avg/p99 = 0` for this run because it did not resolve the current controlled-work field shape. Aggregate frame latency was preregistered diagnostic-only, so this does not affect the local attribution result. Any production A/B tooling must correct this field extraction before closeout.

## Interpretation

The strongest result is not "animation drawing is expensive". It is:

> **The generic render-position abstraction performs work needed by the general API contract, then the batch renderer independently reconstructs committed-position semantics to determine whether that work represented an actual displacement.**

This is a semantic round trip amplified by thousands of visible entities per frame.
