# Decision — UnitRender E4

## Decision

`MAP_RENDER_LOCALITY_GAP_NOT_CONFIRMED`

Do not keep or implement the proposed pre-Map scheduling candidate.

## Why

The preregistered requirement was that executing exact production Cull before MapRender materially improve local Cull core time at both 50% and 100% moving. Instead it regressed:

```text
50%:  baseline-late 1.995 ms -> early-pre-map 2.190 ms
100%: baseline-late 2.278 ms -> early-pre-map 2.508 ms
```

The semantic gate passed perfectly: every sampled early and late ordered visible-unit list matched. Therefore the negative timing result is not caused by different Cull semantics.

A second Cull in the same frame was substantially faster, so E3's first-touch locality signal remains real, but MapRender is not the causal eviction boundary.

## Production

Production remains exactly:

`17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

No E4 runtime code is merged.

## Next

Open E5 as measurement-only spatial-structure decomposition. Split E3's cumulative spatial prewarm into bucket-container, `by_entity` indirection, and record-field touches before selecting any representation optimization.
