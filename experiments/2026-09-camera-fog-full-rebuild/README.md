# Camera Geometry Change -> Fog Full Rebuild

**Status:** CLOSED — complete formal archive  
**STAR repository:** `star-nexus/star`  
**Problem / archive baseline commit:** `54d17745098fb3fc4c43861d839e8dc40164c030`  
**Problem checkpoint tag:** `perf-2026-09-camera-fog-checkpoint-session2`  
**Final production fix:** `717932ec520ffc215ab45c32bd33cbb0fa5a68c2`  
**Closeout / validated commit:** `be28ca172162cac8a4f684507620fca0a661754e`  
**Validated tag:** `perf-2026-09-camera-fog-full-rebuild-closed`

## 1. Problem

Camera motion with Fog enabled caused expensive Fog full rebuilds. The original discrete camera-stress workload exposed `fog_surface_full_build` events in the ~25–30 ms class and large `MapRenderSystem` transition frames. The investigation then replaced the coarse jump workload with deterministic continuous camera attribution and established that geometry-key-visible camera changes rebuild Fog on effectively every changed frame.

The canonical smooth short-pan workload at zoom `0.15` showed:

```text
camera-changing frames              39
Fog full rebuilds                   39
input tiles / rebuild             8281
visible/no-Fog tiles / rebuild     1888
Fog polygon tiles / rebuild        6393
Fog full-build tile loop         ~27.918 ms
```

A stationary 120-frame control produced zero camera changes and zero Fog rebuilds.

## 2. Root cause

The Fog semantic surface was already incremental for visibility-journal changes, but camera geometry was part of its geometry key:

```text
viewport
view faction
camera offset rounded to 3 decimals
zoom rounded to 5 decimals
hex orientation
```

When this key changed, the presenter performed a viewport-sized full rebuild and iterated all camera-visible tiles.

The expensive path was not primarily Surface allocation or polygon rasterization. Most cost was Python-side per-tile geometry work performed during every rebuild:

```text
Fog full-build tile loop            ~27.9 ms
├── polygon rasterization            ~4.4 ms
└── non-polygon work                ~23.4 ms
    ├── get_hex_corners              ~6.7 ms class
    ├── six-point screen transform   ~5.6 ms class
    ├── min/max + pygame.Rect        ~7.3 ms class
    └── membership/clip/union/misc   residual
```

The fine-grained probes were independent attribution experiments and are not strictly additive.

## 3. Accepted production changes

The investigation removed accidental work without changing Fog pixels, camera rounding or Fog semantics.

### L1 — fuse transform and bounds

Commit:

```text
e9c69594a971b0093a78693dfaa503e0f282fd5c
perf: fuse fog transform bounds pass
```

The old path built a transformed point list and then rescanned it with four generator-based `min`/`max` passes. The production path now transforms the six canonical points and accumulates bounds in one pass while preserving exact point order and rounding.

Controlled A/B:

```text
Fog tile loop       28.015 -> 23.964 ms   -4.051 ms / -14.46%
non-polygon         23.628 -> 19.614 ms   -4.014 ms / -16.99%
```

### L2 — precompute camera-independent corner offsets

Commit:

```text
cafddc4ef1626af93127ff83a1c3f375b65c241c
perf: precompute hex corner offsets
```

The six relative hex-corner offsets are precomputed from the same canonical trigonometric construction and keyed by geometry shape/orientation. This removes repeated trigonometric corner construction without substituting approximate constants.

Controlled A/B:

```text
Fog tile loop       24.007 -> 19.972 ms   -4.035 ms / -16.81%
non-polygon         19.673 -> 15.730 ms   -3.942 ms / -20.04%
MapRender           25.607 -> 21.281 ms
frame               37.320 -> 32.631 ms
```

The Fog-local causal metrics are primary; frame/FPS are secondary because host/GC noise can contaminate aggregate tails.

### L3 — cache tile world geometry

Commit:

```text
46f8ab327cfa5175b8dfee2df0d0d4223c1fa3cb
perf: cache fog tile world geometry
```

