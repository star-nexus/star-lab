# Phase 5 E7 — 10K / 100% Moving P99 Tail Composition Attribution

**Status:** DRAFT / PREREGISTERED — measurement pending  
**STAR repository:** `star-nexus/star`  
**Retained production runtime:** `e7ba18b31870577110b591104ef8fa7b4713e43c`  
**Experiment branch:** `experiment/phase5-tail-composition-attribution`  
**Frozen tooling commit:** `33d3715c1310a33bc3b9ff44a8deb7f633bf21d4`

## Question

After E6-1, 10K / 100%-moving production remains very close to the canonical 30 Hz threshold. Repeated formal runs have shown controlled-work p99 around 33.5–33.7 ms while controlled average is around 31.9–32.1 ms.

E7 asks:

> Which controlled-work subsystems rise together in the same tail frames, and which stable per-frame contributor actually creates the p95/p99 uplift above ordinary frames?

This is a diagnostic attribution stage, not an optimization and not a frontier run.

## Measurement principle

The existing `PerformanceProfiler` already stores aligned per-frame controlled-work, section self/inclusive samples and frame metrics. E7 does not add timers to production hot paths. The experiment launcher only:

1. extends the profiler rolling retention horizon from 5 s to 10 s; and
2. augments `get_stats()` at snapshot time with correlation / conditional-tail analysis of the already-recorded aligned deques.

No gameplay, movement, Vision, Fog, render or spatial-index semantics change.

## Formal workload

Three independent repeats of exact retained production:

```text
resident units       10000
moving density       100%
Fog                  ON
motion phase          staggered
seed / phase seed    42 / 42
route steps           12
GC                    realtime_defer
render                uncapped
MiniMap dynamic units OFF
input                 blocked
execution pathfinding OFF
production animation/commits ON
run duration          20 s
sample_after          19 s
profiler horizon      10 s
minimum aligned frames per repeat 250
```

## Tail attribution sets

Primary attribution does **not** use only the top 1% frames because that set is too small.

Per repeat:

```text
tail set      = controlled_work >= per-run p95
reference set = per-run p25 <= controlled_work <= p75
```

For each controlled-category section `s`:

```text
uplift_s = mean(self_ms_s | tail) - mean(self_ms_s | reference)
```

Contribution uses **section self time**, matching the definition of controlled work and avoiding parent/child inclusive double counting.

P99 and frames above 33.33 ms remain diagnostics. They do not define the primary contributor set.

## Stability rule

A section is an actionable stable contributor only if:

```text
appears in positive top-3 uplift in at least 2 of 3 repeats
median tail uplift >= 0.15 ms
```

Possible formal decisions:

```text
STABLE_TAIL_CONTRIBUTORS_FOUND
NO_ACTIONABLE_STABLE_TAIL_CONTRIBUTOR
INVALID_GUARDS
```

When contributors are found, the highest stable median uplift becomes the next causal target. E7 itself authorizes no optimization KEEP.

## Pre-measurement runner correction

An initial invocation reached and passed the tail-math contract (`2 passed`) and targeted regressions (`20 passed`) but stopped before `repeat-1` began because Bash `set -u` expanded a dependent `local` initializer before its sibling local variable had been assigned:

```bash
local repeat="$1" point_dir="$RUN_DIR/repeat-${repeat}" cleanup_rc
```

The runner now splits dependent locals into separate assignments. No formal performance point was produced by the failed invocation, so it is not part of E7 evidence and does not change the preregistered workload, attribution sets, thresholds, or possible decisions.

## 30 Hz rule

The analyzer reports each repeat's 100%-moving controlled p99 and their median against 33.33 ms, but:

```text
frontier_update_authorized = false
```

E7 is attribution-only.

## Artifacts

Canonical command:

```bash
bash tools/run_phase5_tail_composition.sh
```

The runner emits Compact + Raw two-tier evidence. Compact is the default review package; Raw remains the forensic substrate.
