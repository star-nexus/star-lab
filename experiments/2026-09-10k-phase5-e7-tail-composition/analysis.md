# Analysis — Phase 5 E7 Tail Composition Attribution

## Observation

Retained production `e7ba18b3...` is close to but not consistently below the 33.33 ms 10K / 100%-moving canonical p99 gate. The remaining question is tail composition, not another UnitRender representation micro-optimization.

## Hypotheses

- **H1 single subsystem:** one controlled section contributes most of the tail uplift.
- **H2 multi-subsystem coincidence:** several ordinary-cost sections become expensive on the same frames.
- **H3 workload pulse association:** a causal frame metric such as position/Vision/Fog work rises with the same tail frames.
- **H4 no stable signature:** the remaining p99 margin is dominated by run-level/platform noise rather than a repeatable controlled-work pattern.

## Attribution method

Use profiler-aligned per-frame deques already collected in production. For each of three identical 100%-moving repeats:

```text
tail      = controlled_work >= p95
reference = p25 <= controlled_work <= p75
```

For every controlled-category section, compare self-time conditional means. Self time is mandatory for contribution accounting because controlled work itself is the sum of controlled-category self time. Inclusive time may be reported diagnostically but is never summed into contribution shares.

Also record:

- Pearson association with controlled work;
- fraction of tail frames in which each section exceeds its own p90;
- p90 co-occurrence pairs among positive contributors;
- numeric frame-metric tail/reference deltas and correlations;
- exact section composition for frames above 33.33 ms.

## Repeat stability

A section becomes actionable only when it is a positive top-3 uplift contributor in at least 2/3 repeats and its median uplift is at least 0.15 ms.

Do not infer a new optimization from a one-run p99 spike.

## Interpretation

A positive result identifies the next path to instrument/attribute. It is not itself an optimization KEEP. A negative result means Phase 5 should not invent a subsystem target from unstable tail noise; the next decision must then consider whether the observed boundary is sufficiently stochastic to require broader repeated frontier characterization rather than micro-optimization.
