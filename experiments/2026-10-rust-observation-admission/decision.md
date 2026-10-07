# Decision — E8

**Status:** proposed; P0 complete, P1 authorized

## Decision

Proceed to a minimal owned-cache prototype because about 57% of measured queries have eligible continuous segments and repeated census/public builds are demonstrated. Do not claim speedup from profiled handler batching. First prove no_reuse equivalent to single, then encoded equivalence and a short non-diagnostic service screen.

## Resource policy

Latest user explicitly authorizes continuing under memory warning. E8 now uses telemetry only: no automatic pause, kill or runtime timeout. Pressure evidence still governs formal timing validity; no silently accepting interfered performance samples.

## Limits and revisit

Original window operational guards failed; P0 is diagnosis. Existing GAPs/capacity/Frontier unchanged; 5000 Agents deferred; default research off. Later implementation/benefit gates govern P2–P4 and adoption.

## Provenance

[Results](results/p0-complete.json), [Integrity](results/p0-integrity.json), [Raw](artifacts/e8-p0-20261007-raw.zip).
