# STAR Performance Frontier

This record tracks validated movement of STAR's scalability/performance frontier. A result belongs here only when its experiment is reproducible, raw evidence is archived, integrity is verified, guards pass, and the exact STAR source state is recorded.

For admission criteria, see [`../PROTOCOL.md`](../PROTOCOL.md).

Different measurement planes are kept separate rather than mixed into one table.

## Native rendered Agent closed-loop frontier — R4e / API18

Validated2026-09-29. Measurement `5147e4d8e0c33c997bd86960d87fa4b5b3ca90c5`; final docs `7e145d169433695cd4957e186a6b2fda06813c26`, annotated `rust-kernel-r4e-2026-09-29`. [Evidence and checksums](../experiments/2026-09-rust-1000-agent-validation/README.md).

Mac mini M4/16GiB, CPython3.13.12/release API18, Cocoa2480×1239, canonical120×120/FogON, minimap Units OFF, finite-run GC deferred, Chrome open. 5000 living Units/1000 synthetic Agents, one native thread,8ms Agent budget; fixed30Hz world,30±5s wall-clock post-action thinking truncated15–45s, initial offsets0–30s. PerUnit move/attack/wait50/25/25, illegalwait. No thinking-period polling or Protocol/Hub/realLLM. Full-frame work includes Agent service/world/Python display/present, excludes pacing wait. Three independent30s warmups+300s measurements; all9000frames per run retained.

| Run | Frame P99 ms | Observation response P99 ms | Action queue P99 ms | Hz | Alive / peak moving |
|---|---:|---:|---:|---:|---:|
| rust-300-r1 | 29.800 | 45.872 | 35.293 | 30.0 | 5000 / 171 |
| rust-300-r2 | 29.275 | 47.783 | 35.601 | 30.0 | 5000 / 177 |
| rust-300-r3 | 29.470 | 44.798 | 34.744 | 30.0 | 5000 / 173 |

All guards passed, including observation and action queues, survival, clock, backlog and completed-loop fraction. Maximum single frames37.361/35.370/39.215ms; whole-window P99 admission does not guarantee every frame or every short window. Peak movers171–177, not5000. All evidence bound to this workload; high-density combat and5000-Agent expansion are not accepted by this row. Original and normalized Python short negative controls remain archived; single live runs do not establish a universal language speedup. Previous R4c row remains independently valid for its source/profile.

## Native rendered Agent closed-loop frontier — R4c

Validated canonical window profile, 2026-09-25. Build/measurement `e85e3067b1d2aed5cf08be9dbe35b1deed91dba1`; final docs `b05c1465e551072bced220ae12c2474ec7e81e85`, annotated `rust-kernel-r4c-2026-09-25`. [Evidence, raw/compact packages and integrity](../experiments/2026-09-rust-rendered-loop/README.md).

Mac mini M4, CPython3.13/release native API17, Cocoa2480×1243, canonical120×120/FogON, minimap Unit layer OFF, finite-run GC deferred, Chrome open. 5000 living Units /1000 synthetic Agents, selected observations, 30Hz fixed dt; post-action think truncated normal30±5s within15–45s, first requests uniform0–30s. No Hub/realLLM. One native thread, Lab event budget8ms. Whole-frame work includes admission/world/display/render/present; excludes active pacing wait. Three independent30s warmups+300s windows; no removed slow frames.

| Repeat | Frame P99 ms | Observation response P99 ms | Action queue P99 ms | Hz | Living | Peak moving |
|---|---:|---:|---:|---:|---:|---:|
| 1 |32.478751|85.989951|94.090125|30.0|5000|171|
| 2 |32.613375|82.840035|93.040334|30.0|5000|173|
| 3 |32.405167|87.093479|94.272292|30.0|5000|178|

All frame, frequency, observation/action queues, response, backlog, survival and offered-load guards passed independently. Some30s subwindows exceed33.33ms; this is full300s acceptance, not a no-jitter promise. The prior valid R4b300s failure35.561ms remains archived. Fixed-input encoding A/B is distinct from live runs whose admission timing differs. This does not establish5000Agents,5000simultaneouslymoving,10000Units,high-contact/fullminimap or cross-platform capacity; defaults remain Python/1thread while migration completes.

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

## Core 30Hz Canonical Frontier

Phase 5 uses the same controlled-work timing plane but evaluates authoritative 10K Core Runtime capacity against the canonical 30 Hz budget:

```text
primary metric = controlled_work_frame_ms.p99
30 Hz canonical budget = 33.33 ms
Fog = ON
MiniMap dynamic units = OFF
phase = staggered
GC = realtime_defer
```

Optimization A (`MovementSystem` lookup elimination) established the first archived 10K canonical pass:

