# STAR Lab Experiment Index

This directory contains reproducible engineering investigations and controlled experiments for STAR / StarBench.

Read [`../PROTOCOL.md`](../PROTOCOL.md) before adding or modifying a formal experiment package.

## Archived cases

| Experiment | Status | Problem / question | Main conclusion | Raw evidence |
|---|---|---|---|---|
| [`2026-09-realtime-gc`](2026-09-realtime-gc/) | **CLOSED — historical backfill** | Why do rare UnitRender frames jump to ~50 ms? | Automatic CPython Gen2 GC was running inside the timed render section; bounded `realtime_defer` moved cyclic-GC maintenance out of the critical window. | Historical formal JSON not yet recovered; exact source provenance + validated summaries preserved. |
| [`2026-09-memory-retention`](2026-09-memory-retention/) | **CLOSED — historical backfill** | Why do RSS/tracked objects rise although full safe GC collects 0 and ECS/Vision caches are bounded? | Scale runtime retained historical visibility telemetry: up to 100 records/unit. Runtime now keeps the latest transition only. | Historical soak JSON not yet recovered; exact source provenance + validated summaries preserved. |
| [`2026-09-spatial-cull`](2026-09-spatial-cull/) | **CLOSED — historical backfill** | Why is `unit_visible_cull` still ~3.53 ms although spatial candidate discovery already exists? | Residual per-candidate ECS/singleton lookups, repeated coordinate conversion, filter order, and low-zoom overscan were the real costs; ~3.53 -> ~1.3 ms. | Historical before/after JSON not yet recovered; exact problem/fix commits preserved. |
| [`2026-09-vision-cache`](2026-09-vision-cache/) | **CLOSED — complete formal archive** | What bounded geometry-cache capacity avoids memory growth without cache thrashing? | 4096 thrashes; 8192 is measured minimum sufficient; 16384 is the scale/window operational default with headroom. | **Complete:** 4096 / 8192 / 16384 / 32768 formal JSON runs archived. |

## Reading order for a case

Use the same order for every experiment:

```text
README.md
  -> reproduce the problem and validation workload

manifest.yaml
  -> exact source commits, machine/workload identity, artifact list

analysis.md
  -> observation, hypotheses, instrumentation, evidence, root cause

decision.md
  -> accepted engineering choice, rejected alternatives, revisit triggers

results/
  -> raw formal evidence when available
```

## Historical backfill rule

Some important investigations were completed before STAR Lab existed. Backfilling them is allowed, but the archive must distinguish three evidence levels:

```text
1. exact source provenance confirmed from Git
2. validated numeric summaries preserved from the original investigation
3. original raw artifact recovered and committed
```

Never fabricate level 3 from level 2. If a raw artifact cannot be recovered, say so explicitly.

## Next experiments

New work should follow the protocol from the start, so future cases should normally arrive in STAR Lab with raw evidence rather than requiring historical backfill.

The next performance investigation after the current closed milestone is expected to decompose the `render_engine` cost before attempting any redesign.
