# 10K / 100%-Moving 30Hz Frontier Confirmation

**Status:** CLOSED — frontier not established; periodic Vision audit identified as current blocker  
**STAR repository:** `star-nexus/star`  
**Frozen production runtime:** `6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b`

## Question

After Optimization C2a produced the first observed 10K / 100%-moving controlled-work P99 below the canonical 30Hz gate, is that crossing stable enough to establish a new Performance Frontier point?

The C2a closeout observed `33.199 ms` P99, but that experiment preregistered P99 as diagnostic. This case therefore reran the boundary under a separate preregistered frontier rule.

## Preregistered rule

```text
primary metric = controlled_work_frame_ms.p99
30Hz gate      = 33.33 ms
```

The frontier would be established only if all five points passed guards and all three independent 100%-moving runs individually satisfied `P99 <= 33.33 ms`. Median-only or majority-pass reinterpretation was forbidden.

## Formal run

```text
run_id                    20260906-203345
runtime                   6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b
scenario                  chibi-144k-scale-10000
scenario SHA256           e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
Fog                       ON
MiniMap dynamic units     OFF
GC                        realtime_defer
uploaded ZIP SHA256       7176cbee865dd115cc19be05a2d61f7e78966ebcf477d0377863e8a06088648c
raw mirror                pending
```

All five driver/workload guards passed and all ENV process-tree cleanup checks passed.

### Results

| Point | Controlled avg | P95 | P99 | 30Hz |
|---|---:|---:|---:|---|
| 00% moving | 16.292 ms | 16.643 ms | **20.015 ms** | PASS |
| 50% moving | 24.594 ms | 25.586 ms | **28.093 ms** | PASS |
| 100% r1 | 30.834 ms | 31.966 ms | **33.944 ms** | FAIL |
| 100% r2 | 31.305 ms | 32.475 ms | **34.049 ms** | FAIL |
| 100% r3 | 30.938 ms | 32.244 ms | **34.050 ms** | FAIL |

Formal decision:

```text
FRONTIER_NOT_ESTABLISHED
```

The three 100%-moving P99s span only `0.106 ms`, so the failure is highly repeatable rather than a one-off machine drift event.

## Diagnostic attribution from the same run

The failure is concentrated in the periodic Vision safety audit.

Each 100%-moving profile contains exactly two frames above the 33.33ms controlled-work gate, and each contains exactly two `vision_audit_scan` frames in the sampled window.

Audit cost:

```text
r1 vision_audit_scan max ~4.282 ms
r2 vision_audit_scan max ~4.127 ms
r3 vision_audit_scan max ~4.240 ms
```

On ordinary frames, Vision is roughly `3.3 ms`; on audit frames Vision rises by about `4.1-4.3 ms`, producing whole controlled-work frames around `35-36 ms`.

Removing audit frames only as a diagnostic view puts the ordinary full-motion tail below the 30Hz budget. This does **not** change the formal decision, because the canonical metric includes maintenance work. It does identify the next causal question:

> What semantic value does the O(Nresident) periodic Vision safety audit actually provide in an indexed world where movement and death already publish explicit invalidations?

That question is now tracked separately as `2026-09-10k-vision-audit-effectiveness` (Vision D).

## Interpretation

Two conclusions remain deliberately separate:

```text
Optimization C2a
    = CAUSALLY CONFIRMED / KEEP / CLOSED

10K / 100%-moving 30Hz frontier
    = NOT ESTABLISHED
```

The first observed C2a crossing (`33.199 ms`) is retained as a useful signal but is not promoted to frontier evidence because the dedicated confirmation failed 3/3 full-motion repeats.

## Next action

Run Vision D audit-effectiveness attribution before touching C2b refcount representation. The current engineering rule remains:

> **先消灭错误复杂度，再重构必要复杂度。**
