# Historical Performance Archive Coverage Audit — 2026-09-04

**Status:** COMPLETE  
**Scope:** the 2026-08/09 STAR performance/scalability campaign preserved by retained performance tags and the current STAR Lab case library.

## 1. Purpose

This audit verifies that deleting historical `perf/*`, `checkpoint/*`, and integration branches did not make durable engineering knowledge depend on those branches.

The required invariant is:

```text
historical experiment conclusion
        -> canonical STAR Lab case or explicit absorbed mapping
        -> exact STAR source SHA / immutable tag
        -> raw evidence or explicitly documented evidence limitation
        -> discoverable from the STAR Lab index
```

A historical branch may be deleted once this chain exists. A branch must not be the only place where a durable conclusion can be discovered.

## 2. STAR source refs audited

The audit inspected the retained performance milestones that cover the production campaign:

```text
perf-5000-resident-baseline
scale-v1-cull-vision-closed
perf-2026-09-camera-fog-checkpoint-session2
perf-2026-09-camera-fog-full-rebuild-closed
perf-2026-09-window-runtime-premerge
perf-2026-09-window-runtime-production
```

The audit focused on tracked experimental documentation, experiment/control tooling, durable performance conclusions, and their STAR Lab destinations. Normal product/user documentation was not treated as experimental archive material.

## 3. Executive result

```text
canonical STAR Lab performance cases after audit     10
true historical orphan cases found                    1
true orphan cases backfilled                          1
existing cases missing from experiment index          3
index discoverability gaps fixed                      3
remaining known orphan durable conclusions            0
```

The one true orphan was the macOS / SDL event-pump tail-latency finding. It survived in historical STAR `docs/` and source commits but had no STAR Lab case. It is now archived as:

```text
experiments/2026-09-macos-sdl-event-pump-stall/
```

Three other cases were already fully archived but were missing from `experiments/README.md`:

```text
2026-09-render-engine-attribution
2026-09-fog-presentation-bounding
2026-09-terrain-presentation
```

Those were discoverability defects, not evidence-loss defects. The index is corrected by the same audit commit.

## 4. Historical experimental-document coverage

The persistent experiment-oriented Markdown family visible at `scale-v1-cull-vision-closed` and later camera-Fog checkpoints is:

| Historical STAR artifact | Durable meaning | Canonical STAR Lab destination | Audit status |
|---|---|---|---|
| `docs/dynamic-world-scalability.md` | 5K Dynamic World methodology/evolution | `experiments/2026-09-dynamic-world-scaling/` | covered |
| `docs/scale-test-harness.md` | orthogonal scale control plane; planning vs execution; density; synchronized vs staggered; Fog/Vision guards | `experiments/2026-09-dynamic-world-scaling/` | absorbed; no duplicate case needed |
| `docs/realtime-gc-policy.md` | bounded realtime Gen2 GC policy and tail attribution | `experiments/2026-09-realtime-gc/` | covered |
| `docs/vision-geometry-cache-ablation.md` | bounded Vision cache capacity A/B and 16,384 default rationale | `experiments/2026-09-vision-cache/` | covered |
| `docs/macos-sdl-event-pump-stall.md` | rare macOS SDL/Cocoa pump tail and mitigation | `experiments/2026-09-macos-sdl-event-pump-stall/` | backfilled during audit |

`scale-test-harness.md` does not need a second archive package because the Dynamic World case already preserves the exact source-bound V1/V2/V2.1 methodology, startup/driver shape, density controls, temporal-phase distinction, guards, and 14 canonical raw JSON artifacts.

## 5. Historical experiment-tool coverage

The source-side tools were checked for durable conclusions that might exist only in scripts.

### Scale family

```text
tools/generate_scale_map.py
tools/scale_driver.py
```

Canonical destination:

```text
2026-09-dynamic-world-scaling
```

`scale_driver.py` is also referenced as a reproduction dependency by downstream GC, Cull, Vision, RenderEngine, Fog-presentation, and Terrain cases. It is a historical experiment tool, not a separate engineering conclusion.

```text
tools/scale_gc_soak.py
```

Canonical destination:

```text
2026-09-memory-retention
```

with realtime-GC context preserved separately in `2026-09-realtime-gc`.

### Camera / Fog family

The camera-Fog closeout source contains tools including:

```text
fog_camera_attribution.py
fog_camera_closeout.py
fog_pan_translation_feasibility.py
fog_phase_raster_feasibility.py
fog_directed_phase_generalization.py
fog_content_bounds_feasibility.py
fog_presentation_bounds_feasibility.py
```

Their durable attribution, accepted local optimizations, correctness guards, and rejected structural designs are preserved in:

```text
2026-09-camera-fog-full-rebuild
2026-09-fog-presentation-bounding
```

The Camera-Fog manifest explicitly records the attribution commits, four accepted local optimization stages, the rejected translation/phase/global-bounds designs, and the owned raw artifacts. No tool-only durable conclusion remains.

