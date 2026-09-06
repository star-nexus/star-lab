# 10K Vision Residual C2 Attribution

**Status:** RUNNING — attribution prepared, no production candidate selected  
**STAR repository:** `star-nexus/star`  
**Frozen production baseline:** `4218b5368fbe2815b8512384e2c18b0af443ebfa`

## Question

After Optimization C1 removed the redundant terrain-bonus lookup from the ~99.7% geometry-cache hit path, what now dominates residual `VisionSystem` dirty-unit CPU at 10K scale?

The attribution is deliberately limited to three remaining areas already visible in the production update loop:

```text
old/new visibility set diff
faction union / per-tile refcount maintenance
explored-set maintenance
```

Optimization A, Optimization B, and Optimization C1 remain fixed.

## Current production shape

For each changed Vision unit, production currently performs:

```text
visibility geometry
  -> old_tiles / visible_tiles set differences
  -> per-faction refcount decrement/increment for removed/added tiles
  -> 0<->1 faction-visible transitions + fog-delta staging
  -> state writeback
  -> explored.update(visible_tiles)
```

The C2 attribution does not change production source. It mounts a process-local measurement implementation over the exact retained runtime in a detached worktree.

## Pre-measurement hypotheses

### H1 — union/refcount maintenance remains the largest residual block

Every removed/added tile performs Python dict lookup/mutation even when the faction-visible union does not change. The probe measures both total refcount tile operations and the fraction that actually cause 0<->1 union transitions.

### H2 — set-diff remains material

Every changed unit allocates `old_tiles.difference(visible_tiles)` and `visible_tiles.difference(old_tiles)`. The probe measures the paired set-diff cost directly.

### H3 — explored update contains redundant monotonic work

`FogOfWar.explored_tiles[faction]` is monotonic, but production currently executes:

```python
explored.update(visible_tiles)
```

for every changed unit. The probe records:

```text
visible tiles supplied to explored.update
added visibility delta tiles already computed by set-diff
actually new faction explored tiles
```

A future candidate such as `explored.update(added_tiles)` is **not accepted in advance**. It is only a hypothesis until attribution shows material redundant work and a semantic review proves equivalence.

## Measurement contract

```text
scenario                  chibi-144k-scale-10000
scenario SHA256           e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
resident units            10000
moving densities          50% / 100%
phase                     staggered
seed / phase seed         42 / 42
route steps               12
Fog                       ON
GC                        realtime_defer
MiniMap dynamic units     OFF
render                    uncapped
hub                       offline
runtime source            4218b5368...
entity micro-sample       1 / 16
tile micro-sample         1 / 64
```

The experiment runner must terminate the complete `uv -> Python/Pygame` process tree between points. A cleanup failure invalidates the point and blocks the next launch.

## Tooling

Prepared on STAR branch:

```text
experiment/phase5-c2-attribution
```

Tooling HEAD:

```text
f1b16a949a9d4efab312d15a0bd10f42db079542
```

Files:

```text
tools/phase5_vision_c2_attribution.py
tools/run_phase5_vision_c2_attribution.sh
```

The experiment branch differs from the frozen production runtime only by these two measurement files.

## Interpretation boundary

Instrumented aggregate `controlled_work_frame_ms` is diagnostic only. C2 attribution is used to rank removable residual work and quantify operation multiplicity. Any production optimization selected from this case must be implemented alone and validated with an uninstrumented controlled A/B before retention.
