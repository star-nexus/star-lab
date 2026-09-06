# Decision — 10K Vision Geometry Cache-Hit Path

## Final decision

**CAUSALLY CONFIRMED / KEEP / CLOSED.**

Retain Optimization C1 in the window Vision path.

## Accepted implementation

```text
b39eb592833a3413a002aac294cf4e46481f640a
perf: bypass terrain lookup on vision geometry cache hits

b9c63e9d626c9e21a1924121b91cedb116c1f2e1
test: cover vision geometry hit terrain bypass
```

Current retained production composition, including Optimization B restoration:

```text
4218b5368fbe2815b8512384e2c18b0af443ebfa
```

## Closeout evidence

Same-session ABBA:

```text
run       20260906-183456
control   7b37f2d0823149042688059715342faf55c4fbb9
treat     4218b5368fbe2815b8512384e2c18b0af443ebfa
order     A50 -> B50 -> B100 -> A100
```

Treatment regressions:

```text
15 passed in 0.05s
```

All four driver guards and all four ENV process-tree cleanup checks passed.

### Causal local result

```text
50% moving
Vision avg        2.487 -> 2.158 ms/frame
CPU/call          8.634 -> 7.555 us
saving                       1.079 us/call

100% moving
Vision avg        5.629 -> 4.760 ms/frame
CPU/call          7.499 -> 6.474 us
saving                       1.025 us/call
```

The 100% `0.869 ms/frame` Vision reduction closely matches the earlier attributed terrain-bonus cost of `~0.849 ms/frame`.

### Workload preservation

```text
position commits/s delta    -0.040% / -0.001%
Vision dirty/s delta        +0.026% / -0.037%
Vision scan/s delta         +0.026% / -0.037%
geometry-call/s delta       +0.026% / -0.037%
hit-rate delta              -0.005 / +0.008 pp
geometry evictions          0 / 0
```

No authoritative or visibility-work reduction explains the speedup.

## Tail handling

Whole-system controlled P99 is diagnostic only for this closeout, by preregistration.

Treatment controlled P99 changed:

```text
50%   30.803 -> 31.146 ms
100%  39.097 -> 41.805 ms
```

This does not override the KEEP decision because:

- controlled average improves at both densities;
- 100% controlled P95 improves by ~0.969 ms;
- Vision avg and Vision P99 both improve;
- local CPU/call savings are large, stable, and match attribution;
- workload rates and cache semantics are preserved.

No new 10K / 100%-moving 30Hz frontier point is claimed.

## Semantic revisit condition

Current production terrain is immutable after map initialization. If future runtime behavior introduces live LOS-affecting terrain mutation, C1 remains valid only if that mutation establishes:

```text
terrain mutation
  -> VisionSystem.invalidate_all()
  -> cache revision advance / clear
  -> observer recomputation
```

Revisit C1 if this invariant changes.

## Evidence state

Attribution raw is already mirrored and SHA256-covered.

Final closeout run `20260906-183456` has been independently inspected; its uploaded ZIP SHA256 is:

```text
edb940801a95d78b3f059190bb8ae62d75c5a3f9ce3778547c39156e09513c46
```

Formal STAR Lab raw mirror and extension of `RAW_SHA256SUMS` are pending. This affects archive completeness, not the engineering decision.
