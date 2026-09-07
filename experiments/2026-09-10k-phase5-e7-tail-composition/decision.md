# Decision — Phase 5 E7 Tail Composition Attribution

**Status:** VALIDATED ATTRIBUTION — Raw mirror pending

Retained production remains:

```text
e7ba18b31870577110b591104ef8fa7b4713e43c
```

Formal run:

```text
20260908-001411
```

All source/workload/sample guards passed. Three stable controlled-work tail contributors satisfied the preregistered rule in all 3 repeats:

```text
UnitRenderSystem  median self uplift +1.067 ms
VisionSystem      median self uplift +0.401 ms
AnimationSystem   median self uplift +0.350 ms
```

Therefore choose:

```text
STABLE_TAIL_CONTRIBUTORS_FOUND
```

The largest stable contributor is UnitRender, but E7 further shows the remaining UnitRender tail is not primarily Cull:

```text
UnitRender inclusive median uplift  +1.164 ms
UnitRender self median uplift       +1.067 ms
unit_visible_cull median uplift     +0.097 ms
```

Formal next causal target:

```text
UnitRenderSystem self / render-volume path
```

Do not reopen the prior Cull first-touch path without contradictory new evidence.

Strong supporting volume signal:

```text
render_commands median r(controlled) = 0.920
render_commands median tail delta    = +438.34
render_commands median tail ratio    = 1.128
```

The next attribution should determine whether UnitRender tail self time is explained by visible/animated/grouped unit volume and UnitRender-attributable command generation before any optimization is proposed.

## Production / frontier consequence

E7 changes no production runtime and authorizes no KEEP.

The 10 s diagnostic p99 values were:

```text
33.209 / 33.169 / 33.190 ms
median 33.190 ms
3/3 <= 33.33 ms
```

Do not update `performance-frontier.md`: E7 is attribution-only and its profiler horizon differs from the canonical frontier measurement. A later canonical retained-production validation is required.

## Artifacts

```text
Compact SHA256 e69471082847263f65035015e83da211982612befb187691b65d377d159f5b29
Raw SHA256     cdb7a6232d13c0f7d55c26f4f23fabd21782f305eb9b58444bf847612214126a
```

Compact is sufficient for the formal attribution decision. Raw must retain a stable archival mirror/locator before archival closure.
