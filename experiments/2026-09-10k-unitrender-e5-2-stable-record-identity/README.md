# Phase 5 10K UnitRender E5-2 — Stable Record Identity Attribution

**Status:** RUNNING — preregistered attribution  
**Production remains:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

E5 found `RECORD_OBJECT_FIRST_TOUCH_DOMINANT`. E5-1 then showed that `slots=True` is causally beneficial but insufficient:

```text
Cull saving
50%   0.090 ms
100%  0.113 ms

E5-1 decision: DO_NOT_KEEP
```

Slots recovered only roughly one quarter of the earlier record-field first-touch magnitude. Production/slotted movement still allocates a fresh `UnitSpatialRecord` and replaces `by_entity[entity]` on every pure movement commit.

## Question

Does **fresh record replacement / object-working-set churn** explain a material part of the remaining Cull first-touch cost?

## Experimental isolation

Both variants run the exact rejected E5-1 slotted runtime:

```text
base SHA = 682fdb3a4c64002b402eb74bdda2331ca7123ab4
```

Control:

```text
slots=True
pure move -> allocate new UnitSpatialRecord -> replace by_entity entry
```

Treatment:

```text
slots=True
pure move -> keep existing UnitSpatialRecord identity
          -> internally refresh col/row/world_x/world_y/bucket with object.__setattr__
```

The dataclass remains externally `frozen=True`; ordinary callers still cannot assign fields. Generic `upsert_from_world()` / remove paths remain unchanged. Only the pure movement hot path is altered in the treatment probe.

The probe is copied into a detached base worktree at runtime. No runtime source file is changed on the experiment branch.

## Formal A/B

```text
order = A50 -> B50 -> B100 -> A100
A = exact slotted base, normal launcher
B = exact same base, stable-identity treatment launcher
```

Canonical 10K workload remains unchanged.

## Frozen attribution gates

Workload preservation:

```text
position commits/s within ±2%
vision changed/s   within ±2%
fog delta/s        within ±2%
```

Primary local metric, incremental relative to the slotted base:

```text
50%  Cull saving >= 0.08 ms/frame
100% Cull saving >= 0.15 ms/frame
```

Additional requirements:

```text
UnitRender avg improves at both densities
controlled avg does not materially regress by >2%
```

Positive result:

```text
FRESH_RECORD_REPLACEMENT_CANDIDATE_JUSTIFIED
```

Negative result:

```text
FRESH_RECORD_REPLACEMENT_NOT_MATERIAL
```

A positive result is attribution only, **not production KEEP**. It would justify implementing a real combined `slots + stable identity` candidate and comparing that combined treatment against frozen production in a later closeout.

## Forbidden interpretation

- Do not add E5-1 and E5-2 savings arithmetically as if they were independent.
- Do not merge the monkeypatch.
- Do not jump to SoA/custom hash containers before this replacement hypothesis is resolved.
- P99 remains diagnostic.

## Methodology

> **先用同一 slotted baseline 隔离“换对象”这一件事；只有增量 locality 收益成立，才把 stable identity 做成真正 candidate。**
