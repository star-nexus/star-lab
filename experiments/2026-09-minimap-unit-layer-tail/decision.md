# Decision — MiniMap Unit-Layer Tail Latency and 5K 60Hz Core Stress Boundary

**Status:** accepted / CLOSED  
**Decision date:** 2026-09-06  
**Validated STAR commit:** `c5dd895e242b46f193050d8212fcc45b625ad885`  
**Validated STAR tag:** N/A — exact source SHA is recorded; no separate annotated milestone tag was created

## 1. Decision

For the 5000-unit Core 60Hz engineering stress profile, disable only the dynamic MiniMap unit-dot layer through the explicit scale-only `STAR_SCALE_MINIMAP_UNITS=off` override. Preserve normal interactive MiniMap behavior by default. Do not hide MiniMap cost by changing profiler accounting; remove this auxiliary O(Nresident) work from the Core stress execution path instead.

Treat the 5000-resident / 2500-moving / Fog-ON / staggered 50% point as `BORDERLINE ACCEPT` for the current engineering milestone. Its three-run controlled-work P99 median is `16.68202856 ms`, approximately `0.012 ms / 0.07%` above the unchanged literal `16.67 ms` stress threshold. Record the strict threshold result faithfully as a boundary fail, but stop binary searching at 37.5% because the practical conclusion is already sufficient: the current 5K Core runtime sits approximately at the 50%-moving 60Hz stress boundary.

## 2. Decision drivers

- STAR is an Agent/ENV benchmark; auxiliary UI must not define authoritative environment capacity.
- The controlled 25% ON/OFF ablation isolates the MiniMap dynamic unit layer as the dominant tail mechanism.
- The MiniMap refresh is an O(Nresident) presentation pulse rather than essential world simulation work.
- Closed historical GC, Vision-cache, culling, Fog, and movement-continuity signatures are absent.
- The Phase-3 measurement infrastructure already cleanly separates controlled work, platform input, present, wait, and uninstrumented time; no new measurement framework is needed.
- The 50% point is repeatably near 16.67 ms without evidence of a new pathological cliff.

## 3. Measured alternatives

| Option | Relevant causal metrics | System metrics | Decision |
|---|---|---|---|
| Full interactive MiniMap unit layer ON | 15 Hz refresh; full resident-unit redraw; ~4 ms refresh pulse | 25% controlled P99 16.808029 ms; over-budget frames present | Reject for Core 60Hz stress profile |
| Hide MiniMap timing from `controlled_work` but still execute it | Accounting changes, wall-clock work unchanged | Main-thread pulse remains | Reject |
| Dynamic MiniMap unit layer OFF in Core stress profile | `minimap_unit_refreshed=0`; terrain/camera/interaction remain | 25% controlled P99 13.666347 ms; 0 over-budget frames | Accept |
| Rewrite MiniMap now as dirty-cell incremental | Not yet measured | Likely removes O(N) redraw | Defer; not required to close current measurement contamination |
| Move MiniMap to async worker now | Not yet measured | Could remove critical-path work | Defer; broader concurrency architecture work |
| Continue exact density binary search at 37.5% | Would refine a boundary already within ~0.07% of 60Hz target | Additional branch without changing current engineering decision | Reject for now |

## 4. Why this option

The chosen option follows the measured causal chain rather than aggregate FPS intuition.

The decisive evidence is:

```text
MiniMap units ON at 25%
  controlled P99 = 16.80802934 ms
  controlled max = 19.437584 ms

MiniMap units OFF at 25%
  controlled P99 = 13.66634692 ms
  controlled max = 14.082585 ms
  over-budget controlled frames = 0
```

The alternative hypothesis that crossing count itself drives the 25% tail was instrumented and rejected. This prevents a future engineer from reopening movement-continuity or rewriting position-commit logic in response to the same signature.

## 5. Why not the alternatives

### Do not change profiler accounting to make the number pass

