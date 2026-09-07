# Phase 5 10K UnitRender E4 — Pre-Map Cull Scheduling Attribution

**Status:** CLOSED — `MAP_RENDER_LOCALITY_GAP_NOT_CONFIRMED`  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`  
**Run:** `20260907-140419`

## Trigger

E3 reproduced the movement-dependent Cull growth and isolated a spatial first-touch locality effect:

```text
baseline Cull core 00% -> 100%: +0.732 ms
spatial prewarm saving vs context:
00%   0.141 ms
50%   0.275 ms
100%  0.468 ms
```

Because MapRender executes immediately before UnitRender, E4 tested whether Map/Fog presentation was the locality gap.

## Measurement

Most frames ran normal production:

```text
MapRender -> exact production UnitRender Cull
```

Every fourth frame additionally ran the same exact Cull before MapRender. The early result was read-only and never consumed by rendering. The normal late Cull still supplied the render result. Early and late ordered visible lists were compared exactly.

## Result

```text
                    00%       50%       100%
baseline-late       1.543     1.995      2.278 ms
early-pre-map       1.669     2.190      2.508 ms
late-after-early    1.317     1.493      1.659 ms
```

The original baseline growth reproduced:

```text
00% -> 100% = +0.735 ms
```

But pre-Map scheduling regressed local Cull time at every density:

```text
00%   -0.127 ms saving (-8.2%)
50%   -0.195 ms saving (-9.8%)
100%  -0.230 ms saving (-10.1%)
```

Every sampled early/late visible list matched exactly, including order.

Formal decision:

`MAP_RENDER_LOCALITY_GAP_NOT_CONFIRMED`

## Interpretation

MapRender is not the causal eviction boundary. Do not implement an early frame-local Cull cache merely to move Cull before MapRender.

However, the much faster `late-after-early` call shows strong self-warming by the first complete Cull traversal. E3's spatial first-touch signal therefore remains open at a deeper representation/access level.

Next case: **E5 spatial first-touch structure decomposition**:

```text
context
-> bucket container touch
-> by_entity lookup touch
-> UnitSpatialRecord field touch
```

Only after this decomposition may a representation candidate be selected.

## Artifact integrity

```text
ZIP SHA256: 8f47582ec589acb4dd354d2ec98f1cfb7c7eacb3a3139e8d955b63ac46682d20
scenario SHA256: e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
targeted regressions: 65 passed in 0.56s
all driver exits: 0
all cleanup exits: 0
all guards: PASS
```

The host was not isolated; desktop applications may have been running. Aggregate latency is therefore diagnostic only. The formal decision rests on same-session interleaved local core timing and semantic guards.

Raw physical mirror remains pending.
