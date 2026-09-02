# Analysis — Terrain Opaque Presentation Cache

## 1. Observation

After Fog presentation was bounded, Terrain still accounted for most of the remaining scalar RenderEngine cost. The verified overscan path submitted a cropped region from an oversized `SRCALPHA` Surface using `area=source`, and the prior Terrain-off causal ablation removed ~1.37 ms from `render_scalar_execute`.

The optimization target was already content-bounded, so the remaining question was **why** this cropped blit was expensive.

## 2. Competing hypotheses

### H1 — Pixel-format conversion dominates

Source and destination channel layouts might differ, forcing conversion for ~1.22M submitted pixels every frame.

### H2 — Oversized backing Surface / row pitch hurts locality

The cropped region is read from a ~2992x1780 backing Surface even though only ~1028x1191 pixels are submitted.

### H3 — Partial/transparent alpha values dominate

The cost might scale with the fraction of pixels whose alpha is not 255.

### H4 — `SRCALPHA` Surface semantics select an expensive Pygame/SDL software-blit path

Even if most pixels are alpha=255, the whole source Surface can remain on a per-pixel-alpha path because the Surface itself carries `SRCALPHA`.

## 3. Instrumentation / diagnostic changes

At `b2dd5d0...`, diagnostics recorded:

```text
source/display bitsize and masks
SRCALPHA flags
format match
opaque / partial / transparent pixel counts
```

The first attempted opaque variant also showed why `.convert(screen)` was not a valid way to force a non-SRCALPHA Surface on this platform.

At `0f9368c...`, the experiment was orthogonalized:

```text
A original
B compact_alpha
C compact_flat_srcalpha
D compact_opaque_rgb
```

All variants preserved the intended final visual RGB result while separating backing geometry, alpha values, and Surface alpha semantics.

At `54d1774...`, the final production implementation added a same-commit Legacy/Opaque control and deterministic camera stress, plus cache-build timers:

```text
map_terrain_opaque_present_cache_build
map_overscan_build_step
```

## 4. Evidence

### Evidence against H1 — format conversion

The diagnostic showed source and screen were both 32-bit with matching RGB masks. `scale_render_terrain_screen_format_match=true`. There was no evidence that RGB layout conversion explained the steady-state cost.

### Evidence about H2 — compact backing/pitch

A -> B reduced `scalar_execute` from ~2.440 ms to ~2.223 ms, a secondary ~0.22 ms signal. This supports some locality/pitch benefit, although fresh-process aggregate timing also drifted and the effect is much smaller than C -> D.

### Evidence against H3 — alpha-value distribution

The diagnostic pixel distribution was:

```text
opaque          96.126%
partial-alpha    0.426%
transparent      3.447%
```

B -> C changed the compact Surface from original mixed alpha to fully flattened alpha=255 while retaining `SRCALPHA=true`. `scalar_execute` changed only ~2.223 -> ~2.206 ms (~0.02 ms), effectively noise.

Therefore, the fraction of non-opaque pixel values was not the primary cause.

### Evidence for H4 — SRCALPHA Surface semantics

C and D held compact geometry, pitch and final RGB output fixed while changing the Surface semantics:

```text
C: SRCALPHA=true, alpha values all 255
D: SRCALPHA=false, alpha mask=0
```

The response was large and localized:

```text
scalar_execute       2.206 -> 1.375 ms   ~-0.831 ms (-37.7%)
queue_submit         3.130 -> 2.346 ms   ~-0.784 ms (-25.1%)
render_engine        3.206 -> 2.435 ms   ~-0.771 ms (-24.0%)
batch_blits          approximately unchanged
```

This is the strongest causal evidence in the A-B-C-D sequence.

### Why the first opaque experiment is not formal evidence

The first variant used `.convert(screen)` but the resulting Surface still reported `SRCALPHA=true`. The intended independent variable had not changed. Those runs are retained under `results/intermediate/` because they were informative, but they cannot support a conclusion about disabling alpha blending.

### Production fixed-camera validation

At one common source commit (`54d1774...`), Legacy and Opaque modes produced:

