# Decision — UnitRender E2

## Formal decision

```text
CULL_REQUIRES_FURTHER_ATTRIBUTION
```

E2 is **CLOSED as an attribution stage**. No production candidate is authorized.

## Rejected explanations

- candidate-volume growth;
- branch-mix growth;
- >=20% warm `by_entity + bounds` unit-cost inflation;
- >=20% warm Fog-membership unit-cost inflation.

## Remaining open explanation

First-touch locality after same-frame Movement/Vision mutation was not measured by E2 because its bulk replay executes after the production traversal has already warmed the relevant structures.

## Production decision

```text
production = 17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
unchanged
```

Do not implement spatial/Fog data-structure changes from E2.

## Next

Proceed to:

```text
UnitRender E3 — Cull first-touch locality attribution
```

E3 must first require the original baseline Cull growth to reproduce. If it does not reproduce, close the Cull signal rather than optimizing a stale or drift-dependent signature.
