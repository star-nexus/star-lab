# Analysis — Phase 5 E7 Tail Composition Attribution

## Observation

Retained production `e7ba18b31870577110b591104ef8fa7b4713e43c` previously sat near the 33.33 ms 10K / 100%-moving canonical p99 boundary. E7 asks whether the remaining tail has a repeatable controlled-work signature.

## Formal method

Three identical 100%-moving repeats use aligned per-frame profiler data:

```text
tail      = controlled_work >= p95
reference = p25 <= controlled_work <= p75
```

Contribution is based on section **self time**, matching the additive definition of controlled work. P99 is diagnostic only.

Preregistered actionability rule:

```text
positive top-3 in >=2/3 repeats
median self tail uplift >=0.15 ms
```

## Evidence quality

- exact retained runtime source guard: PASS;
- exact profiler blob + scenario SHA guards: PASS;
- workload guards: PASS for all 3 repeats;
- aligned samples: 312 / 311 / 311;
- tail attribution contract: 2 passed;
- targeted regressions: 20 passed;
- Compact SHA256SUMS independently verified.

The decomposition is internally strong: for every repeat, the algebraic sum of all controlled section self-time tail uplifts equals the observed controlled-work tail uplift (within floating-point precision). Thus the ~2.3–2.5 ms tail increase is accounted for by measured sections rather than unexplained budget.

## Stable tail structure

Controlled-work tail uplift:

```text
repeat-1 +2.519 ms
repeat-2 +2.295 ms
repeat-3 +2.307 ms
```

Three stable actionable contributors appear in the positive top-3 in all repeats:

```text
UnitRenderSystem  median +1.067 ms  46.3%  r=0.954
VisionSystem      median +0.401 ms  17.5%  r=0.884
AnimationSystem   median +0.350 ms  15.2%  r=0.741
```

This rejects H4 (no stable signature). H1 is partially supported because UnitRender is the dominant single contributor, while H2 is also supported because Vision and Animation rise on the same tail frames rather than remaining flat.

Stable p90 co-occurrence evidence includes:

```text
UnitRender + render_batch_blits  3/3
UnitRender + Animation           3/3
UnitRender + Vision              2/3
Vision + Animation               2/3
```

So the tail is a repeatable multi-subsystem workload pulse with UnitRender as the largest component, not an isolated random spike.

## UnitRender refinement: Cull is not the new root

Median UnitRender inclusive tail uplift is `+1.164 ms`.

Its median decomposition is approximately:

```text
UnitRender self       +1.067 ms  (~91.6%)
unit_visible_cull     +0.097 ms  (~8.4%)
```

Therefore E7 does **not** reopen the prior Cull first-touch problem. E6-1 remains effective. The dominant remaining UnitRender tail is in the renderer's own batch/render preparation path after visibility has been determined.

## Render-volume association

`render_commands` is the strongest stable numeric association with controlled tail work:

```text
median Pearson r      0.920
median tail delta     +438.34 commands
median tail ratio     1.128
```

`render_simple_blits` and `render_max_batch_size` show the same correlation/delta signature. `render_batch_blits` itself adds only ~0.138 ms median self uplift, so the important observation is not merely submit/blit execution cost. Tail frames appear to carry materially more render work/commands, and UnitRender self time rises with that volume.

This suggests the next causal question should be:

> Why do tail frames create more UnitRender batch/render work and commands?

Candidate explanatory variables for the next attribution stage include visible unit count, animated unit count, static grouped unit count, group count, and UnitRender-attributable command count. These should be measured before optimizing.

## Vision / Animation as shared workload pulse

Vision metrics also rise consistently in the tail. Median examples:

```text
vision_dirty_units     +56.75  ratio 1.088  r=0.761
vision_tile_updates  +1078.33  ratio 1.088  r=0.761
```

Movement-related position commits rise as well (`effect_position_index_changes` median ratio ~1.067, r~0.623). This supports H3: part of the tail is associated with frames carrying more movement/vision work, which then coincides with heavier UnitRender work.

This is not yet proof of one common upstream causal variable, but it is strong enough to motivate volume attribution rather than another representation micro-optimization.

## 30 Hz diagnostic

E7 observed:

```text
p99: 33.209 / 33.169 / 33.190 ms
median: 33.190 ms
<=33.33 ms: 3/3
```

This is encouraging but not a frontier update. E7 uses a 10 s profiler horizon and is attribution-only; aggregate machine state is also faster than some prior formal runs. A later canonical production validation is still required for a release/frontier decision.

## Interpretation

Formal decision:

```text
STABLE_TAIL_CONTRIBUTORS_FOUND
```

Refined next causal target:

```text
UnitRenderSystem self / render-volume path
NOT unit_visible_cull
```

No production optimization or retained-source change is authorized by E7 itself.
