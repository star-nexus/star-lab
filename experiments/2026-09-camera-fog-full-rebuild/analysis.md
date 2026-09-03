# Analysis — Camera Geometry Change -> Fog Full Rebuild

## 1. Observation

The case began as a tail discovered during Terrain camera-stress validation. Discrete pan/zoom transitions repeatedly coincided with `fog_surface_full_build` events in the ~25–30 ms class while the Terrain opaque-presentation optimization itself remained much smaller.

That observation was intentionally treated as reproduction, not yet root cause. A dedicated continuous-camera attribution harness was then added at STAR commit `08afd17bfaf84d680cbc8e2dceb6e58f0329718c`.

The canonical controls established:

```text
stationary, 120 frames
  camera_changed = 0
  Fog full rebuilds = 0

short pan +128 px, zoom .15
  camera_changed = 39
  Fog full rebuilds = 39
  all rebuild reasons = view_geometry_changed / offset_x

long pan +320 px, zoom .15
  raw camera changes = 97
  Fog full rebuilds = 96

zoom trajectory
  raw camera changes = 16
  Fog full rebuilds = 15
```

The one-frame difference in long-pan/zoom is explained by the existing Fog geometry-key precision: camera offsets are rounded to 3 decimals and zoom to 5 decimals. The supported statement is therefore:

> Fog full-rebuilds occur on effectively every geometry-key-visible camera change.

This is stronger and more precise than the original discrete-stress observation.

Canonical initial attribution: [`results/attribution/fog-camera-attribution.json`](results/attribution/fog-camera-attribution.json).

## 2. Competing hypotheses

### H1 — Surface allocation dominates the rebuild

If true, a different surface lifetime or buffer allocation policy would be the first target.

### H2 — polygon rasterization dominates the rebuild

If true, geometry-side Python changes would have limited value and a raster/backend redesign would be more appropriate.

### H3 — repeated Python geometry preparation dominates non-polygon time

Candidates included canonical corner generation, per-corner screen transform, repeated bounds scans and `pygame.Rect` construction.

### H4 — camera pan can reuse a previous raster by rigid translation

If exact, the full rebuild could potentially be replaced by surface scrolling plus exposed-boundary repair.

### H5 — raster phase recurrence makes translation reuse exact after a small number of frames

If exact for all supported starts/directions/zooms, a phase-aware cache could avoid repeated rasterization.

### H6 — presentation bounds can be computed once from global world extrema

If exact, visible/no-Fog tiles might avoid per-tile geometry used only to maintain the legacy map-content presentation rectangle.

### H7 — presentation bounds do not need to cover transparent map content at all

If the actual renderer contract is only that submitted bounds conservatively contain all nonzero Fog alpha, visible/no-Fog tiles can be skipped before geometry and the incremental patch state can preserve a conservative bound within one geometry epoch.

## 3. Instrumentation

The investigation followed a layered attribution sequence rather than stacking all timers at once.

### L1 — rebuild frequency and coarse work split

`08afd17bfaf84d680cbc8e2dceb6e58f0329718c` added:

- exact Fog full-build counters;
- rebuild reasons and changed geometry components;
- input/visible/polygon tile counts;
- Surface allocation region;
- whole tile-loop region;
- polygon attribution behind an experiment-only gate.

The 128 px short pan processed per rebuild:

```text
8281 input tiles
1888 currently visible / no-Fog tiles
6393 Fog polygon tiles
```

Measured clean rebuild classes were approximately:

```text
tile loop             27.9 ms
polygon                 4.4 ms
non-polygon             23.4 ms
allocation              ~0.13 ms
```

This rejected H1 and H2 as the main explanation and focused the investigation on H3.

### L2 — canonical corner generation

`88b5118b1e267b52af5ceb6bf603416f944b4c3a` timed only `get_hex_corners` with a controlled ON/OFF observer-cost correction.

Intrinsic estimate:

```text
~6.71 ms / rebuild
~28.7% of clean non-polygon time
```

The legacy implementation performed radians/cos/sin work for six corners on every tile. For 8281 input tiles, one rebuild requested 49,686 corners.

Relevant raw evidence:

- [`results/attribution/fog-camera-hex-corners-short-pan.json`](results/attribution/fog-camera-hex-corners-short-pan.json)
- `results/attribution/hex-{on,off}-*.json`

### L3 — broader geometry preparation

`5d44981684a2ade1f4f5bdfb6540fe0edddcccf8` isolated geometry preparation around corner generation, transform and bounds.

Directional values:

```text
raw geometry preparation        ~20.56 ms / rebuild
transform+bounds derived class  ~13.81 ms / rebuild
```

This confirmed that the cost was distributed across repeated geometry work rather than one small helper.

### L4 — screen transform