| Date | STAR source | Scenario | Resident | Moving | Density | Map | Controlled avg | Controlled P99 | 30Hz disposition | Evidence |
|---|---|---|---:|---:|---:|---|---:|---:|---|---|
| 2026-09-06 | `b9e0bb92b546b3283cb5c1d30a9a510d0c006ec2` | `chibi-144k-scale-10000` | 10000 | 5000 | 50% | 120×120 | **25.964 ms** | **29.447 ms** | **PASS** | [`50% point`](../experiments/2026-09-10k-movement-system-lookup/results/raw/phase5-10k-core/chibi-144k-scale-10000/20260906-041532/50pct-moving/point.json) |
| 2026-09-06 | `b9e0bb92b546b3283cb5c1d30a9a510d0c006ec2` | `chibi-144k-scale-10000` | 10000 | 10000 | 100% | 120×120 | **34.180 ms** | **38.537 ms** | **FAIL — current capacity boundary** | [`100% point`](../experiments/2026-09-10k-movement-system-lookup/results/raw/phase5-10k-core/chibi-144k-scale-10000/20260906-041532/100pct-moving/point.json) |

The 50% point is the validated 10K frontier pass. The 100% point is retained beside it because it defines the archived same-source capacity boundary and the remaining optimization target.

Optimization B (`position-specialized spatial-index movement update`) is **CAUSALLY CONFIRMED / KEEP / CLOSED** and is part of the retained production baseline. Its same-session ABBA closeout saves approximately `0.5-0.8 us` of Animation CPU per authoritative position commit while preserving position-commit and Vision-dirty rates. B does **not** add a new frontier row: the formal closeout still leaves the 10K / 100%-moving point above the 33.33 ms P99 gate. The accepted implementation was restored at `4218b5368fbe2815b8512384e2c18b0af443ebfa`; canonical evidence is archived in [`2026-09-10k-spatial-index-move-specialization`](../experiments/2026-09-10k-spatial-index-move-specialization/).

Optimization C1 (`Vision geometry cache-hit terrain bypass`) is also **CAUSALLY CONFIRMED / KEEP / CLOSED** and remains in the same retained `4218b536...` runtime. Same-session ABBA shows Vision avg `2.487 -> 2.158 ms` at 50% moving and `5.629 -> 4.760 ms` at 100% moving, corresponding to `1.079 us` and `1.025 us` saved per visibility call while authoritative movement/Vision rates and geometry hit rate remain effectively unchanged. C1 likewise does **not** add a new frontier row: the 100%-moving closeout P99 remains above 33.33 ms. Canonical attribution + closeout evidence is archived in [`2026-09-10k-vision-geometry-hit-path`](../experiments/2026-09-10k-vision-geometry-hit-path/).

## Sustained Core 30Hz — 10K / 100% moving — 2026-09-08

Runtime `9581084835633e10d80aac849925939bc59b9138`, published annotated tag
`scale-10k-100pct-30hz-sustained-e8`. E8-1/2/3/4 reduce repeated texture,
UI roster, component-row and movement-reference work. Single-thread Python Core;
production animation, position commits and Vision remain immediate.

This row uses **complete admitted sustained traces** with fixed initial10s
excluded, while the production profiler itself remains5s/4096. It is distinct
from a last-5s snapshot and is not an every-short-window guarantee. Same
controlled-work33.33ms threshold; every other admitted sample, including slow
clusters, is retained. Mac mini M4/16GB, macOS26.5.2, Python3.13.12, pygame2.6.1,
visible2480x1261, board120x120, 10000 residents/movers, seeds42, staggered12-step
preplanned routes, Fog ON, execution pathfinding OFF, MiniMap units OFF,
realtime_defer, uncapped and input blocked. Chrome remains open.

| Complete trace | Seconds | Frames | Controlled avg ms | Controlled P99 ms | Gate |
| --- | ---: | ---: | ---: | ---: | --- |
| Continuous | 305.447501 | 10240 | 28.220838 | **32.430227** | PASS |
| Repeat 1 | 65.285074 | 2389 | 25.784004 | **28.984507** | PASS |
| Repeat 2 | 65.301032 | 2342 | 26.310417 | **30.026299** | PASS |
| Repeat 3 | 65.271297 | 2336 | 26.370550 | **29.162605** | PASS |

All workload/trace guards and all16 full30s blocks pass (worst33.248388ms).
Position/Vision rates remain~20000/s. 505 tests pass. Integrity verified:23 raw
archives plus fixture,50 checksummed evidence files;8 gate replays match exactly,
including the rejected E8-3 300s result. Evidence:
[`E8 case`](../experiments/2026-09-10k-e8-volume/),
[`long trace compact`](../experiments/2026-09-10k-e8-volume/results/20260908-083745-e8-4-gate300-compact.json),
[`repeat compact`](../experiments/2026-09-10k-e8-volume/results/20260908-143157-e8-4-gate60-compact.json).

Limits: the long trace has64 individual misses (.625%), longest3; its final
rolling5s P99 is34.745ms and frame-body P99 is34.033ms. Repeat2's final5s P99 is
37.231ms. Those counterexamples remain archived. Do not infer every-frame,
every-5s-window, full interactive,60Hz or10K online-Agent passage. Long-run drift
and occasional shared subsystem slow clusters remain revisit conditions; no
specific cluster has been causally assigned to Chrome. P0 publication update: the source is integrated on STAR main, the validated tag
is published unchanged and the Lab case is pushed. See
[P0 closeout](../archives/2026-09-10k-p0/closeout.md). This records publication
and does not create a new timing frontier row.

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
