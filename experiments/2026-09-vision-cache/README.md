# Vision Geometry Cache Working-Set Ablation

**Status:** CLOSED  
**STAR repository:** `star-nexus/star`  
**Problem-state commit:** `615c3ac27f23f73b38d13b97280861fd1b0c9b72`  
**Formal measurement commit:** `253c78730dee2b50c038d9d8cad70c661b2e04c5`  
**Scale-default fix commit:** `6b5a24053a10a0bca721a2750a5753195bbf2d34`  
**Regression commit:** `86672d6f00a995c36a5f268a47f46ffe8d382301`  
**Documented milestone:** `a24482d438157aa23b371b6e34d49b1c04fec7f7`

## 1. Problem

Bounding the previously unbounded Vision geometry cache fixed long-run memory growth, but the initial 4096-entry LRU introduced a new steady-state latency regression. Under the 5000-unit Dynamic World workload, `VisionSystem` rose from the historical ~1.2 ms class to ~2.9 ms.

The question was not simply "should the cache be larger?" It was:

> What is the smallest bounded capacity that covers the measured geometry working set without LRU thrashing, and what operational default leaves reasonable future headroom?

## 2. Reproduce the ablation

Use the commit that contains the fresh-process capacity override and epoch-local cache counters:

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout 253c78730dee2b50c038d9d8cad70c661b2e04c5
uv sync
```

For each capacity, start a **fresh ENV process**. Example for 4096:

```bash
STAR_SCALE_HARNESS_SOCKET=/tmp/star-scale.sock \
STAR_SCALE_GC_POLICY=realtime_defer \
STAR_SCALE_VISION_GEOMETRY_CACHE_MAX_ENTRIES=4096 \
uv run rotk_env/main.py \
  --skip-start \
  --scenario TestMap-8K-scale-5000 \
  --mode real_time \
  --players human_vs_two_ai \
  --seed 42 \
  --no-hub \
  --profile
```

Keep Fog ON, camera fixed, and zoom at `0.15`.

Run:

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
  --output capacity-4096.json
```

Repeat with fresh processes for `8192`, `16384`, and `32768`, changing both the environment variable and output filename.

## 3. Expected signatures

### 4096 — thrashing

```text
Vision self              2.9246 ms
geometry hit rate        72.39%
epoch lookups            68,854
epoch misses             19,010
epoch evictions          19,010
final cache size         4096
avg frame                22.322 ms
P99                      27.117 ms
```

The key signature is not aggregate FPS: after saturation, `misses == evictions`, showing capacity-driven churn.

### 8192 — measured minimum sufficient

```text
Vision self              1.2260 ms
geometry hit rate        99.14%
epoch misses             639
epoch evictions          0
final cache size         5639
avg frame                20.507 ms
P99                      25.296 ms
```

### 16384 — same cache behavior with headroom

```text
Vision self              1.2241 ms
geometry hit rate        99.14%
epoch misses             639
epoch evictions          0
final cache size         5639
avg frame                20.453 ms
P99                      24.290 ms
```

### 32768 — no demonstrated cache benefit

```text
Vision self              1.3496 ms
geometry hit rate        99.04%
epoch misses             639
epoch evictions          0
final cache size         5639
```

The slower aggregate 32768 process is **not** evidence that a larger capacity itself causes slowdown; unrelated subsystems and planning/GC timing were also slower in that process.

## 4. Final decision

```text
8192  = measured minimum sufficient for the validated 5K workload
16384 = scale/window operational default with future headroom
4096  = rejected for scale/window because it thrashes
32768 = not justified by current evidence
```

Capacity is an upper bound, not preallocation. At 5K, 16384 still retained only ~5639 entries.

The working set is keyed by:

```text
(center, effective_range, terrain_revision)
```

so it is not directly proportional to unit count. Future 10K/20K decisions must be driven by occupancy, hit rate, sustained eviction, map scale, and effective-range diversity rather than mechanically doubling capacity with unit count.

## 5. Validate the operational default

```bash
git checkout 86672d6f00a995c36a5f268a47f46ffe8d382301
uv run pytest \
  rotk_env/tests/test_scale_vision_cache_config.py \
  rotk_env/tests/test_scale_vision_cache_ablation.py \
  rotk_env/tests/test_vision_incremental_index.py
```

The scale/window default should be 16384 while the explicit environment override remains available for experiments.

## 6. Formal evidence

- [`results/capacity-4096.json`](results/capacity-4096.json)
- [`results/capacity-8192.json`](results/capacity-8192.json)
- [`results/capacity-16384.json`](results/capacity-16384.json)
- [`results/capacity-32768.json`](results/capacity-32768.json)
- [`manifest.yaml`](manifest.yaml)
- [`analysis.md`](analysis.md)
- [`decision.md`](decision.md)
