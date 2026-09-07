# Phase 5 10K UnitRender E6-1 — Bounded Geometry Ownership

**Status:** VALIDATED / KEEP — raw forensic mirror pending  
**STAR repository:** `star-nexus/star`  
**Problem/control commit:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`  
**Candidate / validated commit:** `e7ba18b31870577110b591104ef8fa7b4713e43c`  
**Formal runner branch HEAD at run:** `8cd4215e1d11d0778ee9db737cc757213f13630d`  
**Validated tag:** N/A

## 1. Problem

E6 attribution validated that long-lived per-hex `(world_x, world_y, bucket)` payloads materially recover the movement-dependent Cull first-touch cost while keeping fresh `UnitSpatialRecord` identity. The attribution treatment used an unbounded visited-coordinate dictionary and therefore was intentionally not eligible for production KEEP.

E6-1 asked the production question:

> Can the same reuse mechanism be implemented with hard board-bounded ownership, preserve semantics/regressions, and retain material Cull/UnitRender benefit against exact production?

The answer is **yes**.

## 2. Candidate design

Only `rotk_env/utils/unit_spatial_index.py` changes in production runtime code.

```text
MapData board snapshot
        ↓
UnitSpatialIndex._geometry_board_hexes
        ↓
lazy cache only for board members
        ↓
(col,row) -> canonical (world_x, world_y, bucket)
        ↓
fresh UnitSpatialRecord on every refresh
```

Properties:

```text
owner                 UnitSpatialIndex
lifetime              current window world / index
hard growth bound     current board hex count captured at rebuild
world without MapData cache disabled
board-external hex    computed normally, never retained
record identity       fresh
record layout         unchanged
Cull algorithm        unchanged
spatial containers    unchanged
HexPosition authority unchanged
```

`rebuild()` clears cached geometry and rebinds the current board snapshot.

## 3. Formal run

Run ID:

```text
20260907-213322
```

Command:

```bash
bash tools/run_phase5_unitrender_e6_1.sh
```

Counterbalanced order:

```text
A50 -> B50 -> B100 -> A100
```

Frozen A/B source:

```text
A control   = 17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
B treatment = e7ba18b31870577110b591104ef8fa7b4713e43c
runtime diff = rotk_env/utils/unit_spatial_index.py only
```

Formal workload:

```text
scenario: chibi-144k-scale-10000
scenario SHA256: e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
resident units: 10000
Fog: ON
motion: staggered
seed / phase seed: 42 / 42
route steps: 12
GC: realtime_defer
render: uncapped
MiniMap dynamic units: OFF
input: blocked
execution pathfinding: OFF
production animation / commits: ON
sample_after: 19 s
```

## 4. Pre-measurement validation

All premeasurement guards passed before any formal density result was admitted:

```text
bounded geometry contract:       5 passed
control targeted regressions:   25 passed
treatment targeted regressions: 30 passed
source diff guard:              PASS
scenario/workload guards:       PASS
```

## 5. Formal result

### 50% moving

```text
controlled avg: 25.633 -> 25.417 ms (-0.84%)
controlled p99: 26.767 -> 26.564 ms
Cull avg:       2.140 -> 1.909 ms  saving 0.231 ms
Cull p95 save:  0.261 ms
UnitRender avg: 9.394 -> 9.224 ms  saving 0.170 ms
Animation avg:  3.474 -> 3.513 ms  +1.12%
position rate:  +0.013%
Vision rate:    +0.021%
Fog delta:      +0.121%
checks:         PASS
```

### 100% moving

```text
controlled avg: 32.567 -> 32.115 ms (-1.39%)
controlled p99: 37.262 -> 33.677 ms
Cull avg:       2.406 -> 1.983 ms  saving 0.423 ms
Cull p95 save:  0.462 ms
UnitRender avg: 10.277 -> 9.910 ms saving 0.367 ms
Animation avg:  7.217 -> 7.258 ms  +0.57%
position rate:  -0.015%
Vision rate:    -0.008%
Fog delta:      -0.035%
checks:         PASS
```

Preregistered production decision:

```text
KEEP_BOUNDED_DERIVED_WORLD_GEOMETRY_REUSE
```

## 6. Canonical 30 Hz gate

The KEEP gate is deliberately separate from the Phase-5 capacity gate.

At 10K / 100% moving:

```text
treatment controlled_work_frame_ms.p99 = 33.677126 ms
gate                                      = 33.33 ms
result                                    = FAIL
margin                                    = +0.347126 ms
```

Therefore:

```text
production candidate = KEEP
Performance Frontier = unchanged
frontier update candidate = false
```

The human-readable analyzer originally printed the operator as `<=` even on a FAIL line. The machine-readable summary correctly recorded `pass: false`; this was a presentation-only formatter bug and did not affect the decision. The formatter was corrected after the formal run.

## 7. Two-tier artifacts

Compact Evidence Package:

```text
20260907-213322-compact.zip
size:   10616 bytes
SHA256: 0c9db01f29a04dcefc7ba896ab7ab533ec313c31a9e3d974d790b22893cb45a9
```

Raw Forensic Package:

```text
20260907-213322-raw.zip
size:   128760 bytes
SHA256: 4322905154b69ec25688fa0775b0efdd62a7a60bf1366aead9d5e8f73d661c07
```

The Compact package was independently inspected after the run: package-local `SHA256SUMS` verified, all four point payloads were present, all workload guards were true, raw profile hashes/sizes were present, and the Raw package hash/size reference matched the runner output.

Compact is sufficient for normal decision review. Raw remains the authoritative forensic substrate.

A stable canonical mirror/storage locator for the Raw package is still pending; therefore this case is **validated but not yet marked CLOSED**.

## 8. Related records

- [`manifest.yaml`](manifest.yaml)
- [`analysis.md`](analysis.md)
- [`decision.md`](decision.md)
- [`../2026-09-10k-unitrender-e6-derived-world-geometry-reuse/`](../2026-09-10k-unitrender-e6-derived-world-geometry-reuse/) — validated causal predecessor
