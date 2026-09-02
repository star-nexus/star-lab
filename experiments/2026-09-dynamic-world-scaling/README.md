# Dynamic World Scaling Methodology Evolution

**Status:** ARCHIVED — raw evidence complete; exact source provenance per cohort pending backfill  
**STAR repository:** `star-nexus/star`

## 1. Purpose

This case preserves how the controlled 5000-unit Dynamic World workload evolved before and during the investigations that later closed realtime GC tails, memory retention, unit culling, and Vision-cache thrashing.

It is not a single optimization A/B. It is a **methodology-evolution case**.

## 2. Archived cohorts

### V1

`results/v1/` contains:

- density 0 / 10 / 25 / 50 / 75 / 100%;
- synchronized burst at 0% and 100%.

The V1 100%-moving run is valid and shows the earlier high-cost rendering state, including an average frame around 32 ms and a large MapRender contribution.

### V2

`results/v2/` preserves 0 / 10 / 100% density points. The 100% point is substantially lower-cost than V1, with MapRender near the ~2 ms class, while UnitRender/cull remain material.

### V2.1

`results/v2.1/` preserves 0%, 100%, and a front-window 100% variant. This cohort is close to the workload context that exposed the later tail/cull/cache investigations.

## 3. Stable workload identity visible in the raw artifacts

Across the archived formal scale family, the important controlled dimensions include:

```text
scenario        TestMap-8K-scale-5000
map             91x91
resident units  5000
seed            42
Fog             ON for formal points
camera/zoom     fixed for a measurement epoch
zoom            0.15 in the canonical large-window runs
measurement     300-frame rolling window
```

Density and motion phase vary according to the experiment point.

## 4. Raw evidence

```text
results/v1/    8 JSON artifacts
results/v2/    3 JSON artifacts
results/v2.1/  3 JSON artifacts
```

All 14 artifacts are covered by:

[`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

Verify:

```bash
shasum -a 256 -c artifacts/SHA256SUMS
```

## 5. Provenance limitation

The raw JSON files were recovered from the original local results directory, but they do not by themselves prove the exact STAR commit for each V1/V2/V2.1 cohort.

Therefore this case intentionally does **not** invent:

```text
v1_commit
v2_commit
v2_1_commit
```

Those fields remain pending until Git history, terminal transcript, or another primary record can bind each cohort to an exact SHA.

This is an example of the STAR Lab rule:

> Real raw data with incomplete provenance is better labeled honestly than completed with a guessed commit.

## 6. Relationship to later cases

The Dynamic World workload became the common diagnostic environment in which later work isolated:

- realtime Gen2 GC tail latency;
- long-run live-state retention;
- residual unit-cull hot-loop work;
- Vision geometry-cache working-set pressure.

Those later cases own their own exact source provenance and canonical formal artifacts.

## 7. Archive state

This case becomes `complete_formal_archive` only after exact source SHA(s) for the V1/V2/V2.1 cohorts are proven and recorded in `manifest.yaml`.
