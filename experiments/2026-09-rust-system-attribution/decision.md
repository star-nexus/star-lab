# Decision — P0 attribution; select one constrained P1 candidate

**Status:** P0 instrumentation accepted; P1 optimization proposed pending admission audit/A-B.
Date:2026-09-30. Measurement source2ac2b29a7a3bf09d92370a0352dcf0fd47f741e5.

## Decision

Keep opt-in per-System diagnostic and dependency table. Ordinary world step stays
sequential. First ACTUAL optimization candidate is an ordered encoded observation
batch for already-admitted adjacent faction queries, reusing ObservationBatch.
This is cross-request immutable fact sharing, not between-System scheduling or
a new sharing algorithm. Do not force world-system worker jobs at this scale.

## Evidence / alternatives

| Candidate | Evidence | Decision |
|---|---|---|
| All Systems in pool | shared component/index/event/RNG/structure writes and original phase order | Reject design; not benchmarked |
| Movement arithmetic workers | mean0.027ms; ordered occupancy/dirty commits remain | Defer; low maximum current-load benefit |
| Vision geometry workers | mean0.045ms; cache/LRU/refcount commits remain ordered | Defer until high-dirty costs justify it |
| Statistics workers | largest world phase mean0.167ms; ordered cycle/history/floating reductions | Audit separately; no permission to reorder samples |
| Adjacent query batch | 7097/11007 queries in2–5 read runs; 1604 same-faction repeats; zero repeated panels | P1 candidate, not accepted speedup |

## P1 concrete boundary / validation gate

Audit the owner admission queue first. Batch only consecutive ALREADY-ADMITTED
get_faction_state entries in existing order; never wait for a future request or
cross a command, failed command, tick, presentation, VLM capture, reset or close.
Callbacks/decisions must not silently change which operation is admitted next.
If the scheduler cannot offer such a boundary, record the negative feasibility
result rather than manufacture batch opportunities by reordering the workload.

Preserve trusted identity/wall metadata, prevalidation, query counters/response
order, Fog/per-request permissions, M→Q→N and standalone response ownership. An
encoded entry must avoid losing R4d gains through Python dict decode/re-encode;
Python keeps friendly interfaces and network/policy orchestration. Use existing
pool only for measured within-query work; no second pool or oversubscription.

First fixed-input same-world full-response/delta/state comparison, then controlled
single vs batch with public-build/output/decode/admission times. Keep small/empty
and write-separated negative controls. Then unchanged R4e1000-Agent short window
and, only if justified, three300s gates. Record changed actual accept timings for
replay. Default1thread/Python unchanged; 5000-Agent tuning remains paused.

## Limits / revisit

This phase selects no new default/thread count, offers no frame speedup estimate,
and closes no G008/G009/R001/R002. Annotated P0 milestone marks scoped attribution
and equivalence only. Revisit world arithmetic/geometry after measured high-dirty
or high-contact evidence; do not borrow capacity conclusions from other profiles.
