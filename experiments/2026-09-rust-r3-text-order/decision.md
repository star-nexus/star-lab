# Decision — preserve semantic text without changing game rules

**Status:** accepted functional checkpoint. **Date:** 2026-09-23.
**Validated STAR commit:** `24215823c74a79774d38cc0b354b6e3d091a3b86`. **Tag:** `rust-kernel-r3d3b-2026-09-23`.

## 1. Decision

Enable preserve_order in locked serde_json, retaining explicit ordered gameplay containers. Use shift_remove for JSON object deletion, preserving remaining relative order. Reproduce Python Unicode15.1 printability with a generated 713-range native table and binary lookup, retaining an ASCII fast path. API10 rejects old wheels; schema5/oracle marker unchanged. Top-level strings remain raw, nested strings use repr.

## 2. Decision drivers

Benchmark-visible text equality, first-report raw-type preservation, export/reset continuity, deterministic gameplay order, no Python callback in native hot loops, no dependency version upgrade.

## 3. Measured alternatives

| Option | Causal result | Decision |
| --- | --- | --- |
| API9 sorted JSON + ASCII-only repr | Four of seven state comparisons differ | Keep as reproducible before |
| API10 ordered JSON + pinned Unicode repr | Seven of seven state comparisons match; all broad guards pass | Use on migration branch |

## 4. Why this option

It restores the normalized oracle at the parsing/representation boundary, including delayed label conversion. It does not normalize inputs differently from Python or change combat/movement rules.

## 5. Why not the alternatives

Pre-stringifying incoming labels would change the legacy first-report raw type; sorting Python inputs would change the approved oracle; ignoring the string difference would invalidate exact benchmark comparison. Rust's Unicode version/escape syntax is not a substitute for the pinned CPython oracle. These are design rejections, not measured performance alternatives.

## 6. Scaling rationale

No throughput/headroom parameter was selected or measured. ASCII repr remains a direct check, non-ASCII uses binary lookup. Ordered containers may alter allocation/lookup costs; capacity must still be measured at R4/R5. No speedup claim.

## 7. Risks / trade-offs

The Unicode table is explicit versioned compatibility data. Object insertion order now survives native state; consumers must not rely on the old incidental alphabetical order. Explicit gameplay iteration and decoded list/text equality remain mandatory.

## 8. Revisit when

Oracle/Python/Unicode upgrades, new permissive handlers, new object-to-text consumers, or capacity evidence identifies material container overhead. VLM/BOT/network host and remaining input risks stay open; default backend remains Python.

## 9. Provenance

[README](README.md), [manifest](manifest.yaml), [analysis](analysis.md), [results](results/). Final documentation-only change is proven equivalent to measured runtime/tests. G006 and G013 retain before history in the production ledger.
