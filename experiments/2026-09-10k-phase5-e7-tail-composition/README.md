# Phase 5 E7 — 10K / 100% Moving P99 Tail Composition Attribution

**Status:** VALIDATED ATTRIBUTION — stable contributors found / Raw mirror pending  
**STAR repository:** `star-nexus/star`  
**Retained production runtime:** `e7ba18b31870577110b591104ef8fa7b4713e43c`  
**Experiment branch:** `experiment/phase5-tail-composition-attribution`  
**Frozen tooling commit:** `33d3715c1310a33bc3b9ff44a8deb7f633bf21d4`

## Question

Which controlled-work subsystems rise together in current retained 10K / 100%-moving production tail frames, and which stable contributor should become the next causal target?

## Method

Three identical independent repeats of exact retained production. Primary attribution is conditional on aligned per-frame profiler data:

```text
tail      = controlled_work >= per-run p95
reference = per-run p25 <= controlled_work <= p75
uplift_s  = mean(section self_ms | tail) - mean(section self_ms | reference)
```

Self time is used for additive accounting. A section is actionable only when it is positive top-3 in at least 2/3 repeats and median uplift is at least 0.15 ms.

Formal workload remained 10K resident / 100% moving / Fog ON / staggered / seed 42 / realtime_defer / production animation+commits / pathfinding OFF / MiniMap dynamic units OFF / blocked gameplay input. The experiment-only profiler horizon was 10 s and each repeat required >=250 aligned frames.

## Formal run

```text
run_id: 20260908-001411
samples: 312 / 311 / 311
source + workload guards: PASS all repeats
tail contract: 2 passed
targeted regressions: 20 passed
```

Controlled-work results:

```text
repeat-1: avg 30.649 ms, p95 32.697, p99 33.209, tail uplift 2.519 ms
repeat-2: avg 30.743 ms, p95 32.832, p99 33.169, tail uplift 2.295 ms
repeat-3: avg 30.770 ms, p95 32.839, p99 33.190, tail uplift 2.307 ms
```

The section self-time algebra closes the controlled tail uplift in all three repeats: positive and negative section uplifts sum back to the measured controlled-work tail uplift.

## Stable contributors

```text
UnitRenderSystem  top3=3/3  median self uplift +1.067 ms  share 46.3%  r=0.954
VisionSystem      top3=3/3  median self uplift +0.401 ms  share 17.5%  r=0.884
AnimationSystem   top3=3/3  median self uplift +0.350 ms  share 15.2%  r=0.741
```

Stable p90 co-occurrence includes:

```text
UnitRender + render_batch_blits  3/3
UnitRender + Animation           3/3
UnitRender + Vision              2/3
Vision + Animation               2/3
```

## UnitRender refinement

The next target is **not Cull**.

Median UnitRender inclusive tail uplift is about `+1.164 ms`, decomposing to:

```text
UnitRender self       +1.067 ms  (~91.6% of UnitRender inclusive uplift)
unit_visible_cull     +0.097 ms  (~8.4%)
```

`render_commands` is strongly associated with controlled tail frames:

```text
median Pearson r = 0.920
median tail delta = +438 commands
median tail ratio = 1.128
```

So the next causal question is why tail frames generate more UnitRender batch/render work and commands, not whether the previous Cull first-touch problem returned.

## Decision

```text
STABLE_TAIL_CONTRIBUTORS_FOUND
NEXT CAUSAL TARGET: UnitRender self / render-volume path
```

Retained production remains `e7ba18b31870577110b591104ef8fa7b4713e43c`. E7 authorizes no production KEEP.

## 30 Hz diagnostic

```text
p99 repeats: 33.209 / 33.169 / 33.190 ms
median p99: 33.190 ms
<=33.33 ms: 3/3
frontier_update_authorized: false
```

This is encouraging but is not a canonical frontier validation: E7 is attribution-only and uses a 10 s profiler horizon; aggregate machine state also differs from prior runs.

## Artifacts

Compact:

```text
20260908-001411-compact.zip
SHA256 e69471082847263f65035015e83da211982612befb187691b65d377d159f5b29
```

Raw:

```text
20260908-001411-raw.zip
SHA256 cdb7a6232d13c0f7d55c26f4f23fabd21782f305eb9b58444bf847612214126a
size 142953 bytes
```

Compact integrity was independently verified. Raw remains the authoritative forensic substrate and still needs its stable archival mirror/locator before archival closure.