`b96c856a747ff0dd0db92d447ccb5513c380f9e4` isolated the six-point screen transform.

Intrinsic estimate:

```text
~5.64 ms / rebuild
~24.2% of non-polygon time
```

Relevant raw evidence: `results/attribution/screen-transform-{on,off}-*.json`.

### L5 — bounds + Rect

`a96ed0f2191626a54edb6a3f472c58a7a01f6209` isolated the four `min/max` scans plus `pygame.Rect` construction.

Intrinsic estimate:

```text
~7.29 ms / rebuild
~31.1% of non-polygon time
```

Relevant raw evidence: `results/attribution/bounds-rect-{on,off}-*.json`.

The fine probes were performed independently. Their corrected estimates are not asserted to be strictly additive.

## 4. Pre-optimization cost tree

The resulting causal model was:

```text
Fog full-build tile loop            ~27.88 ms
├── polygon rasterization            ~4.46 ms
└── non-polygon                     ~23.42 ms
    ├── get_hex_corners              ~6.7 ms class
    ├── six-point screen transform   ~5.64 ms class
    ├── min/max + pygame.Rect        ~7.29 ms class
    └── membership/clip/union/misc   ~3–4 ms directional residual
```

This tree established a stable optimization boundary before production changes were made.

## 5. Controlled production changes

### O1 — fused transform + bounds

Commit: `e9c69594a971b0093a78693dfaa503e0f282fd5c`

The legacy path transformed six points, created a list, then traversed that list four more times through generator-based `min/max`. The fused path preserves the canonical transform and point order while accumulating min/max in the same six-point loop.

Same-commit result:

```text
                         legacy        fused        gain
Fog tile loop           28.015 ms     23.964 ms    -4.051 ms / -14.46%
non-polygon             23.628 ms     19.614 ms    -4.014 ms / -16.99%
```

Raw evidence:

- `results/optimizations/legacy-geometry-{1,2}.json`
- `results/optimizations/fused-geometry-{1,2}.json`

### O2 — precomputed six corner offsets

Commit: `cafddc4ef1626af93127ff83a1c3f375b65c241c`

The implementation precomputes relative corner offsets from the same canonical trig formula keyed by size/orientation. It does not substitute hand-written approximate coordinates.

Same-running-harness aggregate:

```text
                         legacy        precomputed   gain
Fog tile loop           24.007 ms     19.972 ms     -4.035 ms / -16.81%
non-polygon             19.673 ms     15.730 ms     -3.942 ms / -20.04%
MapRender               25.607 ms     21.281 ms
frame                    37.320 ms     32.631 ms
FPS                      26.81         30.65
```

Raw evidence:

- `results/optimizations/legacy-corners-{1,2}.json`
- `results/optimizations/precomputed-corners-{1,2}.json`

The renderer-local tile-loop/non-polygon metrics are the causal metrics. End-to-end frame/FPS remain secondary.

### O3 — camera-independent world-corner cache

Commit: `46f8ab327cfa5175b8dfee2df0d0d4223c1fa3cb`

The Fog presenter caches immutable canonical world corners per tile and invalidates only on hex size/orientation changes. Cache entries survive ordinary presenter `reset()` calls because camera/viewport state does not change world geometry.

Same-running-harness aggregate:

```text
                         legacy        cached        gain
Fog tile loop           20.714 ms     18.400 ms     -2.314 ms / -11.17%
non-polygon             16.702 ms     14.368 ms     -2.334 ms / -13.97%
Fog full build          20.864 ms     18.563 ms     -2.301 ms / -11.03%
MapRender               22.272 ms     19.653 ms     -2.619 ms / -11.76%
```

Both cached replicates had zero misses in the measured steady-state rebuilds. One unrelated legacy run contained a large Gen2 GC / `unit_static_draw` tail; it was not used as causal evidence for the Fog-local effect.

Raw evidence:

- `results/optimizations/world-corners-legacy-{1,2}.json`
- `results/optimizations/world-corners-cached-{1,2}.json`

### O4 — Fog-content presentation bounds + true visible/no-Fog skip

Commit: `717932ec520ffc215ab45c32bd33cbb0fa5a68c2`

Source review established that `presentation_rect` is a submission-area optimization, not semantic Fog state. The required invariant is:

```text
alpha_support(Fog surface) ⊆ presentation_rect
```

It does not need to cover transparent map tiles.

The accepted full-rebuild path therefore checks semantic visibility before geometry:

```text
for tile in visible_tiles:
    if tile is currently visible:
        skip all Fog geometry
    else:
        run canonical geometry + polygon path
        union the clipped polygon rect into presentation_rect
```

Incremental patches only expand the conservative bound when new Fog appears; reveal/clear operations do not shrink it. A later camera/zoom/orientation full rebuild recreates a fresh tight bound.

Correctness evidence before production adoption included:

