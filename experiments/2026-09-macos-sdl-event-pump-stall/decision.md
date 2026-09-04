# Decision — macOS / SDL event-pump tail latency

## Decision

Keep the case **CLOSED** as a known macOS + SDL/Pygame interactive-window limitation.

STAR will:

- keep SDL event pumping on the main thread;
- keep normal gameplay text input disabled with `pygame.key.stop_text_input()`;
- keep the split profiler timings `input_event_pump`, `input_event_get_queue`, and `input_dispatch` so future slow frames are attributable;
- prefer headless execution for benchmark-scale experiments that do not require an interactive window;
- avoid treating a manual Fog-toggle hitch as a Fog regression when the slow frame is dominated by `input_event_pump`.

STAR will **not**:

- move SDL/Cocoa event pumping to a worker thread;
- stop pumping events to hide the latency;
- redesign simulation/rendering code to address a frame whose measured delay is outside those sections;
- reopen this case solely because another rare frame reproduces the same pump-dominated signature.

## Why this choice

The investigation established a clear causal boundary:

```text
platform event pump   -> tens of milliseconds in rare tails
queue retrieval       -> approximately zero
STAR input dispatch   -> approximately zero
```

The practical product-side mitigation was already applied by removing the unnecessary text/IME path from ordinary gameplay. Residual rare pump stalls remain platform-bound and do not justify invasive runtime changes without new evidence.

## Production status

The mitigation and attribution instrumentation are present in the productionized runtime represented by:

```text
57bd8eac0fa8352cc39876092c9068c9e944e8ac
perf-2026-09-window-runtime-production
```

The 2026-09-04 uncapped production validation reproduced the same signature (`48.62 ms` frame, `45.30 ms` in `input_event_pump`) and therefore reinforces rather than invalidates the closure.

## Reopen conditions

Reopen only if one or more of the following is observed:

1. long frames are no longer dominated by `input_event_pump`;
2. `input_event_get_queue` or `input_dispatch` becomes a material contributor;
3. the event-pump stalls become frequent enough to harm normal capped 60 FPS gameplay rather than remaining isolated tails;
4. equivalent behavior is reproduced on Windows/Linux, changing the platform-scope conclusion;
5. an SDL/Pygame upgrade materially changes the event-pump behavior or exposes a new actionable mitigation;
6. a manual Fog-toggle or unit-driven Fog reveal hitch shows substantial Fog/Vision/Terrain/RenderEngine cost rather than the known SDL signature.

## Archive note

This package is a historical backfill. The original full raw artifact for the historical 62.75 ms capture was not recovered, so the archive does not claim raw-evidence completeness. Exact source commits, the contemporaneous closeout document, the preserved numeric signature, and the later production replication are retained instead.
