# Phase 5 Live Progress — E7 100% Moving P99 Tail Composition

> Temporary active-work supplement to `docs/dev/10k-online-roadmap.md`. Durable evidence belongs in STAR Lab.

**Date:** 2026-09-08  
**Status:** VALIDATED ATTRIBUTION — stable tail contributors found / Raw mirror pending in STAR Lab

## Retained production

```text
e7ba18b31870577110b591104ef8fa7b4713e43c
A + B + C1 + C2a + D1 + E6-1
```

E6-2 slotted composition remains CLOSED / NOT MATERIAL and does not modify production.

## Formal E7 result

Run:

```text
20260908-001411
```

Three exact retained-production repeats, 10K / 100% moving, all source/workload guards PASS. Aligned samples: `312 / 311 / 311`. Tail contract: `2 passed`. Targeted regressions: `20 passed`.

Controlled work:

```text
repeat-1 avg 30.649  p95 32.697  p99 33.209  tail uplift +2.519 ms
repeat-2 avg 30.743  p95 32.832  p99 33.169  tail uplift +2.295 ms
repeat-3 avg 30.770  p95 32.839  p99 33.190  tail uplift +2.307 ms
```

Stable actionable contributors:

```text
UnitRenderSystem  top3=3/3  median self uplift +1.067 ms  share 46.3%  r=0.954
VisionSystem      top3=3/3  median self uplift +0.401 ms  share 17.5%  r=0.884
AnimationSystem   top3=3/3  median self uplift +0.350 ms  share 15.2%  r=0.741
```

Decision:

```text
STABLE_TAIL_CONTRIBUTORS_FOUND
```

## UnitRender refinement

The next target is **not** the already-treated Cull first-touch path.

```text
UnitRender inclusive median tail uplift  +1.164 ms
UnitRender self median tail uplift       +1.067 ms (~91.6%)
unit_visible_cull median tail uplift     +0.097 ms (~8.4%)
```

The strongest stable numeric association is render volume:

```text
render_commands median r(controlled) = 0.920
median tail delta = +438 commands
median tail ratio = 1.128
```

Stable co-occurrence also shows UnitRender rising with `render_batch_blits` in 3/3 repeats, with Animation in 3/3 and with Vision in 2/3.

Therefore the next Phase-5 causal question is:

> Why do tail frames create more UnitRender batch/render work and commands?

Next attribution should measure UnitRender volume variables such as visible unit count, animated unit count, grouped/static unit count, group count and UnitRender-attributable render command count before proposing an optimization.

## 30 Hz diagnostic

```text
p99: 33.209 / 33.169 / 33.190 ms
median: 33.190 ms
passes: 3/3
```

This does **not** update the Performance Frontier. E7 is attribution-only and uses a 10 s profiler horizon; a later canonical retained-production validation is still required.

## Tooling / artifacts

Experiment branch:

```text
experiment/phase5-tail-composition-attribution
```

Frozen measurement tooling after the pre-measurement runner fix:

```text
33d3715c1310a33bc3b9ff44a8deb7f633bf21d4
```

Artifacts:

```text
Compact SHA256 e69471082847263f65035015e83da211982612befb187691b65d377d159f5b29
Raw SHA256     cdb7a6232d13c0f7d55c26f4f23fabd21782f305eb9b58444bf847612214126a
```

STAR Lab:

```text
experiments/2026-09-10k-phase5-e7-tail-composition/
```