```text
direct semantic matrix       510 / 510 exact
runtime rebuild comparison   492 / 492 exact
visible_tiles set changes     17 / 17 exact
mismatches                     0
```

The direct oracle checked actual alpha support and final framebuffer equivalence rather than requiring the new internal `presentation_rect` to equal the deliberately different legacy rect.

At zoom `.15`, the same-commit alternating A/B kept the same 39 rebuilds and polygon workload:

```text
                         legacy map-content    fog-content       gain
Fog tile loop                 18.211 ms          15.497 ms       -2.714 / -14.90%
non-polygon                   14.358 ms          11.693 ms       -2.664 / -18.56%
MapRender                     19.991 ms          16.944 ms       -3.047 / -15.24%
frame mean                    30.539 ms          27.760 ms       -2.779 / -9.10%
FPS                           32.75              36.03           +10.02%
```

Each rebuild skipped exactly `1888` visible/no-Fog tiles and still drew `6393` Fog polygons.

At zoom `.50`, only ~180 visible/no-Fog tiles were skipped per rebuild and the improvement correspondingly shrank to ~`0.266 ms` / `3.01%` in the tile loop. This workload sensitivity matches the mechanism.

Raw evidence:

- [`results/fog-content/fog-content-bounds-feasibility.json`](results/fog-content/fog-content-bounds-feasibility.json)
- `results/fog-content/fog-content-z015-*.json`
- `results/fog-content/fog-content-z050-*.json`

## 6. Structural feasibility / negative results

These negative results are part of the final design evidence; they prevent future engineers from re-proposing superficially attractive but non-equivalent shortcuts.

### N1 — adjacent-frame rigid translation rejected

Commit: `1f7d5a84879aa870253a2f01b9f544628b6245ab`

The canonical transform is:

```text
sx = int(round(world_x * zoom + camera_offset_x))
sy = int(round(world_y * zoom + camera_offset_y))
```

The 128 px smooth pan advances by approximately `3.3333333333` screen pixels per camera frame. Per-vertex rounding means `round(a+d)-round(a)` is not globally constant.

Measured result:

```text
39 / 39 changed frames had nonuniform canonical point translation
0 exact rigid-translation frames
natural alpha diff: 995–1690 pixels / frame
```

Therefore naïve `Surface.scroll`, source-rect shift and simple exposed-edge refill cannot preserve pixel-exact Fog.

Raw: [`results/feasibility/fog-pan-translation-feasibility.json`](results/feasibility/fog-pan-translation-feasibility.json).

### N2 — same-phase raster reuse rejected

Preliminary commit: `0ab02f136ac426e7da8f1ab4ec63ff54b320131f`  
Directed generalization: `682a1b96dddc9abf3a40fa8b751703d6a5c35ee3`

The first short-pan phase test found recurrent matches but also tie-sensitive interior pixel populations. The directed matrix expanded coverage to:

```text
3 zoom values
5 fractional camera starts
6 pan directions
90 workloads
3510 canonical camera frames
```

Final result included:

```text
144 interior mismatch cases/events
2152 boundary-only failures
recommendation: ABANDON_PHASE_RASTER_REUSE
```

Because interior mismatches exist, overscan cannot repair the error. The mismatch populations were phase/tie effects, not cumulative translation drift.

Raw:

- `results/feasibility/fog-phase-raster-feasibility.json`
- `results/feasibility/fog-directed-phase-analysis-pack.json`

### N3 — global world-extrema / one-clip presentation bounds rejected

Commit: `def78b9f101bd52a7b71d8f8cb79de3e6bc82d70`

The candidate transformed one camera-independent global world AABB and clipped once. Runtime matrix:

```text
13 workloads
492 / 492 full-rebuild comparisons exact
17 / 17 visible_tiles content-change frames exact
```

However, direct deterministic geometry tests found:

```text
510 comparisons
454 exact
56 mismatches
all mismatches classified VIEWPORT_CLIPPING
```

Four counterexamples used contiguous production-reachable topology. Example:

```text
viewport 320x240
zoom 1.0
camera (310,120)
visible_tiles={(0,0),(1,0)}

legacy    [260,77,60,87]
candidate [260,33,60,131]
```

The failed identity is:

```text
clip(union(all tile rects)) != union(clip(each tile rect))
```

The rejection applies to this specific global-extrema -> one-screen-rect -> one-clip construction. It does not reject all presentation-bound redesigns, which is why O4 remained viable.

Raw: [`results/feasibility/fog-presentation-bounds-feasibility.json`](results/feasibility/fog-presentation-bounds-feasibility.json).

## 7. Final closeout evidence

Closeout implementation/measurement commit: `be28ca172162cac8a4f684507620fca0a661754e`.

