# Analysis

**Observation.** R1 owns the scene but cannot calculate moves/attacks or recover
resources. The new checkpoint performs the tested subset entirely in Rust.
1032 tests and all 360 recorded differential nodes pass. Read the compact summary
for machine-readable case results and the raw trace for both sides of every check.

**Instrumentation.** The low-level fixture deliberately omits normal statistics
and Fog subscribers. It drives actual Python MovementSystem, CombatSystem,
AnimationSystem movement advancement and ResourceRecoverySystem against the native
counterparts. It compares whole transferred state, response lists and ordered
events, including full MT state and the recovery ledger. Additional contracts
cover terrain/type/state/headcount combinations, errors, death, reset, pause,
fractional cadence and larger dt. It does not instrument latency or Agent queues.

**Compatibility causes found.** A new combat roll has hit_threshold=1 and the
forest penalty only applies after a previous hit_roll exists. The port preserves
that behavior rather than the contradictory comments. Enum versus raw string
UnitStatus values can select different coefficients, so the codec retains that
distinction. Missing Terrain is impassable, and some legacy terrain helpers treat
entity ID zero as absent. Rule-mode moves commit immediately; display modes
commit each segment. MP spends start their timer on the following advancing
recovery update, while repeated AP spends retain their original cadence.

**Hypothesis, not a result.** Native data and active queues may reduce large-world
cost. This archive contains no measurement supporting a throughput or frame-time
claim. Full observation, statistics, rendering and Agent integration can introduce
costs absent here.

**Rejected interpretations.** Passing these fixtures is not replay equivalence
of complete World.update, is not a usable Rust Agent backend, and is not evidence
for 5000/1000/30Hz. Requested thread counts remain configuration only; parallel
systems are still a later gate. Failed standalone Python-extension linkage from
an undocumented cargo test invocation is a build-path issue, not evidence that
the Maturin wheel or gameplay algorithms are invalid.
