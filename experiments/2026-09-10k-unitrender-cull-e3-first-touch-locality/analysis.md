# Analysis — Phase 5 UnitRender E3 Cull First-Touch Locality

## Result

E3 reproduced the original movement-dependent Cull growth using the exact production `_get_visible_units()` core:

```text
baseline core:
00%   1.544 ms
50%   1.993 ms
100%  2.276 ms

00% -> 100% = +0.732 ms
candidate count change = +0.12%
```

This clears the preregistered reproduction gate (`>= +0.40 ms`) and confirms the Cull signature is real in this run.

## Spatial prewarm is the causal signal

Read-only spatial prewarm reduces the exact production core increasingly as movement density rises:

```text
spatial vs context saving:
00%   0.141 ms   (9.2%)
50%   0.275 ms  (13.8%)
100%  0.468 ms  (19.7%)
```

The effect is not driven by a few lucky samples. At 50% moving the sampled ranges are fully separated:

```text
context: 1.899 .. 2.111 ms
spatial: 1.614 .. 1.840 ms
```

At 100% they are almost disjoint:

```text
context: 2.066 .. 3.043 ms
spatial: 1.801 .. 2.061 ms
```

This density-monotonic signature is consistent with E2's increasing spatial-index churn and strongly supports a first-touch locality penalty on the spatial working set.

## Fog is secondary

Fog-only prewarm does not meet the preregistered single-mode threshold at 100% moving:

```text
context 2.372 -> fog 2.178 ms
saving 0.194 ms / 8.2%
```

Combined spatial+Fog prewarm is slightly better than spatial alone, but the dominant effect is spatial.

## Prewarm is evidence, not an optimization

At 100% moving, spatial prewarm itself costs about:

```text
1.780 ms/frame
```

while reducing the following Cull core by only:

```text
0.468 ms/frame
```

Therefore adding a production prewarm pass would be a clear net loss. E3 only proves that the first Cull touch of the spatial working set is expensive.

## Host-noise caveat

The operator reported that Chrome and other desktop processes were running during the experiment, so the host was not isolated. This weakens aggregate frame/FPS interpretation but does not invalidate the primary local result:

- modes are interleaved within the same run;
- the metric is one whole exact-production Cull call;
- the spatial/context separation is large and consistent;
- the effect strengthens monotonically with movement density.

External load is therefore treated as extra noise, not as a plausible explanation for the observed causal pattern.

## Scheduling hypothesis

The window system order is:

```text
... -> MapRenderSystem -> UnitRenderSystem -> ...
```

and UnitRender performs Cull at the start of its update. This creates a plausible locality gap:

```text
Movement / spatial-index mutations
    -> render phase begins
    -> MapRender / Fog presentation touches large terrain/surface working sets
    -> UnitRender Cull first-touches spatial index again
```

E3's immediate spatial prewarm before Cull may simply restore the locality that existed before MapRender.

This is a smaller and cleaner hypothesis than immediately changing the spatial-index representation.

## Next

E4 should compare the exact production Cull core when executed before MapRender versus its normal post-MapRender position, without changing the actual rendering consumer path. If pre-Map Cull recovers a material fraction of the 100% locality gap and produces exactly the same visible-unit list, then frame-local early-cull caching becomes a justified candidate.