The closeout deliberately disabled all fine-grained attribution timers and feasibility observers. Production configuration was verified before/effective/requested as:

```text
fused geometry
precomputed corner offsets
cached world corners
fog_content presentation bounds
Fog ON
units stationary
```

The world-corner cache already contained the required 6393 Fog tile entries before the unmeasured prime; the prime confirmed that working set and all measured epochs had zero cache misses.

Formal closeout matrix:

| Epoch | Camera changes | Fog rebuilds | Input/rebuild | Skip/rebuild | Polygon/rebuild | Tile loop | Full build | Frame | FPS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| stationary `.15` | 0 | 0 | — | — | — | — | — | 16.458 ms | 60.76 |
| short-pan `.15` A | 39 | 39 | 8281 | 1888 | 6393 | 13.647 ms | 13.779 ms | 26.939 ms | 37.12 |
| short-pan `.50` | 39 | 39 | 2392.33 | 180 | 2212.33 | 7.638 ms | 7.773 ms | 21.619 ms | 46.26 |
| short-pan `.15` B | 39 | 39 | 8281 | 1888 | 6393 | 14.319 ms | 14.454 ms | 27.859 ms | 35.89 |
| long-pan `.15` | 97 | 96 | 8281 | 1888 | 6393 | 13.955 ms | 14.087 ms | 28.008 ms | 35.70 |
| zoom from `.15` | 16 | 15 | 4092.73 | 622.27 | 3470.47 | 8.901 ms | 9.011 ms | 31.709 ms | 31.54 |

Primary duplicate short-pan aggregate:

```text
Fog tile loop        13.983 ms / rebuild
Fog full build       14.116 ms / rebuild
frame mean           27.399 ms
FPS                   36.51
replicate drift        0.672 ms / 4.81%
```

The `.50` workload reduced Fog polygons from `6393` to `2212.33` and absolute tile-loop time from `13.983` to `7.638 ms`. The remaining cost is therefore workload-sensitive rather than a fixed unexplained camera penalty.

The closeout classification is:

```text
EXPLAINED-WORKLOAD-BOUND
CASE-CLOSEOUT-READY / RECOMMEND-CLOSED
```

Raw: [`results/closeout/fog-camera-closeout.json`](results/closeout/fog-camera-closeout.json).

## 8. Tail analysis and confounders

Aggregate frame tails were never used as the sole causal metric.

A representative long-pan worst frame reached `49.477 ms`, but `unit_static_draw` contributed `23.958 ms` and frame metrics recorded a ~`21.829 ms` GC pause, including ~`21.587 ms` Gen2. The Fog loop on that frame remained in its normal ~14–15 ms class.

This is classified as:

```text
TAIL-CONTAMINATION-OUTSIDE-FOG
```

Similarly, zoom `.50` increases Terrain/render-batch/presentation work because screen-space tiles become larger. High `render_engine` or queue cost in those runs is not evidence that the Fog tile-loop failed to scale down.

## 9. Root cause

The root cause is now formally established:

> Camera geometry-key changes invalidate the Fog presenter geometry and force a full rebuild. The original rebuild performed substantial repeated Python-side geometry work for every camera-visible tile, including tiles whose final Fog alpha was transparent. That accidental work, not Surface allocation, explained most of the pathological rebuild cost.

The accepted production design preserves full rebuild semantics when the geometry key changes but removes avoidable repeated work through:

```text
fused transform/bounds
+ canonical corner-offset precomputation
+ camera-independent world-corner caching
+ semantic visible/no-Fog skip using Fog-content presentation bounds
```

The remaining cost is the real geometry + raster workload for currently fogged tiles.

## 10. Historical supportive trajectory

Across validated commits:

```text
original canonical short-pan     ~27.918 ms
final production closeout        ~13.983 ms
supportive reduction              ~13.935 ms / 49.91%
```

This is explicitly **not** a same-commit A/B. It summarizes the investigation trajectory only. Causal optimization claims come from the individual same-commit A/Bs in Section 5.

## 11. Evidence limits

- Results are from one Apple M4 Mac mini / macOS / Pygame environment.
- The canonical stress map is 91x91 with 5000 resident units; continuous Fog attribution itself holds units stationary to isolate camera causality.
- The case preserves the existing rounded geometry-key semantics rather than redefining sub-key-precision camera changes.
- Pixel-exactness is the correctness standard used to reject translation/phase shortcuts.
- Closure does not imply 60 FPS during continuous low-zoom pan at this extreme workload.
- Unit-driven Fog reveal hitches and manual Fog-toggle hitches are outside this Camera->Fog geometry case.

## 12. Raw evidence and integrity

All 44 local raw artifacts are SHA256-covered by [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS).

The earlier discrete camera-stress artifacts remain canonically owned by the Terrain case and are referenced in `manifest.yaml` rather than duplicated.
