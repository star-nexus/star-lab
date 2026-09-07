# Phase 5 10K UnitRender E6 — Derived World-Geometry Reuse

**Status:** DRAFT / PREREGISTERED — measurement pending  
**STAR repository:** `star-nexus/star`  
**Production/control commit:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`  
**E6 tooling commit:** `8350f7ed01014124bf0b249b859399af02a03ff5`  
**Validated commit:** N/A  
**Validated tag:** N/A

## 1. Problem

E5-3 closed the UnitRender Cull attribution chain with `WORLD_COORD_PAYLOAD_FIRST_TOUCH_DOMINANT`: on the 10K / 100%-moving workload, first-touch of `UnitSpatialRecord.world_x/world_y` accounted for approximately `0.375 ms` of a `0.476 ms` full record-field effect (~78.8%). The retained production spatial index regenerates these derived world-coordinate payloads whenever a unit's authoritative `HexPosition` commits movement.

E6 asks a narrower treatment question:

> Can Cull materially recover that movement-dependent first-touch cost if the pure per-hex derived geometry is long-lived and reused, while `UnitSpatialRecord` itself remains freshly created?

## 2. Why it matters

The goal is not to optimize the spatial index generically. The remaining evidence-aligned target is specifically the derived world-geometry payload consumed by Cull's exact bounds test. A positive result would justify a bounded production representation candidate. A negative result would close this reuse direction before any SoA/native/parallel rewrite.

## 3. Source checkout

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout experiment/phase5-unitrender-e6-derived-world-geometry-reuse
uv sync
```

The runtime under both A and B remains the exact retained production commit:

```text
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
```

The runner creates detached control/treatment worktrees from that SHA and copies only the E6 measurement probe into the treatment worktree.

## 4. Environment

```text
Machine: formal run machine captured by runner manifest (expected Mac mini M4)
OS: captured by uname/sw_vers
Scenario: chibi-144k-scale-10000
Scenario SHA256: e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
Resident units: 10000
Fog: ON
MiniMap dynamic units: OFF
GC: realtime_defer
Render: uncapped
Hub: offline
```

The 10K scenario is the same local fixed fixture used by the preceding Phase-5 cases. The runner refuses to start if its SHA256 differs. For E6, the exact fixture is additionally copied into the formal result ZIP with its own checksum so the archive no longer depends only on the local pathname.

## 5. Treatment contract

Control:

```text
exact production 17ced8d2...
```

Treatment:

```text
exact production 17ced8d2...
  + measurement-only monkeypatch of UnitSpatialIndex._record_for_hex()
```

For each `(col,row)`, treatment canonicalizes only:

```text
(world_x, world_y, bucket)
```

while preserving:

```text
fresh UnitSpatialRecord creation on every refresh
ordinary frozen dataclass layout
existing move_entity / upsert semantics
existing by_entity / by_bucket / by_cell containers
exact Cull implementation
```

This is deliberately orthogonal to E5-2 stable record identity.

The runner performs three pre-measurement validation layers:

```text
E6 identity/isolation contract test
exact-production targeted regressions
same targeted regressions with E6 patch installed in-process
```

No density point runs if any of these fail.

## 6. Formal run

```bash
bash tools/run_phase5_unitrender_e6_attribution.sh
```

The counterbalanced execution order is frozen as:

```text
A50 -> B50 -> B100 -> A100
```

The formal retained window is taken at `t=19 s` of a 20 s sustained run. With the production movement animation at 2 tiles/s and the 12-step out-and-back route, this ages first-fill geometry work out of the normal rolling window and measures steady reuse.

## 7. Preregistered gates

Workload-equivalence guards:

```text
all scale-driver guards PASS
position commits/s within ±2%
Vision changed/s within ±2%
Fog delta tiles/s within ±2%
control contains no E6 treatment metadata
treatment source guard resolves to production 17ced8d2...
```

Candidate-materiality gates, frozen before formal measurement:

```text
50% moving:  Cull avg saving >= 0.10 ms
100% moving: Cull avg saving >= 0.20 ms
UnitRender avg improves at both densities
controlled-work avg regression <= 2%
```

The thresholds intentionally require recovery of a material fraction of the E5-3 `world_x/world_y` signal (`0.201 ms @50%`, `0.375 ms @100%`). P99 is diagnostic for this mechanism experiment and is not used alone to declare causation.

## 8. Expected outcomes

Positive attribution decision:

```text
DERIVED_WORLD_GEOMETRY_REUSE_CANDIDATE_JUSTIFIED
```

Negative attribution decision:

```text
DERIVED_WORLD_GEOMETRY_REUSE_NOT_MATERIAL
```

A positive result is **not** a production KEEP. Before production consideration, geometry ownership must be bounded by authoritative map/board lifetime rather than an unbounded visited-hex cache, then validated against exact production with regression and controlled A/B evidence.

## 9. Formal artifacts

Pending formal run. Do not create an empty STAR Lab `SHA256SUMS` before formal artifacts are mirrored.

Expected local result shape:

```text
results/phase5-unitrender-e6/chibi-144k-scale-10000/<run-id>/
  manifest.txt
  fixtures/chibi-144k-scale-10000.json
  fixtures/SHA256SUMS
  treatment-contract-test.log
  control-targeted-regressions.log
  treatment-targeted-regressions.log
  control/50pct-moving/{point.json,profile.json}
  treatment/50pct-moving/{point.json,profile.json}
  treatment/100pct-moving/{point.json,profile.json}
  control/100pct-moving/{point.json,profile.json}
  unitrender-e6-summary.json
  zip-sha256.txt
```

## 10. Related records

- [`manifest.yaml`](manifest.yaml)
- [`analysis.md`](analysis.md)
- [`decision.md`](decision.md)
- [`../2026-09-10k-unitrender-e5-3-field-payload/`](../2026-09-10k-unitrender-e5-3-field-payload/) — immediate causal predecessor

`records/performance-frontier.md` is intentionally unchanged until a validated production result actually moves the capability frontier.
