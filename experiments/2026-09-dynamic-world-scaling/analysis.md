# Analysis — Dynamic World Scaling Methodology

## 1. Observation

The recovered archive contains three generations of controlled 5000-unit Dynamic World results rather than one isolated benchmark run.

The raw artifacts preserve density curves, synchronized bursts, fixed-camera/Fog guards, and subsystem timing breakdowns. This makes the series useful as a methodology record even before exact source provenance for every cohort is backfilled.

## 2. Representative progression

Representative valid 100%-moving runs show:

```text
V1 density100
  avg frame      ~32.015 ms
  MapRender      ~10.923 ms
  unit cull      ~3.400 ms

V2 density100
  avg frame      ~23.027 ms
  MapRender      ~1.932 ms
  unit cull      ~3.551 ms

V2.1 density100
  avg frame      ~23.092 ms
  MapRender      ~1.978 ms
  unit cull      ~3.570 ms
  later tail behavior remains visible
```

These rows should not be interpreted as a clean one-variable A/B: exact source states are not yet bound and several engineering changes may separate cohorts.

What the series does support is a historical observation:

> As dominant MapRender work was reduced, other costs and tail behavior became visible enough to isolate in later dedicated experiments.

## 3. Why this archive matters

The methodology gradually establishes the dimensions needed for trustworthy realtime scaling work:

```text
resident population
moving density
staggered vs synchronized phase
Fog requirement
camera/zoom stability
warmup / measurement epoch
rolling-window completeness
subsystem timing
```

Without these controls, aggregate FPS would confound workload changes with implementation changes.

## 4. Later dedicated investigations

The controlled workload context later enabled stronger causal experiments for:

```text
GC policy
  -> AUTO vs realtime_defer

memory retention
  -> repeated safe-GC soak

unit culling
  -> pre/post hot-loop implementation

Vision cache
  -> 4096/8192/16384/32768 capacity ablation
```

Those dedicated cases, rather than this methodology series, are the canonical source for their final causal conclusions.

## 5. Provenance caveat

Directory labels `v1`, `v2`, and `v2.1` are archive cohort names. They are not source-control identities.

Until the exact STAR commit is recovered for each cohort, do not use these results to claim that a specific commit caused the observed cross-cohort timing differences.

## 6. Next backfill task

Search Git history / terminal records for the exact points at which each cohort was produced, then update `manifest.yaml` with proven SHAs and add reproducible checkout commands to `README.md`.
