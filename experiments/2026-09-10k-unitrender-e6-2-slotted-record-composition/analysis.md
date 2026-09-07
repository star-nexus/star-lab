# Analysis — Phase 5 10K UnitRender E6-2 Slotted Spatial Record Composition

## 1. Observation

Earlier E5-1 evidence showed a small positive Cull signal from `slots=True` on
`UnitSpatialRecord`:

```text
50% moving:  ~0.090 ms Cull saving
100% moving: ~0.113 ms Cull saving
```

That result was correctly rejected as the main root solution because most of the
record first-touch cost remained unexplained. E5-3 and E6 later established that
`world_x/world_y` payload first-touch was dominant, and E6-1 converted that
mechanism into retained board-bounded production reuse.

E6-1 retained production still misses the canonical 30 Hz 100%-moving gate by a
small tail margin:

```text
controlled p99 = 33.677126 ms
threshold      = 33.33 ms
```

## 2. New composition hypothesis

### H1 — slots retain independent value after E6-1

`slots=True` changes the Python object representation of `UnitSpatialRecord`,
whereas E6-1 changes the lifetime/identity of the derived world-geometry payloads.
The mechanisms are therefore not identical and may compose.

### H2 — the old signal was mostly subsumed by E6-1

Once `world_x/world_y/bucket` are canonicalized, the remaining record-object
first-touch effect may shrink below useful materiality. A slotted treatment may
then add complexity without meaningful retained benefit.

## 3. Instrumentation

No new runtime profiler instrumentation is introduced. Existing Phase-3 metrics
are sufficient:

```text
unit_visible_cull
UnitRenderSystem
AnimationSystem
controlled_work_frame_ms
position commits/s
Vision changed/s
Fog delta tiles/s
```

Treatment metadata proves the slotted representation was installed while the
retained E6-1 runtime SHA remained unchanged.

## 4. Isolation

Both formal arms run:

```text
e7ba18b31870577110b591104ef8fa7b4713e43c
```

Treatment changes only the `UnitSpatialRecord` class representation before any
world/index construction. It preserves:

- field names and values;
- frozen semantics;
- fresh record identity;
- E6-1 bounded geometry reuse;
- Cull and spatial container algorithms.

## 5. Evidence

Pending formal run.

## 6. Decision interpretation

A positive E6-2 result means only:

> The earlier slotted-record signal remains independently material when composed
> with retained E6-1 geometry reuse.

It authorizes a one-line production source candidate (`slots=True`) and a final
source-vs-source validation. It does not itself change retained production or the
Performance Frontier.

A negative result means the old E5-1 partial signal has been effectively subsumed
or is too small to justify production complexity in the current state.

## 7. 30 Hz interpretation

The 100%-moving controlled P99 is diagnostic during E6-2. Even if the attribution
arm happens to cross 33.33 ms, production/frontier movement still requires the
source candidate to be validated as production KEEP under normal archive rules.