The presenter caches immutable canonical world corners by tile and invalidates the cache only when hex size or orientation changes. Camera motion does not invalidate world geometry.

Same-running-harness A/B aggregate:

```text
Fog tile loop       20.714 -> 18.400 ms   -2.314 ms / -11.17%
non-polygon         16.702 -> 14.368 ms   -2.334 ms / -13.97%
Fog full build      20.864 -> 18.563 ms
MapRender           22.272 -> 19.653 ms
```

### L4 — bound presentation to actual Fog content and skip visible tiles

Commit:

```text
717932ec520ffc215ab45c32bd33cbb0fa5a68c2
perf: bound fog presentation to rendered content
```

The semantic Fog surface remains viewport-sized, but `presentation_rect` is required only to conservatively contain nonzero Fog alpha. On a full rebuild, a tile already visible to the faction therefore needs no Fog geometry at all and is skipped before world-corner lookup, screen transform, bounds, `Rect`, clipping and polygon work.

At zoom `0.15`, every rebuild skips exactly `1888` visible/no-Fog tiles and processes `6393` Fog polygons.

Same-commit alternating A/B aggregate:

```text
                         legacy map bounds    fog-content bounds
Fog tile loop                  18.211 ms          15.497 ms
non-polygon                    14.358 ms          11.693 ms
MapRender                      19.991 ms          16.944 ms
frame mean                     30.539 ms          27.760 ms
FPS                            32.75              36.03

Fog tile-loop gain                              -2.714 ms / -14.90%
non-polygon gain                                -2.664 ms / -18.56%
```

The accepted path passed direct semantic, incremental-patch and runtime framebuffer equivalence checks before becoming the production default.

## 4. Important rejected structural designs

The investigation deliberately tested reuse designs before accepting continued full rebuilds.

### R1 — integer surface translation

Commit: `1f7d5a84879aa870253a2f01b9f544628b6245ab`

A `+128 px` smooth pan is implemented as ~`3.333333 px` camera increments. Because the canonical transform uses per-vertex `int(round(...))`, adjacent frames are not a rigid integer translation. All 39 changed frames showed nonuniform canonical point translation; no exact rigid translation was found.

Result: reject naïve `Surface.scroll`, simple source-rect translation and Terrain-style exposed-boundary refill for pixel-exact Fog.

### R2 — phase-based raster reuse

Commits:

```text
0ab02f136ac426e7da8f1ab4ec63ff54b320131f
682a1b96dddc9abf3a40fa8b751703d6a5c35ee3
```

The final directed generalization matrix covered 90 workloads across zooms, fractional starts and six directions. Interior pixel mismatches remained, so overscan could not repair the error.

Result: `ABANDON_PHASE_RASTER_REUSE`.

### R3 — global world extrema -> one screen rect -> one viewport clip

Commit: `def78b9f101bd52a7b71d8f8cb79de3e6bc82d70`

Runtime workloads looked promising, but direct deterministic tests found clipping counterexamples, including a contiguous production-reachable two-tile topology. The failed identity was:

```text
clip(union(all tile rects)) != union(clip(each tile rect))
```

Result: reject this specific global-extrema/one-clip construction. This does not reject all presentation-bounds redesigns; the later Fog-content bound uses a different invariant.

## 5. Final production closeout

Closeout commit:

```text
be28ca172162cac8a4f684507620fca0a661754e
perf: add camera fog closeout reassessment
```

All fine-grained timers and feasibility observers were disabled. Effective production configuration was:

```text
geometry              fused
corner offsets        precomputed
world corners         cached
presentation bounds   fog_content
Fog                   ON
units                 stationary
```

The world-corner working set required by Fog was already warm at closeout; every measured epoch had zero cache misses.

Primary duplicate short-pan result at zoom `0.15`:

```text
C1 tile loop          13.647 ms
C3 tile loop          14.319 ms
aggregate             13.983 ms / rebuild
Fog full build        14.116 ms / rebuild
frame mean            27.399 ms
FPS                    36.51
replicate drift         4.81%
```

Workload scaling check:

