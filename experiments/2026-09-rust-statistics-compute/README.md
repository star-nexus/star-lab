# E2 Statistics compute / ordered commit research

Status: DRAFT, in progress (2026-10-01).

Progress: `serial split █ | attribution █ | scoped prototype █ | equivalence ▒ | net benefit ░ | live capacity ░`.

Target remains5000 Units/1000 Agents;5000 Agents paused. Production branch
codex/rust-ecs-parallel, isolated worktree /Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main.
E1 design and P0 evidence remain immutable. Default threads=1; prototype normal
dispatch remains serial until net/crossover validation. This draft is not capacity evidence.

Source: baseline c058d75c0ad67a7c340c2a6ac74a9d5bc2888adf;
serial split44c3696814b82d7c9d92a83ef7d160ef462168af;
scoped prototype7ab0ac1d97f5d68b8d81c505fa505a1cb234a56c.
Exact source/binary guards and canonical R4e input are used by
tools/rust_migration/profile_statistics_trace.py. Independent-binary cases use
statistics_contract_matrix.py and an archived fixed input. Formal reproduction,
analysis, decision, artifact index and checksums will be completed after gates.

Preliminary attribution is scoped to recorded input including warmup. Independent
arithmetic is tiny; JSON record construction, ordered commits and bounded history
trim dominate. Only pure current-batch row construction enters the existing scoped
instance pool; no world copy, extra pool, sampling/batch-size change or worker write.