### Terrain family

```text
tools/terrain_camera_stress.py
```

Canonical destination:

```text
2026-09-terrain-presentation
```

The Terrain case preserves the A-B-C-D attribution, invalid-but-informative first opaque experiment, same-commit production A/B, camera-stress validation, and checksummed raw evidence.

### RenderEngine attribution

The queue-drain / presentation attribution was driven primarily by profiler instrumentation and controlled environment-variable ablations rather than a unique external driver. Its canonical evidence is fully owned by:

```text
2026-09-render-engine-attribution
```

including queue-breakdown, submit-breakdown, pixel-diagnostic, and causal-ablation raw artifacts.

## 6. Canonical STAR Lab performance case inventory

After the audit, the campaign has ten canonical cases:

| Case | Archive role | State |
|---|---|---|
| `2026-09-dynamic-world-scaling` | scale methodology / source-bound workload evolution | ARCHIVED |
| `2026-09-realtime-gc` | Gen2 realtime tail | CLOSED |
| `2026-09-memory-retention` | visibility-history retention | CLOSED |
| `2026-09-spatial-cull` | residual candidate hot loop after spatial prefilter | CLOSED |
| `2026-09-vision-cache` | geometry-cache working-set capacity | CLOSED |
| `2026-09-render-engine-attribution` | queue-drain and Surface-presentation attribution | CLOSED |
| `2026-09-fog-presentation-bounding` | full-window Fog presentation volume | CLOSED |
| `2026-09-terrain-presentation` | SRCALPHA Terrain presentation path | CLOSED |
| `2026-09-camera-fog-full-rebuild` | camera-induced Fog full-rebuild attribution/optimization | CLOSED |
| `2026-09-macos-sdl-event-pump-stall` | macOS SDL/Cocoa event-pump platform tail | CLOSED / known platform limitation |

## 7. Product documentation correctly excluded from STAR Lab

The audit intentionally does **not** migrate normal STAR documentation such as:

```text
agent-protocol.md
hub-envelope.md
observation-affordance.md
architecture.jpg
rotk.jpg
star-runtime-architecture.en.html
starbench_rotk.gif
```

These are product/benchmark/user documentation rather than engineering experiment evidence.

`docs/window-runtime-rendering.md` is also correctly retained in production `main`: it describes the final product runtime behavior and the `--uncapped` measurement clock, not the discarded experiment history.

This confirms the intended repository boundary:

```text
star/main    -> final runtime + user/product documentation
star-lab     -> reproducible experiment evidence + decisions
STAR tags    -> immutable exact historical source states
```

## 8. Evidence limitations that are documented, not hidden

The audit found no unresolved archive ownership gap, but several cases deliberately retain explicit evidence limitations:

- `2026-09-macos-sdl-event-pump-stall`: original full raw profiler artifact for the historical 62.75 ms frame was not recovered; exact source commits, contemporaneous summary, and a later production replication are preserved instead.
- `2026-09-memory-retention`: the recovered post-fix 120 s raw JSON does not encode its exact checkout SHA; the archive records the proven source bounds and does not guess a SHA.
- RenderEngine / Fog presentation / Terrain presentation did not receive dedicated immutable milestone tags at the time; their exact problem/measurement/fix/validation SHAs and checksummed evidence are recorded in their manifests.

These are provenance-quality notes, not reasons to keep deleted working branches alive.

## 9. Production-cleanliness check

The historical `scale-v1-cull-vision-closed` / camera-Fog states contain the experiment documentation and control tools expected from an active performance campaign.

By `perf-2026-09-window-runtime-premerge`, the experimental Markdown family had been removed from production and the tracked `docs/` tree contained product documentation plus:

```text
window-runtime-rendering.md
```

This is the intended productionization result. Experimental evidence is not required in `star/main` for later reproduction because STAR Lab + exact tags own that responsibility.

## 10. Future branch-cleanup gate

Before deleting a future performance/research branch, run this checklist:

```text
1. enumerate new experiment-oriented docs and control tools since the last stable tag
2. identify every durable conclusion / rejected design / platform limitation
3. map each to an existing STAR Lab case or create a new package
4. ensure exact source SHA(s) and validated tag(s), when available, are recorded
5. archive canonical raw evidence or state the evidence limitation explicitly
6. verify checksum coverage for local formal artifacts
7. ensure the case is discoverable from experiments/README.md
8. only then delete temporary perf/checkpoint branches
```

A historical script does not automatically require its own case. The unit of archival ownership is a **durable engineering conclusion**, not a filename.

## 11. Audit conclusion

The recent branch cleanup is safe from an engineering-memory perspective.

```text
historical perf branches       disposable working refs
retained performance tags      exact source provenance
STAR Lab cases                 durable evidence / decisions
STAR main                      clean production runtime
```

No currently known durable conclusion from the audited 2026 performance campaign depends solely on a deleted branch.
