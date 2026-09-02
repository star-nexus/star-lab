# Analysis — Vision Geometry Cache Working Set

## 1. Observation

After the Vision geometry cache was bounded to prevent long-run retention, the 5000-unit staggered workload showed an unexpected Vision regression:

```text
historical steady Vision   ~1.2 ms
4096 bounded LRU            2.9246 ms self
```

The cache was memory-safe, but latency had regressed.

## 2. Competing hypotheses

### H1 — Vision returned to O(Nresident)

The incremental dirty-driven design may have regressed and begun scanning/recomputing too much resident state.

### H2 — 4096 is below the geometry working set

The bounded LRU may be repeatedly evicting useful geometry and recomputing LOS work.

### H3 — GC or unrelated frame noise explains the Vision increase

The apparent Vision regression may actually be another tail-latency artifact.

## 3. Instrumentation

The formal ablation added fresh-process capacity selection and measurement-epoch-local counters:

```text
geometry cache start/current size
capacity
hits
misses
evictions
lookups
hit rate
Vision self/inclusive time
process RSS at measurement boundaries
```

Counters are measured as epoch deltas so bootstrap/warmup activity does not contaminate the comparison.

## 4. Evidence

### 4096

```text
lookups          68,854
hits             49,844
misses           19,010
evictions        19,010
hit rate          72.39%
size              4096/4096
Vision self       2.9246 ms
```

After saturation, every miss requires an eviction. This is a direct capacity-thrashing signature.

### 8192

```text
lookups          74,697
hits             74,058
misses              639
evictions             0
hit rate          99.14%
final size          5639
Vision self       1.2260 ms
```

### 16384

```text
lookups          74,697
hits             74,058
misses              639
evictions             0
hit rate          99.14%
final size          5639
Vision self       1.2241 ms
```

8192 and 16384 have effectively identical cache behavior and Vision latency. Therefore the performance plateau is already reached at 8192 for this workload.

### 32768

The cache again has zero evictions and the same 5639 final size. The process has worse aggregate frame timing, but multiple unrelated sections and planning/GC timings are simultaneously slower. Therefore the run does not establish that capacity 32768 itself causes slowdown.

## 5. Root cause

> 4096 is below the active geometry working set for the validated 5000-unit workload and causes sustained LRU thrashing. Bounding memory was correct; the initial bound was simply too tight for this workload.

## 6. Causal chain

```text
4096 capacity below working set
 -> cache saturated
 -> every new miss evicts useful geometry
 -> future reuse misses again
 -> repeated LOS geometry recomputation
 -> Vision self ~2.9 ms

capacity >= measured working set
 -> zero sustained eviction
 -> ~99.14% hit rate
 -> Vision self ~1.22 ms
```

## 7. Rejected explanations

- **Vision returned to resident-wide O(N).** Rejected: the dirty-driven architecture remained intact; changing only cache capacity restored latency.
- **GC caused the 4096 Vision cost.** Rejected for the formal comparison: `realtime_defer` was active and guarded in every run.
- **16384 is faster than 8192 because its P99 was lower.** Rejected as causal inference: cache intermediate metrics and Vision time are essentially identical; aggregate P99 differs due to unrelated process/system variation.
- **32768 itself makes the engine slower.** Not supported: unrelated sections were slower in that fresh process as well.

## 8. Scaling interpretation

The geometry key is:

```text
(center, effective_range, terrain_revision)
```

Therefore cache working set is not directly `O(number of units)`. Units at the same center/effective range share geometry. Increasing from 5K to 10K/20K on the same map may increase lookup pressure without proportionally increasing distinct cached geometries. Enlarging the map or range diversity is more directly relevant to capacity pressure.

At the measured 5K workload:

```text
working set observed ≈ 5639 entries
8192 / 5639         ≈ 1.45x minimum headroom
16384 / 5639        ≈ 2.9x operational headroom
```

Capacity is not preallocated, so selecting 16384 does not force 16384 geometry objects to exist under the 5K workload.

## 9. Limits

This experiment validates the 5K / 91×91 workload. It does not prove 16384 is sufficient for all future 20K or larger-map workloads. Future decisions must use measured occupancy, hit rate, misses, evictions, and Vision latency rather than unit count alone.

## 10. Raw evidence

- `results/capacity-4096.json`
- `results/capacity-8192.json`
- `results/capacity-16384.json`
- `results/capacity-32768.json`
