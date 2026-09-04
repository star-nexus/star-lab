# STAR Lab Experiment Index

This directory is the STAR / StarBench engineering **case library**: reproducible problems, investigation evidence, fixes, decisions, and validated performance milestones.

Read [`../PROTOCOL.md`](../PROTOCOL.md) before adding or modifying a case.

Historical coverage of the 2026 performance campaign is tracked in [`../records/historical-performance-archive-audit-2026-09.md`](../records/historical-performance-archive-audit-2026-09.md).

## Archived cases

| Experiment | Status | Problem / question | Main conclusion | Evidence state |
|---|---|---|---|---|
| [`2026-09-dynamic-world-scaling`](2026-09-dynamic-world-scaling/) | **ARCHIVED — complete formal archive** | How did the controlled 5K Dynamic World workload evolve into the scale methodology used by later investigations? | V1/V2/V2.1 preserve the progression from formal density control through incremental Fog to rare-tail attribution. | 14 raw JSON runs + SHA256; exact source HEADs recovered for V1 `0f0d0a2`, V2 `571ea207`, V2.1 `916d88dc`. |
| [`2026-09-realtime-gc`](2026-09-realtime-gc/) | **CLOSED — complete formal archive** | Why do rare UnitRender frames jump to ~50 ms? | Automatic CPython Gen2 GC ran inside the timed render section; bounded `realtime_defer` moved cyclic-GC maintenance outside the critical window. | AUTO/defer raw JSON recovered and SHA256-verified. |
| [`2026-09-memory-retention`](2026-09-memory-retention/) | **CLOSED — raw evidence complete** | Why do RSS/tracked objects rise although full safe GC collects 0 and ECS/Vision caches are bounded? | Runtime retained historical visibility telemetry (up to 100 records/unit); scale/window now keeps the latest transition only. | Pre-fix 600s + post-fix 120s raw JSON recovered and SHA256-verified. Exact checkout SHA for the recovered post-fix run is not encoded and is documented rather than guessed. |
| [`2026-09-spatial-cull`](2026-09-spatial-cull/) | **CLOSED — canonical cross-case evidence** | Why is `unit_visible_cull` still ~3.53 ms although spatial candidate discovery already exists? | Residual per-candidate ECS/singleton/coordinate work and low-zoom overscan were the real costs; ~3.53 -> ~1.33 ms. | No duplicated local raw; before references GC A/B raw, after references Vision 16384 raw. |
| [`2026-09-vision-cache`](2026-09-vision-cache/) | **CLOSED — complete formal archive** | What bounded geometry-cache capacity avoids memory growth without thrashing? | 4096 thrashes; 8192 is measured minimum sufficient; 16384 is the scale/window operational default with headroom. | Four original formal JSON runs + SHA256. |
| [`2026-09-render-engine-attribution`](2026-09-render-engine-attribution/) | **CLOSED — complete formal archive** | Where does the ~5.5 ms RenderEngine queue-drain time actually go? | Queue submission is ~98% of RenderEngine; Fog + Terrain presentation causally explain ~4.41 ms, about 81%, while Python queue packing is only ~0.2 ms. | Queue/submit/pixel/causal-ablation raw JSON families + SHA256; exact attribution commits recorded. |
| [`2026-09-fog-presentation-bounding`](2026-09-fog-presentation-bounding/) | **CLOSED — complete formal archive** | Why is Fog still expensive after semantic updates became incremental? | The steady-state path still submitted 3,144,640 SRCALPHA pixels/frame; bounding only final presentation cut submitted pixels by 61.06% and RenderEngine by ~1.99 ms. | Three fixed-run JSON artifacts + SHA256; canonical pre-fix baseline cross-referenced from RenderEngine attribution; 43-test regression validation. |
| [`2026-09-terrain-presentation`](2026-09-terrain-presentation/) | **CLOSED — complete formal archive** | Why does Terrain remain a large scalar presentation cost after Fog bounding? | A-B-C-D attribution isolates Pygame/SDL `SRCALPHA` Surface semantics as the dominant cost; a compact opaque RGB presentation cache reduces RenderEngine by ~0.889 ms in same-commit fixed-camera A/B. | Diagnostics + A-B-C-D + fixed-camera + camera-stress raw JSON, including invalid-but-informative first opaque runs, all checksum-covered. |
| [`2026-09-camera-fog-full-rebuild`](2026-09-camera-fog-full-rebuild/) | **CLOSED — complete formal archive** | Why does smooth camera motion with Fog enabled trigger expensive full rebuilds, and which work can be removed without changing pixels? | Geometry-key-visible camera changes legitimately require rebuilds, but repeated Python geometry and transparent-tile work were avoidable; canonical short-pan Fog tile loop moved from ~27.918 to 13.983 ms/rebuild as a cross-commit supportive trajectory, with final residual `EXPLAINED-WORKLOAD-BOUND`. | 44 local raw JSON artifacts + SHA256, four same-commit optimization A/B stages, three structural negative-result lines, correctness matrices, uninstrumented closeout, immutable validated tag. |
| [`2026-09-macos-sdl-event-pump-stall`](2026-09-macos-sdl-event-pump-stall/) | **CLOSED — known platform limitation / historical backfill** | Why do rare macOS interactive frames stall for 30–70+ ms? | The tail is inside SDL/Cocoa `pygame.event.pump()`, not Python queue retrieval or STAR input dispatch; later capped-60 movement validation reproduced the same signature even with `text_input=False`. | Exact attribution/mitigation SHAs + contemporaneous closeout summary + multiple 2026-09-04 replications; original historical full raw artifact not recovered. |
| [`2026-09-unit-movement-continuity`](2026-09-unit-movement-continuity/) | **CLOSED — investigation complete; production integration pending** | Was the visible hitch at Fog boundaries caused by Fog reveal work? | No. Fog ON/OFF A/B rejected Fog causality; STAR had movement segment time loss plus renderer animation dead zones. Both were fixed, residual micro-judder was accepted, and rare large tails cross-reference the macOS/SDL case. | Exact problem/fix SHAs, controlled human A/B, profiler excerpts, regression-test source and uploaded-log SHA256 identities; full raw logs and pytest transcript are not archived. |

