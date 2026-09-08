# Analysis — active

## Observation

At baseline, 1000 canonical units / 1000 registered Agents, three static queries return 333 own-unit panels each; build times 194.018 / 149.934 / 144.886ms. The 999 `_unit_reachable` calls total 480.729ms. No attackable targets in this fixture: attack cost cannot be inferred from it.

In the separate interleaved fixture (same source, 1000 units), baseline queries return 333 panels, 17,646 reachable cells and 87 attackable targets. Build times 265.849 / 274.762 / 263.633ms. Inclusive helper times: reachable 456.815ms, attackable 313.654ms across three queries.

## Root cause

`handle_faction_state` computes every own-unit panel/affordance even for a one-unit Agent. `reachable_hexes` rebuilds dynamic occupancy by scanning all units per mover. `_unit_attackable` tests every visible enemy per own unit. Source and inclusive helper counts agree; profiling calls are diagnostic only.

## Candidates

1. Explicit `unit_ids` projection keeps shared faction observation intact; omitted parameter preserves full payload. This is a declared scope change, not an equivalent full-payload speedup.
2. Reuse existing window `occupancy_for_mover_local` with the existing movement oracle.
3. Spatial candidate filtering + unchanged final combat oracle for attackable. Fallback remains scan-based for unindexed worlds.

## Evidence limits

Selected interleaved probes retain nonempty reachable and attackable targets. They expose visible-terrain construction and serialization as substantial residuals. Short diagnostics do not establish 30Hz runtime capacity. CPU/Chrome interference has not been used to remove samples. Positive formal repeated-window evidence is pending.
