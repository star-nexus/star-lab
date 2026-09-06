# Decision — Vision D Attribution

## Status

```text
ATTRIBUTION COMPLETE
NO OBSERVED SEMANTIC CONTRIBUTION
D1 CANDIDATE JUSTIFIED
PRODUCTION RETENTION NOT YET DECIDED
```

## Decision

Do not spend effort optimizing the internals of the periodic 10K safety scan first.

The canonical indexed workload produced `140,000` entity-scan opportunities across `14` periodic audits and discovered `0` unqueued Vision mismatches, while `4,623` already-prequeued changes demonstrated that the incremental path was active. Each scan still cost about `4.13 ms`.

Proceed with one isolated D1 candidate that removes the periodic full-world scan only from the indexed **window** runtime boundary while preserving:

- force-all bootstrap reconciliation;
- non-indexed direct-write safety auditing;
- explicit movement invalidation;
- unit-death lifecycle cleanup;
- all Vision/Fog state semantics.

Do not change C2b refcount representation, set-diff, geometry, movement, rendering, GC, or parallelism in D1.

## Retention gate

D1 is not retained from attribution alone. It requires:

1. targeted semantic regressions;
2. uninstrumented same-session controlled A/B against production `6896cdc0...`;
3. unchanged authoritative movement/Vision/Fog workload rates;
4. removal of the ~4ms periodic audit pulse from the indexed treatment;
5. no whole-system regression outside the intended tail removal.

If retained, run a new formal 10K / 100%-moving 30Hz frontier confirmation with three fresh-process full-motion repetitions. The frontier moves only if the preregistered 33.33ms P99 rule is then satisfied.
