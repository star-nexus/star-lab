# Analysis — macOS / SDL event-pump tail latency

## Observation

STAR interactive runs on macOS occasionally produced isolated 30–60 ms long frames during heavy keyboard/mouse activity. The event count in those frames was small, so queue volume alone did not explain the stall.

The historical closeout records a representative frame:

```text
frame_ms=62.75
input_event_pump=54.76ms
input_event_get_queue≈0.01ms
input_dispatch≈0.01ms
input_events=1
input_key_down=1
```

A later production validation on 2026-09-04 reproduced the same pattern:

```text
frame_ms=48.62
input_event_pump=45.30ms
input_event_get_queue≈0ms
input_dispatch≈0ms
input_events=4
input_key_down=1
fog_toggle_this_frame=1
```

## Hypotheses considered

1. STAR input callbacks / EventBus dispatch were expensive.
2. Python-side Pygame queue draining was expensive because of an event backlog.
3. SDL/Cocoa platform-event pumping was stalling.
4. The coincident Fog toggle was the dominant cause of the observed hitch.

## Instrumentation

### Stage 1 — separate queue retrieval from dispatch

Commit `8477aa12de159b153c1cdafc3dbb667ec0f78ffe` changed the previously combined input path into:

```text
pygame.event.get() -> input_event_get
STAR callbacks     -> input_dispatch
```

This allowed a slow frame to distinguish Pygame/SDL work from STAR callback work.

### Stage 2 — remove unnecessary text/IME path

Commit `7cfbecf1d1d5632fe15c60bdd08a26b5723da23d` disabled SDL text input during normal gameplay because STAR gameplay uses physical key events rather than editable text. This removed the unnecessary macOS InputMethodKit/IME path and reduced stall frequency.

### Stage 3 — separate SDL pump from queue drain

Commit `ea6cd8d7e97344e957ec1dfa8e589fd742f92ed5` split the remaining Pygame work into:

```text
pygame.event.pump()          -> input_event_pump
pygame.event.get(pump=False) -> input_event_get_queue
STAR EventBus dispatch       -> input_dispatch
```

This preserves input ordering and semantics while identifying the platform pump independently.

## Evidence

The representative long frame spent 54.76 ms in `input_event_pump`, while both queue retrieval and STAR dispatch were approximately 0.01 ms. Only one event was returned.

That evidence rejects both the large-backlog hypothesis and the STAR callback hypothesis for this signature.

The 2026-09-04 production replication independently showed 45.30 ms in `input_event_pump` with queue retrieval and dispatch near zero. A Fog toggle occurred in the same frame, but the slow-frame section breakdown did not attribute the delay to Fog/Vision/Terrain/RenderEngine work.

## Root cause

The observed tail is a macOS + SDL/Pygame platform-event pumping stall inside `pygame.event.pump()` / SDL/Cocoa processing.

This is an attribution conclusion, not a claim that SDL itself is universally defective. The important engineering boundary is that the measured delay occurs before Python queue retrieval and before STAR input callbacks.

## Rejected explanations

### STAR EventBus dispatch

Rejected for this signature because `input_dispatch` remains near zero during captured long frames.

### Large queued-event backlog

Rejected for the representative capture because only one event was returned and `input_event_get_queue` remained near zero after the pump was separated.

### Fog renderer / Vision / Terrain as the manual-toggle hitch root cause

Rejected for the 2026-09-04 captured frame because `input_event_pump=45.30ms` dominates the 48.62 ms frame. A future manual Fog-toggle hitch should only be associated with this case when the same attribution signature is present.

## Evidence limitations

The original full raw profiler artifact containing the 62.75 ms capture was not recovered into STAR Lab. This case is therefore a historical backfill based on:

- the contemporaneous source-side closeout document;
- exact source commits for instrumentation and mitigation;
- preserved representative numeric summaries;
- a later production replication with the same causal signature.

The missing original raw artifact is recorded explicitly rather than reconstructed or guessed.
