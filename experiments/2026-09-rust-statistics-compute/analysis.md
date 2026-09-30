# Analysis — E2 (draft)

## Observation

Serial split matches the independent P0 binary on40994requests/9880ticks/9880
full presentation extractions. All36synthetic cases/174steps also match in full
state, errors, one-shot deltas and reset outputs at1/2/4threads. Parallel canonical
replay and controlled net latency measurements are in progress.

## Hypothesis

The meaningful independent work is history JSON construction, not health arithmetic.
Parallelize only that current batch, preserve first-error successful prefix and all
history/observation/cycle semantics. Net benefit and crossover are not yet proven.

## Instrumentation

Const-generic per-call timing is absent from ordinary execution. Pure inputs borrow
only typed row facts; owned outputs return in original ordinal order. Gather,
compute, JSON construction, commit, trim and visibility/faction costs are split.
Parallel kernel wall time is separate from summed worker durations; scheduling
residual includes join/merge/timer bookkeeping and is not a pure scheduler estimate.

## Limits

No capacity or frame benefit claim yet. A disk-full pytest interruption is not a
gameplay GAP; compilation cache cleanup and fresh79test pass supersede that incomplete
validation. Two matrix setup errors (inconsistent mode, invalid zero batch) were
corrected before final36-case evidence; do not count setup failures as formal negative performance.
