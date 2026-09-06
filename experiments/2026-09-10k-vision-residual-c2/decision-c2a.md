# Decision — Vision C2a Explored History on Faction Visibility Transition

## Final state

```text
Optimization C2a
explored history on faction visibility 0 -> 1

CAUSALLY CONFIRMED
KEEP
CLOSED
```

Production restoration:

```text
perf/10k-online
6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b
```

The production branch now retains Optimization A + B + C1 + C2a.

## Attribution basis

C2 attribution run:

```text
20260906-194311
runtime 4218b5368fbe2815b8512384e2c18b0af443ebfa
ZIP SHA256 c3b8202308a0f0eb80e694136e6316cb5ed74e9920645915d863cd5c6cf2efee
```

At 100% moving, production fed about `14281` visible tiles/frame into the monotonic explored-history set while only about `16.27` tiles/frame became newly explored. Only about `35.17` add-side faction refcount transitions/frame were `0 -> 1` transitions. The existing per-unit full-set update therefore processed overwhelmingly stable historical state.

Measured explored container + update opportunity:

```text
50%   0.381 ms/frame   ~1.364 us / changed unit
100%  0.838 ms/frame   ~1.116 us / changed unit
```

## Treatment

Control:

```text
4218b5368fbe2815b8512384e2c18b0af443ebfa
```

Treatment implementation:

```text
c95a5ce7b353a3d77c7cf6f8e2f5fb69933f94e1
```

Treatment + dedicated regression:

```text
6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b
```

The treatment removes per-changed-unit:

```python
explored.update(visible_tiles)
```

and updates explored history only when faction-level visibility refcount transitions from `0 -> 1` in `_add_tiles()`.

Refcount representation, set-diff, geometry, movement, rendering, and audit scheduling are unchanged.

## Same-session closeout

Run:

```text
20260906-200509
order A50 -> B50 -> B100 -> A100
ZIP SHA256 53aed7a6889ab961fe940e5b5c5f15584140ab253ee41231e5c5d8ae448d03f7
```

All driver guards passed, all ENV process-tree cleanup exit codes were zero, and the treatment targeted regression suite reported `88 passed`.

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

The actual local savings consume roughly 71% of the attributed opportunity at 50% moving and 76% at 100% moving, while authoritative workload and faction-level visibility rates remain effectively unchanged.

## Decision rationale

C2a is retained because:

1. the removed work is semantically redundant monotonic-history maintenance;
2. attribution predicted the magnitude and production A/B reproduced it;
3. both densities exceed the preregistered `0.4 us / changed unit` saving floor;
4. Vision average improves at both densities;
5. 100% controlled average improves;
6. workload, geometry, faction visibility, and fog-delta rates remain within preregistered tolerances;
7. semantic regressions pass.

The observed 100%-moving P99 of `33.199 ms` is the first crossing below the `33.33 ms` canonical 30Hz gate, but C2a's closeout preregistered P99 as diagnostic. It is therefore recorded only as a **frontier candidate observation**, not as a formally established capacity point.

A separate frontier-confirmation experiment is required before the Performance Frontier is advanced.

## Methodology

This case strengthens the Phase-5 rule:

> **先消灭错误复杂度，再重构必要复杂度。**

C2a removed wrong semantic granularity. C2b faction-refcount representation and C2c visibility set-diff remain necessary-complexity candidates and are deferred until the frontier confirmation is resolved.
