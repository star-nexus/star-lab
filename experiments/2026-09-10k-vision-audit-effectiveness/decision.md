# Decision — Vision D / D1

## Final status

```text
Vision D attribution
ATTRIBUTION COMPLETE
NO OBSERVED SEMANTIC CONTRIBUTION

Optimization D1
INDEXED PERIODIC-AUDIT BOUNDARY
CAUSALLY CONFIRMED
KEEP
CLOSED
```

## Attribution basis

Canonical indexed workloads produced:

```text
periodic audit invocations   14
entity scans                 140000
already-prequeued changes    4623
audit-only discoveries       0
average audit CPU            4.127 ms/invocation
```

The audit repeatedly re-confirmed state already present in the incremental dirty queue and discovered no unqueued `new / dirty / position / range / faction / stale` mismatch.

## D1 boundary

D1 removes only the periodic full-world reconciliation from the indexed **window** runtime. It preserves:

- force-all bootstrap reconciliation;
- non-indexed direct-write safety auditing;
- explicit movement invalidation;
- unit-death lifecycle cleanup;
- Vision/Fog state semantics.

Shared/headless Vision safety behavior is unchanged.

## Controlled A/B

Run: `20260906-223546`

```text
control   6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b
D1        17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
order     A50 -> B50 -> B100 -> A100
```

50% moving:

```text
controlled avg    24.368 -> 24.741 ms   (+1.53%, within preregistered +2% bound)
controlled p99    27.882 -> 26.429 ms
Vision avg         1.549 ->  1.522 ms   (-1.73%)
audit max          4.331 ->  0.001 ms
audit scanned max 10000  ->  0
```

100% moving:

```text
controlled avg    31.019 -> 30.858 ms   (-0.52%)
controlled p99    33.931 -> 32.497 ms
Vision avg         3.395 ->  3.325 ms   (-2.06%)
audit max          4.233 ->  0.001 ms
audit scanned max 10000  ->  0
```

Authoritative movement/Vision/Fog workload rates remained within preregistered tolerances. Geometry evictions remained zero. Seventeen targeted regressions passed, and all driver/cleanup/guard checks passed.

The 50% aggregate-average drift does not overturn D1: the modified path improved locally, the periodic pulse disappeared exactly as predicted, P99 improved materially, and authoritative workload rates were preserved.

## Decision

Retain D1 in production.

Production branch after retention:

```text
perf/10k-online
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
= A + B + C1 + C2a + D1
```

The closeout's `100% P99 = 32.497 ms` is supporting evidence only. Capacity-frontier status remains separate. Run a new formal post-D1 frontier confirmation with one complete `0/50/100-r1` canonical sweep plus two additional fresh-process `100%` repetitions. All three 100% runs must independently satisfy `controlled_work_frame_ms.p99 <= 33.33 ms` before advancing the Performance Frontier.

## Evidence identity

```text
D attribution run          20260906-215357
D1 closeout run            20260906-223546
D1 closeout ZIP SHA256     455f1173a3cb904f3deeb779ed80dd68ffad82464b697e4f0137fcc0d2234860
```

Raw STAR Lab mirrors remain a separate archive-completion step.
