# Decision — Camera Geometry Change -> Fog Full Rebuild

**Status:** proposed  
**Decision date:** 2026-09-02  
**Validated STAR commit:** N/A — investigation remains open  
**Validated STAR tag:** N/A

## 1. Decision

Do **not** optimize Fog camera-geometry handling yet. First build a deterministic continuous-camera attribution workload and explicit Fog rebuild counters/reasons so that pan, zoom, threshold crossings and small per-frame camera changes can be separated. The current discrete stress is sufficient to reproduce a serious Fog rebuild tail, but not sufficient to choose the correct production design.

## 2. Decision drivers

- `fog_surface_full_build` reaches ~25-30 ms in the archived discrete camera-stress runs.
- `MapRenderSystem` reaches ~39-46 ms and epoch worst slow frames reach ~56-68 ms.
- Terrain opaque-cache rebuild cost is much smaller (~2.5 ms class) and does not explain the tail.
- The camera workload changes state only every 0.75 s and therefore does not measure realistic continuous-motion invalidation frequency.
- Pan and zoom are currently mixed in one pattern.
- The exact Fog full-rebuild trigger condition has not been causally separated.

## 3. Measured alternatives

| Option | Relevant evidence | Decision |
|---|---|---|
| Optimize Terrain rebuild further | Terrain build cost is much smaller; Legacy/Opaque tail nearly identical | Reject as explanation for this issue |
| Immediately make Fog rebuild incremental | Plausible but exact invalidation mechanism not yet attributed | Defer |
| Translate/reuse Fog geometry during pan | Plausible but pan-only behavior not yet measured | Defer |
| Build continuous-camera attribution first | Directly resolves missing frequency/trigger evidence | Accept as next step |

## 4. Why this option

The current evidence identifies an expensive operation but not yet the minimal condition that triggers it. Choosing a fix now would violate STAR's `Instrument -> Attribute -> Optimize` discipline and could replace one rebuild mode with unnecessary complexity.

The next experiment should answer:

```text
When camera state changes, how often does Fog actually full-rebuild?
Which changes cause it: pan, zoom, boundary crossing, or every offset delta?
How much of the tail belongs to rebuild preparation vs Surface construction?
```

Only after these questions are measured should a production design be selected.

## 5. Why not the alternatives

### Immediately cache/translate the Fog Surface during pan

Not selected yet because we do not know whether small pan deltas already reuse enough state or whether only certain geometry transitions trigger rebuilds.

### Make every Fog geometry update incremental

Potentially over-engineered. The workload must first show the actual rebuild frequency and trigger distribution under smooth motion.

### Treat the issue as a Terrain regression

Rejected by controlled Legacy/Opaque stress results. Terrain opaque presentation still improves the renderer path, while the large transition tail remains essentially unchanged.

## 6. Headroom and scaling rationale

No new production default or capacity is selected in this case. The next threshold is evidentiary:

```text
minimum evidence required before optimization
= explicit full-rebuild frequency and reason under controlled continuous pan/zoom modes
```

## 7. Risks / trade-offs

- Leaving the issue open means discrete camera geometry transitions can still produce large render tails.
- A continuous-camera harness adds testing/instrumentation code, but that cost is preferable to choosing the wrong Fog architecture.
- The final solution may be backend-specific if the dominant cost remains Pygame Surface construction/composition.

## 8. Revisit when

This decision MUST be revisited as soon as:

- continuous pan-only stress exists;
- zoom-only stress exists;
- Fog full-rebuild count/reason is measured per camera-change frame;
- the exact invalidation condition is identified;
- a candidate fix can be compared under the same controlled workload.

## 9. Provenance

- Reproduction: [`README.md`](README.md)
- Experiment identity: [`manifest.yaml`](manifest.yaml)
- Current analysis: [`analysis.md`](analysis.md)
- Canonical raw evidence: [`../2026-09-terrain-presentation/results/validation/camera-stress/`](../2026-09-terrain-presentation/results/validation/camera-stress/)
- Canonical checksums: [`../2026-09-terrain-presentation/artifacts/SHA256SUMS`](../2026-09-terrain-presentation/artifacts/SHA256SUMS)
