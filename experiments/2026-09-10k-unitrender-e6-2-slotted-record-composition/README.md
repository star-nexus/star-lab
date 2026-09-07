# Phase 5 10K UnitRender E6-2 — Slotted Spatial Record Composition

**Status:** DRAFT / PREREGISTERED — measurement pending  
**STAR repository:** `star-nexus/star`  
**Retained E6-1 production:** `e7ba18b31870577110b591104ef8fa7b4713e43c`  
**Experiment branch:** `experiment/phase5-unitrender-e6-2-slotted-composition`  
**Frozen tooling commit:** `a524e610bdfce7eab37fee3fcf4cff69dac89ab5`

## Question

E5-1 previously found a small but repeatable Cull improvement from making
`UnitSpatialRecord` a slotted frozen dataclass (~0.090 ms @50%, ~0.113 ms @100%).
That result was correctly rejected as a root solution because it recovered only a
small fraction of the then-unexplained record first-touch cost.

E6-1 has now removed the dominant world-coordinate payload first-touch mechanism
and is retained production. E6-2 asks a new composition question:

> Does the old slotted-record signal remain independently material when composed
> with the retained E6-1 bounded geometry reuse?

This does **not** reopen E5 root-cause attribution.

## Treatment isolation

Both control and treatment run exact retained E6-1 source:

```text
e7ba18b31870577110b591104ef8fa7b4713e43c
```

Treatment installs only the source-equivalent representation change before world
creation:

```python
@dataclass(frozen=True, slots=True)
class UnitSpatialRecord:
    ...same fields...
```

Preserved:

```text
E6-1 bounded geometry ownership
fresh UnitSpatialRecord identity
record fields and values
Cull algorithm
spatial containers
HexPosition authority
movement / Vision / Fog semantics
```

## Formal run

```bash
bash tools/run_phase5_unitrender_e6_2.sh
```

Order:

```text
A50 -> B50 -> B100 -> A100
```

Workload is the existing canonical Phase-5 10K workload: Fog ON, staggered
movement, seed 42, route preparation outside measurement, realtime_defer,
production animation/commits, execution pathfinding OFF, MiniMap dynamic units
OFF, uncapped render, late steady-state sample window.

## Preregistered candidate-justification gates

Workload equivalence:

```text
all driver guards PASS
position commits/s within ±2%
Vision changed/s within ±2%
Fog delta tiles/s within ±2%
```

Composition materiality / no-tradeoff:

```text
Cull avg saving >= 0.05 ms @50%
Cull avg saving >= 0.07 ms @100%
UnitRender avg regression <= 1%
controlled-work avg regression <= 1%
Animation avg regression <= 2%
```

Possible decisions:

```text
SLOTTED_RECORD_COMPOSITION_CANDIDATE_JUSTIFIED
SLOTTED_RECORD_COMPOSITION_NOT_MATERIAL
```

A positive decision is **not** production KEEP. It authorizes the trivial
one-line source candidate and exact source-vs-source validation.

## Canonical 30 Hz diagnostic

At 10K / 100% moving:

```text
controlled_work_frame_ms.p99 <= 33.33 ms
```

is reported separately. E6-2 attribution alone cannot update the Performance
Frontier.

## Two-tier artifacts

Canonical runner emits:

```text
<run-id>-compact.zip
<run-id>-raw.zip
```

Compact is default review evidence; Raw remains the authoritative forensic base.