Rejected because the MiniMap work consumes real main-thread time. Excluding it from `controlled_work` while continuing to execute the same O(N) redraw would improve a metric without improving realtime execution.

### Do not immediately rewrite MiniMap

Rejected for the current milestone because the Core stress profile can cleanly isolate an auxiliary presentation layer without altering production defaults. A dirty-cell incremental or asynchronous MiniMap remains a valid future Full Interactive optimization, but it is not required to answer the current system-scale question.

### Do not reopen old performance cases

Rejected because the current signature does not match the closed GC, Vision-cache, cull, Fog-presentation, macOS SDL, or movement-continuity cases.

### Do not continue 37.5% binary search

Rejected because the 50% three-run median differs from the literal 16.67 ms target by only `0.01202856 ms`, about `0.07%`, while steady-state subsystem behavior is repeatable and non-pathological. The engineering question is sufficiently answered without pretending that the literal threshold was met.

## 6. Headroom and scaling rationale

Current 5K Core stress interpretation:

```text
25% moving / 1250 units
  -> CLEAR PASS
  -> controlled P99 13.66634692 ms

50% moving / 2500 units
  -> literal strict threshold: boundary FAIL
  -> three-run median controlled P99 16.68202856 ms
  -> engineering disposition: BORDERLINE ACCEPT
```

The current practical 60Hz stress boundary is therefore approximately the 50%-moving point for this host/scenario, not a precisely binary-searched density maximum.

This is distinct from canonical benchmark runtime semantics. A 30 Hz canonical competition/runtime mode and a 60 Hz engineering stress mode may coexist, but that runtime-policy split is not claimed as validated by this case alone.

## 7. Risks / trade-offs

- Core stress runs do not display live MiniMap unit dots, so they are not a complete interactive-client workload.
- Full Interactive performance with dynamic unit dots remains lower until MiniMap is redesigned.
- `BORDERLINE ACCEPT` must not be rewritten later as `P99 <= 16.67`; the literal median is `16.68202856 ms`.
- Exact host macOS minor version and memory capacity were not captured in the canonical raw artifacts.
- The current conclusion is host/scenario specific until larger resident populations or other platforms are measured.

## 8. Revisit when

This decision must be revisited when any of the following occurs:

- strict 60Hz Full Interactive operation is required with dynamic MiniMap units enabled;
- MiniMap receives a true dirty-cell incremental or asynchronous implementation;
- the resident population increases materially beyond 5000;
- the render/simulation scheduling architecture becomes multi-core or otherwise changes the critical path;
- the Core stress criterion is changed;
- new evidence contradicts the archived raw artifacts.

## 9. Closure evidence

The case is CLOSED because:

```text
problem reproduced                         yes
competing hypotheses recorded             yes
crossing-count hypothesis instrumented     yes
root cause demonstrated                    yes
controlled ON/OFF ablation                 yes
scale-only ablation protected by test      yes
formal raw artifacts archived              yes
all 12 formal artifacts SHA256-covered     yes
checksum verification                      all OK
exact STAR source SHAs recorded            yes
engineering decision documented            yes
Performance Frontier updated               yes
```

No annotated milestone tag was created because this case records a scale/profile-isolation decision rather than a production-default algorithm rewrite; the immutable source identity is the exact validated STAR commit SHA.

## 10. Provenance

- Reproduction: [`README.md`](README.md)
- Experiment identity: [`manifest.yaml`](manifest.yaml)
- Root-cause analysis: [`analysis.md`](analysis.md)
- Raw evidence: [`results/`](results/)
- Integrity: [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)
- Phase-3 measurement foundation: [`../../records/performance-measurement-regression-infra-2026-09.md`](../../records/performance-measurement-regression-infra-2026-09.md)
- Historical density methodology: [`../2026-09-dynamic-world-scaling/`](../2026-09-dynamic-world-scaling/)
- Performance Frontier: [`../../records/performance-frontier.md`](../../records/performance-frontier.md)
