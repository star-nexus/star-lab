# Closeout Summary

Run `20260907-024432` completed the preregistered UnitRender moving-path attribution against exact production `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`.

Formal decision: `ANIMATED_SINGLE_PATH_DOMINANT_NEEDS_DECOMPOSITION`.

Refined result: the original draw-dedup / committed-hex aggregation-collapse hypothesis is rejected. Exact raster-equivalent duplicates were only `0.6%` at 50% moving and `1.1%` at 100% moving, with estimated removable CPU of only `0.009` and `0.035 ms/frame`.

The 0%→100% UnitRender increase of `+2.912 ms/frame` decomposes as:

- animation-position classification `+1.743 ms` (59.8%)
- visible cull `+0.727 ms` (25.0%)
- actual static→animated render-stage change `+0.241 ms` (8.3%)
- residual `+0.202 ms` (6.9%)

The next attribution target is therefore **Cull + Animation Classification**, not raster dedup and not committed-hex merging.

ZIP SHA256: `98161316609716e74a8beef443a2d1d94df33894fbfedc5ad0b4e89539514aa6`.

Raw physical mirror remains pending.
