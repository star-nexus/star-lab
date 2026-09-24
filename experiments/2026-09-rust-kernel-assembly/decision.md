# Decision — R3k3 owned JSON assembly

**Status:** accepted  
**Decision date:** 2026-09-24  
**Validated STAR commit:** `a3ff47b796537e2a543d42da6094aa13d64f6e63`  
**Validated STAR tag:** `rust-kernel-r3k3-2026-09-24`

## 1. Decision
Move already-owned JSON arrays into the final response/envelope. Retain copies required for independent responses and original batch cache ownership.

## 2. Decision drivers
Remove evidenced redundant CPU/allocation work without changing benchmark information, admission/permission checks, statistics order, or the Python API.

## 3. Measured alternatives
| Option | Identical response/state | 5000Unit public eight-query median | Decision |
| --- | --- | --- | --- |
| serialize-to-Value assembly | yes | 173.365ms | replace |
| ownership transfer | yes | 95.241ms | keep |

## 4. Why this option
Small native-only change, same fields/work counters and full regression behavior; benefit reaches authenticated public batches. Source explains removal of recursive reconstruction, while A/B provides measured effect.

## 5. Why not the alternatives
Cross-frame caching, dropping fields, delaying requests and approximate visibility would change benchmark semantics and are unnecessary for this improvement. A shared/streaming response representation remains a future option, not implemented here.

## 6. Headroom and scaling rationale
No tuning constant, capacity recommendation or default thread count is selected. API14 remains compatible; exact source/wheel SHA identifies the performance checkpoint.

## 7. Risks / trade-offs
A response still needs independent ownership when cached facts are reused. Move only arrays whose old owner is finished. Full output and encode/decode costs remain proportional to payload. No allocator counter or whole-frame benchmark is claimed.

## 8. Revisit when
Read-only parallel tasks change ownership requirements; a borrowed/serialized shared response representation is introduced; profiling identifies remaining shared copies or encoding as dominant. Preserve exact state/response/permission and lifecycle guards.

## 9. Provenance
See README.md, manifest.yaml, analysis.md, results/ and artifacts/SHA256SUMS.
