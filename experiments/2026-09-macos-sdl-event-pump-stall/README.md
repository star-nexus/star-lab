# macOS / SDL event-pump tail latency

**Status:** CLOSED — known platform limitation / historical backfill  
**Scope:** macOS interactive Pygame window only

## Conclusion

Rare 30–60 ms interactive long frames were isolated to `pygame.event.pump()` / SDL/Cocoa platform-event pumping. Python-side queue retrieval and STAR `EventBus` dispatch remain negligible in the representative captures. This is not a STAR simulation, renderer, pathfinding, agent, or input-dispatch bottleneck.

STAR already applies the practical mitigation: normal gameplay disables SDL text input / IME with `pygame.key.stop_text_input()`. The event pump remains on the main thread and must continue to be serviced normally.

The case stays CLOSED unless future attribution changes.

## Historical source

The original closeout note survives in the STAR source history at:

```text
star commit: def78b9
path: docs/macos-sdl-event-pump-stall.md
blob: 8307e98e3fa7c277e988af97b68bcebfcf2904c1
```

The investigation progressed through exact commits:

```text
8477aa12de159b153c1cdafc3dbb667ec0f78ffe
  profiler: split input queue and dispatch stalls

7cfbecf1d1d5632fe15c60bdd08a26b5723da23d
  Disable SDL text input during gameplay

ea6cd8d7e97344e957ec1dfa8e589fd742f92ed5
  perf: split SDL event pump from queue retrieval
```

The final attribution instrumentation and mitigation are also present in the productionized runtime at:

```text
57bd8eac0fa8352cc39876092c9068c9e944e8ac
perf-2026-09-window-runtime-production
```

## Representative historical signature

A 200-unit macOS stress run using Pygame 2.6.1 / SDL 2.28.4 / Python 3.13.12 recorded:

```text
frame_ms=62.75
input_event_pump=54.76ms
input_event_get_queue≈0.01ms
input_dispatch≈0.01ms
input_events=1
input_key_down=1
```

The important causal signature is not the absolute frame time. It is:

```text
input_event_pump >> input_event_get_queue + input_dispatch
```

with only a small number of returned events.

## 2026-09-04 production replication

During final production validation of the 15×15 `river_split` scenario on `57bd8ea`, an uncapped interactive run captured:

```text
frame_ms=48.62
input_event_pump=45.30ms
input_event_get_queue≈0ms
input_dispatch≈0ms
input_events=4
input_key_down=1
fog_toggle_this_frame=1
```

This matches the historical platform-stall signature. The simultaneous Fog toggle does not reopen a Fog-rendering case because the long-frame attribution remains inside SDL event pumping rather than Fog, Vision, Terrain, or RenderEngine work.

## Reproduction

Historical reproduction procedure:

1. Use macOS with an interactive Pygame window.
2. Check out a source state containing the split input timers, for example `ea6cd8d7e97344e957ec1dfa8e589fd742f92ed5` or later.
3. Run:

   ```bash
   uv run rotk_env/main.py --profile
   ```

4. Use a large real-time match (historically reproduced with 33×33 / 200 units).
5. Continuously pan/zoom while rapidly clicking units and issuing movement commands.
6. Run for hundreds or thousands of frames and inspect `[SLOW FRAME]` diagnostics.

A reproduction succeeds when a rare long frame is dominated by `input_event_pump` while `input_event_get_queue` and `input_dispatch` stay near zero.

For production-scale benchmark experiments where interactive rendering is unnecessary, prefer headless mode.

## Evidence state

The original full raw profiler artifact for the historical 62.75 ms capture has not been recovered into STAR Lab. The archived evidence therefore consists of:

- the contemporaneous source-side closeout document at exact commit `def78b9`;
- exact Git commits for the attribution instrumentation and mitigation;
- the preserved representative numeric signature;
- an independent production replication on 2026-09-04 with the same attribution pattern.

No empty `SHA256SUMS` is created because this backfilled case currently owns no canonical raw artifact.

See `manifest.yaml`, `analysis.md`, and `decision.md` for provenance and the closure rule.
