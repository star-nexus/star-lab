# Decision — DO_NOT_KEEP

The E5-1 `slots=True` candidate is rejected for production.

The treatment produced a real and consistent Cull improvement of roughly 5% at both movement densities, including matching p95/p99 reductions. However, the preregistered local causal floors were not met:

```text
50% required >= 0.10 ms; observed 0.090 ms
100% required >= 0.20 ms; observed 0.113 ms
```

Workload rates and semantics were preserved, UnitRender improved at both densities, and 100% controlled average also improved. Those supporting signals do not override the frozen Cull gate.

Interpretation: ordinary dataclass attribute layout accounts for a minority of the E5 record first-touch effect. The remaining signal is more consistent with fresh-record replacement/object-working-set churn during movement commits.

Next research should isolate stable record identity / in-place movement updates on top of the slotted experimental baseline before any combined treatment is compared against production. Do not jump directly to SoA or custom hash structures.
