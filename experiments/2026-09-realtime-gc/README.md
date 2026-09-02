# Realtime Gen2 GC Tail Latency

**Status:** CLOSED — complete formal archive  
**STAR repository:** `star-nexus/star`  
**Diagnostic pre-policy commit:** `916d88dcd3d796fe49a0cadd64be40b68c331b5c`  
**GC policy implementation:** `6bdeabe210fbc2e8dc3612a03e0cab11df1e77a1`  
**Scale integration:** `74708af3f1bf2c31b050cf816e30aa52613fcda8`  
**Formal A/B measurement commit:** `33b18bc777df992ff8665d458d70782451d05a51`  
**Later milestone tag:** `scale-v1-cull-vision-closed`

## 1. Problem

The 5000-unit realtime workload had acceptable average throughput but rare frame tails near the 50 ms class. Initial profiling attributed the spike to `UnitRenderSystem`; GC instrumentation showed that a CPython generation-2 cyclic collection was occurring inside the timed render call.

> The profiler showed where execution was paused, not which semantic subsystem owned the maintenance work.

## 2. Reproduce the diagnostic state

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout 916d88dcd3d796fe49a0cadd64be40b68c331b5c
uv sync
```

Expected slow-frame signature under the formal 5K / 100%-moving workload:

```text
GC pause in worst frame        30.896833 ms
Gen2 portion                   30.845625 ms
GC collected objects           0
```

## 3. Reproduce the controlled A/B

Use:

```bash
git checkout 33b18bc777df992ff8665d458d70782451d05a51
```

Start a fresh ENV for each policy:

```bash
STAR_SCALE_HARNESS_SOCKET=/tmp/star-scale.sock \
STAR_SCALE_GC_POLICY=<auto|realtime_defer> \
uv run rotk_env/main.py \
  --skip-start \
  --scenario TestMap-8K-scale-5000 \
  --mode real_time \
  --players human_vs_two_ai \
  --seed 42 \
  --no-hub \
  --profile
```

Run the same 100%-moving staggered density point with Fog ON, fixed camera, zoom `0.15`, warmup 5 s, sustained duration 20 s, and the 300-frame formal measurement window.

The policy guard must match the requested runtime state.

## 4. Canonical raw evidence

- [`results/density-100-auto.json`](results/density-100-auto.json)
- [`results/density-100-realtime-gc.json`](results/density-100-realtime-gc.json)
- [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

Verify from this experiment directory:

```bash
shasum -a 256 -c artifacts/SHA256SUMS
```

## 5. Formal A/B result

| Metric | AUTO | `realtime_defer` |
|---|---:|---:|
| Avg frame | 23.244 ms | 21.837 ms |
| P50 | 21.861 ms | 21.001 ms |
| P95 | 25.984 ms | 24.940 ms |
| P99 | 48.815 ms | 25.489 ms |
| Max frame | 52.742 ms | 26.581 ms |
| UnitRender max | 34.839 ms | 7.103 ms |
| Animated draw max | 29.434 ms | 1.582 ms |
| In-window worst GC pause | 30.897 ms | none observed |

The deferred run performs a proactive full Gen2 collection before the measured critical epoch (`19.745916 ms`, `collected=0`) and keeps automatic cyclic GC disabled only for the bounded realtime phase.

## 6. Policy

```text
before bounded realtime critical phase:
  full generation-2 collection
  disable automatic cyclic GC

during critical phase:
  CPython reference counting remains active
  automatic cyclic collection is deferred

at deadline / explicit safe point:
  restore caller's previous GC-enabled state
```

This is not “disable GC forever.” It schedules unpredictable maintenance outside the latency-critical loop.

## 7. Result

```text
P99             48.815 -> 25.489 ms
UnitRender max  34.839 ->  7.103 ms
```

The raw A/B artifacts are now recovered and integrity-verified; this case no longer depends on summary-only historical backfill.
