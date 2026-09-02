# Decision — Realtime Cyclic-GC Policy

**Status:** accepted / closed  
**Decision date:** 2026-09-02  
**Policy implementation:** `6bdeabe210fbc2e8dc3612a03e0cab11df1e77a1`  
**Scale integration:** `74708af3f1bf2c31b050cf816e30aa52613fcda8`  
**Formal guarded measurement state:** `33b18bc777df992ff8665d458d70782451d05a51`

## 1. Decision

Use a **bounded `realtime_defer` cyclic-GC policy** for latency-critical scale/realtime measurement windows when explicitly selected. Before the critical phase, run a full generation-2 collection; during the bounded critical window, disable automatic cyclic GC while leaving CPython reference counting active; at deadline, stop, clear, cleanup, or another explicit safe point, restore the exact automatic-GC state observed before activation.

Do not globally or permanently disable GC.

## 2. Decision drivers

- remove unpredictable generation-2 pauses from the latency-critical loop;
- preserve ordinary reference-count reclamation;
- preserve caller/runtime GC state outside the bounded phase;
- move maintenance cost rather than pretending it disappears;
- keep the policy explicitly measurable and A/B selectable.

## 3. Measured alternatives

| Policy | P99 | Max | UnitRender max | GC placement | Decision |
|---|---:|---:|---:|---|---|
| `auto` | 48.815 ms | ~52.7 ms; worst 57.756 ms | 34.839 ms | arbitrary automatic Gen2 inside hot loop | Rejected for formal latency-critical phase |
| `realtime_defer` | 25.489 ms | 26.581 ms | 7.103 ms | explicit pre-phase safe-point collection | **Chosen** |

## 4. Why this option

The controlled A/B changes the timing policy for cyclic GC and collapses the abnormal tail while preserving normal rendering semantics. The worst AUTO frame includes ~30.9 ms of Gen2 GC, closely explaining the tail magnitude; moving that work outside the critical epoch is therefore causally justified.

The policy does **not** claim to make GC free. The pre-phase full collection itself cost about 19.7 ms in the representative deferred run. The engineering goal is temporal placement:

> expensive, unpredictable maintenance should not occur randomly inside a latency-critical hot loop.

## 5. Why not global GC disable

Permanent disablement would make application behavior depend on an implicit long-term object-lifecycle assumption and could allow cyclic garbage to accumulate indefinitely. The accepted policy is bounded and restores the prior state.

## 6. Why not "run GC more often"

More frequent arbitrary GC would increase the probability of maintenance inside the critical phase. The problem is not simply total GC work; it is unpredictable placement relative to the realtime latency budget.

## 7. Risks / trade-offs

- cyclic garbage created during a deferred window is not reclaimed until automatic GC is restored or an explicit safe-point collection runs;
- safe-point full collections have visible cost and must remain outside measured/latency-critical epochs;
- much longer critical windows or materially different object graphs require fresh memory/latency validation.

## 8. Revisit when

Re-profile and reconsider this policy when:

- CPython GC behavior changes materially;
- STAR moves to a different Python implementation;
- critical realtime windows become much longer;
- cyclic garbage accumulation during the bounded window becomes measurable;
- safe-point collection cost itself becomes an operational bottleneck;
- native/runtime restructuring removes Python object churn from the critical loop.

## 9. Principle

> Necessary maintenance may be moved to a safe point; it must not be allowed to appear unpredictably inside the latency-critical path merely because the runtime scheduler chose that moment.
