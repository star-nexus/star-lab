# Analysis — native projection and team state

## Observation

Python team ownership and faction projection were not computed by R2b. Current
native results match252 recorded handler queries and all corresponding imported
states. Full suite1075 passes, including155native contracts. No timing comparison.

## Hypothesis and instrumentation

Shared factual data should be reusable while owner/commandable fields must remain
per-request. The probe interleaves different factions and same-faction callers,
explicit selections, claim conflict/transfer/release, movement and reset. Native
counters measure census, faction, panel, enemy and terrain fact builds per batch.

## Evidence

Each of36batches builds one census, three faction projections and three own-unit
panels. Contract tests verify enemy/terrain sharing across factions under Fog off.
After claim transfer, identical units receive caller-specific commandable values;
after a write, the next batch recomputes current facts. Full trace records60nodes.
Separate contract tests cover attack/death-query order, empty/invalid/duplicate IDs,
team FIFO caps0/1/3/64, unbounded imported queues and mid-state restore.

## Root cause / mechanism

Faction facts and Unit facts do not depend on the querying Agent. Team ownership
does affect the caller's commandable wrapper. A Rust shared borrow prevents writes
for the entire batch and is dropped at its end, without TTL or a stale snapshot.
Reverse owner indexing makes release-all proportional to that Agent's holdings.

## Rejected alternatives / limits

No performance claim follows from fewer fact builds. Trees still clone during
response assembly, and some faction/attack candidate paths still scan. No actual
thread-pool execution, full Agent registration/authentication, full World.update,
window pixels, Protocol/Hub or capacity test. R0b corrected a separate uncovered
skill ordering gap; old R0 tags and earlier evidence were not overwritten.
