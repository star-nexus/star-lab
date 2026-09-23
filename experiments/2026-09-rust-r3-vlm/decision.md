# Decision — keep VLM image work at the Python display boundary

**Status:** accepted functional checkpoint. **Date:** 2026-09-23.
**Validated STAR commit:** `30c4b76c152857c98ff45fc7952af9ceb758059e`. **Tag:** `rust-kernel-r3d3c-2026-09-23`.

## 1. Decision

Rust performs authoritative authorization and structured projection; Python copies/encodes the existing framebuffer using the same helper as the legacy handler. Keep the explicit action allowlist and original error/counter semantics. API11 enforces matching adapters; schema5 and oracle unchanged.

## 2. Decision drivers

Same Benchmark inputs, no per-Unit language crossings, no rendering or Python callbacks inside Rust, correct request ordering and lifecycle fencing. Python still owns graphics and UI by the approved architecture.

## 3. Measured alternatives

| Version/check | Result | Decision |
| --- | --- | --- |
| API10 enabled VLM |54 unimplemented calls|Retain before evidence|
| API11 structured native + display attachment |54 full differential cases,1935 regressions,4 Cocoa byte comparisons pass|Accept on migration branch|
| Initial raw framebuffer RGB equality guard |Fails while Python/Rust bytes equal|Retain diagnostic; not a migration equivalence criterion|
| Independent old/new alpha codec control |Same transformed stored bytes in both|Preserve historical encoding; version future correction separately|

## 4. Why this option

A shared media helper avoids duplicating legacy image/error behavior. Whole-batch prevalidation and detached JSON retain the existing no-prefix-on-decode-error contract and freeze future parameters across capture. Ordinary non-VLM requests keep the native batching path. One admission lock spans the cross-language attachment boundary.

## 5. Why not alternatives

Postponing all captures until after all actions would observe a later batch state. Forcing an Agent-specific view, synchronous redraw, PNG encoding or label correction would silently change the Benchmark visual contract. Callback rendering inside the Rust mutex violates the chosen kernel boundary and can deadlock/reenter state. These are design rejections, not performance measurements.

## 6. Scaling rationale

No throughput/headroom default chosen. Capture remains one copy/encoding per accepted successful VLM request; no cross-frame image TTL or sharing policy introduced. The admission lock preserves the current single-writer model; cost must be measured later, no parallel speedup claim.

## 7. Risks / trade-offs

Inherited current-window viewpoint, timing, TGA/PNG label mismatch and alpha transformation remain visible contract limitations, explicitly documented in the main GAP ledger. Caller uses the public Python RustRuntime, not low-level native JSON methods for complete media payloads. Display ownership remains an application responsibility.

## 8. Revisit when

A separately authorized VLM contract revision changes format/perspective/timing, network host integration needs owner-thread dispatch, or measured capacity motivates a defined image batching policy. Complete G008/G009 and R3 before R4/R5/default switch. Main merges still require annotated tag then squash.

## 9. Provenance

[README](README.md), [manifest](manifest.yaml), [analysis](analysis.md), results/commands.json and artifacts/SHA256SUMS. Final doc-only source difference is recorded; no source tag moved.
