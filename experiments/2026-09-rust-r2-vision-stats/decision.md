# Decision — retain exact Fog and sampler state

Status: accepted for this partial checkpoint. Date:2026-09-12.
Source `062141d97fd6c8122c93e3dd1bc0b94736442e1e`; tag `rust-kernel-r2b-2026-09-12`.

## Decision and drivers

Keep native observer refcounts, explored cells, geometry LRU and statistics cycle
state. Continue R2 with registration/ownership and full action/observation dispatch.
Use explicit external timestamps for historical telemetry and dt for simulation.

## Alternatives and evidence

Discarding cache/cycle state at restore is incompatible with continued replay.
Unifying ordinary/window sampling is a gameplay/telemetry change and was not tested
as an optimization. The selected version passes284full-state operation comparisons;
this is not a measured throughput comparison.

## Headroom and trade-offs

No capacity/default-thread value selected. Thread counts remain reserved and
parallel execution is R4 work. Preserve historical ordering before removing scans.
JSON-backed cold statistics and existing audits still incur native costs to measure.

## Revisit and provenance

Revisit after full Agent closure, presentation journals, dynamic map changes or
parallel scheduling. Full R2/R3–R5 remain open; Python remains default. See
[reproduce](README.md), [manifest](manifest.yaml), [analysis](analysis.md).
