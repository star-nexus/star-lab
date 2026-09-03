# Decision — Camera Geometry Change -> Fog Full Rebuild

**Status:** CLOSED  
**Decision date:** 2026-09-04  
**Final production fix:** `717932ec520ffc215ab45c32bd33cbb0fa5a68c2`  
**Validated STAR commit:** `be28ca172162cac8a4f684507620fca0a661754e`  
**Validated STAR tag:** `perf-2026-09-camera-fog-full-rebuild-closed`

## 1. Decision

Close `2026-09-camera-fog-full-rebuild`.

Keep the existing geometry-key full-rebuild semantics, but retain the four validated production optimizations developed during this investigation:

```text
1. fused transform + bounds pass
2. precomputed canonical hex-corner offsets
3. Fog-local camera-independent world-corner cache
4. Fog-content presentation bounds with true visible/no-Fog skip
```

Do not adopt integer raster translation, phase-based raster reuse or the tested global-world-extrema/one-clip presentation bound.

The final residual is classified:

```text
EXPLAINED-WORKLOAD-BOUND
```

No further optimization is required to close this case.

## 2. Decision drivers

### The invalidation mechanism is established

A stationary camera performs no Fog full rebuilds. Smooth short pan at zoom `.15` produces 39 camera-change frames and 39 Fog rebuilds. Long-pan and zoom may differ by one raw camera frame because the existing Fog geometry key rounds offsets to 3 decimals and zoom to 5 decimals.

The accurate engineering statement is:

> Fog full rebuilds occur on effectively every geometry-key-visible camera change.

### The original hot path was decomposed before optimization

The canonical pre-optimization short-pan tile loop was ~`27.9 ms`, of which ~`23.4 ms` was non-polygon work. Allocation was only ~`0.13 ms`; polygon rasterization was ~`4.4 ms` class.

Fine attribution identified repeated corner generation, screen transforms and repeated bounds scans as major Python-side costs.

### Each accepted optimization has controlled same-commit evidence

| Change | Commit | Primary causal result |
|---|---|---|
| Fused transform/bounds | `e9c69594...` | tile loop `28.015 -> 23.964 ms`, `-14.46%` |
| Precomputed corner offsets | `cafddc4e...` | tile loop `24.007 -> 19.972 ms`, `-16.81%` |
| World-corner cache | `46f8ab32...` | tile loop `20.714 -> 18.400 ms`, `-11.17%` |
| Fog-content bounds / skip | `717932ec...` | tile loop `18.211 -> 15.497 ms`, `-14.90%` |

The first three changes remove repeated geometry work. The fourth removes geometry entirely for currently visible/no-Fog tiles.

### Structural reuse was not assumed to be correct

Three superficially attractive designs were explicitly tested and rejected on pixel-exact correctness evidence:

1. **Rigid translation** — adjacent smooth-pan frames are not a uniform integer translation because canonical per-vertex rounding changes differently across vertices.
2. **Phase raster reuse** — a 90-workload directed matrix still produced interior mismatches; overscan cannot repair interior error.
3. **Global extrema -> one clip** — direct deterministic tests found viewport-clipping counterexamples, including production-reachable contiguous topology.

These negative results justify retaining a full rebuild at geometry-key changes rather than introducing an incorrect reuse mechanism.

### The accepted Fog-content bound passed semantic and runtime equivalence

Before production adoption:

```text
510 / 510 direct semantic cases exact
492 / 492 runtime full-rebuild comparisons exact
17 / 17 visible_tiles content-change frames exact
0 mismatches
```

The invariant is not legacy-rect equality. It is:

```text
alpha_support(surface) ⊆ presentation_rect
```

plus exact final framebuffer equivalence.

### The closeout residual scales with actual Fog workload

Final uninstrumented production closeout:

```text
primary z=.15 Fog tile loop      13.983 ms / rebuild
primary Fog full build           14.116 ms / rebuild
replicate drift                    4.81%
cache misses across measured runs  0
```

At zoom `.50`, Fog polygon workload falls from `6393` to `2212.33` polygons/rebuild and absolute Fog tile-loop cost falls to `7.638 ms`.

That is the expected behavior of real geometry/raster work, not a fixed unexplained camera penalty.

## 3. Why the issue is CLOSED even though ~14 ms remains

Closure is based on causality, not an arbitrary FPS threshold.

The investigated issue was:

> Why does camera movement make Fog rebuild unexpectedly expensive, and which of that cost is avoidable without changing pixel semantics?

That question is answered.

The remaining low-zoom cost corresponds to processing `6393` actual Fog polygons per rebuild. Further reduction would require a new rendering representation/backend or a newly proven exact reuse mechanism. That is a different optimization problem.

Therefore CLOSED means:

```text
no unexplained Camera->Fog pathology remains
```

It does not mean:

```text
Fog rebuild cost == 0
continuous-pan FPS == 60 on the extreme 91x91 workload
```

## 4. Selected production design

### 4.1 Preserve geometry-key semantics

Do not change camera rounding or invalidation merely to reduce rebuild frequency. Existing semantics are part of the renderer behavior validated throughout this investigation.

### 4.2 Fuse local screen geometry work

Transform each canonical corner exactly once and accumulate bounds in that same loop.

