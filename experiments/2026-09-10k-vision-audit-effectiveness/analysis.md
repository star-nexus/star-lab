# Analysis — Vision D Periodic Safety-Audit Effectiveness

## Valid run

```text
run_id                    20260906-215357
caller                     2e46dfd9691ac9343d30342900476df1cf3b5763
runtime                    6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b
scenario SHA256            e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
uploaded ZIP SHA256        dbe698b4377259aaaf10f3e387e83f5e012ec4dd5665baeda7b3b36ada1ad8bc
all driver exits           0
all ENV cleanup exits      0
all canonical guards       PASS
```

The sampled window contains periodic audits only; `force_all=0` at every point, so bootstrap work is not mixed into the effectiveness result.

## Results

| point | periodic audits | entities scanned | prequeued changed | audit-only discoveries | audit CPU / invocation |
|---|---:|---:|---:|---:|---:|
| 0% moving | 5 | 50,000 | 0 | 0 | 3.965 ms |
| 50% moving | 3 | 30,000 | 783 | 0 | 4.281 ms |
| 100% r1 | 2 | 20,000 | 1,215 | 0 | 4.197 ms |
| 100% r2 | 2 | 20,000 | 1,255 | 0 | 4.134 ms |
| 100% r3 | 2 | 20,000 | 1,370 | 0 | 4.227 ms |
| **total** | **14** | **140,000** | **4,623** | **0** | **4.127 ms mean** |

Every audit-only reason remained zero:

```text
missing/new Vision membership   0
Vision.dirty without queue      0
position mismatch               0
range mismatch                  0
faction mismatch                0
stale/lifecycle entity          0
multi-reason discovery          0
```

The important control is the `4,623` prequeued changes. The workload was not static and the probe did observe real Vision mismatches at audit time; all of them had already been scheduled by explicit invalidation before the full-world scan ran.

## Interpretation

Under the canonical indexed window workload, the periodic `O(Nresident)` audit had **no observed semantic contribution**:

```text
140,000 entity-scan opportunities
0 audit-only semantic discoveries
```

A rough zero-event rule-of-three gives an upper bound of approximately `3 / 140000 = 0.0021%` per entity-scan at 95% confidence. This is not a proof that an uninstrumented direct component write can never occur; it is strong evidence that the canonical production mutation paths already publish the required invalidations.

The cost is real and repeatable: 14 periodic scans consumed `57.78 ms` total CPU, approximately `4.13 ms` per invocation. The earlier frontier-confirmation case independently showed that this pulse is sufficient to push the otherwise sub-33.33ms full-motion workload over the canonical 30Hz P99 gate.

## Semantic boundary review

Existing regression coverage explicitly preserves direct `HexPosition` write detection in **non-indexed** worlds on the next tick. That safety behavior must remain.

For indexed window production, movement already publishes `mark_vision_dirty()`, unit death publishes a dirty event, and bootstrap uses `force_all`. The periodic 60-frame full scan is therefore a defensive fallback rather than the primary authoritative path.

## Candidate justified

The evidence supports one isolated D1 candidate:

```text
force_all bootstrap audit                 KEEP
non-indexed shared safety audit           KEEP
indexed window periodic full scan         BOUNDARY / no-op candidate
```

D1 must be validated with targeted semantic regressions and an uninstrumented controlled A/B before retention. A subsequent formal 3x full-motion frontier confirmation is still required before the 10K / 100%-moving / Fog-ON 30Hz frontier can move.