```text
                         Legacy       Opaque       delta
scalar_execute            2.346        1.383 ms    -0.963 ms
queue_submit              3.255        2.354 ms    -0.901 ms
render_engine             3.333        2.444 ms    -0.889 ms
batch_blits               0.696        0.736 ms    noise class
```

The three per-run scalar improvements were approximately -0.968, -0.961 and -0.960 ms, giving unusually stable subsystem-local evidence even though aggregate frame time drifted between process groups.

### Camera-stress validation

Under deterministic discrete pan/zoom stress:

```text
                         Legacy       Opaque       delta
scalar_execute            1.872        1.209 ms    -0.663 ms
queue_submit              3.594        2.946 ms    -0.648 ms
render_engine             3.717        3.073 ms    -0.645 ms
```

Opaque cache builds occurred ~9-10 times/run. Maximum cache-build time averaged ~2.51 ms; maximum `map_overscan_build_step` averaged ~4.16 ms versus ~1.53 ms Legacy.

Tail metrics did not show a new pathology:

```text
                         Legacy       Opaque
P95                      38.230       38.759 ms
P99                      58.730       59.385 ms
rolling max              67.204       67.464 ms
```

The larger camera-stress tail was instead dominated by Fog full rebuilds, which became the next open investigation.

### Regression evidence

The final combined renderer regression suite was executed at the exact validated production commit `54d17745098fb3fc4c43861d839e8dc40164c030` and reported:

```text
43 passed in 1.12s
```

The suite covered Terrain presentation cache behavior, camera stress, overscan behavior, rendering ablations, render batching, RenderEngine profiling, profiler-v2 export behavior, Fog integration, and scale measurement plumbing.

## 5. Root cause

> The dominant Terrain presentation overhead was not pixel-format mismatch or the small fraction of non-opaque pixels. It was the Pygame/SDL software-blit path selected by a `SRCALPHA` source Surface. A secondary cost came from reading a compact crop out of a much larger backing Surface. The production fix therefore changes presentation representation rather than Terrain construction semantics.

## 6. Causal chain

```text
oversized SRCALPHA Terrain overscan Surface
  -> cropped `area=` scalar blit
  -> SDL/Pygame SRCALPHA software composition
  -> ~1 ms extra scalar cost

cache-install boundary
  -> crop actual content once
  -> precompose against frame clear color
  -> compact RGB Surface, alpha mask=0, SRCALPHA=false
  -> cheap steady-state opaque blit
```

## 7. Rejected explanations

- **RGB pixel-format conversion dominates** — rejected because source/display RGB formats already match.
- **The 3.9% non-opaque pixels dominate** — rejected by B -> C; making every pixel alpha=255 while retaining SRCALPHA produces almost no gain.
- **`.convert(screen)` guarantees an opaque Surface** — rejected by direct metadata; on this platform it still produced `SRCALPHA=true`.
- **A-D gain is only machine/session drift** — rejected by same-commit production Legacy/Opaque validation and the stable ~0.96 ms scalar delta across three runs.
- **Opaque cache causes unacceptable rebuild spikes** — rejected for this workload; cache-build max is ~2.5 ms class and P95/P99/max do not materially diverge from Legacy stress.

## 8. Limits of the evidence

- Root cause is specific to the Pygame/SDL software Surface backend; a GPU renderer will expose different primitives and costs.
- A -> B locality/pitch attribution has lower confidence than C -> D because process-level load drift was present.
- Camera stress uses discrete state jumps every 0.75 s, not smooth per-frame pan/zoom.
- The stress test proves rebuild resilience for this discrete workload; it does not yet characterize continuous-camera invalidation frequency.
- Exact Python runtime version was not captured in archived raw metadata.

## 9. Raw evidence

- [`results/diagnostics/`](results/diagnostics/)
- [`results/intermediate/`](results/intermediate/) — informative, not final causal evidence
- [`results/abcd/`](results/abcd/)
- [`results/validation/fixed-camera/`](results/validation/fixed-camera/)
- [`results/validation/camera-stress/`](results/validation/camera-stress/)
- [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)
- [`manifest.yaml`](manifest.yaml)
