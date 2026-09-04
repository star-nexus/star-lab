# Analysis — unit movement continuity misattributed to Fog reveal

## Observation

The initial user-visible symptom was a small hitch while a moving unit crossed the Fog boundary. Because Fog reveal is triggered when authoritative `HexPosition` changes, the visual timing made Fog work look causal.

Initial profiler runs did not support that interpretation. Fog/Vision work remained very small, while captured >=30 ms slow frames were dominated by unrelated platform sections such as `input_event_pump` or `display_present`.

The investigation therefore separated two questions:

1. Is the regular micro-stutter caused by Fog reveal work?
2. Are occasional large frame-time tails caused by the same mechanism?

## Hypotheses

### H1 — Fog/Vision incremental reveal is expensive

A unit commits a new hex, Vision becomes dirty, the Fog journal changes, and the incremental Fog presenter patches the surface. The initial visual correlation suggested this chain might cause the hitch.

### H2 — movement animation loses temporal continuity at hex segment boundaries

The movement integrator might discard elapsed time or repeat endpoint presentation when transitioning between segments.

### H3 — renderer presentation suppresses small interpolated motion

Even if animation state is continuous, the renderer might collapse small offsets back to the committed hex position.

### H4 — remaining large hitches are independent platform tails

The already-known macOS SDL event-pump issue could occasionally overlap movement and be perceived as a movement/Fog hitch.

## Controlled Fog A/B

The decisive first experiment was visual rather than aggregate-FPS based:

```text
Fog ON  -> micro-stutter visible when crossing hex boundaries
Fog OFF -> the same micro-stutter remains
```

The workload stayed capped at 60 Hz on the 15×15 `river_split` scenario. This rejects Fog reveal as a necessary cause of the regular movement discontinuity.

The result also explains the misleading correlation:

```text
                 committed hex transition
                 /                    \
                /                      \
       movement presentation        Vision/Fog update
                |                      |
          visible stutter           Fog edge changes
```

The two effects shared the same semantic boundary but one did not cause the other.

## Root cause 1 — movement segment time loss

At the problem baseline, movement progression effectively followed:

```python
anim.progress += anim.speed * delta_time
if anim.progress >= 1.0:
    commit_hex_position(...)
    anim.current_target_index += 1
    anim.progress = 0.0
```

This contains two continuity defects.

### Overshoot was discarded

If a frame advances from `0.98` to `1.02`, the old code resets to `0.0` instead of carrying `0.02` into the next segment. Elapsed movement time disappears at every boundary.

### Exact 60 Hz boundary was vulnerable to floating-point representation

At the default `2.0 tiles/s` and fixed `1/60 s` step, the theoretical segment increment is `1/30`. Repeated floating-point accumulation can produce:

```text
tick 30 -> 0.9999999999999999
```

which is still `< 1.0`, delaying the authoritative transition until tick 31 and producing a repeated-looking endpoint.

### Stage-1 fix

Commit:

```text
acc77f8928933dd68f4dc57690d8ae686b06afe1
fix: preserve movement animation continuity
```

changed the model to:

- use a tiny epsilon only for exact-boundary floating-point error;
- subtract complete segments rather than resetting progress;
- preserve fractional overshoot;
- use a loop so a large delta can consume multiple complete segments.

Human validation reported a clear improvement in continuity but still found residual non-uniform judder.

## Root cause 2 — renderer animation dead zones

Further inspection found an independent presentation discontinuity.

The rich unit-render path only used animation coordinates when the interpolated position was more than 5 world pixels from the authoritative hex centre. The batch path used a 1-pixel threshold.

At `HEX_SIZE=50` in flat-top geometry, adjacent hex centres are about 86.6 world pixels apart. At 2 tiles/s and 60 Hz the visual displacement is only about:

```text
86.6 / 30 ~= 2.89 world pixels per frame
```

Therefore the rich path could do this immediately after a commit:

```text
frame N     committed centre
frame N+1   animation offset ~2.89 px -> suppressed by <=5 px gate
frame N+2   animation offset ~5.77 px -> suddenly accepted
```

