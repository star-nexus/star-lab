# C2c Analysis — Visibility-Delta Multiplicity

Run: `20260907-013612`

Frozen production runtime:

```text
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
= A + B + C1 + C2a + D1
```

Uploaded ZIP SHA256:

```text
66336a8333e78b83a59a4f578b5d96726debad987f48c73e68708974eec92bc1
```

The run is valid: 96 targeted regressions passed, all three driver exits were 0, all ENV cleanup exits were 0, and all canonical workload guards passed.

## Result

| point | diff calls/frame | unique pairs/frame | repeated/frame | reuse | same-object | est. diff CPU/frame | est. repeated removable |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0% | 0.0 | 0.0 | 0.0 | 0.00% | 0.0 | 0.000 ms | 0.000 ms |
| 50% | 262.9 | 262.4 | 0.47 | 0.18% | 0.0 | 0.353 ms | ~0.000 ms |
| 100% | 658.6 | 655.6 | 3.01 | 0.46% | 0.0 | 0.847 ms | 0.003 ms |

At 100% moving, 99.54% of exact `(old_visibility_object, new_visibility_object)` pairs are unique within the frame. Maximum observed pair frequency is only 3. No `old_tiles is visible_tiles` case was observed at either moving density.

Geometry cache hit rate remains extremely high (99.526% at 50%, 99.710% at 100%), but this does **not** translate into repeated visibility transitions. Many observers reuse cached geometry objects individually, while the old->new pair combinations remain almost entirely unique.

## Interpretation

The C2c hypothesis was that necessary `old-new` / `new-old` set differences might be recomputed with the wrong multiplicity. The data rejects that hypothesis under the canonical workload.

A per-frame exact-object-pair delta cache would eliminate only about 0.003 ms/frame at 100% moving before accounting for cache lookup/storage overhead. The preregistered 100% threshold was 0.35 ms/frame. Identity bypass has zero opportunity because no same-object pairs were observed.

The new low-rate estimate places the complete two-difference path at about 0.847 ms/frame at 100% moving. This is somewhat below the older C2 direct-timing estimate (~1.03 ms/frame), consistent with the old per-unit timing instrumentation adding measurable overhead. Both measurements agree on the same qualitative conclusion: set-diff is a real necessary cost, but there is no useful exact-pair multiplicity to remove.

## Consequence

C2c should close without a production candidate. Do not implement:

- identity short-circuit;
- per-frame `(old,new)` delta cache;
- handwritten Python set-diff replacement.

The result also narrows the remaining Vision optimization space. C1, C2a and D1 removed wrong work; C2b-1 failed its production gate; C2c found no multiplicity opportunity. Further Vision work should require a new causal hypothesis rather than continuing to micro-tune existing necessary operations.
