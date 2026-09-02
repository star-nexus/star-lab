# Decision — Terrain Opaque Presentation Cache

**Status:** accepted  
**Decision date:** 2026-09-02  
**Validated STAR commit:** `54d17745098fb3fc4c43861d839e8dc40164c030`  
**Validated STAR tag:** N/A — no separate Terrain-presentation milestone tag has been created

## 1. Decision

Use a compact opaque RGB Surface as the **Terrain presentation representation**, while retaining the existing oversized `SRCALPHA` overscan Surface as the **Terrain construction representation**. Build the compact cache only when a new overscan cache is installed; use it for steady-state `area=` presentation.

## 2. Decision drivers

- Format diagnostics rule out a meaningful source/display RGB format mismatch.
- 96.13% of submitted Terrain pixels are already opaque in value.
- B -> C shows flattening alpha values while retaining `SRCALPHA` produces essentially no gain.
- C -> D isolates disabling `SRCALPHA` and reduces scalar execution by ~0.83 ms.
- Final same-commit production A/B reduces `render_scalar_execute` by ~0.963 ms and `render_engine` by ~0.889 ms.
- Camera stress retains ~0.645 ms RenderEngine improvement and does not create a new P95/P99/max pathology.
- The accepted design does not rewrite the already-verified overscan construction logic.

## 3. Measured alternatives

| Option | Relevant causal metrics | System metrics | Decision |
|---|---|---|---|
| Original large SRCALPHA Surface | A scalar ~2.440 ms | A RenderEngine ~3.529 ms | Reject |
| Compact SRCALPHA, RGBA preserved | A -> B scalar ~-0.22 ms | Secondary benefit only | Reject as final design |
| Compact flattened but still SRCALPHA | B -> C ~-0.02 ms | No meaningful gain | Reject |
| Compact opaque RGB | C -> D scalar ~-0.83 ms | Production RenderEngine ~-0.889 ms | Accept |

## 4. Why this option

The strongest orthogonal result is C -> D: compact geometry, pitch and final RGB output are held constant while the Surface changes from `SRCALPHA=true` to `SRCALPHA=false` with alpha mask zero. The large localized scalar reduction identifies the Pygame/SDL alpha Surface path as the dominant cost.

The production implementation preserves the abstraction boundary that the evidence supports:

```text
construction representation != presentation representation
```

This avoids contaminating Terrain build semantics with a backend-specific presentation optimization.

## 5. Why not the alternatives

### Only compact the backing Surface

Rejected as the final design because A -> B is a useful but much smaller effect and leaves the dominant SRCALPHA cost intact.

### Only flatten alpha values

Rejected because B -> C is effectively noise. Alpha values of 255 do not cause Pygame/SDL to automatically select the opaque fast path while the Surface retains `SRCALPHA` semantics.

### Use `.convert(screen)` as the opaque conversion

Rejected because the first experiment proved that this does not guarantee `SRCALPHA=false` on the measured platform. The production cache explicitly constructs a 32-bit RGB Surface with display RGB masks and alpha mask zero, and raises if `SRCALPHA` unexpectedly remains set.

### Rewrite Terrain overscan construction

Rejected because the construction path was already validated and is not the measured bottleneck. The lower-risk change is a representation boundary at cache installation.

## 6. Headroom and scaling rationale

The compact cache is approximately the actual content area rather than the full overscan backing area. For the validated workload it stores ~1.224M pixels, roughly 4.9 MB at 4 bytes/pixel.

The measured rebuild trade-off is:

```text
steady-state renderer gain       ~0.9 ms/frame
opaque cache max build           ~2.5 ms class under stress
overscan build-step max          ~4.16 ms mean max under stress
```

This is favorable for the measured camera pattern because rebuilds are infrequent relative to steady-state frames and do not materially worsen tail metrics.

## 7. Risks / trade-offs

- The optimization is deliberately backend-specific to Pygame/SDL software Surfaces.
- It adds one compact presentation copy per active Terrain overscan cache.
- Background/frame-clear color semantics must remain consistent with the precomposition step.
- Larger viewports can increase rebuild cost and should be remeasured.
- Smooth camera behavior was not measured by the discrete stress workload.

## 8. Revisit when

- renderer migrates away from Pygame/SDL software Surfaces;
- GPU-backed rendering is introduced;
- frame clear/background color semantics change;
- viewport scale causes opaque-cache rebuild to become a tail problem;
- Terrain introduces visual semantics that require preserved per-pixel alpha at final presentation;
- continuous-camera measurements show much higher cache-rebuild frequency than the discrete stress test.

## 9. Closure status

The engineering decision, root-cause attribution, fixed-camera A/B and camera-stress validation are accepted. Formal `PROTOCOL.md` CLOSED status remains pending archived regression-test evidence for the validated commit. The existing JSON and SHA256 evidence does not need to change for that closure step.

## 10. Provenance

- Reproduction: [`README.md`](README.md)
- Experiment identity: [`manifest.yaml`](manifest.yaml)
- Root-cause analysis: [`analysis.md`](analysis.md)
- Formal and intermediate evidence: [`results/`](results/)
- Integrity metadata: [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)
