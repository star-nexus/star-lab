# Phase 5 10K UnitRender E6-1 — Bounded Geometry Ownership

**Status:** DRAFT / PREREGISTERED — measurement pending  
**STAR repository:** `star-nexus/star`  
**Problem/control commit:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`  
**Candidate commit:** `e7ba18b31870577110b591104ef8fa7b4713e43c`  
**E6-1 tooling commit:** `1855f34c14463a6c165d85b11403e4cc2e7938b4`  
**Validated commit:** N/A  
**Validated tag:** N/A

## 1. Problem

E6 attribution validated that long-lived per-hex `(world_x, world_y, bucket)` payloads materially recover the movement-dependent Cull first-touch cost while keeping fresh `UnitSpatialRecord` identity. The attribution treatment used an unbounded visited-coordinate dictionary and therefore was intentionally not eligible for production KEEP.

E6-1 asks the production question:

> Can the same reuse mechanism be implemented with hard board-bounded ownership, preserve semantics/regressions, and retain material Cull/UnitRender benefit against exact production?

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

## 3. Source checkout

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout experiment/phase5-unitrender-e6-bounded-geometry-ownership
uv sync
```

Formal A/B does not compare moving branch names. The runner creates detached worktrees from the two frozen SHAs above.

## 4. Formal run

```bash
bash tools/run_phase5_unitrender_e6_1.sh
```

Counterbalanced order:

```text
A50 -> B50 -> B100 -> A100
```

Formal workload remains the existing 10K Phase-5 workload:

```text
scenario: chibi-144k-scale-10000
scenario SHA256: e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
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

The late retained window measures steady geometry reuse rather than initial cache fill.

## 5. Pre-measurement validation

No density point executes unless all of the following pass:

```text
candidate runtime diff guard:
  only rotk_env/utils/unit_spatial_index.py

candidate bounded-geometry contract tests
control targeted regressions
treatment targeted regressions
scenario SHA256 guard
exact control/treatment SHA guard
```

## 6. Preregistered KEEP gates

Workload equivalence:

```text
all scale-driver guards PASS
position commits/s within ±2%
Vision changed/s within ±2%
Fog delta tiles/s within ±2%
```

Candidate materiality / no-tradeoff gates:

```text
50% moving:  Cull avg saving >= 0.10 ms
100% moving: Cull avg saving >= 0.20 ms
UnitRender avg improves at both densities
Animation avg regression <= 2% at both densities
controlled-work avg regression <= 2% at both densities
```

Possible production decisions:

```text
KEEP_BOUNDED_DERIVED_WORLD_GEOMETRY_REUSE
DO_NOT_KEEP_BOUNDED_DERIVED_WORLD_GEOMETRY_REUSE
```

## 7. Canonical 30 Hz gate is separate

Production KEEP does not move the Phase-5 release threshold.

At 10K / 100% moving:

```text
controlled_work_frame_ms.p99 <= 33.33 ms
```

is reported separately as the canonical 30 Hz capacity result.

A candidate may be a valid KEEP while the 30 Hz frontier remains FAIL. `records/performance-frontier.md` changes only after the ordinary STAR Lab frontier admission requirements are met.

## 8. Two-tier artifacts

The canonical runner emits:

```text
<run-id>-compact.zip  # default review / Agent / LLM input
<run-id>-raw.zip      # authoritative forensic substrate
```

Compact never replaces Raw. Both SHA256 values are printed and recorded.

## 9. Formal artifacts

Pending formal run. Do not create an empty STAR Lab `SHA256SUMS`.

Expected compact evidence includes:

```text
evidence.json
raw-artifact.json
manifest.txt
source-guards.json (via point/raw provenance; raw package authoritative)
unitrender-e6-1-summary.json
treatment-contract-test.log
control-targeted-regressions.log
treatment-targeted-regressions.log
SHA256SUMS
```

## 10. Related records

- [`manifest.yaml`](manifest.yaml)
- [`analysis.md`](analysis.md)
- [`decision.md`](decision.md)
- [`../2026-09-10k-unitrender-e6-derived-world-geometry-reuse/`](../2026-09-10k-unitrender-e6-derived-world-geometry-reuse/) — validated causal predecessor