## Reading order for a case

```text
README.md
  -> reproduce / understand the case

manifest.yaml
  -> exact source identity, workload, artifact references

analysis.md
  -> observation -> hypotheses -> evidence -> root cause

decision.md
  -> accepted engineering choice and revisit conditions

results/
  -> canonical raw evidence when owned by this case

artifacts/SHA256SUMS
  -> byte-integrity verification for local raw artifacts
```

## Evidence ownership

One raw artifact has one canonical archive location. If a measurement supports several cases, keep the raw file once and cross-reference it elsewhere.

Example:

```text
realtime-gc/results/density-100-realtime-gc.json
        -> GC policy A/B evidence
        -> also pre-fix Spatial Cull baseline

vision-cache/results/capacity-16384.json
        -> Vision cache ablation evidence
        -> also post-fix Spatial Cull evidence
```

## Historical backfill rule

Some investigations predate STAR Lab. Preserve evidence levels explicitly:

```text
1. exact source provenance confirmed from Git or a contemporaneous primary run record
2. validated numeric summary preserved
3. original raw artifact recovered
4. checksum/integrity verified
```

Never fabricate a higher evidence level from a lower one. A recovered artifact may have complete raw evidence while still carrying an explicit provenance limitation if the artifact itself did not record its exact source SHA.

For source identity recovered from an external run-handoff record, archive the basis explicitly: the record must identify the active HEAD, and Git inspection should independently match the implementation/diagnostic generation represented by the raw artifacts.

## Next performance work

The Camera->Fog full-rebuild case and the unit-driven Fog/movement-continuity investigation are closed.

For future interactive hitches, classify the slow frame before opening a case:

```text
input_event_pump dominated
  -> known macOS/SDL platform-tail case; do not reopen without new attribution

movement / Fog / Vision / Terrain / RenderEngine dominated
  -> open a new subsystem case only when the measured signature is materially different
```

The next planned engineering phase is performance measurement/regression infrastructure, followed by system-scale frontier work across ENV / Hub / Protocol / Agent / rendering resource trade-offs.
