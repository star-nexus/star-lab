# E7 analysis — P0 completed, P1 in progress

Full 9880-tick diagnostic replay at source 57b6520, same native extension, ordinary consumer: apply 2.6499ms, display including clear 8.5771ms, RMS 1.9456ms; D+Q 10.5227ms. Inclusive territory traversal 2.3707ms versus batch packing 0.1118ms. Typed layer separately: territory traversal 2.7087ms. These contain diagnostic overhead and do not predict speedup.

Initial snapshot and all 9880 canonical full deltas contain zero TerritoryControl components. Real Cocoa short diagnostics corroborate territory traversal cost; diagnostic scope aggregation includes warmup. Both short runs fail frame P99 and not_diagnostic guards: no capacity conclusion. A 600-tick baseline/probed-baseline/unprobed-baseline control passes fields, commands and pixels (development control only).

Select C, empty territory ECS lookup avoidance, rather than A command packing. Cache only validated coordinate sequence, capped at32768. Tile IDs remain live; any component membership or nonstandard input falls back. Complexity remains O(visible), no computed ownership, style, Fog, Surface or entity reference retained. Ordinary update untouched. No default enablement or native changes.

P1/P2/P3 preregistration fixes modes and the original plan gates before formal performance. Baseline diagnostics are not formal performance. Correctness and net speed remain pending.
