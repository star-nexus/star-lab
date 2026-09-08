# Decision — provisional

Keep the four-layer architecture. Reuse existing multi-unit ownership, request gate, movement/combat oracles and window spatial index. No network/Hub or real LLM dependency for this phase.

P1/P2 are skipped per user instruction. Agent response delays are 1/5/15/60s. Preserve full faction Fog/intelligence; explicit selected panels are documented separately from compatibility full-state responses. Do not cache stale legality or change shared vision to make a point pass.

Production integration is pending tests and controlled runtime evidence. Before any squash merge to main, create an immutable annotated tag on the exact development tip and record pre-main / tagged development / post-main SHAs. See active progress for checkpoints.