That produces a visible freeze-then-jump even though the underlying animation state is continuous.

### Stage-2 fix

Commit:

```text
cf779e642c9620ed71bbb0ed713f0f2aa7c6c33d
fix: remove unit animation render dead zones
```

made the window rich and batch paths use any real non-zero animation displacement, with only an extremely small numerical epsilon distinguishing true static position from interpolation.

Human validation after this change reported:

- most movement is now smooth;
- the systematic boundary discontinuity is materially improved;
- a small, non-uniform residual judder remains visible on close inspection;
- the remaining animation quality is acceptable.

The user also reported that the archer appeared more visibly juddery than cavalry. No unit-type-specific movement-animation speed difference was found in the source (`MovementAnimation.speed` is the same default), so this subjective difference was not promoted to a causal performance conclusion. Sprite shape, direction and integer-pixel rasterization remain plausible perceptual factors.

## Performance evidence after the fixes

The important question after visual acceptance was whether the fixes themselves harm FPS or runtime latency.

Representative steady-state capped-60 windows remained healthy.

### Fog OFF

Approximately:

```text
frame p99            17.65–17.84 ms
AnimationSystem       0.01–0.02 ms
UnitRenderSystem      0.16–0.22 ms
```

### Fog ON

Approximately:

```text
frame p99            17.60–17.81 ms
AnimationSystem       0.01–0.02 ms
UnitRenderSystem      0.08–0.13 ms
fog_surface_patch     0.00–0.02 ms
```

These measurements do not support a claim that the accepted movement fixes create a meaningful performance regression in the tested 15-unit workload.

## Residual large hitches — cross-case attribution

The final Fog-ON validation contained two particularly useful slow frames.

### Frame 2739

```text
frame_ms=76.53
input_event_pump=68.98 ms
vision_fog_delta_tiles=0
vision_units_changed=0
```

The log was immediately followed by:

```text
error messaging the mach port for IMKCFRunLoopWakeUpReliable
```

### Frame 2828

```text
frame_ms=35.18
input_event_pump=28.50 ms
input_events=0
vision_fog_delta_tiles=0
vision_units_changed=0
```

These match the already-closed `2026-09-macos-sdl-event-pump-stall` signature: the long frame is dominated by native event pumping, while STAR movement/Fog/Vision work is negligible.

A Fog-OFF validation also captured a 30.92 ms frame dominated by `input_event_pump=26.17 ms` during the Fog-toggle input frame, again with no Vision/Fog delta work.

Therefore occasional large hitches are not evidence that the movement fixes or Fog renderer remain pathological.

## Rejected explanations

### Fog reveal is the cause of the regular movement stutter

Rejected by controlled Fog ON/OFF visual A/B and by negligible Fog/Vision timing.

### The remaining accepted micro-judder is a major CPU bottleneck

Not supported. `AnimationSystem` and `UnitRenderSystem` remain sub-millisecond and typically tens/hundreds of microseconds in this workload.

### Every occasional large hitch should reopen the movement case

Rejected when attribution matches the existing macOS SDL platform-tail case or a separate display-present tail. Slow-frame classification must follow measured subsystem attribution rather than visual coincidence.

## Remaining uncertainty

Small non-uniform visual judder can remain because final Pygame presentation quantizes interpolated float positions to integer pixel coordinates and the runtime presents at capped 60 Hz. That residual was not optimized because:

1. the user judged continuity acceptable;
2. current evidence does not show a material FPS/latency cost;
3. eliminating pixel-level judder could require a different rendering model with disproportionate engineering cost.

This is an accepted presentation limit, not an unresolved performance blocker.

## Evidence limitations

The two final validation logs were supplied during the investigation but were not committed byte-for-byte into STAR Lab through the available repository connector. Their SHA256 identities are preserved in `manifest.yaml` and `README.md` so a future recovered copy can be verified.

GitHub exposes no CI status for `cf779e6`, and no local pytest transcript was archived. Regression test source is present at the exact fix SHAs, but production integration must rerun the release regression gate.
