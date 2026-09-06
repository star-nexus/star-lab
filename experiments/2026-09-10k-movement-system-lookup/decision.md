# Decision — 10K MovementSystem Lookup Elimination

## Decision

**Retain the optimization. Case CLOSED.**

Resolve `MovementSystem` once per `AnimationSystem` movement update rather than once per moving entity.

## Why retained

The change is:

- causally attributed before optimization;
- extremely small and low-risk;
- semantically neutral within a synchronous ECS update;
- validated by targeted regression coverage;
- confirmed by production controlled A/B;
- consistent with unchanged authoritative transition throughput.

The measured result is large enough to change system capability: the 10K / 50%-moving point moved from canonical 30Hz FAIL to PASS.

## Production state

The fix was introduced at:

```text
b9e0bb92b546b3283cb5c1d30a9a510d0c006ec2
```

After the subsequent rejected spatial-index specialization experiment, STAR was explicitly restored at:

```text
7f72e352f95e20125c29502abd934f0f81a3e0f2
```

The Git tree at `7f72e352...` is byte-identical to the Optimization-A tree (`git compare` reports no changed files), while preserving the negative experiment in history.

## Revisit conditions

Revisit only if one of these becomes true:

1. `MovementSystem` membership can legitimately change during a single synchronous animation update;
2. the dependency is replaced by an explicit system reference / registry and `_get_movement_system()` disappears;
3. movement animation architecture is replaced entirely.

Do not reintroduce per-entity system discovery without new semantic requirements and measurement evidence.
