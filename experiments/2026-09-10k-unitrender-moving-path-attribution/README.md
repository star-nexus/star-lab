# Phase 5 10K UnitRender Moving-Path Attribution

**Status:** CLOSED — attribution complete  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Result

Run `20260907-024432` completed the preregistered moving-path attribution with all guards passing and `14 passed` targeted regressions.

Formal analyzer decision:

```text
ANIMATED_SINGLE_PATH_DOMINANT_NEEDS_DECOMPOSITION
```

The initial aggregation-collapse / draw-dedup hypothesis is rejected:

```text
exact raster duplicates
50% moving   0.6%   estimated removable 0.009 ms/frame
100% moving  1.1%   estimated removable 0.035 ms/frame
```

Committed-hex grouping is structural evidence only and produces effectively no reducible calls under the existing six-per-hex static cap. Texture cache hit rate is 100% at all points.

## Refined causal result

The important 0%→100% UnitRender delta is:

```text
UnitRender total        +2.912 ms/frame
unit_visible_cull       +0.727 ms   25.0%
classification          +1.743 ms   59.8%
render stage            +0.241 ms    8.3%
residual                +0.202 ms    6.9%
```

The visible set also grows from `2873.0` to `3659.7` (`+27.4%`).

Therefore the next target is **Cull + Animation Classification**, not `_render_single_unit_fast()` raster micro-optimization.

## Evidence

Uploaded ZIP SHA256:

`98161316609716e74a8beef443a2d1d94df33894fbfedc5ad0b4e89539514aa6`

See:

- `analysis.md`
- `decision.md`
- `result.yaml`
- `summary.md`

Raw physical mirror remains pending.
