# Findings and limits

The trusted dispatcher preserves registration precedence, transport identity overriding
payload identity, faction/claim rejection, action subsets, error shape and action
counts. Re-registration retains legacy team membership and replaces registry rows
within the registered faction. These rules were ported without rebalancing gameplay.

Each native batch holds the runtime's exclusive lock. Only consecutive faction queries
share a read-only borrow. Query action counts are committed in order after the segment;
the projection never reads these counters and no external observer can interleave.
A command, including a rejected or partially failing command, ends the cache lifetime.
No stale frame, TTL, worker copy, or added batching wait is introduced.

The fixture checks both own and teammate views of the same Unit, force transfer,
partial release failure, faction switches, invalid selections and snapshots retained
across reset. Every configuration matches Python sequentially; batch matches the same
responses and final state. The 1/2/4 comparisons are determinism checks only.

This is not exhaustive equivalence for every malformed Python object, huge integer,
non-string faction or unusual Unicode repr. The public adapter requires normalized
JSON dictionaries, while legacy handlers historically accepted some Python-only values.
Those edge cases, complete World.update lifecycle, visual combat entities, remaining
verbs and native parallel scheduling are still open migration coverage. Nothing here
establishes 5000U/1000A throughput or 30Hz real-time performance.
