# 10K Vision C2c — Visibility-Delta Multiplicity Attribution

**Status:** RUNNING — preregistered attribution; production unchanged  
**STAR repository:** `star-nexus/star`  
**Frozen production runtime:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

C2b-1 attempted to replace window faction refcount tuple-key dicts with a dense-core `list[int]` plus sparse off-bbox overflow. Its uninstrumented closeout was a valid negative result:

```text
C2b-1 = CLOSED / DO_NOT_KEEP
50% saved per changed unit:   0.281 us  (< 0.4 us gate)
100% saved per changed unit:  0.064 us  (< 0.4 us gate)
production remains:           17ced8d...
```

The result showed that the ~1.37 ms/frame full-motion refcount path was not primarily tuple-dict representation tax. Do not pursue C2b-2 micro-tuning without new evidence.

Post-D1 capacity remains margin-limited rather than pathology-limited. Formal frontier confirmation is still:

```text
FRONTIER_NOT_ESTABLISHED
100% P99 = 32.926 / 33.348 / 33.764 ms
worst headroom = -0.434 ms
```

## C2c question

Production performs, for each changed observer:

```python
removed_tiles = old_tiles.difference(visible_tiles)
added_tiles = visible_tiles.difference(old_tiles)
```

The set-diff itself is semantically necessary. However, geometry-cache hits are overwhelmingly common and `_unit_visibility` stores the canonical cached `frozenset` objects. Multiple units may therefore execute the exact same:

```text
old visibility object A -> new visibility object B
```

within one frame.

C2c asks:

> Is necessary set-diff work being recomputed with the wrong multiplicity?

This is deliberately different from asking whether Python's set implementation can be rewritten faster.

## Frozen production runtime

```text
perf/10k-online
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
= A + B + C1 + C2a + D1
```

C2b-1 is **not** in production.

## Tooling

STAR branch:

```text
experiment/phase5-c2c-delta-multiplicity
```

Final branch HEAD after preregistration:

```text
f73077b465f070e0d0b6f3a3a5fbe1935e718b36
```

Measurement tools only:

```text
tools/phase5_vision_c2c_delta_multiplicity.py
tools/phase5_vision_c2c_delta_multiplicity_analyze.py
tools/run_phase5_vision_c2c_delta_multiplicity.sh
```

Commits:

```text
probe          95040029300d49cdebb41999cd8af806eea6c6dc
analyzer       161d598761c3f4339f9a9687239d1a076c13079b
runner         8410790eeb93cb7a72a227e51aac120f79fb4198
final gates    f73077b465f070e0d0b6f3a3a5fbe1935e718b36
```

The branch is based on exact production, is ahead by four commits / behind by zero, and modifies no runtime source file.

## Source guard

The probe refuses to run unless the detached runtime worktree is exactly `17ced8d...` and these blobs match:

```text
rotk_env/systems/vision_system.py          b7d62aa2c70e0c8b1b9bd159156915ce2e6a6060
rotk_env/systems/window_vision_system.py   7dda713caa48a26e72ef71ac7d14feb09cd22c6a
rotk_env/systems/window_movement_system.py d1abc9b403ea10be7868044752c575f05823d062
rotk_env/utils/unit_spatial_index.py        2c2fb26c6ae5f422516a6c3927049d8a78a72b32
```

## Measurement design

The probe copies the frozen `VisionSystem.update()` body only so it can observe the exact point immediately before the two production `frozenset.difference()` calls. Semantics are unchanged.

Per frame it records:

```text
diff calls
unique old visibility object identities
unique new visibility object identities
unique (old object, new object) pairs
repeated pair observations
number of repeated pair groups
same-object pairs: old is new
max pair frequency
top-5 pair observations
```

Object identity is intentional. If two units share the same `(old_object, new_object)` pair, their two difference results are guaranteed identical; no semantic approximation is involved.

Combined two-difference CPU is sampled at low rate (`1 / 64` calls) and classified as:

```text
first occurrence of pair
repeated occurrence of pair
old is new
```

Aggregate instrumented frame latency is diagnostic only.

## Canonical workload

```text
scenario                  chibi-144k-scale-10000
scenario SHA256           e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
resident units            10,000
points                     0% / 50% / 100% moving
seed / phase seed         42 / 42
route steps               12
Fog                       ON
GC                        realtime_defer
MiniMap dynamic units     OFF
render                    uncapped
hub                       offline
```

Fresh ENV process + full process-tree cleanup are required between points.

## Preregistered attribution decisions

C2c may choose **at most one** next candidate, in this priority order.

### 1. `IDENTITY_BYPASS_CANDIDATE_JUSTIFIED`

Choose the simplest candidate first if sampled `old is new` work is material at both densities:

```text
50% estimated same-object removable CPU  >= 0.05 ms/frame
100% estimated same-object removable CPU >= 0.15 ms/frame
```

and same-object timing samples are actually observed at both densities.

### 2. `DELTA_CACHE_CANDIDATE_JUSTIFIED`

Only if identity bypass does not win, select a per-frame exact-object-pair delta cache when all of these hold:

```text
50% repeated-pair ratio                  >= 25%
100% repeated-pair ratio                 >= 25%
50% estimated repeated removable CPU     >= 0.15 ms/frame
100% estimated repeated removable CPU    >= 0.35 ms/frame
```

### 3. `NO_MULTIPLICITY_CANDIDATE`

If neither set of thresholds is met, close C2c without implementing a candidate. Do not fall back to hand-written Python set-diff code merely to continue optimizing.

All point guards must pass for either positive attribution decision.

## Candidate semantics if justified

Any later candidate must preserve exactly:

```text
removed_tiles = old - new
added_tiles   = new - old
faction-change handling
refcount transitions
explored history
fog journal deltas
lifecycle cleanup
geometry-cache semantics
```

A positive attribution result is **not** a production KEEP. It only justifies semantic regression + uninstrumented controlled A/B.

## Out of scope

Do not mix into C2c attribution:

```text
refcount representation (C2b is closed/rejected at current layer)
geometry algorithm/cache policy
movement
D1 audit behavior
rendering
GC
native/parallel rewrite
```

## Methodology

> **先消灭错误复杂度，再重构必要复杂度；必要计算也要检查 multiplicity 是否正确。**
