# Scale Runtime Memory Retention — Visibility History

**Status:** CLOSED — raw evidence complete; exact post-fix run SHA not encoded in artifact  
**STAR repository:** `star-nexus/star`  
**Problem/reproduction commit:** `c16aed62975f48a80b85db0f594789372cf2a782`  
**Fix commit:** `cc47acb661500787395b2b9b241256edadfed1d4`  
**Later milestone tag:** `scale-v1-cull-vision-closed`

## 1. Problem

After the Vision geometry cache had already been bounded, a repeated 600-second realtime soak still showed growing RSS and tracked Python objects even though safe-point full generation-2 collections repeatedly reported `collected=0`, the Vision cache stayed capped, and ECS entity/component counts stayed flat.

The useful question became:

> What reachable application state is intentionally retaining historical objects?

## 2. Canonical pre-fix evidence

Formal completed soak:

- [`results/realtime-gc-soak-v2-600s.json`](results/realtime-gc-soak-v2-600s.json)
- SHA256: `84e67049916b9fc49f0c20aa5b07c864ebd283a2780fdecda0b47b517e72a35d`

It completed **40/40 cycles (600 s)** and reported:

```text
baseline RSS                    328.359 MB
final post-collect RSS          380.312 MB
RSS growth                      +51.953 MB
baseline tracked objects        200,104
final tracked objects           350,054
tracked-object growth           +149,950
total safe-GC collected         0
entity growth                   0
component-instance growth       0
Vision geometry-cache size      4096 (bounded)
```

An earlier partial but diagnostically useful soak remains under:

- [`results/intermediate/realtime-gc-soak-600s-incomplete.json`](results/intermediate/realtime-gc-soak-600s-incomplete.json)

It executed eight valid cycles before ending as `soak_incomplete`; it is investigation evidence, not formal validation evidence.

## 3. Root cause

Inspection found:

```text
VisibilityTracker.visibility_history
VISIBILITY_HISTORY_LIMIT = 100
```

At 5000 units this permits up to:

```text
5000 × 100 = 500,000
```

reachable historical transition records.

Because those objects remained reachable by application state, more GC was the wrong remedy. Current visibility semantics already lived in current-state structures; the full per-unit transition trajectory was telemetry.

## 4. Fix

At commit `cc47acb661500787395b2b9b241256edadfed1d4`:

```text
VISIBILITY_HISTORY_LIMIT = 100
                         ↓
VISIBILITY_HISTORY_LIMIT = 1
```

Canonical/headless behavior is unchanged.

> Runtime state is not historical telemetry.

## 5. Canonical post-fix evidence

Recovered formal validation:

- [`results/realtime-gc-soak-v3-120s.json`](results/realtime-gc-soak-v3-120s.json)
- SHA256: `7db3c6fe035bf56a800d021dabaea4c33c465e01c7d4ecb351d0f98907145de3`

The artifact is a valid completed run:

```text
top-level ok                      true
cycles completed                  8 / 8
realtime completed                120 s
GC policy                         realtime_defer
Fog guard                         ON
requested density                 1.0
```

All eight cycles passed their run guards. One cycle had 4999 active movers (`0.9998` density), within the configured `max_missing_moving_units=10` tolerance.

Post-safe-GC retained-state invariants were stable throughout the run:

```text
visibility_history_records        5000 exactly
visibility_history_max_per_unit   1 exactly
entities                           13288 exactly
component instances               79852 exactly
Vision geometry-cache size        4096 exactly
total safe-GC collected           0
```

Memory/tracked-object sequence after each safe collection:

```text
priming tracked                   198808
15s                               202693
30s                               206762
45s                               209291
60s                               209508
75s                               209741
90s                               209747
105s                              209700
120s                              209756

priming RSS                       368.812 MB
120s RSS                          337.438 MB
post-collect RSS growth           -31.374 MB
```

The tracked-object series warms into a plateau near 209.7k rather than continuing the pre-fix leak-shaped rise. For the final five post-GC samples:

```text
mean                              209690.4
sample SD                         104.2
range                             248
```

For the final four samples (75–120 s), the linear slope is approximately:

```text
-48 objects / hour
```

which is effectively flat at this scale.

### Why the JSON's whole-run slope is not the steady-state leak metric

The raw summary also contains a large positive `post_collect_tracked_objects_slope_per_hour`. That regression includes the initial state-population/warm-up transition from `198808` toward the ~`209.7k` steady-state working set. It must not be interpreted as the late steady-state retention slope.

For leak diagnosis, the relevant question is whether the post-warmup retained working set continues to grow. In this run it does not: the late samples stay within a 248-object band and the final-four slope is approximately zero.

## 6. Source-provenance note for the recovered post-fix run

The recovered JSON does not encode a Git SHA. Repository history proves:

```text
cc47acb6  perf: bound scale visibility history to latest change
5382834a  diagnostics: expose retained statistics history in memory soak
0c65bfc4  test: bound scale visibility history retention
04c58ad5  test: expose retained statistics counts in soak snapshots
```

The JSON contains the retained-statistics fields introduced by this sequence, so it is definitely post-fix and post-diagnostics. The exact checkout SHA used for this individual run is not encoded in the artifact and is therefore not guessed here. The later validated milestone remains `a24482d438157aa23b371b6e34d49b1c04fec7f7` / `scale-v1-cull-vision-closed`.

## 7. Integrity

From this experiment root:

```bash
shasum -a 256 -c artifacts/SHA256SUMS
```

The checksum set covers:

```text
results/intermediate/realtime-gc-soak-600s-incomplete.json
results/realtime-gc-soak-v2-600s.json
results/realtime-gc-soak-v3-120s.json
```
