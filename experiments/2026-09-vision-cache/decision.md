# Decision — Vision Geometry Cache Capacity

**Status:** accepted / closed  
**Decision date:** 2026-09-02  
**Validated STAR commit:** `86672d6f00a995c36a5f268a47f46ffe8d382301`  
**Documented scale milestone:** `a24482d438157aa23b371b6e34d49b1c04fec7f7`

## 1. Decision

Use **16384 entries** as the default Vision geometry-cache capacity for large interactive / scale-window mode. Preserve **8192** as the measured minimum sufficient capacity for the validated 5000-unit workload. Keep the explicit fresh-process environment override for future ablations. Canonical/headless defaults remain separate rather than inheriting the scale-window setting automatically.

## 2. Measured alternatives

| Capacity | Vision self | Hit rate | Epoch misses | Evictions | Final size | Interpretation |
|---:|---:|---:|---:|---:|---:|---|
| 4096 | 2.9246 ms | 72.39% | 19,010 | 19,010 | 4096 | Thrashing |
| 8192 | 1.2260 ms | 99.14% | 639 | 0 | 5639 | Minimum sufficient |
| 16384 | 1.2241 ms | 99.14% | 639 | 0 | 5639 | Chosen operational default |
| 32768 | 1.3496 ms | 99.04% | 639 | 0 | 5639 | No demonstrated cache benefit |

## 3. Why 16384 rather than 8192

8192 is sufficient for the measured 5K workload, but an operational default should not sit immediately above the first measured working-set threshold when future larger maps and 10K/20K workloads are planned.

16384 provides roughly 2.9× capacity over the observed 5639-entry working set while producing the same cache behavior and Vision latency as 8192.

The capacity is an upper bound, not preallocation, so the 5K workload still retains only the geometries it uses.

## 4. Why not 32768

There is no measured need for it. The 32768 run does not improve cache pressure relative to 16384: both have zero evictions and the same final working set. Future capacity increases should be justified by measured pressure, not by "more memory is available."

## 5. Scaling rule

Do not scale cache capacity mechanically with unit count.

Re-evaluate using:

```text
cache size / capacity
geometry hit rate
miss rate
eviction rate
Vision latency
map scale
effective-range diversity
```

Because the key is `(center, effective_range, terrain_revision)`, distinct geometry demand is related more directly to spatial/range diversity than to raw unit count.

## 6. Revisit when

Re-run a controlled capacity ablation when:

- sustained evictions become nonzero at 16384;
- hit rate materially declines;
- occupancy persistently approaches 16384;
- map area increases materially;
- effective-range diversity increases;
- 10K/20K testing demonstrates a new working-set regime.

## 7. Broader principle

This case establishes an important STAR engineering pattern:

```text
unbounded cache
 -> memory problem exposed
 -> bounded 4096 cache
 -> latency regression exposed
 -> working-set measurement
 -> bounded memory + sufficient capacity + restored latency
```

A tight resource bound was useful because it exposed hidden cache-pressure behavior; the final solution adds headroom only after the mechanism is understood.
