# Decision — Fog Presentation Bounding

**Status:** accepted  
**Decision date:** 2026-09-02  
**Validated STAR commit:** `6a61115ab29a0c4aeb39fa8b74c7cbcded314180`  
**Validated STAR tag:** N/A — no separate Fog-presentation milestone tag has been created

## 1. Decision

Keep the viewport-sized Fog semantic Surface and its incremental patch semantics, but bound the final presentation to a cached map-content screen-space rectangle computed during full rebuild. Do not redesign Fog semantics merely to reduce presentation cost.

## 2. Decision drivers

- Presentation-only suppression causally removed ~3.04 ms from the Fog batch-blit path.
- The bounded rectangle cuts submitted Fog pixels from 3,144,640 to 1,224,510, a 61.06% reduction.
- Production validation reduces RenderEngine by ~1.99 ms while preserving Fog ON and the existing semantic update path.
- The rectangle is computed only during full rebuild, so the fix does not add a new steady-state map scan.
- Keeping the semantic Surface preserves stable screen-space dirty-patch coordinates and existing view/faction invalidation semantics.

## 3. Measured alternatives

| Option | Relevant causal metrics | System metrics | Decision |
|---|---|---|---|
| Keep full-window presentation | ~3.145M pixels/frame | `render_engine` ~5.425 ms baseline | Reject |
| Shrink/redesign semantic Fog Surface | Not required by evidence | Higher semantic risk | Reject |
| Bound only final presentation | 1.225M pixels/frame | `render_engine` ~3.433 ms | Accept |

## 4. Why this option

The controlled evidence shows that the expensive work lives at the presentation boundary. The accepted design changes exactly that boundary and leaves the already-correct incremental Fog semantics intact. The observed timer migration from batch blit to one bounded scalar blit is consistent with the code change and explains the gain.

## 5. Why not the alternatives

### Redesign the Fog semantic Surface

Rejected because there is no evidence that semantic storage is the steady-state bottleneck, and changing it would complicate incremental patches, screen-space coordinates and later clear-to-fog transitions.

### Recompute content bounds every frame

Rejected because it would replace a pixel-volume problem with avoidable steady-state geometry work. The accepted implementation computes the bounds only at an existing full-rebuild boundary.

### Disable or approximate Fog presentation

Rejected because benchmark semantics require Fog to remain visually and semantically correct.

## 6. Headroom and scaling rationale

The fix scales presentation cost with visible map-content area rather than full viewport area. It should be revisited when the relationship between viewport size and map-content area changes substantially.

## 7. Risks / trade-offs

- The bounded command becomes an `area=` scalar blit; this is acceptable because total pixel work is much lower.
- Camera/zoom changes can still trigger expensive Fog full rebuilds; that is a separate open investigation.
- The optimization is partly tied to the Pygame/SDL software-rendering cost model.

## 8. Revisit when

- Fog semantic representation changes;
- the renderer backend changes;
- the map can visually occupy regions outside the cached presentation bounds without a full rebuild;
- viewport/map geometry changes make the current bounding rule insufficient;
- camera-induced full rebuild behavior is redesigned.

## 9. Closure status

The engineering decision and performance validation are accepted. Formal `PROTOCOL.md` CLOSED status is still pending archived regression-test evidence for the validated commit. No raw result needs to be regenerated for that closure step.

## 10. Provenance

- Reproduction: [`README.md`](README.md)
- Experiment identity: [`manifest.yaml`](manifest.yaml)
- Root-cause analysis: [`analysis.md`](analysis.md)
- Fixed raw evidence: [`results/`](results/)
- Pre-fix baseline: [`../2026-09-render-engine-attribution/results/causal-ablation/`](../2026-09-render-engine-attribution/results/causal-ablation/)
