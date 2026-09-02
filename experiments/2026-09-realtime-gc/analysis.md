# Analysis — Realtime Gen2 GC Tail Latency

## 1. Observation

The 5000-unit realtime workload had acceptable average throughput but rare latency cliffs. The profiler initially showed the worst time inside `UnitRenderSystem`, with individual UnitRender / animated-draw paths reaching tens of milliseconds.

The central question was whether rendering itself was occasionally expensive or whether some unrelated runtime maintenance happened to execute while the render section was on the stack.

## 2. Competing hypotheses

### H1 — Unit rendering performs rare expensive work

Possible sources included texture scaling/cache churn, font/glyph cold paths, command allocation, unusually large visible batches, or other rendering-specific work.

### H2 — Python cyclic GC pauses occur inside the render section

Because profiler sections are wall-clock scoped, an automatic GC pause triggered during UnitRender would be attributed to UnitRender even if the rendering work itself did not cause a comparable amount of useful rendering work.

### H3 — The tail is simply normal frame-load variation

If true, no single runtime event should correlate tightly with the worst tails and changing GC policy should not collapse the tail distribution.

## 3. Instrumentation

Commit `916d88dcd3d796fe49a0cadd64be40b68c331b5c` added low-overhead tail attribution while keeping the verified renderer behavior intact. The diagnostics included:

```text
Python GC callbacks
collection generation
GC pause duration
collected/uncollectable counts
render command counts
static/animated command paths
GC location relative to UnitRender sub-phases
```

The controlled policy was then added in `6bdeabe210fbc2e8dc3612a03e0cab11df1e77a1` and integrated into scale measurements in `74708af3f1bf2c31b050cf816e30aa52613fcda8`.

Formal runs could later select and guard the requested policy through `STAR_SCALE_GC_POLICY` at `33b18bc777df992ff8665d458d70782451d05a51`.

## 4. Evidence

A representative AUTO worst frame showed:

```text
GC pause                 30.897 ms
Gen2 pause               30.846 ms
collected objects        0
```

At the run level:

```text
AUTO
avg frame                23.244 ms
P50                      21.861 ms
P95                      25.984 ms
P99                      48.815 ms
max                      ~52.742 ms; worst observed 57.756 ms
UnitRender max           34.839 ms
animated draw max        29.434 ms
```

The rendering tail therefore coincided with a generation-2 collection large enough to explain almost all of the abnormal latency.

The `collected=0` result is particularly informative: an expensive cyclic-GC traversal can pause the critical thread even when it ultimately reclaims nothing.

With `realtime_defer`:

```text
pre-measurement Gen2     ~19.746 ms at safe boundary
avg frame                21.837 ms
P50                      21.001 ms
P95                      24.940 ms
P99                      25.489 ms
max                      26.581 ms
slow frames              0
UnitRender max           7.103 ms
animated draw max        1.582 ms
```

Moving the cyclic collection outside the measured critical phase removes the tail cliff while leaving CPython reference counting active.

## 5. Root cause

> Rare UnitRender tails were primarily automatic CPython generation-2 cyclic-GC pauses occurring while UnitRender was the active timed section, not rare rendering work of comparable magnitude.

## 6. Causal chain

```text
allocation history reaches automatic cyclic-GC trigger
 -> Gen2 traversal begins on latency-critical thread
 -> ~30 ms stop-the-world-style pause for that Python thread
 -> profiler attributes elapsed time to active UnitRender section
 -> P99 / max frame cliff

explicit safe-point Gen2 collect
 + bounded automatic-cyclic-GC deferral
 -> no arbitrary Gen2 collection inside critical window
 -> UnitRender tail collapses
 -> P99 returns to ~25 ms class
```

## 7. Rejected explanations

- **Actual UnitRender rendering work explains the ~30 ms spike.** Rejected: the slow frame contained a Gen2 pause of almost the same duration, and UnitRender max collapsed when only the GC timing policy changed.
- **Texture/font work is the main remaining tail mechanism.** Not supported by the controlled A/B; the dominant abnormal cliff disappeared with GC deferral.
- **Disabling automatic cyclic GC disables ordinary Python object reclamation.** Incorrect: CPython reference counting continues to reclaim non-cyclic short-lived objects. The policy only defers the cyclic collector.
- **The right fix is to disable GC globally.** Rejected: the validated policy is bounded, performs maintenance at a safe boundary, and restores the previous automatic-GC state.

## 8. Limits of the evidence

This establishes the dominant cause of the observed 5K realtime tail on the tested CPython/macOS environment. It does not imply that every future UnitRender tail is GC-related, nor that the same GC policy is optimal for every Python implementation or workload.

The policy should be re-profiled when the runtime, object graph, or critical-window duration changes materially.

## 9. Historical artifact status

The original formal AUTO/defer JSON files were not available when STAR Lab was initialized. The archive therefore preserves exact source commits and validated numeric summaries but intentionally does not fabricate raw result files.
