# 10K Vision Residual C2

**Status:** RUNNING — C2 attribution complete; C2a CAUSALLY CONFIRMED / KEEP / CLOSED; C2b/C2c deferred  
**STAR repository:** `star-nexus/star`  
**Attribution baseline:** `4218b5368fbe2815b8512384e2c18b0af443ebfa`  
**Current production after C2a:** `6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b`

## Question

After C1 removed redundant terrain-bonus work from the geometry-cache hit path, what residual Vision work remains at 10K scale, and which part is wrong complexity versus necessary complexity?

The C2 decomposition covers:

```text
old/new visibility set diff
faction union / per-tile refcount maintenance
explored-set maintenance
```

## C2 attribution

Canonical attribution run:

```text
run_id                    20260906-194311
runtime                   4218b5368fbe2815b8512384e2c18b0af443ebfa
scenario SHA256           e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
Fog                       ON
MiniMap dynamic units     OFF
GC                        realtime_defer
50% / 100% moving         PASS guards
ENV cleanup               PASS
ZIP SHA256                c3b8202308a0f0eb80e694136e6316cb5ed74e9920645915d863cd5c6cf2efee
raw mirror                pending
```

### 50% moving

```text
Vision avg                         3.305 ms/frame
changed units                    279.289 / frame
set diff                           0.388 ms/frame
union/refcount wrapper             1.630 ms/frame   instrumentation-inflated
explored container + update        0.381 ms/frame
visible tiles                    5306.489 / frame
added / removed                  1396.444 / 1396.444
refcount tile ops                2792.889 / frame
faction union transitions          37.511 / frame
union transition rate               1.337%
add 0->1 transitions               21.717 / frame
actually new explored tiles        10.356 / frame
visible / added ratio                3.8x
```

### 100% moving

```text
Vision avg                         8.160 ms/frame
changed units                    751.639 / frame
set diff                           1.029 ms/frame
union/refcount wrapper             3.998 ms/frame   instrumentation-inflated
explored container + update        0.838 ms/frame
visible tiles                   14281.143 / frame
added / removed                  3758.195 / 3758.195
refcount tile ops                7516.391 / frame
faction union transitions          59.188 / frame
union transition rate               0.786%
add 0->1 transitions               35.173 / frame
actually new explored tiles        16.271 / frame
visible / added ratio                3.8x
```

The wrapper timing is not used as direct production cost because the probe performs per-tile counters and sampled sub-probes inside the wrapper. Exact operation multiplicity is trusted.

## Interpretation

### H1 — faction union/refcount

At 100% moving only about `0.786%` of `7516` refcount tile operations/frame change the faction-visible union. The other ~99.2% maintain observer overlap multiplicity so the system knows when the last observer leaves a tile.

This is expensive, but it is currently **necessary bookkeeping**, so it becomes C2b rather than the first optimization target.

### H2 — visibility set diff

The paired set differences cost about `0.39 ms/frame` at 50% and `1.03 ms/frame` at 100%. They compute the exact observer-private visibility delta and remain semantically useful. This is deferred as C2c.

### H3 — explored history

`FogOfWar.explored_tiles[faction]` is monotonic history, but production previously executed:

```python
explored.update(visible_tiles)
```

for every changed observer.

At 100% moving:

```text
full visible input             14281 tiles/frame
added observer delta            3758 tiles/frame
faction add 0->1 transitions      35 tiles/frame
actually new explored             16 tiles/frame
```

Only about `0.114%` of full-set input actually creates new history. The correct semantic trigger is faction visibility refcount `0 -> 1`.

## Optimization C2a

C2a moves explored-history maintenance to the faction-level `0 -> 1` visibility transition in `_add_tiles()` and removes the per-unit full-set update.

```text
implementation commit          c95a5ce7b353a3d77c7cf6f8e2f5fb69933f94e1
candidate + regression HEAD    6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b
control                        4218b5368fbe2815b8512384e2c18b0af443ebfa
production after retention     6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b
```

Refcount representation, set-diff, geometry, movement, rendering, and audit scheduling are unchanged.

## C2a same-session closeout

```text
run_id                    20260906-200509
order                     A50 -> B50 -> B100 -> A100
ZIP SHA256                53aed7a6889ab961fe940e5b5c5f15584140ab253ee41231e5c5d8ae448d03f7
all driver guards         PASS
all ENV cleanup           PASS
targeted regressions      88 passed
raw mirror                pending
```

### 50% moving

```text
controlled avg                 24.840 -> 24.695 ms   (-0.58%)
controlled p99                 28.150 -> 28.641 ms   diagnostic
Vision avg                      1.852 -> 1.587 ms    (-14.3%)
Vision CPU / changed unit       7.033 -> 6.060 us
saved / changed unit                               0.973 us
position commits/s delta                           +0.008%
Vision dirty/s delta                               +0.020%
faction add/s delta                                -0.176%
faction remove/s delta                             -0.243%
```

### 100% moving

```text
controlled avg                 31.722 -> 30.942 ms   (-2.46%)
controlled p95                 32.955 -> 32.170 ms
controlled p99                 34.669 -> 33.199 ms
Vision avg                      4.011 -> 3.368 ms    (-16.0%)
Vision CPU / changed unit       6.037 -> 5.189 us
saved / changed unit                               0.847 us
position commits/s delta                           +0.022%
Vision dirty/s delta                               +0.017%
faction add/s delta                                -0.293%
faction remove/s delta                             -0.540%
fog delta/s delta                                  -0.394%
```

The production local savings consume about 71% of the attributed opportunity at 50% moving and 76% at 100% moving while workload and faction-level semantics remain stable.

## C2a decision

```text
Optimization C2a
explored history on faction visibility 0 -> 1

CAUSALLY CONFIRMED
KEEP
CLOSED
```

The treatment is now retained on `perf/10k-online` at `6896cdc0...`.

The `33.199 ms` 100%-moving P99 is the first observed crossing below the `33.33 ms` canonical 30Hz gate, but the C2a closeout preregistered P99 as diagnostic. It is therefore only a **frontier candidate observation**. A separate capacity-boundary experiment must confirm the crossing before the Performance Frontier advances.

See `decision-c2a.md` for the formal closeout rationale.

## Methodology

> **先消灭错误复杂度，再重构必要复杂度。**

C2a removes redundant monotonic-history work. C2b faction-refcount representation and C2c visibility set-diff are deferred until the 10K full-motion frontier confirmation is resolved.
