# Decision — R4a scoped read panels

**Status:** accepted narrow implementation; no capacity/default acceptance  
**Decision date:** 2026-09-25  
**Validated STAR commit:** `45bd11cca09a88fb4c757feecc234a4efe932dae`  
**Validated STAR tag:** `rust-kernel-r4a-2026-09-25`

## 1. Decision

Keep threads1 as default. Make2/4 actual fixed read-worker options, limited to independent missing Unit panels. Retain Python usability/API/SDK/UI and serial world writes. No gameplay approximation or TTL.

## 2. Drivers and alternatives

| Option | Evidence | Decision |
| --- | --- | --- |
| Single caller | least scheduling overhead, exact results | keep default |
| 2workers | actual parallel execution; some MP6 single-query benefit | explicit option |
| 4workers | actual parallel execution; not consistently better than2 | explicit option |
| WholeECS parallel rewrite | shared mutation/RNG/occupancy dependencies remain | not introduced |
| Tuned minimum-panel threshold | onlytwo selected sizes tested, no sufficient threshold evidence | no empirical magic constant;0/1panelinline |

## 3. Headroom and scaling rationale

Measured minimum sufficient for the fullframe/queuegate: unknown. Operational default:1. A microbench improvement cannot justify more default threads; neither2nor4 met a formal capacity gate in this phase. No extra headroom claim.

## 4. Lifecycle / rule constraints

Scoped jobs join before cache commit or next write, deterministic chunk merge, no random consumption. Reset reuses pool atomically, close releases it. Keep historical skill failure and MPweakening; GAPledger updated. Diagnostic utilization may vary; full Agent contract must not.

## 5. Revisit

Measure public construction, panel computation, scheduling/join and final encoding separately on realistic varying Agent subsets. Then run whole30Hz acceptance with world/display/queue guards and choose the least thread count satisfying all gates. Preserve small-case regressions. Do not migratePython network/BOTpolicy as performancekernel work.
