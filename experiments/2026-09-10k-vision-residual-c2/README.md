# 10K Vision Residual C2

**Status:** RUNNING — attribution complete; C2a selected and closeout preregistered  
**STAR repository:** `star-nexus/star`  
**Frozen production baseline:** `4218b5368fbe2815b8512384e2c18b0af443ebfa`

## Question

After Optimization C1 removed the redundant terrain-bonus lookup from the ~99.7% geometry-cache hit path, what now dominates residual `VisionSystem` dirty-unit CPU at 10K scale?

The attribution was deliberately limited to three remaining areas already visible in the production update loop:

```text
old/new visibility set diff
faction union / per-tile refcount maintenance
explored-set maintenance
```

Optimization A, Optimization B, and Optimization C1 remain fixed.

## Current production shape

For each changed Vision unit, production currently performs:

```text
visibility geometry
  -> old_tiles / visible_tiles set differences
  -> per-faction refcount decrement/increment for removed/added tiles
  -> 0<->1 faction-visible transitions + fog-delta staging
  -> state writeback
  -> explored.update(visible_tiles)
```

## Attribution run

Canonical local run pending raw mirror:

```text
run_id                    20260906-194311
runtime                   4218b5368fbe2815b8512384e2c18b0af443ebfa
scenario SHA256           e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
Fog                       ON
MiniMap dynamic units     OFF
GC                        realtime_defer
50% / 100% moving         PASS guards
ENV cleanup               PASS
uploaded ZIP SHA256       c3b8202308a0f0eb80e694136e6316cb5ed74e9920645915d863cd5c6cf2efee
```

### 50% moving

```text
Vision avg                         3.305 ms/frame
changed units                    279.289 / frame
set diff                           0.388 ms/frame
union/refcount wrapper             1.630 ms/frame   (instrumentation-inflated)
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
union/refcount wrapper             3.998 ms/frame   (instrumentation-inflated)
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

The union wrapper timing is not treated as direct production cost because the C2 probe adds per-tile counters and sampled sub-probes inside that wrapper. Exact operation multiplicity is trusted; production retention still requires uninstrumented A/B.

## Interpretation

### H1 — union/refcount is structurally expensive, but mostly necessary bookkeeping

At 100% moving, only ~`0.786%` of `7516` refcount tile operations actually change the faction-visible union. Roughly 99.2% maintain overlap multiplicity so the system knows when the last observer leaves a tile. This is a real data-structure problem, not obviously removable work.

### H2 — set diff remains material but semantically useful

The paired old/new set difference costs ~`0.39 ms` at 50% and ~`1.03 ms` at 100%. It computes the exact observer-private visibility delta and is therefore retained for a later C2 subproblem.

### H3 — explored history contains clear wrong complexity

`explored_tiles[faction]` is monotonic history, but production re-inserts every changed observer's full visible set.

At 100% moving:

```text
explored input                  14281 tiles/frame
add visibility delta            3758 tiles/frame
faction 0->1 add transitions      35 tiles/frame
actually new explored             16 tiles/frame
```

So only ~`0.114%` of the current explored input actually creates new history. Even `explored.update(added_tiles)` would still process far more candidates than necessary.

The correct semantic trigger is the faction-level visibility transition:

```text
refcount 0 -> 1
    => faction newly becomes able to see tile now
    => tile must be in explored history
```

If `old > 0`, another same-faction observer already sees the tile, therefore that tile must already have entered explored history earlier.

## C2a selected candidate

C2a moves explored maintenance into `_add_tiles()` only when the faction tile refcount transitions `0 -> 1`, and removes the per-unit:

```python
explored.update(visible_tiles)
```

Candidate source identities:

```text
implementation commit          c95a5ce7b353a3d77c7cf6f8e2f5fb69933f94e1
candidate + regression HEAD    6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b
control                        4218b5368fbe2815b8512384e2c18b0af443ebfa
closeout branch                experiment/phase5-c2a-closeout
```

The candidate changes only explored-history maintenance. Refcount representation, set-diff, geometry, movement, rendering, audit scheduling, and cache policy are unchanged.

## C2a semantic contract

The treatment must preserve:

1. bootstrap explored history equals the initial faction-visible union;
2. overlap refcount increments (`old > 0`) do not touch explored history;
3. leaving visibility never removes explored history;
4. re-entry into historically explored tiles is harmless;
5. faction visibility and fog-journal transitions are unchanged;
6. observation and fog presentation consumers see identical explored semantics.

Targeted regressions include dedicated operation-level coverage plus existing Vision, observation, fog-presentation, and C1 geometry-path tests.

## C2a production closeout — preregistered before measurement

Same-session ABBA:

```text
A50 -> B50 -> B100 -> A100
A = 4218b536... retained A+B+C1 baseline
B = 6896cdc... A+B+C1+C2a candidate
```

Workload remains the canonical 10K Core configuration.

### Workload preservation gates

```text
all driver/semantic guards                PASS
position commits/s                         +/-2%
Vision dirty/s                             +/-2%
Vision scanned/s                           +/-2%
geometry calls/s                           +/-2%
faction visible add/remove rates           +/-5%
fog delta rate                             +/-5%
geometry hit-rate drop                     <=0.5 pp
geometry evictions                         0
```

### Causal local gate

Normalize the uninstrumented `VisionSystem` inclusive cost by changed units:

```text
Vision CPU / changed unit
```

Attribution predicts removable explored container+update work of roughly:

```text
50%   ~1.36 us / changed unit
100%  ~1.12 us / changed unit
```

The preregistered retention floor is intentionally conservative:

```text
saving >= 0.4 us / changed unit
Vision avg/frame improves at both densities
```

### Whole-system supporting gate

```text
controlled avg regression <=2%
100% controlled avg must improve
P99 is diagnostic only, not a KEEP/REVERT gate
```

Decision is `CAUSALLY_CONFIRMED_KEEP` only if both densities pass all preregistered checks.

## Methodological rule

C2 follows the same rule used for A/B/C1:

> **先消灭错误复杂度，再重构必要复杂度。**

C2a removes redundant monotonic-history work first. Only after C2a is closed should C2b revisit the necessary faction-refcount representation, followed by C2c set-diff if evidence still warrants it.
