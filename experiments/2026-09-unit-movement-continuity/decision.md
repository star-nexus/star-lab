# Decision — unit movement continuity misattributed to Fog reveal

## Decision

Close the investigation as a STAR-side movement/presentation correctness case with two accepted fixes:

```text
acc77f8928933dd68f4dc57690d8ae686b06afe1
fix: preserve movement animation continuity

cf779e642c9620ed71bbb0ed713f0f2aa7c6c33d
fix: remove unit animation render dead zones
```

The accepted experiment source is `cf779e6`.

Do **not** continue optimizing the remaining small visual judder unless future evidence shows a material FPS/latency impact or a systematic gameplay-visible regression.

## Why

The investigation established three separate phenomena that initially looked like one Fog-related hitch:

```text
1. Regular boundary stutter
   -> STAR movement time integration defect
   -> fixed

2. Freeze/jump around committed hex centre
   -> STAR renderer animation dead zone
   -> fixed

3. Rare large 30–76 ms hitches
   -> macOS SDL event-pump platform tail
   -> existing CLOSED case
```

Fog reveal was correlated with the first symptom because both occurred at committed hex transitions, but controlled Fog ON/OFF observation showed Fog was not the cause.

## Accepted runtime behavior

STAR will keep:

- epsilon-safe movement segment completion;
- residual movement progress across segment boundaries;
- multi-segment delta consumption;
- zero-dead-zone animation-position semantics in window rich and batch unit rendering;
- existing Fog/Vision incremental behavior unchanged;
- existing `input_event_pump` attribution instrumentation unchanged.

STAR will not:

- add more Fog instrumentation solely to explain this now-rejected causal hypothesis;
- introduce sub-pixel/OpenGL rendering work merely to remove an acceptable residual visual judder without performance evidence;
- reopen movement/Fog when a slow frame is already explained by the closed macOS SDL platform-tail signature.

## Performance acceptance

The accepted fix showed no material cost in the tested 15-unit capped-60 workload:

- `AnimationSystem` remained approximately 0.01–0.02 ms;
- `UnitRenderSystem` remained sub-millisecond;
- Fog patch work remained approximately 0.00–0.02 ms when active;
- steady window p99 remained around the high-17 ms range.

Therefore the movement continuity fixes are accepted on performance grounds for this workload.

## Productionization requirement

This archive closes the investigation, not the production merge.

Before deleting `perf/unit-fog-reveal-tail`, production integration must preserve the accepted source delta from `cf779e642c9620ed71bbb0ed713f0f2aa7c6c33d` and rerun the ordinary release gates, including at least:

```text
focused movement/render regression tests
full pytest suite
compileall
git diff --check
interactive capped-60 smoke
```

No CI status or local pytest transcript for `cf779e6` is part of this archive, so this case must not be cited as proof that the production release gate already passed.

## Cross-case decision for rare large hitches

The final Fog-ON validation reproduced the known macOS/SDL signature:

```text
frame 2739: 76.53 ms total, 68.98 ms input_event_pump
frame 2828: 35.18 ms total, 28.50 ms input_event_pump
```

Both had zero Fog/Vision delta work; frame 2828 also returned zero input events. The first was adjacent to an `IMKCFRunLoopWakeUpReliable` macOS message.

These observations reinforce `2026-09-macos-sdl-event-pump-stall` and do not reopen it. That platform case remains monitor-only unless its documented reopen conditions are met.

## Reopen this movement case only if

1. comparable capped-60 movement again shows a systematic pause at every committed hex boundary;
2. a future change removes overshoot preservation or reintroduces animation-position dead zones;
3. `AnimationSystem` or `UnitRenderSystem` becomes a material frame-time contributor;
4. Fog ON becomes causally slower than Fog OFF with substantial Fog/Vision timing;
5. residual visual judder becomes product-significant enough to justify changing the rendering model.

## Final classification

```text
Original label:
Unit-driven Fog reveal hitch

Final classification:
Fog correlation rejected
+ movement temporal discontinuity fixed
+ renderer animation dead zone fixed
+ residual pixel/frame presentation judder accepted
+ rare macOS/SDL platform tail cross-referenced

Status:
CLOSED — investigation complete; production integration pending
```
