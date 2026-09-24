# Decision — R3k4 encoded read-segment facts

**Status:** accepted  
**Decision date:** 2026-09-24  
**Validated STAR commit:** `3892f95af6638e213f1b842fd9c0fe4b7b3dab80`  
**Validated STAR tag:** `rust-kernel-r3k4-2026-09-24`

## 1. Decision
Share immutable Arc-owned encoded faction fields and Unit base panels within a write-free segment. Capture per-request ownership/commandability separately; serde serializes already validated kernel-created RawValue fields.

## 2. Drivers
Reduce evidenced repeated tree cloning/encoding, retain exact benchmark information, and make response lifetime independent of subsequent world writes.

## 3. Alternatives measured
| Option | Exact Agent/state guards | 5000Unit public8 median | Decision |
| --- | --- | --- | --- |
| Per-request JSON trees | pass | 88.366ms | replace |
| Shared encoded facts | pass | 23.552ms | keep |

## 4. Reason
Single/batch/diagnostic paths use the same representation; counters demonstrate one encoding per shared fact. Existing counter timing and query/write boundaries remain unchanged. Regression and explicit mixed-write tests validate the lifetime model.

## 5. Alternatives not chosen
No cross-frame/TTL snapshots, field dropping, approximate visibility, custom unsafe raw-JSON concatenation or request admission delay. Full multithreading is separate work and not inferred from Arc.

## 6. Headroom / defaults
No pool size or capacity parameter selected. Thread parameters remain serial. API15 guards the matching extension and new diagnostic counters; schema/rules/default backend unchanged.

## 7. Risks / trade-offs
Response bytes must still be emitted per Agent, and Python decode still scales with output. Cached encoded fields are immutable, but building gameplay facts remains serial. Future parallel changes must preserve admission and stats order, permission capture and query state provenance.

## 8. Revisit
Parallel read task introduction; new authoritative/cold-component write paths; changed response schema or serialization; larger output/Agent scale. Keep exact response/state and lifecycle guards.

## 9. Provenance
README.md, analysis.md, manifest.yaml, results/ and artifacts/SHA256SUMS.
