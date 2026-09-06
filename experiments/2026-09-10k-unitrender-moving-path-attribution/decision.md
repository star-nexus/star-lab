# Decision — Phase 5 10K UnitRender Moving-Path Attribution

## Status

**ATTRIBUTION COMPLETE / ORIGINAL DEDUP HYPOTHESIS REJECTED / NEXT DECOMPOSITION JUSTIFIED**

## Decision

The preregistered decision is:

`ANIMATED_SINGLE_PATH_DOMINANT_NEEDS_DECOMPOSITION`

However, the data refine the target substantially:

- exact raster-equivalent duplicates are only `0.6%` at 50% moving and `1.1%` at 100% moving;
- estimated exact-raster removable CPU is only `0.009 ms/frame` and `0.035 ms/frame`;
- animated committed-hex grouping does not create meaningful reducible draw calls under the existing six-per-hex static cap;
- texture cache hit rate is 100%, so texture scaling/cache misses are not the cause;
- `_render_single_unit_fast()` per-call cost does not increase with motion;
- the dominant 0%→100% UnitRender growth term is animation-position classification (`+1.743 ms`, 59.8%), followed by visible-cull growth (`+0.727 ms`, 25.0%).

Therefore:

1. **Do not implement committed-hex animation collapse.**
2. **Do not implement exact-raster draw dedup.** The opportunity is too small.
3. **Do not optimize the texture cache.** It is already 100% hit in this workload.
4. **Do not jump directly into `_render_single_unit_fast()` raster micro-optimization.** Its incremental contribution is small relative to classification/cull.
5. Proceed with one measurement-only experiment decomposing:
   - `unit_visible_cull` candidate/accept/reject counts and cost;
   - `_get_fast_animation_screen_position()` / `AnimationSystem.get_unit_render_position()` sub-costs and branch frequencies;
   - duplicate `HexPosition` / committed-pixel work in the renderer classification path.

## Candidate boundary

A production optimization is justified only if the next attribution shows a removable classification cost with a source-level causal signature. The likely candidate is a window/batch-specific animation-position fast path or cached active-animation state, but no implementation is selected yet.

## Production

Production remains unchanged at:

`17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

Retained optimizations remain:

`A + B + C1 + C2a + D1`

## Evidence

Run: `20260907-024432`

ZIP SHA256:

`98161316609716e74a8beef443a2d1d94df33894fbfedc5ad0b4e89539514aa6`

Raw physical mirror remains pending; this decision must not be interpreted as raw-mirror complete until the run tree/ZIP is copied into STAR Lab and checksummed there.
