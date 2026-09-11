# Decision — keep team authority separate from shared projection

Accepted2026-09-12 for source `582dbdab6e7b060c2589096cd41bc45ee96a474f` / `rust-kernel-r2c-2026-09-12`.
Keep typed team state plus a reverse ownership index, and borrow-scoped factual
caches with fresh per-Agent permissions. Tests support equivalence at this
component/handler boundary. Continue with trusted identity/action dispatch next.

Do not expose private probes to Agents or change the default backend. Do not
select capacity, TTL, cache headroom or worker count from these functional tests.
R4 will measure cloning, candidate scans, serialization and scheduling costs.
Revisit after registration dispatch, full lifecycle mutation or parallel jobs join.
See README.md, manifest.yaml, analysis.md and canonical results for reproduction.
