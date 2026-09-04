# Analysis — macOS / SDL event-pump tail latency

## Observation

STAR interactive runs on macOS occasionally produced isolated 30–60+ ms long frames during keyboard/mouse activity and, in later validation, even when no events were returned. The event count in these frames is small, so queue volume alone does not explain the stall.

The historical closeout records a representative frame:

```text
frame_ms=62.75
input_event_pump=54.76ms
input_event_get_queue≈0.01ms
input_dispatch≈0.01ms
input_events=1
input_key_down=1
```

A production validation on 2026-09-04 reproduced the same pattern:

```text
frame_ms=48.62
input_event_pump=45.30ms
input_event_get_queue≈0ms
input_dispatch≈0ms
input_events=4
input_key_down=1
fog_toggle_this_frame=1
```

A later capped-60 movement-continuity validation reproduced it again:

```text
frame 2739
frame_ms=76.53
input_event_pump=68.98ms
input_events=2
vision_fog_delta_tiles=0
vision_units_changed=0
```

followed immediately by:

```text
error messaging the mach port for IMKCFRunLoopWakeUpReliable
```

and then:

```text
frame 2828
frame_ms=35.18
input_event_pump=28.50ms
input_events=0
vision_fog_delta_tiles=0
vision_units_changed=0
```

## Hypotheses considered

1. STAR input callbacks / EventBus dispatch were expensive.
2. Python-side Pygame queue draining was expensive because of an event backlog.
3. SDL/Cocoa platform-event pumping was stalling.
4. Coincident Fog or unit-movement work was the dominant cause of an observed hitch.
5. The residual platform tail disappeared once SDL text input was disabled.

## Instrumentation

### Stage 1 — separate queue retrieval from dispatch

Commit `8477aa12de159b153c1cdafc3dbb667ec0f78ffe` changed the previously combined input path into:

```text
pygame.event.get() -> input_event_get
STAR callbacks     -> input_dispatch
```

This allowed a slow frame to distinguish Pygame/SDL work from STAR callback work.

### Stage 2 — remove unnecessary text/IME path

Commit `7cfbecf1d1d5632fe15c60bdd08a26b5723da23d` disabled SDL text input during normal gameplay because STAR gameplay uses physical key events rather than editable text. This removed unnecessary text/IME handling and reduced avoidable platform work.

### Stage 3 — separate SDL pump from queue drain

Commit `ea6cd8d7e97344e957ec1dfa8e589fd742f92ed5` split the remaining Pygame work into:

```text
pygame.event.pump()          -> input_event_pump
pygame.event.get(pump=False) -> input_event_get_queue
STAR EventBus dispatch       -> input_dispatch
```

This preserves input ordering and semantics while identifying the platform pump independently.

## Evidence

The representative historical long frame spent 54.76 ms in `input_event_pump`, while both queue retrieval and STAR dispatch were approximately 0.01 ms. Only one event was returned.

That evidence rejects both the large-backlog hypothesis and the STAR callback hypothesis for this signature.

The first 2026-09-04 production replication independently showed 45.30 ms in `input_event_pump` with queue retrieval and dispatch near zero. A Fog toggle occurred in the same frame, but the slow-frame section breakdown did not attribute the delay to Fog/Vision/Terrain/RenderEngine work.

The later movement-continuity run strengthens the boundary further:

- frame 2739 spent 68.98 ms in `input_event_pump` with no Vision/Fog delta work;
- frame 2828 spent 28.50 ms in `input_event_pump` while `input_events=0` and no Vision/Fog delta work occurred;
- runtime metadata still reported `text_input=False`;
- an `IMKCFRunLoopWakeUpReliable` macOS message appeared adjacent to the worst frame.

The InputMethodKit message is useful contextual evidence, but it is not sufficient to claim that InputMethodKit is the universal root cause. The measured causal boundary remains native platform pumping inside `pygame.event.pump()`.

## Root cause

The observed tail is a macOS + SDL/Pygame platform-event pumping stall inside `pygame.event.pump()` / SDL/Cocoa processing.

This is an attribution conclusion, not a claim that SDL itself is universally defective. The important engineering boundary is that the measured delay occurs before Python queue retrieval and before STAR input callbacks.

## Rejected explanations

### STAR EventBus dispatch

Rejected for this signature because `input_dispatch` remains near zero during captured long frames.

### Large queued-event backlog

Rejected because captured tails occur with very small event counts, and the later frame 2828 returned zero input events while `input_event_pump` still consumed 28.50 ms.

### Fog renderer / Vision / Terrain as the manual-toggle or unit-movement hitch root cause

Rejected when the captured slow frame is pump-dominated and Fog/Vision delta metrics remain zero. The separate `2026-09-unit-movement-continuity` case found and fixed actual STAR movement/presentation discontinuities without reopening this platform case.

### Disabling text input completely eliminates the tail

Rejected by the later capped-60 replication: runtime metadata reported `text_input=False`, yet pump-dominated tails still occurred. The mitigation remains sensible, but residual native platform stalls are still possible.

## Evidence limitations

The original full raw profiler artifact containing the historical 62.75 ms capture was not recovered into STAR Lab. This case is therefore a historical backfill based on:

- the contemporaneous source-side closeout document;
- exact source commits for instrumentation and mitigation;
- preserved representative numeric summaries;
- independent later replications with the same causal signature.

The two later movement-validation logs are not duplicated into this case. Their artifact SHA256 identities and investigation context are recorded in `../2026-09-unit-movement-continuity/manifest.yaml`.

The missing original raw artifact is recorded explicitly rather than reconstructed or guessed.