### 4.3 Precompute/copy only camera-independent geometry

Hex shape offsets and world-space tile corners are independent of camera offset and zoom and can be cached without changing raster semantics.

### 4.4 Use Fog content, not transparent map content, to bound presentation

The semantic surface remains viewport-sized for stable patch coordinates. `presentation_rect` only needs to conservatively contain actual Fog alpha.

Full rebuild:

```text
visible tile
  -> semantic membership check
  -> skip all Fog geometry

fogged tile
  -> canonical geometry
  -> polygon draw
  -> union clipped rect into presentation bounds
```

Incremental patch:

```text
new Fog outside current bound
  -> draw + expand bound immediately

reveal / clear
  -> do not shrink conservative bound

next geometry full rebuild
  -> recompute fresh tight Fog-content bound
```

## 5. Rejected alternatives

### Integer `Surface.scroll` / exposed-edge refill

**Decision:** Reject.

Reason: 39/39 smooth-pan changed frames showed nonuniform canonical point translation. There was no exact rigid integer translation compatible with canonical rounding.

Revisit only if the rendering representation changes such that translation is defined in a different exact coordinate domain.

### Same-phase raster cache

**Decision:** Reject.

Reason: recurrent phases produced interior mismatches in the directed generalization matrix. Boundary overscan cannot repair interior pixel differences.

Revisit only with a new exact phase definition and a proof/test matrix that eliminates all interior mismatch populations.

### Global world extrema -> one screen rect -> one viewport clip

**Decision:** Reject the tested construction.

Reason: clipping does not commute with global union. Direct tests produced 56 mismatches, including production-reachable contiguous topology.

This rejection is intentionally narrow. It does **not** prohibit other presentation-bound representations.

### Native/Rust migration

**Decision:** Not selected.

Reason: the case exposed large removable algorithmic/Python work before any need to move the hot path native. The protocol principle remains `Profile first. Native second.`

A future backend redesign may still be justified for the remaining polygon workload, but this case does not establish that requirement.

## 6. Aggregate metrics and noise policy

End-to-end frame/FPS improvements support the accepted changes but are not the primary causal metrics.

Examples of unrelated contamination observed during the investigation include:

- Gen2 GC pauses inside `unit_static_draw`;
- Terrain overscan/presentation-cache rebuilds under zoom;
- render-batch work whose screen-space cost changes with zoom.

The final closeout explicitly avoids deciding closure from P99/max frame.

Representative long-pan worst frame:

```text
frame                  49.477 ms
unit_static_draw max   23.958 ms
GC pause               ~21.829 ms
Fog tile loop          normal ~14–15 ms class
```

Classification:

```text
TAIL-CONTAMINATION-OUTSIDE-FOG
```

## 7. Historical performance trajectory

For engineering history only:

```text
initial canonical short-pan     ~27.918 ms / Fog tile loop
final production closeout       ~13.983 ms / Fog tile loop
supportive change                -13.935 ms / -49.91%
```

This comparison crosses source commits and is not presented as a controlled A/B. Every accepted optimization has its own same-commit evidence.

## 8. Regression / validation state

Final Fog-content implementation validation:

```text
Fog focused suite      881 passed
canonical suite        1683 passed, 11 known failed
new regressions        0
```

Final closeout/infrastructure state:

```text
closeout + attribution     23 passed
Fog focused suite          896 passed
canonical suite            1698 passed, 11 known failed
known failure set unchanged
py_compile                 pass
git diff --check           pass
```

The 11 canonical failures were the existing baseline failure set and were not introduced by this case.

## 9. Performance Frontier decision

Do **not** update `records/performance-frontier.md` for this case.

This investigation closes a renderer pathology and records a local subsystem improvement; it does not establish a new validated maximum 5K/10K/20K/50K scalability frontier under a complete benchmark workload.

## 10. Scope boundary / separate future cases

This closure does not claim to solve:

- unit movement revealing a Fog edge and producing a hitch;
- manual Fog toggle with key `1` producing a hitch.

Those are different trigger paths. If still reproducible, archive them as separate investigations rather than reopening this Camera->Fog geometry case without evidence that its closure assumptions are invalid.

## 11. Revisit when

Revisit this decision only if one of the following becomes true:

- a supported platform/backend changes polygon or Surface semantics materially;
- a new exact translation/raster-reuse representation is demonstrated against the full pixel-equivalence matrix;
- map scale / Fog polygon count expands enough that the explained workload-bound residual becomes a new product bottleneck;
- camera invalidation semantics intentionally change;
- evidence appears that the current world-corner cache invalidates unexpectedly in production;
- a future renderer can preserve exact output while avoiding per-frame polygon reconstruction through a different architecture.

A high absolute Fog cost by itself is not sufficient reason to reopen this specific case; the new evidence must invalidate the current causal/closure model or define a distinct optimization objective.

## 12. Provenance

- Reproduction and commands: [`README.md`](README.md)
- Experiment/source identity: [`manifest.yaml`](manifest.yaml)
- Causal chain: [`analysis.md`](analysis.md)
- Local raw artifacts: [`results/`](results/)
- Integrity: [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)
- Earlier discrete stress evidence: [`../2026-09-terrain-presentation/`](../2026-09-terrain-presentation/)
