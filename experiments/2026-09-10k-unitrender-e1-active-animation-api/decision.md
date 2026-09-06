# Decision — UnitRender E1 Active-Animation API

**Decision:** `DO_NOT_KEEP`  
**Production:** remains `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Reason

The candidate passed semantic regression and delivered a strong 50%-moving improvement, but failed the preregistered full-motion causal gate:

```text
required 100% non-cull saving >= 0.50 ms/frame
observed                         0.0338 ms/frame
```

The treatment primarily accelerates static-unit classification. At 100% moving that opportunity disappears, so the candidate does not provide the margin required for the active Phase-5 frontier.

Do not merge `e186135dc25d34f51a77218e2105126be3180b3e` into production.

## Learned constraint

Do not use the prior fine-grained E stage estimates as removable-cost predictions. Very short operation-level timings were instrumentation-inflated. Production uninstrumented A/B is authoritative.

## Next action

Proceed to the separately open UnitRender cull signal (`E2`). Do not combine E1 with E2.
