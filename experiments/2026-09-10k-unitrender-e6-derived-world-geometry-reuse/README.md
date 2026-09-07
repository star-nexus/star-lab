# Phase 5 10K UnitRender E6 — Derived World-Geometry Reuse

**Status:** VALIDATED ATTRIBUTION — production candidate justified; raw forensic mirror pending  
**STAR repository:** `star-nexus/star`  
**Production/control commit:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`  
**Formal measurement tooling commit:** `ac68b4e5c50837feb8f978ffe2c2a9dc2caca1df`  
**Validated production commit:** N/A — attribution treatment is measurement-only  
**Validated tag:** N/A

## 1. Problem

E5-3 closed the UnitRender Cull attribution chain with `WORLD_COORD_PAYLOAD_FIRST_TOUCH_DOMINANT`: on the 10K / 100%-moving workload, first-touch of `UnitSpatialRecord.world_x/world_y` accounted for approximately `0.375 ms` of a `0.476 ms` full record-field effect (~78.8%). The retained production spatial index regenerates these derived world-coordinate payloads whenever a unit's authoritative `HexPosition` commits movement.

E6 asked the narrower treatment question:

> Can Cull materially recover that movement-dependent first-touch cost if the pure per-hex derived geometry is long-lived and reused, while `UnitSpatialRecord` itself remains freshly created?

Formal answer:

```text
YES — DERIVED_WORLD_GEOMETRY_REUSE_CANDIDATE_JUSTIFIED
```

This is an attribution result, **not** a production KEEP.

## 2. Why it matters

The goal is not to optimize the spatial index generically. E6 tested exactly the evidence-aligned payload isolated by E5-3. Reuse recovered a material Cull cost at both 50% and 100% movement while the movement/Vision/Fog workload rates remained within the preregistered ±2% tolerance.

The next engineering step is therefore narrow:

> Design a **bounded** production representation for derived per-hex world geometry, tied to authoritative map/board lifetime or another demonstrably bounded owner, then validate it against exact production.

Do not jump to SoA/native/parallelism from this result.

## 3. Source checkout

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout ac68b4e5c50837feb8f978ffe2c2a9dc2caca1df
uv sync
```

The runtime under both formal A and B remained the exact retained production commit:

```text
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
```

The formal runner created detached control/treatment worktrees from that SHA and copied only the E6 measurement probe into the treatment worktree.

## 4. Environment

Formal run `20260907-203733`:

```text
Machine class: Mac mini / Apple Silicon formal Phase-5 machine
OS: macOS 26.5.2 (build 25F84)
Kernel: Darwin 25.5.0 arm64
Display: window 2480x1261
Scenario: chibi-144k-scale-10000
Scenario SHA256: e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
Resident units: 10000
Fog: ON
MiniMap dynamic units: OFF
GC: realtime_defer
Render: uncapped
Hub: offline
Input: blocked gameplay events
```

The exact 10K fixture is inside the raw forensic ZIP with an archive-relative checksum.

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

For each `(col,row)`, treatment canonicalized only:

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

This remains deliberately orthogonal to E5-2 stable record identity.

Pre-measurement validation passed:

```text
E6 isolation / identity contract: 2 passed
exact-production targeted regressions: 25 passed
same targeted regressions with E6 patch installed: 25 passed
```

## 6. Formal run

The executed formal command at tooling SHA `ac68b4e5...` was:

```bash
bash tools/run_phase5_unitrender_e6_attribution.sh
```

Counterbalanced order:

```text
A50 -> B50 -> B100 -> A100
```

The retained window was taken at `t=19 s` of a 20 s sustained run, after the 12-step out-and-back route had entered steady geometry reuse.

For future reruns, the canonical entrypoint is now:

```bash
bash tools/run_phase5_unitrender_e6.sh
```

That wrapper preserves the same measurement/analyzer semantics and emits both:

```text
<run-id>-compact.zip
<run-id>-raw.zip
```

according to STAR Lab `PROTOCOL.md` v1.2. Packaging is downstream of measurement and does not change the preregistered gates.

## 7. Preregistered gates

Frozen before the formal run:

```text
all scale-driver guards PASS
position commits/s within ±2%
Vision changed/s within ±2%
Fog delta tiles/s within ±2%
control contains no E6 treatment metadata
treatment source guard resolves to production 17ced8d2...

50% moving:  Cull avg saving >= 0.10 ms
100% moving: Cull avg saving >= 0.20 ms
UnitRender avg improves at both densities
controlled-work avg regression <= 2%
```

P99 was diagnostic and did not independently determine causation.

## 8. Formal result

| Metric | 50% control | 50% reuse | Change | 100% control | 100% reuse | Change |
|---|---:|---:|---:|---:|---:|---:|
| Controlled avg | 25.412 ms | 25.267 ms | -0.57% | 32.880 ms | 32.386 ms | -1.50% |
| Controlled p99 | 30.373 ms | 26.484 ms | diagnostic | 35.366 ms | 34.409 ms | diagnostic |
| Cull avg | 2.076 ms | 1.875 ms | **-0.201 ms** | 2.404 ms | 1.971 ms | **-0.433 ms** |
| Cull relative | | | **-9.7%** | | | **-18.0%** |
| UnitRender avg | 9.268 ms | 9.134 ms | **-0.134 ms** | 10.242 ms | 10.026 ms | **-0.217 ms** |
| Animation avg | 3.525 ms | 3.518 ms | -0.007 ms | 7.320 ms | 7.279 ms | -0.041 ms |
| Position rate drift | | | +0.733% | | | -0.109% |
| Vision changed drift | | | +0.447% | | | -0.054% |
| Fog delta drift | | | +0.693% | | | +0.319% |

Both formal comparisons passed every preregistered check.

Decision:

```text
DERIVED_WORLD_GEOMETRY_REUSE_CANDIDATE_JUSTIFIED
```

A particularly strong consistency check is that the 50% Cull recovery (`0.201 ms`) exactly matches the E5-3 `world_x/world_y` first-touch contribution estimate (`0.201 ms`). At 100%, E6 recovered `0.433 ms` versus the earlier E5-3 `0.375 ms` world-coordinate estimate. The excess must not be over-interpreted as >100% causal recovery; run noise and the treatment's joint reuse of `bucket` are sufficient nearby explanations. The formal conclusion remains the preregistered materiality result, not an exact percentage decomposition.

## 9. Artifact model

This case is the first migration to the STAR Lab v1.2 two-tier artifact standard:

```text
Compact Evidence Package
        +
Raw Forensic Package
```

Formal raw package:

```text
20260907-203733.zip
SHA256: d4f7bab293ced78ab11231fe0e370fe51a257e1cb95b12666340a7a628819bc4
```

A post-run compact sample was generated successfully and is suitable for normal review. Future canonical reruns generate `-compact.zip` and `-raw.zip` directly from `tools/run_phase5_unitrender_e6.sh`.

The raw forensic package remains the authoritative low-level audit substrate. This case must not be marked fully CLOSED until the raw package has a stable canonical STAR Lab storage/mirror locator; its checksum is already frozen.

## 10. Related records

- [`manifest.yaml`](manifest.yaml)
- [`analysis.md`](analysis.md)
- [`decision.md`](decision.md)
- [`../2026-09-10k-unitrender-e5-3-field-payload/`](../2026-09-10k-unitrender-e5-3-field-payload/) — immediate causal predecessor

`records/performance-frontier.md` remains unchanged: E6 justified a production candidate but did not itself create a validated production source state or move the capability frontier.
