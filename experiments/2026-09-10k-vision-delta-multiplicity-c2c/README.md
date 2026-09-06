# 10K Vision C2c — Visibility-Delta Multiplicity Attribution

**Status:** CLOSED — `NO_MULTIPLICITY_CANDIDATE`; production unchanged  
**STAR repository:** `star-nexus/star`  
**Frozen production runtime:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

C2b-1 was a valid negative result (`DO_NOT_KEEP`). Post-D1 capacity remained margin-limited, and old C2 attribution had shown set-diff to be a real Vision cost. C2c therefore tested whether the necessary set-diff was being recomputed with the wrong multiplicity.

Production computes for each changed observer:

```python
removed_tiles = old_tiles.difference(visible_tiles)
added_tiles = visible_tiles.difference(old_tiles)
```

The hypothesis was that very high geometry-cache hit rates might cause many units in one frame to share the exact same `(old_visibility_object, new_visibility_object)` pair.

## Measurement

Run:

```text
20260907-013612
```

Runtime:

```text
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
= A + B + C1 + C2a + D1
```

ZIP SHA256:

```text
66336a8333e78b83a59a4f578b5d96726debad987f48c73e68708974eec92bc1
```

Integrity:

```text
96 targeted regressions passed
all driver exits = 0
all cleanup exits = 0
all canonical guards = PASS
```

The pre-measurement Bash `local` initialization bug was fixed before any measurement point ran. Probe, analyzer, thresholds and production runtime were unchanged, so the preregistration remained valid.

## Result

| point | diff calls/frame | unique pairs/frame | repeated/frame | reuse | same-object | est. diff CPU/frame | est. repeated removable |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0% | 0.0 | 0.0 | 0.0 | 0.00% | 0.0 | 0.000 ms | 0.000 ms |
| 50% | 262.9 | 262.4 | 0.47 | 0.18% | 0.0 | 0.353 ms | ~0.000 ms |
| 100% | 658.6 | 655.6 | 3.01 | 0.46% | 0.0 | 0.847 ms | 0.003 ms |

Geometry cache hit rate was still 99.526% at 50% moving and 99.710% at 100% moving, but exact old->new transition-pair reuse was almost absent.

At 100% moving:

```text
658.6 diff calls/frame
655.6 unique exact pairs/frame
3.0 repeated observations/frame
reuse = 0.46%
max pair frequency = 3
same-object pairs = 0
```

Thus 99.54% of exact visibility transitions were unique within the frame.

## Decision

Preregistered thresholds were missed by orders of magnitude:

```text
50% pair reuse:   0.18% vs >=25%
100% pair reuse:  0.46% vs >=25%

50% repeated removable CPU: ~0.000 ms/frame vs >=0.15
100% repeated removable CPU: 0.003 ms/frame vs >=0.35

same-object opportunity: 0 at both moving densities
```

Formal decision:

```text
ATTRIBUTION COMPLETE
NO_MULTIPLICITY_CANDIDATE
CLOSED
PRODUCTION UNCHANGED
```

Do not implement an identity bypass, per-frame visibility-delta cache, or handwritten Python set-difference replacement from this evidence.

## Interpretation

The important result is:

> **Geometry reuse is high, transition reuse is not.**

Many observers can obtain their geometry from the cache, yet their previous and next cached geometry objects form almost entirely unique pairs because units are moving through different origin->destination transitions.

The low-rate C2c estimate places the complete two-difference path at about 0.847 ms/frame at full motion. This is somewhat below the older ~1.03 ms/frame direct-timing estimate, consistent with the older per-unit timing instrumentation adding overhead. The qualitative conclusion is unchanged: set-diff is real necessary work, but there is no useful multiplicity to remove.

C1, C2a and D1 removed clear wrong work. C2b-1 failed production retention. C2c found no multiplicity opportunity. Further Vision micro-tuning now requires a new causal hypothesis rather than continuing down the exhausted subpaths.

## Next action

Re-rank the remaining post-D1 steady-state blocks under exact production `17ced8d...` and choose the next target from measured contribution rather than continuing to optimize Vision by inertia.

> **先消灭错误复杂度，再重构必要复杂度；必要计算也要检查 multiplicity 是否正确。**
