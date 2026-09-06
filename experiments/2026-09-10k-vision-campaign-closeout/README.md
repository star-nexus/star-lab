# Phase 5 10K Vision Optimization Campaign Closeout

**Status:** CLOSED — current evidence-backed Vision optimization hypotheses exhausted  
**STAR production:** `star-nexus/star@17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Scope

This rollup closes the Phase 5 Vision performance campaign for the 10K window runtime. It does not claim Vision is globally optimal; it records that the currently evidenced high-value hypotheses have been tested and either retained or rejected.

Methodology remained:

```text
Instrument -> Attribute -> Optimize -> Controlled A/B -> Stress/Regression -> STAR Lab archive
```

and:

> **先消灭错误复杂度，再重构必要复杂度。**

## Production-retained Vision changes

### C1 — cache-ordering inversion

Geometry-cache hits were checking terrain bonus before the cache lookup. Moving the overwhelmingly common hit path before terrain resolution reduced Vision CPU by roughly 13–15% under 10K moving workloads.

**Decision:** `KEEP / CLOSED`.

### C2a — explored-history overmaintenance

`explored_tiles` is monotonic history, but production was reinserting every changed observer's full current visibility set. C2a moved maintenance to the faction refcount `0 -> 1` semantic transition.

**Decision:** `KEEP / CLOSED`.

### D1 — periodic indexed-world reconciliation

The final pre-D1 tail blocker was a periodic O(Nresident) defensive audit. Attribution observed 140,000 entity scans across 14 periodic audits, 4,623 real changes already prequeued by explicit invalidation, and **zero audit-only discoveries**. D1 preserved bootstrap and non-indexed safety while making the periodic indexed-window audit an O(1) no-op.

**Decision:** `KEEP / CLOSED`.

Production after retained Vision work:

```text
17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a
= A + B + C1 + C2a + D1
```

## Rejected / closed Vision hypotheses

### C2b-1 — dense-core faction refcount representation

Attribution showed about 200k refcount operations/s and ~1.37 ms/frame of add/remove path activity at 100% moving. A window-only dense `list[int]` core plus off-bbox dict overflow preserved semantics but saved only:

```text
50%:  0.281 us / changed unit
100%: 0.064 us / changed unit
```

against a preregistered 0.4 us floor.

**Decision:** `DO_NOT_KEEP / CLOSED`.

Engineering lesson: the path cost is not primarily Python tuple-key dict representation tax; replacing C-backed dict work with Python bounds/index bytecode did not provide enough production benefit.

### C2c — visibility-delta multiplicity

C2c tested whether the necessary pair of set differences was being recomputed for the same exact `(old_visibility_object, new_visibility_object)` transition many times per frame.

At 100% moving:

```text
diff calls/frame       658.6
unique pairs/frame     655.6
repeated observations    3.0
pair reuse              0.46%
same-object pairs       0
estimated repeated removable CPU ~0.003 ms/frame
```

**Decision:** `NO_MULTIPLICITY_CANDIDATE / CLOSED`.

Key lesson:

> **Geometry reuse is high, transition reuse is not.**

Do not add a delta cache or hand-write a Python set-diff path without new evidence.

## Campaign conclusion

The Vision campaign removed three evidence-backed forms of wrong work:

```text
cache-ordering inversion
monotonic-history overmaintenance
semantically unproductive periodic full-world audit
```

It then tested two necessary-complexity hypotheses and rejected both at the current layer:

```text
refcount representation rewrite
visibility-delta multiplicity cache
```

Therefore Vision is no longer the active Phase 5 optimization target.

### Reopen rule

Do **not** reopen this campaign merely because Vision remains measurable. Reopen only when a new causal signature appears, for example:

- a new isolated Vision pulse;
- a workload/schema change that invalidates the current contracts;
- a new representation/multiplicity signal with quantified opportunity materially above the current 10K margin requirement.

## Capacity state at closeout

Post-D1 formal 10K / 100%-moving / 30Hz confirmation remains:

```text
P99 = 32.926 / 33.348 / 33.764 ms
FRONTIER_NOT_ESTABLISHED
worst headroom = -0.434 ms
```

The runtime is margin-limited rather than dominated by a known Vision pathology.

## Next target

The next attribution target is **UnitRender moving-path amplification**.

The stable movement-dependent UnitRender delta is approximately:

```text
Phase-5 baseline:  +2.835 ms from 0% -> 100% moving
recent diagnostic: +2.831 ms from 0% -> 100% moving
```

Production batch rendering groups static units by committed hex and renders at most six per group, while animated units are removed from that grouping path and rendered individually. The next experiment will attribute whether that aggregation collapse explains a material share of the movement-dependent UnitRender cost.

## Archive completeness note

This campaign rollup links logical decisions only. Some underlying case manifests still mark raw evidence as `raw_mirror_pending`; therefore this rollup deliberately does **not** claim that every raw ZIP/tree has already been physically mirrored into STAR Lab.
