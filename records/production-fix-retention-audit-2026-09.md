# Production Fix Retention Audit — 2026-09

**Status:** ACTIVE / FIRST-PASS COMPLETE  
**Scope:** production retention of accepted decisions from the 2026-08/09 STAR performance campaign after experiment-branch cleanup and window-runtime productionization.

## 1. Why this audit exists

The earlier historical archive audit proved an engineering-memory invariant:

```text
historical conclusion
  -> STAR Lab case
  -> exact source SHA / tag
  -> raw evidence or documented limitation
  -> discoverable archive entry
```

That was necessary, but it did **not** prove a second invariant:

```text
accepted engineering decision
  -> retained production behavior when applicable
  -> retained regression protection when applicable
  -> explicit classification when intentionally experiment-only
```

Phase 4 exposed this missing layer. Reintroducing the scale harness without first rehydrating the CLOSED realtime-GC decision reproduced the historical UnitRender/Gen2 tail signature. The Vision-cache review then found a different class: the accepted 16,384 window default survived productionization, but its dedicated regression test did not.

This record adds a production-retention audit to the archive discipline. It does not reopen CLOSED performance cases.

## 2. Productionization boundary that caused the ambiguity

The scalable-window production PR explicitly retained production runtime improvements while excluding:

```text
experimental harnesses
attribution tooling
raw results
A/B selectors
rejected implementations
```

That is the correct default for a clean `star/main`, but it is insufficient by itself. A piece of code must be classified by the **accepted decision it implements**, not only by whether it originated inside an experiment branch.

In particular:

- a temporary probe may be deleted;
- a rejected implementation should be deleted;
- a reproduction-only driver may live only in STAR Lab/source tags;
- an accepted production fast path must survive;
- an accepted formal-measurement invariant must either survive with the measurement capability or be explicitly rehydrated whenever that capability returns;
- a retained behavior should retain a regression test or structural contract when practical.

## 3. First-pass findings

| Case | Accepted durable behavior | Current retention | Regression protection | Audit result |
|---|---|---|---|---|
| Dynamic World Scaling | planning/execution separation; common route/plan pool; nested density; staggered/synchronized; fixed Fog/camera; formal guarded epoch | historical harness intentionally removed; Phase-4 production-path harness rebuilt | Phase-4 scale-harness structural tests and driver guards now present | **Experiment tooling intentionally removed; methodology rehydration was initially incomplete** |
| Realtime GC | bounded `realtime_defer` for explicitly selected latency-critical scale/realtime measurement windows | missing from production tree after cleanup; restored on `perf/system-scale-frontier` from historical implementation | restored `test_realtime_gc_policy.py` plus profile/start/window guards | **REAL RETENTION GAP — repaired in Phase 4** |
| Memory Retention | window visibility history retains only bounded latest state (`VISIBILITY_HISTORY_LIMIT = 1`) | retained in `window_statistics_system.py` | retained window statistics/history tests | **RETAINED** |
| Spatial Cull | visible-unit path uses spatial candidates rather than resident-wide scan | retained in window renderer | `test_window_unit_render_spatial_cull.py` included in structural performance contracts | **RETAINED** |
| Vision Geometry Cache | 4096 rejected for 5K window workload; 8192 minimum sufficient; 16384 bounded operational window default | retained in `window_vision_system.py` as explicit 16384 default | original scale-adapter default test was removed; new `test_window_vision_cache_config.py` added in Phase 4 and included in structural contracts | **BEHAVIOR RETAINED / TEST RETENTION GAP — repaired in Phase 4** |
| RenderEngine Attribution | preserve ordered batching; consecutive plain blits use batch submission | retained in production render engine | render batching structural test retained | **RETAINED** |
| Fog Presentation Bounding | incremental Fog patches and bounded presentation rectangle | retained in `fog_surface_presenter.py` | pixel-equivalence / bounded-presentation tests retained; incremental contract included in structural suite | **RETAINED** |
| Terrain Presentation | completed terrain presentation uses opaque compact path rather than repeated SRCALPHA composition | retained in window terrain presentation | opaque-presentation cache test retained in structural suite | **RETAINED** |
| Camera → Fog Full Rebuild | cache camera-independent tile world corners; skip fully visible tiles; canonical rounded transform; conservative Fog-content bounds | retained in `fog_surface_presenter.py` | full-rebuild pixel/camera/geometry and presentation-bound tests retained | **RETAINED** |
| macOS SDL Event Pump | text input disabled; platform-input attribution kept separate; no unsafe pump-skipping redesign | retained in current input/profiler semantics | covered by measurement semantics and platform-input instrumentation; platform limitation remains CLOSED | **RETAINED** |
| Unit Movement Continuity | preserve segment overshoot/residual progress; remove animation boundary dead zones | residual-progress implementation retained in `animation_system.py`; production render path remains continuous | dedicated retained regression coverage should be checked again at Phase-4 closeout | **IMPLEMENTATION RETAINED / TEST COVERAGE FOLLOW-UP** |

