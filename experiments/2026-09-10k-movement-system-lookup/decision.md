# Decision — 10K MovementSystem Lookup Elimination

## Decision

**CAUSALLY CONFIRMED / KEEP / CLOSED.**

Resolve `MovementSystem` once per `AnimationSystem` movement update rather than once per moving entity.

## Why retained

The change is:

- causally attributed before optimization;
- extremely small and low-risk;
- semantically neutral within a synchronous ECS update;
- validated by targeted regression coverage;
- confirmed by production controlled A/B;
- consistent with unchanged authoritative transition throughput.

The measured result changes system capability: the 10K / 50%-moving point moved from canonical 30Hz FAIL to PASS.

At 100% moving, Phase-5.1 predicted approximately `5.55 ms/frame` of repeated lookup work and the production A/B reduced `AnimationSystem` by approximately `5.77 ms/frame`, a direct causal match.

## Production state

The fix was introduced at:

```text
b9e0bb92b546b3283cb5c1d30a9a510d0c006ec2
```

A later Optimization-B experiment temporarily returned the production tree to the Optimization-A state at:

```text
7f72e352f95e20125c29502abd934f0f81a3e0f2
```

That rollback is historical provenance only. Optimization B was subsequently confirmed beneficial by a same-session ABBA closeout and restored at:

```text
4218b5368fbe2815b8512384e2c18b0af443ebfa
```

The current mainline therefore retains **Optimization A + confirmed Optimization B + later Vision work**.

## Revisit conditions

Revisit A only if one of these becomes true:

1. `MovementSystem` membership can legitimately change during a single synchronous animation update;
2. the dependency is replaced by an explicit system reference / registry and `_get_movement_system()` disappears;
3. movement animation architecture is replaced entirely.

Do not reintroduce per-entity system discovery without new semantic requirements and measurement evidence.
