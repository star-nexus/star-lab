# STAR Performance Frontier

This record tracks validated movement of STAR's scalability/performance frontier. A result belongs here only when its experiment is reproducible, raw evidence is archived, integrity is verified, guards pass, and the exact STAR source state is recorded.

For admission criteria, see [`../PROTOCOL.md`](../PROTOCOL.md).

## Frontier

| Date | STAR source | Milestone tag | Scenario | Resident | Moving | Map | Phase | Fog | Avg frame | P99 | Avg FPS | Platform | Evidence |
|---|---|---|---|---:|---:|---|---|---|---:|---:|---:|---|---|
| 2026-09-02 | `a24482d438157aa23b371b6e34d49b1c04fec7f7` | `scale-v1-cull-vision-closed` | `TestMap-8K-scale-5000` | 5000 | 5000 | 91×91 | staggered | ON | **20.453 ms** | **24.290 ms** | **48.892** | Mac mini / macOS | [`capacity-16384.json`](../experiments/2026-09-vision-cache/results/capacity-16384.json) |

## First archived frontier point

The first row is the validated 16,384-capacity Vision-cache run. Its canonical raw artifact is SHA256-verified in the Vision case:

```text
f9ea376497c8c0f39a343ec99965dc2b27800c509b2bef89eb578df108daaa32
```

At the corresponding milestone:

- realtime cyclic GC is deferred during the bounded latency-critical window;
- scale visibility-history retention is bounded;
- unit viewport culling has removed legacy per-candidate hot-loop work;
- Vision geometry-cache capacity no longer thrashes under the validated 5K workload.

The source milestone is preserved both as:

```text
checkpoint/scale-cull-vision-closed
scale-v1-cull-vision-closed
```

The annotated tag resolves to commit:

```text
a24482d438157aa23b371b6e34d49b1c04fec7f7
```

## Frontier rules

A new row never replaces an older row. This is a progression record, not a single current-best leaderboard.

Preserve enough dimensions to distinguish:

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
canonical raw artifact + checksum
```

A future 10K or 20K point is not directly comparable to the 5K point unless workload differences are explicit.
