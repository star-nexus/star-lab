# Analysis — Realtime Gen2 GC Tail Latency

## 1. Observation

The 5000-unit realtime workload had acceptable average throughput but rare latency cliffs. The profiler initially showed the worst time inside `UnitRenderSystem`, raising two competing explanations:

1. rendering occasionally performs unusually expensive work;
2. unrelated runtime maintenance happens while the render section is on the stack.

## 2. Instrumentation

Commit `916d88dcd3d796fe49a0cadd64be40b68c331b5c` added low-overhead GC/tail attribution:

```text
GC generation
pause duration
collected/uncollectable counts
render command counts
static/animated sub-phase location
```

The bounded policy was added in `6bdeabe210fbc2e8dc3612a03e0cab11df1e77a1`, integrated into scale measurement in `74708af3f1bf2c31b050cf816e30aa52613fcda8`, and formally selectable/guarded at `33b18bc777df992ff8665d458d70782451d05a51`.

## 3. Canonical evidence

AUTO artifact:

`results/density-100-auto.json`

Worst-frame metrics include:

```text
unit_gc_pause_ms                 30.896833
unit_gc_gen2_pause_ms            30.845625
unit_gc_collected_objects        0
UnitRender max                   34.838917 ms
animated draw max                29.434208 ms
P99 frame                        48.815013 ms
```

`realtime_defer` artifact:

`results/density-100-realtime-gc.json`

```text
pre-measurement full Gen2        19.745916 ms
full-collect collected           0
UnitRender max                    7.102958 ms
animated draw max                 1.582250 ms
P99 frame                        25.489481 ms
slow frames                       0
```

The rendering command path did not need a comparable ~30 ms amount of useful rendering work to explain the AUTO tail; the Gen2 pause itself accounts for the abnormal latency.

## 4. Root cause

> Rare UnitRender tails were primarily automatic CPython generation-2 cyclic-GC pauses occurring while UnitRender was the active timed section.

## 5. Causal chain

```text
automatic cyclic-GC trigger
 -> Gen2 traversal on latency-critical thread
 -> ~30 ms pause
 -> elapsed time attributed to active UnitRender scope
 -> P99 / max cliff

safe-boundary full Gen2
 + bounded automatic cyclic-GC deferral
 -> no arbitrary Gen2 inside critical window
 -> UnitRender tail collapses
 -> P99 returns to ~25 ms class
```

## 6. Rejected explanations

- **Rare rendering work itself explains the ~30 ms cliff:** rejected by the direct Gen2 timing and the policy-only A/B.
- **Texture/font churn is the dominant remaining mechanism:** not supported by the A/B; the large cliff disappears with GC scheduling.
- **Disable GC globally:** rejected; the policy is bounded and restores prior state.
- **Reference counting is disabled:** false; ordinary CPython refcount reclamation remains active.

## 7. Artifact status

The original formal AUTO/defer JSON artifacts have now been recovered and are stored unchanged in this case. Both are covered by `artifacts/SHA256SUMS`; this analysis no longer depends on summary-only historical evidence.
