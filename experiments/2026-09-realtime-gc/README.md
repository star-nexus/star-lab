# Realtime Gen2 GC Tail Latency

**Status:** CLOSED (historical archive; original A/B JSON backfill pending)  
**STAR repository:** `star-nexus/star`  
**Diagnostic pre-policy commit:** `916d88dcd3d796fe49a0cadd64be40b68c331b5c`  
**GC policy implementation:** `6bdeabe210fbc2e8dc3612a03e0cab11df1e77a1`  
**Scale integration:** `74708af3f1bf2c31b050cf816e30aa52613fcda8`  
**Formal env-selected A/B guard:** `33b18bc777df992ff8665d458d70782451d05a51`  
**Policy documentation:** `3c9f54124686b1b3c8c94a12d0174228d78a87f9`

## 1. Problem

The 5000-unit realtime workload had acceptable average throughput but rare frame/UnitRender tails near the 50 ms class. Initial profiling attributed the spike to `UnitRenderSystem`, but detailed GC instrumentation showed that the long pause was a CPython generation-2 cyclic collection occurring inside the timed render call.

This is a classic attribution trap:

> The profiler showed where the process was paused, not necessarily which subsystem created the expensive work.

## 2. Diagnostic source state

The commit below contains low-overhead UnitRender/GC tail attribution but predates the controlled realtime GC policy:

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout 916d88dcd3d796fe49a0cadd64be40b68c331b5c
uv sync
```

Under the formal 5000-unit 100%-moving workload, the historical slow-frame signature included:

```text
UnitRender / frame tail        ~50 ms class
GC pause in worst frame        30.897 ms
Gen2 portion                   30.846 ms
GC collected objects           0
```

The fact that the collection reclaimed zero objects was also important: the pause itself was expensive even when it found nothing to reclaim.

## 3. Reproduce the controlled A/B

Use the formal measurement source:

```bash
git checkout 33b18bc777df992ff8665d458d70782451d05a51
```

Start a fresh ENV for each policy.

### AUTO

```bash
STAR_SCALE_HARNESS_SOCKET=/tmp/star-scale.sock \
STAR_SCALE_GC_POLICY=auto \
uv run rotk_env/main.py \
  --skip-start \
  --scenario TestMap-8K-scale-5000 \
  --mode real_time \
  --players human_vs_two_ai \
  --seed 42 \
  --no-hub \
  --profile
```

Run the formal 100%-moving staggered density point with Fog ON and fixed camera/zoom.

### realtime_defer

Restart a fresh ENV and change only:

```bash
STAR_SCALE_GC_POLICY=realtime_defer
```

The measurement guard must report that the requested policy matches the active runtime state.

## 4. Historical A/B result

### AUTO

```text
avg frame                 23.244 ms
P50                       21.861 ms
P95                       25.984 ms
P99                       48.815 ms
max                       ~52.742 ms (worst observed 57.756 ms)
UnitRender max            34.839 ms
animated draw max         29.434 ms
worst-frame GC            30.897 ms
Gen2                      30.846 ms
collected                 0
```

### realtime_defer

```text
pre-measurement Gen2 GC   ~19.746 ms at safe boundary
avg frame                 21.837 ms
P50                       21.001 ms
P95                       24.940 ms
P99                       25.489 ms
max                       26.581 ms
slow frames               0
UnitRender max            7.103 ms
animated draw max         1.582 ms
```

## 5. Policy

```text
before bounded realtime critical phase:
  full generation-2 collection
  disable automatic cyclic GC

during critical phase:
  CPython reference counting remains active
  automatic cyclic collection is deferred

at explicit safe point / deadline:
  restore the caller's previous automatic-GC state
  maintenance may run outside the latency-critical epoch
```

The policy is bounded and restores the exact prior GC-enabled state. It is not "disable garbage collection forever."

## 6. Result

The P99 cliff was removed by moving unpredictable cyclic-GC maintenance out of the realtime measurement window:

```text
P99: 48.815 ms -> 25.489 ms
max: ~52-58 ms -> 26.581 ms
UnitRender max: 34.839 ms -> 7.103 ms
```

## 7. Archive note

This investigation predates STAR Lab. Exact implementation/diagnostic commits and validated numeric summaries are preserved, but the original AUTO/defer JSON artifacts are not present in the current archive workspace. Add them if recovered; do not synthesize replacements.
