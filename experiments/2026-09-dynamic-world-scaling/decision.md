# Decision — Dynamic World Scaling Archive

## Decision

Preserve V1/V2/V2.1 as one methodology-evolution case with the original 14 JSON artifacts, SHA256 checksums, and exact source HEAD for each cohort.

The recovered provenance is:

```text
V1    0f0d0a2a173457de099af714b2ee5b86600f91b2
V2    571ea207db52478a56f0710c6cad7e45de3bf0e3
V2.1  916d88dcd3d796fe49a0cadd64be40b68c331b5c
```

## Why keep the series

The series records how the large-scale test harness and rendering path evolved until distinct realtime bottlenecks could be isolated cleanly. It preserves evidence that would otherwise remain as disconnected local benchmark files.

## Provenance decision

The raw JSON artifacts do not encode Git SHAs. Exact source identity is instead recovered from contemporaneous run-handoff records that explicitly state the current pushed `perf/scale-harness` HEAD before each cohort was tested.

Those records are corroborated by Git inspection:

- V1 HEAD contains the formal common-plan-pool Density Curve protocol and explicit `dynamic-world-v1` output paths;
- V2 HEAD contains incremental Fog/tail diagnostic fields matching the V2 generation;
- V2.1 HEAD is the rare UnitRender tail-attribution overlay used immediately before the V2.1 measurements.

Therefore the cohort SHAs are recorded as proven source anchors rather than guessed associations.

## Interpretation boundary

Source provenance being complete does **not** make V1→V2→V2.1 a one-variable A/B experiment.

Multiple engineering changes separate the cohorts, so cross-cohort timing differences are historical progression evidence, not isolated causal estimates.

Dedicated cases own the causal conclusions:

```text
Realtime GC
Memory retention
Spatial cull
Vision cache
```

Dynamic World owns the workload/methodology evolution and the source context that made those investigations reproducible.

## Reproduction rule

To replay a cohort:

1. checkout the cohort's bound STAR SHA;
2. launch `TestMap-8K-scale-5000` in realtime/no-Hub/profile mode;
3. run the scale driver with the archived seed, target radius, density/phase, Fog guard, warmup, duration, and sample timing;
4. compare achieved guards/metadata, not merely requested parameters;
5. do not mix measurements from different source cohorts under one provenance label.

## Archive state

```text
raw evidence        verified
SHA256              verified
workload metadata   present
V1 source HEAD      proven
V2 source HEAD      proven
V2.1 source HEAD    proven
formal-complete     yes
```

## Principle

> Source provenance tells us **what code produced an observation**; controlled A/B design tells us **what caused a difference**. They are related, but not interchangeable.
