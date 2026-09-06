# Decision — 10K Spatial-Index Movement Specialization

## Decision

**Reject and revert the specialized movement update.**

The candidate was technically correct, but it did not produce a measurable causal performance improvement in the directly modified `AnimationSystem` path.

## Why rejected

The candidate introduced new production concepts and branches:

```text
move_entity()
move_unit_spatial_index()
same-bucket update path
cross-bucket update path
missing-entry fallback path
additional specialized regression surface
```

The direct measured benefit was approximately zero:

```text
50%  Animation avg 3.633 -> 3.664 ms
100% Animation avg 7.770 -> 7.749 ms
```

Carrying extra state-maintenance complexity without measured benefit violates the STAR performance-engineering rule:

> No measured win, no additional production complexity.

## Rollback

Production was restored with:

```text
7f72e352f95e20125c29502abd934f0f81a3e0f2
revert: drop non-beneficial spatial index movement specialization
```

The rollback commit uses the exact Optimization-A tree. `b9e0bb92...` vs `7f72e352...` has zero file differences.

The B commits remain in Git history as experimental provenance, but no B implementation or B-only tests remain in the current production tree.

## What this rules out

Do not repeat this exact approach under the assumption that the Phase-5.1 `~3.19 ms/frame` spatial-index attribution is mostly generic-lifecycle overhead.

That interpretation is experimentally rejected.

## What remains open

A future spatial-index investigation is still justified if new attribution targets the mandatory work itself, for example:

- record / coordinate derivation;
- cell set/dict maintenance;
- bucket representation;
- batched movement-index maintenance;
- alternative data layout.

Such work must start with new instrumentation rather than reintroducing the rejected specialization.

## Next direction

Return to the accepted Optimization-A baseline and proceed to Vision steady dirty-path work, beginning with the geometry cache-hit path.
