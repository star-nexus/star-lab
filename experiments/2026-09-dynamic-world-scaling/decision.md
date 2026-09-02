# Decision — Dynamic World Scaling Archive

## Decision

Preserve V1/V2/V2.1 as one methodology-evolution case with the original 14 JSON artifacts and their SHA256 checksums.

Do **not** assign exact STAR commit SHAs to the cohorts until provenance is proven.

## Why keep the series

The series records how the large-scale test harness became capable of exposing distinct realtime bottlenecks. It preserves evidence that would otherwise remain as disconnected local benchmark files.

## Why not promote it to a complete formal archive yet

STAR Lab requires exact source provenance for formal reproduction. The recovered raw JSON is authentic and integrity-verified, but current evidence does not establish the exact source commit for each V1/V2/V2.1 cohort.

Therefore:

```text
raw evidence        = verified
workload metadata   = present
source provenance   = pending
formal-complete     = no
```

## Why not guess SHAs

A guessed SHA would make the archive look more complete while making long-term reproduction less trustworthy. An explicit `null / pending` is preferable.

## Relationship to later cases

Dedicated GC, Memory, Cull, and Vision cases own their causal conclusions. Dynamic World remains the methodology/context case and should cross-link to those cases rather than duplicate their evidence.

## Revisit when

Upgrade this case to `complete_formal_archive` when exact source SHA(s) for V1/V2/V2.1 have been proven and reproduction commands have been checked against those states.
