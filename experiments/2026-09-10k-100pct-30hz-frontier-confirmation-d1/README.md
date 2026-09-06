# Post-D1 10K / 100%-Moving 30Hz Frontier Confirmation

**Status:** CLOSED — `FRONTIER_NOT_ESTABLISHED`  
**STAR repository:** `star-nexus/star`  
**Frozen production runtime:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Question

After D1 removed the periodic ~4ms Vision audit pulse, does the retained production runtime establish a repeatable canonical 10K / 100%-moving / Fog ON / 30Hz frontier?

## Preregistered rule

```text
controlled_work_frame_ms.p99 <= 33.33 ms
```

Formal establishment required all five guards to pass and all three independent 100%-moving fresh-process runs to pass the gate. No majority/median reinterpretation was permitted.

## Result — run `20260906-225405`

```text
00pct-moving       avg=16.382  p99=18.804  PASS
50pct-moving       avg=24.696  p99=26.249  PASS
100pct-moving-r1   avg=30.860  p99=32.926  PASS
100pct-moving-r2   avg=31.229  p99=33.348  FAIL
100pct-moving-r3   avg=31.299  p99=33.764  FAIL
```

All runtime/workload guards passed. Full-motion P99s were:

```text
32.926 / 33.348 / 33.764 ms
```

Worst headroom to the canonical gate was `-0.434 ms`; therefore the preregistered decision is:

```text
FRONTIER_NOT_ESTABLISHED
```

Raw ZIP SHA256 supplied from the run:

```text
2cdf93cd09db273dd18fab6753bdccbbeb0bba755860f7e11e741090061ff770
```

Raw STAR Lab mirror remains pending.

## Interpretation

D1 remains independently `CAUSALLY CONFIRMED / KEEP / CLOSED`. The periodic Vision audit pulse is absent in the retained runtime and is not reopened by this frontier result.

The post-D1 failure signature is different from the pre-D1 audit-tail failure. There is no replacement low-frequency maintenance pulse. The three 100%-moving runs show a mild distributed steady-state drift:

```text
controlled avg   30.860 -> 31.229 -> 31.299 ms
```

while authoritative position commits stay at approximately `20,000/s`. Animation per-position-commit cost is essentially stable; Vision and UI show small per-unit/system-state drift. The runtime is therefore **margin-limited rather than pathology-limited**.

The remaining gap is small (`~0.5 ms` minimum, preferably `~1 ms` engineering margin). With the clearly identified wrong-complexity cases A/C1/C2a/D1 already removed, the next step is to begin necessary-complexity optimization rather than repeat frontier runs.

## Next step

Proceed to **C2b — faction refcount representation attribution** on exact production `17ced8d...`.

C2b must not delete overlap bookkeeping: the refcount is semantically necessary to distinguish `3 -> 2 -> 1 -> 0` observers. The attribution instead asks whether the current Python `Dict[(col,row), int]` representation is unnecessarily expensive for a bounded 120x120 world.
