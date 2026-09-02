# Analysis — RenderEngine Queue-Drain and Presentation Attribution

## 1. Observation

At the validated 5K/5K realtime workload, `render_engine` was consistently in the ~5.5 ms class even though `pygame.display.flip()` was measured separately as `display_present`.

The first decomposition showed that almost all of this time was inside queue submission rather than queue preparation or clear:

```text
RenderEngine Phase-I 3-run mean
render_engine                 5.583 ms
render_queue_submit           5.492 ms
render parent self            0.088 ms
prepare                       0.0015 ms
clear                         0.0016 ms
```

Queue topology was also stable:

```text
~1698 commands/frame
6 batch runs
4 actual multi-blit batches
~1692 simple blits
6 scalar commands
max batch ~1679 commands
```

## 2. Competing hypotheses

### H1 — Python queue preparation / list construction is the bottleneck

Plausible because thousands of commands are scanned, grouped and repacked every frame.

### H2 — Excessive command fragmentation or ordering barriers cause many expensive submission calls

Plausible because the renderer preserves layers and command semantics while batching only compatible plain blits.

### H3 — The large plain-blit batch is expensive because it contains a very large Surface workload

Plausible because command count alone does not describe submitted pixel volume.

### H4 — Terrain's nonbatchable cropped blit is a separate scalar Surface hot path

Plausible because `area=source` makes the terrain presentation command nonbatchable.

### H5 — Off-screen clipping is the primary reason the plain-blit workload is large

Plausible if many queued source pixels are later clipped by the destination framebuffer.

## 3. Instrumentation / diagnostic changes

Three instrumentation stages were used.

### Queue-drain decomposition — `b2bda2f...`

Added:

```text
render_queue_prepare
render_queue_submit
render_queue_clear
queue command/layer/batch/scalar topology
```

### Submission decomposition — `d25271f...`

Added:

```text
render_batch_pack
render_batch_blits
render_scalar_execute
optional pixel metrics
```

The resulting 3-run mean was:

```text
render_queue_submit      5.511 ms
submit self              0.021 ms
render_batch_pack        0.226 ms
render_batch_blits       3.839 ms
render_scalar_execute    1.426 ms
```

The child timers close the parent to measurement noise.

### Presentation causal ablations — `6e8c151...`

Added testing-only suppression controls:

```text
STAR_RENDER_ABLATE_FOG_PRESENT=1
STAR_RENDER_ABLATE_TERRAIN_PRESENT=1
```

The semantic Fog update and Terrain build work remained active; only the final presentation command was removed.

## 4. Evidence

### Evidence against H1 — queue packing is too small

`render_batch_pack` was only about 0.226 ms, roughly 4.1% of queue submission. Rewriting list construction could not plausibly recover the multi-millisecond RenderEngine cost.

### Evidence against H2 — queue topology is already highly consolidated

The stable frame had only four true multi-blit batches and one huge batch containing approximately 99% of simple blits. There was no evidence of pathological fragmentation.

### Evidence for H3 — one full-window Surface dominates plain-blit pixels

Pixel diagnostics measured approximately:

```text
plain source pixels             3,393,195
clipped source pixels           3,392,547
pixels removed by clipping            648
largest plain Surface           3,144,640 = 2480 * 1268
largest batch source pixels     3,318,614
```

The full-window Surface alone represented about 92.7% of total plain source pixels. The clipping ratio was ~99.98%, so off-screen clipping did not explain the workload.

### Evidence for Fog causality

3-run means:

```text
Normal
render_engine           5.425 ms
submit                  5.344 ms
batch_blits             3.748 ms
scalar                  1.383 ms

Fog presentation off
render_engine           2.441 ms
submit                  2.351 ms
batch_blits             0.704 ms
scalar                  1.414 ms
```

Causal delta:

```text
render_engine          -2.984 ms  (-55.0%)
batch_blits            -3.043 ms  (-81.2%)
scalar                  +0.031 ms  (noise class)
```

The response is localized to the expected batch-blit path.

### Evidence for Terrain causality

3-run mean with Terrain presentation suppressed:

```text
render_engine           4.114 ms
submit                  4.030 ms
batch_blits             3.795 ms
scalar                  0.017 ms
```

Causal delta from normal:

```text
render_engine          -1.311 ms  (-24.2%)
scalar                 -1.366 ms  (-98.8%)
batch_blits            +0.048 ms  (noise class)
```

Again, the response is localized to the predicted scalar path.

## 5. Root cause

> The RenderEngine bottleneck was primarily Surface presentation work. Fog submitted a viewport-sized full-window Surface through the batched plain-blit path every frame, while Terrain submitted a large cropped overscan Surface through the scalar `area=` path. Together these two presentation workloads accounted for about 4.41 ms, or ~81% of the normal 5.425 ms RenderEngine cost.

Python queue packing, command fragmentation and off-screen clipping were not the primary causes.

## 6. Causal chain

```text
Fog semantic presenter
  -> full-window plain BlitCommand
  -> ~3.145M source pixels/frame
  -> pygame/SDL batch blit
  -> ~3.0 ms RenderEngine cost

Terrain overscan presenter
  -> cropped area BlitCommand
  -> nonbatchable scalar execute
  -> ~1.37 ms RenderEngine cost

combined
  -> ~4.41 ms of ~5.43 ms RenderEngine
```

## 7. Rejected explanations

- **Python batch packing is the main bottleneck** — rejected because `render_batch_pack` was only ~0.23 ms.
- **Command fragmentation is the main bottleneck** — rejected because queue topology collapses to only four true multi-blit batches, with one dominant batch.
- **Off-screen clipping is the main source of wasted pixels** — rejected because only ~648 of ~3.39M source pixels were clipped in the diagnostic run.
- **`pygame.display.flip()` / VSync is inside `render_engine`** — rejected by source instrumentation: display presentation is separately timed as `display_present`.
- **Command count alone explains cost** — rejected because ~1690 small blits contributed little pixel area compared with one viewport-sized Surface.

## 8. Limits of the evidence

- The measurements were taken on one Mac mini / macOS software-rendering environment.
- The attribution is specific to the Pygame/SDL Surface renderer; another backend can have a different cost model.
- Aggregate frame/FPS varied across fresh processes and was not used as the primary causal signal.
- The experiment attributes the hot paths but does not itself choose the final Fog or Terrain production representation; those decisions are archived separately.
- Exact Python runtime version was not captured in the archived raw result metadata.

## 9. Raw evidence

- [`results/queue-breakdown/`](results/queue-breakdown/)
- [`results/submit-breakdown/`](results/submit-breakdown/)
- [`results/pixel-diagnostics/`](results/pixel-diagnostics/)
- [`results/causal-ablation/`](results/causal-ablation/)
- [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)
- [`manifest.yaml`](manifest.yaml)
