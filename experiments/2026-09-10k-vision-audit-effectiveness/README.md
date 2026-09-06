# 10K Vision D — Periodic Safety-Audit Effectiveness

**Status:** RUNNING — attribution prepared; no production candidate selected  
**STAR repository:** `star-nexus/star`  
**Frozen production runtime:** `6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b`

## Trigger

The dedicated 10K / 100%-moving 30Hz frontier confirmation failed all three full-motion repeats:

```text
P99 = 33.944 / 34.049 / 34.050 ms
30Hz gate = 33.33 ms
```

All guards passed. The failure is highly repeatable and concentrated in `VisionSystem`'s periodic safety audit. Each full-motion sampled window contained exactly two controlled-work frames above 33.33ms and exactly two periodic Vision audit frames. `vision_audit_scan` costs about `4.1-4.3 ms` per invocation.

The ordinary non-audit workload appears to fit within the 30Hz budget, but that is diagnostic only. Canonical capacity includes maintenance work, so the frontier remains formally **NOT ESTABLISHED**.

## Question

The indexed window runtime already publishes explicit Vision invalidations for authoritative movement and unit death. Every 60 frames, however, `VisionSystem` still scans all resident units as a defensive safety net for direct component writes or lifecycle changes that bypass those invalidations.

The next question is therefore not:

> How can the 10K audit scan be made faster?

It is:

> **What new semantic information does the periodic O(Nresident) audit actually discover?**

This follows the campaign rule:

> **先消灭错误复杂度，再重构必要复杂度。**

## Current production semantics

Indexed worlds use:

```text
movement commit
  -> mark_vision_dirty(entity)

unit death
  -> UnitDeathEvent
  -> dirty(entity)

initial world
  -> force_all bootstrap audit

periodically every 60 frames
  -> _audit_all_units(force_all=False)
  -> scan every resident Vision unit
```

The periodic audit checks whether any entity is missing from the Vision index, has `Vision.dirty`, changed position/range/faction without explicit invalidation, or disappeared without lifecycle notification.

## Attribution distinction

The probe separates two fundamentally different outcomes.

### Prequeued mismatch

```text
entity already in Vision dirty queue before audit
+ audit observes the same mismatch
```

The scan contributes no new semantic knowledge for that entity; it merely re-confirms a change already scheduled for processing.

### Audit-only discovery

```text
entity NOT in dirty queue before audit
+ audit detects a real mismatch
```

This is the periodic audit's actual safety value.

Audit-only discoveries are split into:

```text
missing Vision membership / new entity
Vision.dirty flag without queue membership
position mismatch
range mismatch
faction mismatch
stale/lifecycle entity
multi-reason discovery
```

## Frozen experiment

STAR branch:

```text
experiment/phase5-vision-d-audit-effectiveness
```

Production runtime under test:

```text
6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b
= A + B + C1 + C2a
```

The experiment branch adds measurement tooling only. The runner launches the exact production SHA in a detached worktree and copies the process-local probe into it.

Tool identities:

```text
probe commit                  e8a7eccaf182cefc5431610370a363e3e2644c23
analyzer final commit         e0fbe5ae9f30bd1f4e709bc7aadc667d650b9eda
runner commit                 88e5aa3bd1ec814038c0a25512fd48297667041a
```

## Workload

```text
scenario                  chibi-144k-scale-10000
scenario SHA256           e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25
resident units            10000
Fog                       ON
MiniMap dynamic units     OFF
GC                        realtime_defer
phase                     staggered
seed / phase seed         42 / 42
route steps               12
render                    uncapped
hub                       offline
```

Execution order:

```text
00pct-moving
50pct-moving
100pct-moving-r1
100pct-moving-r2
100pct-moving-r3
```

Full-motion replication is intentional: the audit is currently the repeatable blocker at the formal 100%-moving frontier.

## Measurement outputs

For every sampled frame, non-audit frames publish explicit zeroes. Periodic audit frames publish:

```text
phase5_d_audit_invoked
phase5_d_audit_scanned
phase5_d_audit_dirty_before
phase5_d_audit_changed_current_total
phase5_d_audit_prequeued_current_changed
phase5_d_audit_only_current_changed
phase5_d_audit_only_missing_visibility
phase5_d_audit_only_vision_dirty_flag
phase5_d_audit_only_position_mismatch
phase5_d_audit_only_range_mismatch
phase5_d_audit_only_faction_mismatch
phase5_d_audit_only_stale
phase5_d_audit_only_total
phase5_d_audit_effectiveness_ratio
```

`vision_audit_scan` remains separately timed by the production profiler.

## Interpretation rules — frozen before measurement

This is attribution, not a production A/B.

### Case A — zero audit-only discoveries

If all measured periodic audits across 0%, 50%, and three 100%-moving fresh processes discover zero unqueued semantic mismatches, classify the periodic indexed-world audit as **no observed semantic contribution under the canonical workload**.

That finding is sufficient to design one isolated candidate, but not to retain it automatically. The candidate must still preserve:

```text
force_all bootstrap reconciliation
non-indexed-world direct-write safety behavior
explicit movement invalidation
unit-death lifecycle cleanup
all Vision/Fog observation semantics
```

and must pass a later uninstrumented production A/B plus another formal frontier confirmation.

### Case B — nonzero audit-only discoveries

If any audit-only mismatch is observed, do **not** remove the audit. First trace every reason back to the authoritative mutation path and determine whether the correct fix is to publish the missing invalidation explicitly.

The audit must not be optimized away while it is masking a real contract gap.

## Out of scope

Do not mix the following into Vision D attribution:

```text
C2b faction-refcount representation
C2c set-diff changes
geometry cache policy
movement semantics
rendering
GC
parallelism/native code
```

Vision D is specifically about whether the periodic O(Nresident) reconciliation scan is semantically necessary in the indexed production runtime.