## 4. Vision-cache clarification

The canonical Vision-cache case records a **capacity cliff**, not a smooth linear capacity response:

```text
4096
  hit rate      72.39%
  evictions     19,010
  Vision self   2.9246 ms

8192
  hit rate      99.14%
  evictions     0
  Vision self   1.2260 ms

16384
  hit rate      99.14%
  evictions     0
  Vision self   1.2241 ms
```

Thus the important nonlinearity is:

```text
capacity below working set
  -> sustained LRU thrash
  -> repeated LOS recomputation
  -> latency cliff

capacity >= working set
  -> no sustained eviction
  -> performance plateau
```

The current Phase-4 5K profile is **not** showing this regression. Window Vision is running with capacity 16,384, final cache occupancy around 5.6K, and zero evictions.

The current 25%-density `VisionSystem` percentile shape has another known component: indexed window worlds intentionally run a low-rate semantic safety audit every 60 frames. That periodic `vision_audit_scan` can leave Vision P50/P95 small while lifting P99. The same ~2 ms audit already appears in the historical accepted 16,384-capacity result, so this is not evidence that the cache fix disappeared.

## 5. What actually went wrong in Phase 4 startup

The failure mode was procedural:

```text
STAR Lab preserved the CLOSED realtime-GC conclusion
        +
production cleanup removed experiment/control infrastructure
        +
Phase 4 rebuilt the scale harness from production systems
        +
accepted GC measurement condition was not rehydrated initially
        ->
AUTO Gen2 pause reappeared inside UnitRender scope
        ->
old CLOSED tail looked like a new UnitRender regression
```

Once `realtime_defer` was restored, the 25% density UnitRender distribution changed from approximately:

```text
AUTO:
  P99 ~15.9 ms
  max ~26.6 ms

realtime_defer:
  P99 ~4.37 ms
  max ~4.43 ms
```

This validates the old case and demonstrates why production-fix retention must be audited separately from evidence retention.

## 6. New cleanup / productionization gate

Before deleting a future performance branch or stripping experiment code, perform **both** audits.

### A. Evidence retention

```text
1. durable conclusion has a canonical STAR Lab owner
2. exact source SHA/tag recorded
3. raw evidence preserved or limitation stated
4. rejected hypotheses/designs preserved
5. case discoverable from the index
```

### B. Production retention

For every accepted decision:

```text
1. classify it as:
   - production behavior
   - formal measurement invariant
   - experiment-only reproduction facility
   - rejected / disposable

2. if production behavior:
   verify exact behavior exists in the productionized tree

3. if formal measurement invariant:
   retain it with the measurement capability, or record an explicit
   rehydration dependency that must be restored before future formal runs

4. retain or migrate a regression test / structural contract where practical

5. after cleanup, execute a source-to-production decision matrix review;
   do not infer safety merely because the STAR Lab evidence is complete
```

## 7. Phase-4 action

Before further frontier refinement:

- realtime-GC retention gap has been repaired on the Phase-4 branch;
- the 16,384 Window Vision default now has a dedicated regression contract again;
- current 25% Vision behavior should not be treated as cache thrashing while capacity remains 16,384 and evictions remain zero;
- CLOSED cases should be consulted before opening new optimization work when a signature resembles a historical case.

No existing CLOSED case is reopened by this audit.

## 8. Audit conclusion

The archive cleanup was **safe for engineering knowledge**, but the original audit scope was too narrow to guarantee production-decision retention.

The observed state is mixed rather than catastrophic:

```text
most accepted runtime optimizations      retained
several structural regression guards     retained
realtime_defer formal measurement policy lost, now restored
Vision 16384 behavior                    retained
Vision dedicated default regression test lost, now restored
historical experiment tooling            intentionally removed
```

The durable process correction is therefore:

> Archive completeness and production retention are separate invariants. Future cleanup must prove both.
