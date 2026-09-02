# Decision — RenderEngine Queue-Drain and Presentation Attribution

**Status:** accepted  
**Decision date:** 2026-09-02  
**Validated STAR commit:** `6e8c151494de2b37071ecdcd5f1898b7387e057a`  
**Validated STAR tag:** N/A — no separate attribution milestone tag was created

## 1. Decision

Do not spend the next optimization cycle rewriting RenderManager queue packing, command ordering, or batch-list construction. Treat Fog presentation and Terrain presentation as two independent production optimization cases, because controlled causal ablations show that they account for roughly 81% of the normal RenderEngine cost while Python queue packing is only ~0.2 ms.

## 2. Decision drivers

- `render_queue_submit` accounts for approximately 98% of RenderEngine queue-drain time.
- `render_batch_pack` is only ~0.23 ms and therefore cannot explain the multi-millisecond bottleneck.
- Fog presentation suppression removes ~3.04 ms specifically from `render_batch_blits`.
- Terrain presentation suppression removes ~1.37 ms specifically from `render_scalar_execute`.
- Queue topology is already highly consolidated and does not show pathological fragmentation.
- Pixel diagnostics show one viewport-sized Surface dominates submitted pixel volume.

## 3. Measured alternatives

| Option | Relevant causal metrics | System metrics | Decision |
|---|---|---|---|
| Rewrite queue packing | `render_batch_pack` ~0.23 ms | Cannot recover multi-ms hot path | Reject as current target |
| Rework batching/order | 4 actual multi-blit batches; one dominant batch | No fragmentation signature | Reject as current target |
| Bound Fog presentation | Fog-off `batch_blits -3.04 ms` | `render_engine -2.98 ms` | Promote to dedicated case |
| Rework Terrain presentation | Terrain-off `scalar -1.37 ms` | `render_engine -1.31 ms` | Promote to dedicated case |

## 4. Why this option

The decision follows localized causal responses rather than aggregate FPS. Fog suppression changes the batch-blit timer while leaving the scalar path effectively unchanged; Terrain suppression changes the scalar timer while leaving the batch path effectively unchanged. This is the signature expected if the two Surface submissions are independent dominant costs.

By contrast, queue packing and queue topology were measured directly and are too small / too consolidated to justify architectural work at this stage.

## 5. Why not the alternatives

### Rewrite RenderManager queue structures

Rejected because the measured Python packing cost is only a few tenths of a millisecond. Even a perfect implementation would leave the dominant Surface work untouched.

### Increase batching aggressiveness

Rejected because the queue already produces only four true multi-blit batches and one very large batch. The expensive batch is expensive because of pixel volume, not because it is fragmented.

### Optimize clipping

Rejected because diagnostic clipping removed only ~648 pixels from ~3.39M source pixels. There is no meaningful clipping waste to recover in this workload.

### Native/Rust rewrite

Rejected as premature. The stable hot boundary is Surface composition/submission in Pygame/SDL, not Python queue iteration.

## 6. Headroom and scaling rationale

This is an attribution decision rather than a capacity decision. The important scaling trigger is whether future workloads move the dominant cost away from Surface presentation.

```text
current measured hot boundary
= Fog presentation + Terrain presentation

future trigger
= queue preparation/order becomes a material fraction of RenderEngine after presentation work is reduced
```

## 7. Risks / trade-offs

- The attribution is backend-specific; a GPU renderer can move the bottleneck elsewhere.
- Aggregate FPS varies across fresh processes, so subsystem-local metrics must remain the primary causal evidence.
- Removing the two dominant presentation costs can expose a new lower-level renderer frontier; this decision does not claim the remaining ~1 ms is already optimal.

## 8. Revisit when

This decision MUST be revisited when any of the following occurs:

- the renderer backend changes away from Pygame/SDL Surface submission;
- `render_batch_pack` or RenderEngine parent self becomes a material share after later optimizations;
- queue topology changes substantially;
- new workloads introduce many ordering barriers or nonbatchable commands;
- a future profiler shows presentation is no longer the dominant queue-drain cost.

## 9. Provenance

- Reproduction: [`README.md`](README.md)
- Experiment identity: [`manifest.yaml`](manifest.yaml)
- Root-cause analysis: [`analysis.md`](analysis.md)
- Raw evidence: [`results/`](results/)
- Integrity metadata: [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)
