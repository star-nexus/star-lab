# Analysis — Fog Presentation Bounding

## 1. Observation

Fog semantic updates were already incremental, but the final presentation path still submitted a viewport-sized `SRCALPHA` Surface every frame. The pre-fix causal baseline therefore paid for 3,144,640 source pixels per frame.

The RenderEngine attribution case showed that suppressing only Fog presentation changed the expected path:

```text
render_batch_blits       -3.043 ms
render_engine            -2.984 ms
render_scalar_execute    ~unchanged
```

## 2. Competing hypotheses

### H1 — Fog semantic patching is still the dominant cost

Plausible because Fog visibility changes continuously while 5000 units move.

### H2 — The semantic work is already bounded, but final full-window presentation dominates

Plausible because the presenter retains a viewport-sized Surface and queued it every frame.

### H3 — Bounding presentation would require recomputing map bounds every frame and merely move cost elsewhere

Plausible if the content rectangle had to scan all visible map tiles in steady state.

## 3. Instrumentation / diagnostic changes

The causal ablation at `6e8c151...` suppressed only the final Fog `RMS.draw` while preserving semantic updates.

The production fix at `6a61115...` added cached presentation metadata:

```text
scale_fog_present_full_viewport_pixels
scale_fog_present_last_rect
scale_fog_present_last_source_pixels
scale_fog_present_last_saved_pixels
```

The presentation rectangle is derived during `_full_rebuild` while that code is already traversing visible tiles. It is cached and reused during steady-state incremental updates.

## 4. Evidence

### Evidence against H1

Fog-off removes about 3.04 ms from `render_batch_blits`, not from semantic patch timers. This localizes the dominant cost to final Surface presentation.

### Evidence for H2

The production fix consistently reports:

```text
full viewport pixels     3,144,640
bounded rect             1029 x 1190
bounded pixels           1,224,510
saved pixels             1,920,130
saved ratio              61.06%
```

3-run mean before vs after:

```text
                         before      bounded
render_engine             5.425       3.433 ms
queue_submit              5.344       3.343 ms
batch_blits               3.748       0.726 ms
scalar_execute            1.383       2.382 ms
avg frame                21.331      20.690 ms
P99                      25.114      25.005 ms
```

The command moves from the plain/batchable path to one bounded `area=` scalar command. The observed cost migration matches that representation change:

```text
batch_blits              -3.022 ms
scalar_execute           +0.999 ms
queue_submit             -2.001 ms
render_engine            -1.992 ms
```

### Evidence against H3

Source inspection confirmed the content rectangle is computed only during `_full_rebuild`, piggybacking on the existing visible-tile traversal. Normal incremental frames reuse `self.presentation_rect`; no new steady-state O(Nmap) scan was introduced.

### Regression evidence

The final combined renderer regression suite ran at integration commit `54d17745098fb3fc4c43861d839e8dc40164c030` and reported:

```text
43 passed in 1.12s
```

A source comparison from the Fog fix commit `6a61115...` to that regression commit shows no subsequent change to the Fog production presenter. The regression therefore validates the integrated descendant state without changing the original performance-measurement provenance.

## 5. Root cause

> Fog had an already-bounded semantic update path but an unbounded presentation representation: the entire viewport-sized alpha Surface was still composed every frame. The steady-state bottleneck was therefore presentation pixel volume, not semantic Fog recomputation.

## 6. Causal chain

```text
incremental Fog semantic updates
  -> viewport-sized retained semantic Surface
  -> full-window presentation every frame
  -> 3.145M alpha-composed pixels
  -> ~3 ms batch-blit cost

cached map-content presentation rect
  -> 1.225M submitted pixels
  -> one bounded area blit
  -> ~2.0 ms lower queue-submit / RenderEngine cost
```

## 7. Rejected explanations

- **Fog semantic patching is the primary 3 ms cost** — rejected by the presentation-only causal ablation.
- **The fix works by disabling Fog** — rejected because formal guards keep Fog semantically ON and only presentation geometry changes.
- **The optimization adds a steady-state full-map bounds scan** — rejected by source inspection; bounds are computed during full rebuild and cached.
- **The RenderEngine gain is unexplained workload drift** — rejected by the exact command-topology migration: batch cost disappears while one scalar bounded blit appears.

## 8. Limits of the evidence

- Validated on one Mac mini / macOS Pygame software-rendering environment.
- Fixed-camera production validation does not characterize camera-induced Fog full rebuilds; that later frontier is recorded separately.
- Aggregate FPS is noisier than the renderer-local causal metrics and should not be used alone.
- Exact Python runtime version was not captured in archived metadata.
- Regression validation was executed at descendant integration commit `54d1774...`, not by rerunning pytest on the exact performance-measurement commit; Fog production code was unchanged across that interval.

## 9. Raw evidence

- Fixed canonical evidence: [`results/`](results/)
- Pre-fix canonical baseline: [`../2026-09-render-engine-attribution/results/causal-ablation/`](../2026-09-render-engine-attribution/results/causal-ablation/)
- Integrity metadata: [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)
- [`manifest.yaml`](manifest.yaml)
