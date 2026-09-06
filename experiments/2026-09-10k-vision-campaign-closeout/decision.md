# Decision — Phase 5 10K Vision Campaign

## Decision

```text
VISION CAMPAIGN CLOSED
CURRENT EVIDENCE-BACKED HYPOTHESES EXHAUSTED
PRODUCTION REMAINS 17ced8d2...
NEXT TARGET: UNITRENDER MOVING PATH
```

Retain:

```text
C1   cache-ordering inversion
C2a  explored-history semantic trigger
D1   indexed periodic audit boundary
```

Reject / close:

```text
C2b-1  dense-core refcount representation -> DO_NOT_KEEP
C2c    visibility-delta multiplicity       -> NO CANDIDATE
```

## Why stop Vision now

The remaining Vision work is measurable but no longer has an evidence-backed wrong-complexity or multiplicity candidate large enough to justify more production complexity.

Continuing with ad hoc tuple/set/dict micro-tuning would violate the campaign methodology. A future Vision case requires a new causal signature, not merely the fact that Vision consumes CPU.

## Next action

Start UnitRender moving-path attribution from exact production `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`.

Primary hypothesis to test, not assume:

> Static batch rendering retains hex-level aggregation and caps rendering at six entities per group, while animated units bypass that grouping and are rendered individually. Under 10K stress movement, this may cause a movement-dependent multiplicity amplification.

No UnitRender candidate is selected until attribution quantifies the path split and visual-equivalence opportunity.
