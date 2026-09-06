# Analysis — 10K MovementSystem Lookup Elimination

## Observation

At the Phase-5 10K Core Runtime baseline, residency itself was acceptable but dynamic workload was not:

```text
0% moving   controlled P99 20.595 ms  PASS @30Hz
50% moving  controlled P99 36.581 ms  FAIL
100% moving controlled P99 46.191 ms  FAIL
```

From 0% to 100% moving, `AnimationSystem` rose from ~0.011 ms to ~13.541 ms average and was the largest dynamic-system contributor.

## Hypothesis

`AnimationSystem._update_movement_animations()` called `_get_movement_system()` inside the loop over moving entities. `_get_movement_system()` scans `world.systems` by class name. Because system membership is stable during one synchronous ECS update, repeated lookup work has no additional semantic value.

Expected signature:

```text
moving units 5000 -> 10000
lookup calls 5000 -> 10000
per-call time approximately stable
lookup frame cost approximately linear
```

## Instrumentation

Phase-5.1 added measurement-only section timing and sampled hot-loop probes without changing production source. The attribution harness was source-guarded against exact production blobs.

Attribution run `20260906-033723` measured:

```text
50% moving:
  lookup calls/frame  5000
  estimated lookup    ~2.794 ms/frame
  per call             ~0.559 us

100% moving:
  lookup calls/frame  10000
  estimated lookup    ~5.550 ms/frame
  per call             ~0.555 us
```

The nearly constant per-call cost and linear frame total confirm the repeated dependency scan as first-class scaling work.

The attribution run itself added measurable probe overhead, so its absolute frame time was not used as canonical performance evidence. The production baseline remained canonical.

## Candidate fix

Move one line:

```text
before:
for mover:
    movement_system = _get_movement_system()

fixed:
movement_system = _get_movement_system()
for mover:
    ...
```

No component-access, movement-progress, position-commit, spatial-index, Vision, rendering, or GC semantics changed.

## Controlled A/B evidence

### 50% moving

```text
controlled avg   30.239 -> 25.964 ms
controlled P95   34.759 -> 27.392 ms
controlled P99   36.581 -> 29.447 ms
Animation avg     6.530 ->  3.633 ms
Animation P99     8.591 ->  4.106 ms
30Hz gate          FAIL -> PASS
```

### 100% moving

```text
controlled avg   41.589 -> 34.180 ms
controlled P95   43.744 -> 35.686 ms
controlled P99   46.191 -> 38.537 ms
Animation avg    13.541 ->  7.770 ms
Animation P99    14.890 ->  8.481 ms
```

The direct production `AnimationSystem` reduction at 100% moving is ~5.771 ms/frame, closely matching the attribution estimate of ~5.55 ms/frame.

## Workload preservation

The fix did not reduce authoritative world evolution. At 100% moving:

```text
baseline: 23.132 fps * 863.897 position-index changes/frame ~= 19.98K/s
fixed:    27.977 fps * 713.914 position-index changes/frame ~= 19.97K/s
```

Vision dirty throughput remained approximately 20K/s as well. Faster frames redistributed the same realtime state-transition throughput across more frames.

## Root cause

A stable system dependency was resolved in the per-moving-entity hot loop. The resulting `O(Nmoving * Nsystems)` work was semantically redundant and became large at 10K movement density.

## Rejected explanations

- **Machine-wide speedup:** rejected because the 0%-moving point stayed essentially unchanged while dynamic points improved strongly.
- **Reduced movement workload:** rejected because committed-position and Vision-dirty throughput per second remained stable.
- **Vision optimization:** no Vision code changed; the secondary per-frame Vision reduction is explained by realtime feedback from higher FPS and fewer commits per frame.

## Lesson

A tiny lookup can dominate scale when placed at the wrong complexity level. The relevant question is not how expensive one call looks, but how often the architecture forces it to execute at target scale.
