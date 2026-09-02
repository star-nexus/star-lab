# STAR Performance Frontier

This record tracks validated movement of STAR's scalability/performance frontier. It is intentionally conservative: a result belongs here only when its experiment is reproducible, raw evidence is archived, guards pass, and the exact STAR source state is recorded.

For methodology and admission criteria, see [`../PROTOCOL.md`](../PROTOCOL.md).

## Frontier

| Date | STAR source | Scenario | Resident | Moving | Map | Phase | Fog | Avg frame | P99 | Avg FPS | Platform | Evidence |
|---|---|---|---:|---:|---|---|---|---:|---:|---:|---|---|
| 2026-09-02 | `a24482d438157aa23b371b6e34d49b1c04fec7f7` | `TestMap-8K-scale-5000` | 5000 | 5000 | 91×91 | staggered | ON | **20.453 ms** | **24.290 ms** | **48.892** | Mac mini / macOS | [`2026-09-vision-cache`](../experiments/2026-09-vision-cache/) |

### Notes on the first archived frontier point

The 20.453 ms / 24.290 ms row is the validated 16,384-capacity Vision-cache run from the 5000-unit, 100%-moving Dynamic World workload. It is recorded as a historical frontier/baseline, not as a universal hardware-independent claim.

At this source milestone:

- realtime cyclic GC is deferred during the bounded latency-critical measurement window;
- long-lived runtime memory growth from scale visibility history has been bounded;
- unit viewport culling has had its legacy per-candidate hot-loop work removed;
- Vision geometry-cache capacity no longer thrashes under the validated 5K workload.

The corresponding STAR checkpoint is:

```text
checkpoint/scale-cull-vision-closed
```

An annotated immutable milestone tag is recommended but was not yet published when this archive entry was created. Once published, add it here without changing the underlying source SHA.

## Frontier rules

A new row must not replace an older row. The purpose is historical progression, not a single current best number.

When scale changes, preserve enough dimensions to distinguish:

```text
N_resident
N_moving
map size
state-transition density
staggered vs synchronized
Fog state
camera / zoom
hardware
source commit/tag
```

A 10K or 20K result is not directly comparable to this 5K row unless the workload differences are explicit.
