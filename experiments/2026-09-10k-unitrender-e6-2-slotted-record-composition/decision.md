# Decision — Phase 5 10K UnitRender E6-2 Slotted Spatial Record Composition

**Status:** PENDING FORMAL CONTROLLED A/B

## Baseline

Retained E6-1 production:

```text
e7ba18b31870577110b591104ef8fa7b4713e43c
```

## Treatment

Install only:

```python
@dataclass(frozen=True, slots=True)
class UnitSpatialRecord:
    ...same fields...
```

before world creation, while preserving the retained E6-1 geometry ownership and
all authoritative semantics.

## Preregistered decision rule

Choose:

```text
SLOTTED_RECORD_COMPOSITION_CANDIDATE_JUSTIFIED
```

only when both densities satisfy all guards and:

```text
position / Vision / Fog rates within ±2%
Cull avg saving >= 0.05 ms @50%
Cull avg saving >= 0.07 ms @100%
UnitRender avg regression <= 1%
controlled-work avg regression <= 1%
Animation avg regression <= 2%
```

Otherwise choose:

```text
SLOTTED_RECORD_COMPOSITION_NOT_MATERIAL
```

Do not change these thresholds after seeing the formal result.

## Production rule

A positive result is **not production KEEP**. It authorizes the exact one-line
source candidate and source-vs-source validation against retained E6-1 production.

A negative result closes the slotted-record composition path and production stays
at E6-1.

## Canonical capacity rule

Report 10K / 100%-moving:

```text
controlled_work_frame_ms.p99 <= 33.33 ms
```

separately. E6-2 attribution cannot update `performance-frontier.md` by itself.

## Artifact rule

Preserve both Compact Evidence Package and Raw Forensic Package. Compact is the
default review artifact; Raw remains the final audit substrate.
