# Analysis — Phase 5 10K UnitRender E6-1 Bounded Geometry Ownership

## 1. Observation

Validated predecessor evidence:

```text
E5-3:
  world_x/world_y first-touch = 0.201 ms @50%
  world_x/world_y first-touch = 0.375 ms @100%

E6 attribution:
  Cull saving = 0.201 ms @50%
  Cull saving = 0.433 ms @100%
  workload-equivalence guards PASS
```

E6 therefore established that long-lived per-hex derived geometry is materially causal. It did not establish a production-safe ownership model because the attribution cache retained every visited coordinate.

## 2. Production hypothesis

### H1 — Board-bounded lazy geometry ownership retains the causal benefit

Why plausible:

- geometry is a pure function of fixed hex projection and `(col,row)`;
- normal skirmish movement is board-bounded;
- stable payload identity, not stable `UnitSpatialRecord` identity, was the validated mechanism;
- a cache limited to current board members gives the same steady-state payload reuse with a hard finite growth bound.

### H2 — Production ownership/lookup overhead erases or moves the benefit

Why plausible:

- every movement refresh adds a board-membership check and dict lookup;
- `_bucket_for_hex()` also enters the shared geometry path;
- a local Cull improvement is insufficient if equivalent cost shifts into Animation or controlled work.

## 3. Instrumentation / diagnostic changes

No new per-frame profiler instrumentation is added to the candidate hot path.

Formal discrimination uses existing Phase-3 metrics:

```text
unit_visible_cull
UnitRenderSystem
AnimationSystem
controlled_work_frame_ms
position commits/s
Vision changed/s
Fog delta tiles/s
```

Structural boundedness is validated by deterministic candidate tests before performance measurement.

## 4. Source isolation

Formal runner guard requires:

```text
control SHA   = 17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
treatment SHA = e7ba18b31870577110b591104ef8fa7b4713e43c
non-test rotk_env diff:
  rotk_env/utils/unit_spatial_index.py
```

No density point runs if this guard fails.

## 5. Evidence

### Bounded ownership contract

Pending formal run.

### Targeted regressions

Pending formal run.

### 50% moving A/B

Pending formal run.

### 100% moving A/B

Pending formal run.

## 6. Root cause / mechanism

The upstream root mechanism is already established by E5-3 + E6:

> Movement refreshes replace otherwise-pure world-coordinate payload objects; Cull's subsequent first touch of those refreshed payloads is a material moving-density-dependent cost. Reusing canonical per-hex geometry removes most of that cost.

E6-1 does **not** reopen this root-cause question. It tests whether the production-safe bounded representation preserves the validated mechanism without introducing a compensating cost elsewhere.

## 7. Causal chain under test

```text
MapData board
  -> hard-bounded lazy per-hex geometry cache
  -> movement refresh reuses world_x/world_y/bucket objects
  -> fresh UnitSpatialRecord still created
  -> Cull first-touch cost decreases
  -> UnitRender decreases
  -> no material Animation / controlled-work regression
```

## 8. Rejected explanations preserved

Do not reopen without new matching evidence:

- exact duplicate raster draw;
- candidate count growth;
- Fog branch mix;
- by_entity lookup;
- MapRender locality gap;
- `slots=True` as sufficient solution;
- stable `UnitSpatialRecord` identity.

## 9. Limits of evidence

Before formal A/B, this case proves only a bounded source representation and deterministic semantic contract. It does not yet prove:

- retained performance benefit;
- production KEEP;
- 10K / 100% canonical 30 Hz PASS;
- Performance Frontier movement.

## 10. Raw evidence

Pending two-tier formal artifacts. Compact will be the default review entrypoint; Raw remains the authoritative forensic substrate.
