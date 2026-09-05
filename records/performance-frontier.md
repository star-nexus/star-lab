# STAR Performance Frontier

This record tracks validated movement of STAR's scalability/performance frontier. A result belongs here only when its experiment is reproducible, raw evidence is archived, integrity is verified, guards pass, and the exact STAR source state is recorded.

For admission criteria, see [`../PROTOCOL.md`](../PROTOCOL.md).

Different measurement planes are kept separate rather than mixed into one table.

## Historical whole-frame frontier

| Date | STAR source | Milestone tag | Scenario | Resident | Moving | Map | Phase | Fog | Avg frame | P99 | Avg FPS | Platform | Evidence |
|---|---|---|---|---:|---:|---|---|---|---:|---:|---:|---|---|
| 2026-09-02 | `a24482d438157aa23b371b6e34d49b1c04fec7f7` | `scale-v1-cull-vision-closed` | `TestMap-8K-scale-5000` | 5000 | 5000 | 91×91 | staggered | ON | **20.453 ms** | **24.290 ms** | **48.892** | Mac mini / macOS | [`capacity-16384.json`](../experiments/2026-09-vision-cache/results/capacity-16384.json) |

The first archived frontier point used whole-frame timing from the Vision-cache validation generation. It remains preserved as historical capability evidence and is not retroactively converted to the later `controlled_work` measurement plane.

Its canonical raw artifact is SHA256-verified in the Vision case:

```text
f9ea376497c8c0f39a343ec99965dc2b27800c509b2bef89eb578df108daaa32
```

At that milestone:

- realtime cyclic GC is deferred during the bounded latency-critical window;
- scale visibility-history retention is bounded;
- unit viewport culling has removed legacy per-candidate hot-loop work;
- Vision geometry-cache capacity no longer thrashes under the validated 5K workload.

The source milestone is preserved as:

```text
checkpoint/scale-cull-vision-closed
scale-v1-cull-vision-closed
```

and the annotated tag resolves to:

```text
a24482d438157aa23b371b6e34d49b1c04fec7f7
```

## Core 60Hz Stress Frontier

This plane uses the Phase-3 measurement semantics:

```text
primary metric = controlled_work_frame_ms.p99
60 Hz stress budget = 16.67 ms
platform input / present / wait remain separately observable
```

Auxiliary MiniMap dynamic unit dots are disabled for this Core profile through the explicit scale-only override. This does not change the normal Full Interactive default.

| Date | STAR source | Scenario | Resident | Moving | Density | Map | Phase | Fog | MiniMap units | Controlled avg | Controlled P99 | Disposition | Platform | Evidence |
|---|---|---|---:|---:|---:|---|---|---|---|---:|---:|---|---|---|
| 2026-09-06 | `c5dd895e242b46f193050d8212fcc45b625ad885` | `TestMap-8K-scale-5000` | 5000 | 1250 | 25% | 91×91 | staggered | ON | OFF | **11.974983 ms** | **13.666347 ms** | **CLEAR PASS** | Mac mini M4 / macOS | [`density-025-minimap-units-off.json`](../experiments/2026-09-minimap-unit-layer-tail/results/density-025-minimap-units-off.json) |
| 2026-09-06 | `c5dd895e242b46f193050d8212fcc45b625ad885` | `TestMap-8K-scale-5000` | 5000 | 2500 | 50% | 91×91 | staggered | ON | OFF | **14.190961 ms**¹ | **16.682029 ms**¹ | **BORDERLINE ACCEPT**² | Mac mini M4 / macOS | [`minimap-unit-layer-tail`](../experiments/2026-09-minimap-unit-layer-tail/) |

¹ 50% values are medians of three fresh-process run-level metrics. Run-level controlled P99 values are `16.68202856`, `16.13298628`, and `16.80107026 ms`; the median is `16.68202856 ms`. The run-level controlled-work average median is `14.190960876971609 ms`.

² The literal strict classification is a boundary fail because `16.68202856 > 16.67 ms`. Engineering disposition is intentionally `BORDERLINE ACCEPT`: the excess is about `0.012 ms / 0.07%`, the threshold is unchanged, and the exact density boundary was not binary-searched further.

### Why MiniMap units are OFF in the Core plane

The associated closed case demonstrated that the 15 Hz dynamic MiniMap unit layer used incremental invalidation but still performed a full O(Nresident) redraw of all 5000 unit dots on refresh, creating an approximately 4 ms periodic main-thread pulse. The controlled same-source A/B changed 25% moving from:

```text
MiniMap units ON   P99 16.808029 ms
MiniMap units OFF  P99 13.666347 ms
```

while preserving the authoritative movement/Vision/Fog workload.

The Core stress frontier therefore measures authoritative runtime capacity without letting this auxiliary presentation layer define the 60 Hz result. Full Interactive performance remains a separate concern.

## Frontier rules

A new row never replaces an older row. This is a progression record, not a single current-best leaderboard.

Preserve enough dimensions to distinguish:

```text
measurement plane
N_resident
N_moving
movement density
map size
state-transition density
staggered vs synchronized
Fog state
auxiliary presentation profile
camera / zoom
hardware
source commit/tag
canonical raw artifact + checksum
```

Do not compare a whole-frame historical row numerically against a `controlled_work` row as if they used identical timing semantics.

A future 10K or 20K point is not directly comparable to the 5K point unless workload and measurement-plane differences are explicit.
