# 10K Vision D — Periodic Safety-Audit Effectiveness

**Status:** CLOSED — D1 causally confirmed / KEEP; raw mirror pending  
**STAR repository:** `star-nexus/star`

## Trigger

The first formal 10K / 100%-moving 30Hz confirmation failed all three full-motion repeats at:

```text
33.944 / 34.049 / 34.050 ms
```

The only repeatable controlled-work frames above the 33.33ms gate coincided with the periodic Vision safety audit, whose full 10K scan cost about `4.1-4.3 ms` per invocation.

## Vision D attribution

Question:

> What new semantic information does the periodic O(Nresident) audit actually discover in the indexed production runtime?

Run `20260906-215357` measured five fresh-process points (`0%, 50%, 100%-r1/r2/r3`) against exact production `6896cdc0...`.

```text
periodic audits             14
entity scans                140000
already-prequeued changes   4623
audit-only discoveries      0
average audit CPU           4.127 ms/invocation
```

Every possible audit-only reason was zero:

```text
new / missing membership    0
Vision.dirty unqueued       0
position mismatch           0
range mismatch              0
faction mismatch            0
stale / lifecycle           0
```

Classification:

```text
NO OBSERVED SEMANTIC CONTRIBUTION
UNDER CANONICAL INDEXED WORKLOAD
```

This is observational evidence, not a proof that an audit can never help. It was sufficient to justify one isolated candidate.

## D1 — indexed periodic-audit boundary

D1 keeps the safety semantics where they are actually contracted:

```text
bootstrap force_all audit          KEEP
non-indexed direct-write audit     KEEP
indexed window periodic 10K scan   REMOVE FROM HOT RUNTIME
```

Shared/headless Vision behavior remains unchanged. Indexed movement continues to publish `mark_vision_dirty()`, and unit death continues through the lifecycle dirty path.

Candidate:

```text
implementation  5f271d7e9ead40882dcc00c6c89f30284bde9f1e
treatment       17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
```

## D1 controlled A/B

Run `20260906-223546`:

```text
A control     6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b
B treatment   17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
order         A50 -> B50 -> B100 -> A100
```

50% moving:

```text
controlled avg      24.368 -> 24.741 ms   (+1.53%)
controlled p99      27.882 -> 26.429 ms
Vision avg           1.549 ->  1.522 ms
periodic audit max   4.331 ->  0.001 ms
audit scanned max   10000 -> 0
```

100% moving:

```text
controlled avg      31.019 -> 30.858 ms
controlled p99      33.931 -> 32.497 ms
Vision avg           3.395 ->  3.325 ms
periodic audit max   4.233 ->  0.001 ms
audit scanned max   10000 -> 0
>33.33ms frames      2 -> 0
```

All authoritative workload preservation gates passed. Geometry evictions remained zero. `17` targeted regressions passed; driver, process-tree cleanup and runtime guards passed at all four points.

Decision:

```text
D1
CAUSALLY CONFIRMED
KEEP
CLOSED
```

The 50% aggregate-average drift stayed inside the preregistered +2% bound while the modified Vision path improved locally and the targeted audit pulse disappeared. It therefore does not overturn the causal result.

## Production state

D1 is retained on:

```text
perf/10k-online
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
= A + B + C1 + C2a + D1
```

## Frontier status

The D1 closeout's `100% P99 = 32.497 ms` is supporting evidence only. It does not establish the capacity frontier because P99 was diagnostic in the optimization closeout.

A separate post-D1 formal confirmation is preregistered:

```text
00pct-moving
50pct-moving
100pct-moving-r1
100pct-moving-r2
100pct-moving-r3
```

The frontier advances only if all guards pass and **all three** full-motion runs independently satisfy:

```text
controlled_work_frame_ms.p99 <= 33.33 ms
```

No median-only or majority-only reinterpretation is allowed.

## Evidence identity

```text
D attribution run       20260906-215357
D1 closeout run         20260906-223546
D1 ZIP SHA256           455f1173a3cb904f3deeb779ed80dd68ffad82464b697e4f0137fcc0d2234860
```

Raw STAR Lab mirrors remain pending as an archive-completion step.

## Methodology

> **先消灭错误复杂度，再重构必要复杂度。**

Vision D/D1 is a direct instance: the system already had sufficient incremental invalidation semantics, but still paid a periodic O(Nresident) reconciliation pulse that observed no additional canonical-state changes.
