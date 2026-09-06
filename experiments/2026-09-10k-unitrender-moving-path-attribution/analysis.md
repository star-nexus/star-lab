# Phase 5 10K UnitRender Moving-Path Attribution — Analysis

## Validity

Run: `20260907-024432`

Uploaded ZIP SHA256:

`98161316609716e74a8beef443a2d1d94df33894fbfedc5ad0b4e89539514aa6`

The run is valid for attribution:

- caller branch: `experiment/phase5-unitrender-moving-path-attribution`
- caller SHA: `3a256f8fbaacbdf1bb41a706ef589fd4019c8d4a`
- detached runtime SHA: `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`
- scenario SHA256: `e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25`
- execution order: `00pct-moving → 50pct-moving → 100pct-moving`
- all point guards: PASS
- driver exits: 0
- cleanup exits: 0
- targeted UnitRender/animation regressions: `14 passed in 0.42s`

Aggregate frame latency is diagnostic only; the conclusion below is based on local causal metrics.

## Results

| point | UnitRender avg ms | visible | animated | classify ms | static render ms | animated render ms | exact raster dup | estimated removable ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0% | 6.931 | 2873.0 | 0.0 | 2.194 | 3.072 | 0.000 | 0.0% | 0.000 |
| 50% | 9.120 | 3398.5 | 1729.4 | 3.318 | 1.909 | 1.668 | 0.6% | 0.009 |
| 100% | 9.844 | 3659.7 | 3659.7 | 3.936 | 0.000 | 3.313 | 1.1% | 0.035 |

Texture-cache hit rate was 100% at all three points, with zero misses/frame.

The structural committed-hex grouping signal is not a candidate: the estimated calls removable by the existing static six-per-hex cap were effectively zero (`0.0` at 50%, `0.2` at 100%). Exact raster-equivalent duplicates were also negligible: `0.6%` at 50% and `1.1%` at 100%, far below the preregistered 20% threshold. The corresponding estimated removable CPU was only `0.009 ms/frame` and `0.035 ms/frame`.

Therefore the original aggregation-collapse hypothesis is rejected as an optimization candidate.

## More precise delta accounting

The analyzer's preregistered decision `ANIMATED_SINGLE_PATH_DOMINANT_NEEDS_DECOMPOSITION` is directionally correct but should not be read as saying `_render_single_unit_fast()` itself explains the movement-dependent delta.

From 0% → 100% moving:

- UnitRender: `+2.912 ms/frame`
- `unit_visible_cull`: `+0.727 ms` = **25.0%** of the UnitRender delta
- batch classification: `+1.743 ms` = **59.8%**
- total render stage (`static + animated`): `+0.241 ms` = **8.3%**
- residual: `+0.202 ms` = **6.9%**

From 0% → 50% moving:

- UnitRender: `+2.189 ms/frame`
- cull: `+0.440 ms` = **20.1%**
- classification: `+1.125 ms` = **51.4%**
- render stage: `+0.505 ms` = **23.1%**
- residual: `+0.120 ms` = **5.5%**

The largest causal growth term is therefore **animation-position classification**, not raster submission.

The per-call render cost reinforces that conclusion:

- 0% static fast render: about `1.069 µs/call`
- 50% animated fast render: about `0.964 µs/call`
- 100% animated fast render: about `0.905 µs/call`

Animated `_render_single_unit_fast()` calls are not intrinsically more expensive than the static calls in this workload.

## Visible-set expansion

The visible set also grows with movement:

- 0%: `2873.0`
- 50%: `3398.5` (`+18.3%`)
- 100%: `3659.7` (`+27.4%`)

This is a real workload effect and plausibly explains much of the cull growth. It must be decomposed before attempting to optimize culling; a larger necessary visible set is not itself wrong complexity.

## Source-level clue for the next attribution

Current batch classification calls `_get_fast_animation_screen_position()` for every visible unit. That helper calls the generic `AnimationSystem.get_unit_render_position(entity)`, then independently fetches `HexPosition` again and recomputes the committed hex pixel position for the displacement test.

The generic animation API itself already:

1. fetches `HexPosition`;
2. checks `AttackAnimation`;
3. checks `MovementAnimation`;
4. either interpolates a moving position or computes the static hex pixel position.

Thus the batch renderer is paying a general-purpose animation lookup contract plus an additional position lookup / base-position conversion for every visible entity. This is a strong wrong-complexity candidate, but it still requires local decomposition before any production change.

## Conclusion

Formal attribution decision:

`ANIMATED_SINGLE_PATH_DOMINANT_NEEDS_DECOMPOSITION`

Refined engineering interpretation:

> The movement-dependent UnitRender cost is dominated by per-visible-unit animation classification and, secondarily, visible-set/cull growth. Exact-raster duplicate drawing and committed-hex aggregation loss do not explain the cost.

Next experiment should decompose **Cull + Animation Classification** first. `_render_single_unit_fast()` should only be decomposed further if those two paths fail to explain enough of the remaining cost.
