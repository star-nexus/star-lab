# What passed and what remains

Derived living counts are built at import/reset and decremented on death. Base policy
counts living units with Unit+UnitCount; the indexed window policy additionally
requires position. Per-frame victory checking is O(number of factions), not O(Units).
Mutual wipe/annihilation take precedence over timeout. Real-time timeout reads
simulation seconds; turn timeout uses the existing strict greater-than max-turn rule.
GameOverEvent is emitted once. GameTimeSystem syncs turn clocks only when enabled.

The 394-node small trace covers exact core World.update results/events/state through
move, query, recovery, a lethal rule-mode attack, next-tick victory and reset.
The full regression's 37 new lifecycle cases cover timeout, pause and enabled/mode
edges. This is core fixture coverage, not full GameScene/UI or settlement coverage.

The large native trace proves actual registered/claimed interaction with1000 Agents,
not a prefilled identity map or frozen observation benchmark. The Python world is
released before the run. All5000 Units remain alive. Each Agent completes1–3 loops;
there are2007 observations,4017 accepted moves,64 attacks and63 rejected moves.
No simultaneous-moving claim is possible: the chosen none profile moves instantly.

The recorded loop is a diagnostic, with no warmup and per-response digest overhead.
P99 loop41.926ms, world29.635Hz, observation119.214ms, action queue120.651ms; end queue
has no overdue events. Native step median1.209ms and P9916.861ms, but this does not
identify one proven bottleneck or predict rendered performance. Further attribution
and optimization belong to R4, after full functionality is connected.

Full trace replay validates8151 response digests,1779 tick event sequences and final
state SHA2560bd67e13000db8cfdcc39013b93d836ebe51c19b0b06cbc3835f52d77a8826ac.
It is native deterministic replay, not a5000-Unit Python/native differential run.
The smaller trace provides the Python comparison; those are distinct evidence claims.

R3 still needs turn handoff/reset, other verbs/BOT/settlement, and actual window
handoff including visual combat entity allocation/lifetime and Fog presentation.
Unusual malformed-input compatibility and expanded scenario coverage remain tracked.
R4 workers/cost changes, and R5 full rendered capacity/platform wheels/default switch,
are not accepted by this checkpoint. Python remains default.
