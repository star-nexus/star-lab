# Dynamic World Scaling Methodology Evolution

**Status:** ARCHIVED — complete provenance-bound formal archive  
**STAR repository:** `star-nexus/star`  
**Branch at time:** `perf/scale-harness`

## 1. Purpose

This case preserves how the controlled 5000-unit Dynamic World workload evolved before and during the investigations that later closed realtime GC tails, memory retention, unit culling, and Vision-cache thrashing.

It is not a single optimization A/B. It is a **methodology-evolution case**.

## 2. Provenance-bound cohorts

The three archived cohorts are now bound to exact STAR HEADs from contemporaneous run-handoff records. The raw JSON files themselves do not encode Git SHAs, so the archive records the provenance basis explicitly rather than pretending the artifacts self-identify their source revision.

| Cohort | STAR HEAD | Provenance meaning |
|---|---|---|
| V1 | `0f0d0a2a173457de099af714b2ee5b86600f91b2` | Formal first Dynamic World Density Curve protocol: warmup, common 5000-plan pool, nested execution density, fixed Fog/camera/zoom guards, deferred measurement epoch. |
| V2 | `571ea207db52478a56f0710c6cad7e45de3bf0e3` | Incremental Fog presentation generation with explicit fog/tail diagnostics present in the source snapshot. |
| V2.1 | `916d88dcd3d796fe49a0cadd64be40b68c331b5c` | Rare UnitRender tail attribution + zero-copy Fog presenter handoff on top of the verified renderer implementation. |

### Why these SHAs are considered proven

For each cohort, the contemporaneous development/run handoff explicitly recorded the current pushed `perf/scale-harness` HEAD immediately before the user ran that generation of measurements. Git inspection independently confirms that the commit snapshots contain the implementation/diagnostic contract associated with the corresponding archived cohort.

The evidence is therefore:

```text
contemporaneous run-handoff HEAD
        +
Git commit contents
        +
raw artifact schema / workload signature
        -> provenance-bound cohort
```

The raw JSON files still remain the canonical measurement evidence; the recovered run-handoff record supplies source identity.

## 3. Archived results

### V1 — first formal Density Curve

`results/v1/` contains:

- density 0 / 10 / 25 / 50 / 75 / 100%;
- synchronized burst at 0% and 100%.

The V1 protocol isolates execution density using a common 5000-plan pool and nested deterministic prefixes. Its 100%-moving point preserves the earlier high-cost rendering state, including roughly 32 ms average frame time and a large MapRender contribution.

### V2 — incremental Fog generation

`results/v2/` preserves 0 / 10 / 100% density points after the Fog presentation path became incremental. The 100% point is substantially lower-cost than V1, with MapRender reduced to the ~2 ms class while UnitRender/cull remain material.

The V2 source snapshot exposes diagnostic fields including:

```text
fog_render_mode
fog_delta_tiles
fog_patch_tiles
epoch_worst_slow_frame_ms
```

which matches the V2 artifact generation contract.

### V2.1 — rare-tail attribution

`results/v2.1/` preserves 0%, 100%, and a front-window 100% variant after adding low-overhead UnitRender/GC/command-queue tail diagnostics and the MapRender visible-set handoff cleanup.

This cohort is the immediate methodology context that led into the dedicated realtime-GC investigation.

## 4. Stable workload identity

Across the archived formal scale family, the controlled dimensions include:

```text
scenario        TestMap-8K-scale-5000
map             91x91
resident units  5000
seed            42
target radius   12
Fog             ON for formal points
camera/zoom     fixed for a measurement epoch
zoom            0.15 in canonical large-window runs
warmup          5 wall-clock seconds in formal V1 protocol
sustained       20 simulation seconds
snapshot        10 wall-clock seconds after kickoff
measurement     300-frame rolling window
```

Density and motion phase vary according to the experiment point. V1 also retains explicit synchronized burst points separately from the staggered scalability curve.

## 5. Source-bound replay entrypoint

For a cohort, checkout its bound STAR source state first:

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags

git checkout <cohort-sha>
uv sync
```

The formal density-point shape is:

```bash
STAR_SCALE_HARNESS_SOCKET=/tmp/star-scale.sock \
uv run rotk_env/main.py \
  --skip-start \
  --scenario TestMap-8K-scale-5000 \
  --mode real_time \
  --players human_vs_two_ai \
  --seed 42 \
  --no-hub \
  --profile
```

Then, from another shell:

```bash
uv run tools/scale_driver.py \
  --socket /tmp/star-scale.sock \
  density-point \
  --density 1.0 \
  --seed 42 \
  --target-radius 12 \
  --duration 20 \
  --phase staggered \
  --require-fog on \
  --warmup 5 \
  --sample-after 10 \
  --output result.json
```

Use the raw artifact metadata/guards to verify that a replay actually matches the archived point. Do not substitute requested density for achieved density.

## 6. Raw evidence and integrity

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

## 7. Interpretation boundary

The three cohorts are now source-bound, but they still must **not** be treated as a single-variable A/B series. Multiple engineering changes separate V1, V2, and V2.1.

What the series supports is a historical methodology claim:

> As dominant rendering work was removed and measurement controls improved, previously hidden residual costs and rare tails became measurable enough to isolate with dedicated experiments.

Dedicated GC, Memory, Cull, and Vision cases remain the canonical source for their causal conclusions.

## 8. Archive state

This case is now provenance-complete:

```text
raw evidence        verified
artifact integrity  SHA256 verified
workload metadata   present
V1 source HEAD      bound
V2 source HEAD      bound
V2.1 source HEAD    bound
formal archive      complete
```

The provenance SHAs come from contemporaneous run-handoff records plus matching Git commit inspection; they are not inferred from directory names or benchmark values.