```text
zoom                  0.15           0.50
Fog polygons          6393           2212.33
Fog tile loop         13.983 ms       7.638 ms
```

The absolute Fog cost fell materially when the actual Fog workload fell. The higher normalized cost per polygon at zoom `0.50` is consistent with larger screen-space polygons and is not treated as an invariant violation.

The final residual classification is:

```text
EXPLAINED-WORKLOAD-BOUND
CASE-CLOSEOUT-READY / RECOMMEND-CLOSED
```

## 6. Historical trajectory

The original and final production numbers are from different commits, so this is supportive history, not a same-commit A/B:

```text
original canonical short-pan tile loop     27.918 ms
final uninstrumented production closeout   13.983 ms
absolute reduction                         13.935 ms
supportive reduction                        49.91%
```

Individual L1/L2/L3/L4 claims above are supported by their own controlled same-commit A/B experiments.

## 7. What CLOSED means

CLOSED means:

- the problem is reproducible;
- camera/Fog invalidation behavior is attributed;
- the large accidental Python-side geometry costs were decomposed and reduced;
- the selected changes preserve pixel semantics;
- plausible structural reuse designs were tested rather than assumed;
- remaining cost scales with actual Fog geometry/raster workload;
- no unexplained Camera->Fog pathology remains in the investigated model.

CLOSED does **not** mean that Fog camera rebuild cost is zero or that the extreme 91x91 / 5000-unit stress workload reaches 60 FPS while continuously panning.

A future redesign that changes the raster backend or representation may legitimately target the remaining ~14 ms class workload as a new performance case.

## 8. Scope boundary

Two originally observed user-visible symptoms are intentionally **not** claimed as solved by this case:

1. unit movement revealing the Fog boundary can hitch;
2. manually toggling Fog with key `1` can hitch.

Those paths are not Camera->Fog geometry invalidation and should be investigated separately if they remain user-visible.

## 9. Reproduce the final closeout

Checkout the validated tag:

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout perf-2026-09-camera-fog-full-rebuild-closed
uv sync
```

Start the canonical environment:

```bash
STAR_SCALE_HARNESS_SOCKET=/tmp/star-scale-closeout.sock \
uv run rotk_env/main.py \
  --skip-start \
  --scenario TestMap-8K-scale-5000 \
  --mode real_time \
  --players human_vs_two_ai \
  --seed 42 \
  --no-hub \
  --profile
```

Run:

```bash
uv run tools/fog_camera_closeout.py \
  --socket /tmp/star-scale-closeout.sock \
  --warmup 1 \
  --between-epochs 0.25 \
  --timeout-per-epoch 60 \
  --stationary-frames 120 \
  --output results/fog-camera-attribution/fog-camera-closeout.json
```

Expected final signature:

```text
stationary:                 0 camera changes / 0 Fog rebuilds
primary z=.15 tile loop:    ~14 ms / rebuild
primary replicate drift:    <10%
world-corner cache misses:  0 in measured epochs
z=.50 tile-loop cost:       materially below z=.15
residual classification:    EXPLAINED-WORKLOAD-BOUND
closeout recommendation:    CASE-CLOSEOUT-READY / RECOMMEND-CLOSED
```

## 10. Evidence and integrity

This case owns 44 Camera->Fog raw JSON artifacts under [`results/`](results/). They include causal attribution, controlled optimization A/Bs, structural feasibility/negative results, Fog-content correctness/A-B evidence and the final uninstrumented closeout.

Verify byte integrity from this experiment directory:

```bash
shasum -a 256 -c artifacts/SHA256SUMS
```

All 44 entries must report `OK`.

The earlier discrete Terrain camera-stress reproduction remains canonically owned by the Terrain case and is cross-referenced rather than duplicated.

## 11. Related records

- [`manifest.yaml`](manifest.yaml)
- [`analysis.md`](analysis.md)
- [`decision.md`](decision.md)
- [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)
- [`../2026-09-terrain-presentation/`](../2026-09-terrain-presentation/)
- [`../2026-09-fog-presentation-bounding/`](../2026-09-fog-presentation-bounding/)
