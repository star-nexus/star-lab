# Performance Measurement & Regression Infrastructure — 2026-09

**Status:** CLOSED / VALIDATED  
**STAR repository:** `star-nexus/star`  
**Development branch:** `perf/measurement-regression-infra`  
**Baseline before Phase 3:** `83bae994b6904adc9bce335b11df0e8fdb5c1fc9`  
**Validated Phase 3 commit:** `ee81087175d51fb626836d0c1514433076bf62bd`  

## Scope

Phase 3 combined two goals:

- **B — Performance Regression Infrastructure**
- **F — Performance Measurement Refinement**

The objective was not to optimize another subsystem. It was to make STAR performance evidence causally interpretable and to add small regression contracts that protect already validated fast paths without turning platform noise into STAR regressions.

## Final measurement semantics

The production profiler now uses a ~5 second wall-clock rolling horizon with a 4096-frame hard capacity. Capped and uncapped runs therefore represent comparable elapsed time rather than a fixed number of frames.

Frame cost is separated into:

```text
STAR-controlled work
  work + update + render + vision + STAR input dispatch

platform input
  SDL/Pygame event pump + queue retrieval

present
  display/compositor boundary

wait
  intentional FPS limiter wait

uninstrumented
  measured frame-body residual not covered by profiler sections
```

`controlled_work` is computed from exclusive/self category times to avoid nested double counting. `active_ms` remains a compatibility field and is not used as the generic STAR regression signal.

The profiler also distinguishes:

```text
frame_body_fps
window_throughput_fps
inter_frame_gap_ms
```

and explicitly reports slow-frame history scope as `gameplay_epoch`.

## Platform boundary discovered

Visible-window throughput on the macOS/Pygame path was observed to be presentation-state dependent even when STAR-controlled work remained stable.

Repeated profiled runs showed approximately:

```text
STAR controlled_work avg   ~2.29–2.33 ms
render_engine avg           ~1.59–1.61 ms
render_scalar_execute avg   ~1.28–1.29 ms

display_present avg         ~1.88 ms OR ~5.7 ms
```

The presentation split could move visible throughput from roughly 230 FPS to roughly 122 FPS while STAR-controlled work remained nearly unchanged.

Decision:

> `display_present`, `platform_input`, raw FPS and visible-window throughput remain diagnostic/attribution signals, not generic STAR merge-blocking regression gates.

This is consistent with the separately archived macOS SDL event-pump platform-tail case.

## Regression design

The final design was intentionally reduced to two mechanisms.

### 1. Portable structural contracts

`tools/run_performance_contracts.py` curates deterministic tests for validated architecture/complexity invariants, including:

- profiler measurement/accounting semantics;
- render blit batching;
- one-dirty-unit Vision recomputation;
- incremental Fog presentation;
- spatial Unit culling;
- map overscan reuse;
- opaque Terrain presentation fast path.

These checks are suitable for normal developer machines and CI because they primarily protect what work happens rather than machine-specific milliseconds.

### 2. Deterministic visible-window workloads

#### `static-window-v1`

Fixed production visible-window workload with no gameplay input or world movement. It protects steady-state workload shape and pinned-host timing.

Reference timing contract:

```text
controlled_work p99       <= 3.6 ms
render_engine avg          <= 2.0 ms
render_scalar_execute avg  <= 1.6 ms
uninstrumented p99         <= 0.2 ms
```

The `uninstrumented` threshold is a measurement-coverage guard, not a performance target: substantial new uninstrumented frame work must not bypass the controlled-work gate.

#### `one-mover-v1`

A single production `MovementSystem` order is issued at the start of the final 5-second measurement window. The plan is selected during warm-up from production `reachable_hexes()` rules; benchmark target selection is therefore excluded from the measured dynamic interval.

With fixed seed/map the validated workload was deterministic across three runs:

```text
mover entity   236
from           (3, 3)
to             (6, -1)
path length    7
move cost      6
```

The workload exercised the intended dynamic chain:

```text
MovementSystem
→ Animation
→ HexPosition commit
→ Vision dirty/refcount update
→ incremental Fog delta
```

Three validated runs produced:

| Metric | Run 1 | Run 2 | Run 3 |
|---|---:|---:|---:|
| controlled_work max | 3.143416 ms | 3.086375 ms | 3.192083 ms |
| uninstrumented p99 | 0.023930 ms | 0.025642 ms | 0.024416 ms |
| measurement throughput | 222.8 FPS | 226.8 FPS | 221.6 FPS |
| Fog delta max | 7 | 7 | 7 |
| Vision dirty max | 1 | 1 | 1 |
| Vision scanned max | 1 | 1 | 1 |
| Vision changed max | 1 | 1 | 1 |
| Vision cache evictions max | 0 | 0 | 0 |

The final dynamic timing rule uses `max`, not `p99`, because movement commits occupy less than one percent of frames and could otherwise fall outside the p99 boundary:

```text
controlled_work max       <= 4.0 ms
uninstrumented p99        <= 0.2 ms
```

All three runs passed the final `one-mover-v1-reference` contract: **22/22 rules per run**.

## Validation evidence

Final local validation at the validated STAR commit/source state:

```text
uv run python tools/run_performance_contracts.py
→ 29 passed

focused measurement/gate tests
→ 22 passed

uv run python -m compileall -q framework protocol rotk_agent rotk_env performance_profiler.py tools
→ PASS / no output

git diff --check 83bae994b6904adc9bce335b11df0e8fdb5c1fc9...HEAD
→ PASS / no output
```

A full `uv run pytest -q` reported:

```text
809 passed
5 failed
```

All five failures were caused by unrelated local map-editor work: tracked `rotk_env/maps/chibi.json` had been deleted/replaced locally, so tests requiring scenario `chibi` failed with `FileNotFoundError` or catalog assertions. Those local map changes were explicitly excluded from the Phase 3 production delta and are not evidence of a Phase 3 regression.

Temporary local `results/` JSON files were likewise excluded from production source history; their durable conclusions are summarized in this record.

## Negative regression coverage

The performance gate has an explicit negative test proving a material controlled-work regression causes gate failure. This prevents the contract layer from being an always-pass reporting mechanism.

## Final engineering decision

Phase 3 is CLOSED.

```text
F — Performance Measurement Refinement       VALIDATED
B — Performance Regression Infrastructure    VALIDATED
```

The durable rule for future STAR performance work is:

> Gate deterministic complexity invariants and STAR-controlled cost. Keep platform input/presentation observable, but do not relabel platform variance as a STAR algorithmic regression.

Future scale work should reuse this measurement framework by adding a deterministic workload plus only the few causal/timing contracts needed for that workload, rather than redesigning the profiler or creating a larger performance-testing framework.
