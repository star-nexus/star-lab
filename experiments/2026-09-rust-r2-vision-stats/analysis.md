# Analysis — R2b Fog and statistics

## 1. Observation

R2a had imported Fog/statistics state but did not advance those systems. Current
Rust and normalized Python agree at all284 recorded operation nodes. All1046
production tests and3Rust tests pass.

## 2. Competing hypotheses

H1: preserving only faction unions would preserve observations. H2: compatibility
also depends on observer contributions, explored history, dirty membership, LRU
order and partially completed statistics cycles. The differential interface exports
these ledgers, so equality is checked beyond a final visible union.

## 3. Instrumentation

The Lab driver records the complete transferred state, results and ordered events
at each operation. Statistics wall metadata/default factories are frozen. Kernel
clock ticks are aligned explicitly. No random duration or performance selection.

## 4. Evidence

Six mode/display combinations all pass. Tests separately cover LOS at map edges,
ID-zero terrain behavior, geometry eviction, overlapping observers, death
invalidation, mode-specific visibility histories and public dataclass attributes.
The startup codec now retains Agent registration attributes attached dynamically
to GameStats; the original declared-field-only codec omitted them.

## 5. Root cause / compatibility requirement

Final position or faction visibility alone is insufficient replay state. Cached
geometry and sampler progress affect later counters/history/order; omitting them
changes subsequent results after restore. The native runtime retains these owned
ledgers and consumes them in the historical order: time, statistics, animation,
resource recovery, vision.

## 6. Causal chain

Movement/death -> dirty observer contributions -> union/exploration -> later
statistics sample. Window sampling spans multiple updates and intentionally sees
live components in each slice. Its cycle state must survive reset.

## 7. Rejected explanations

No aggregate FPS is used to infer a speedup. Ordinary and window statistics retain
their distinct historical behavior; making them identical is outside migration.
Stats wall timestamps do not imply wall-clock cooldown progression.

## 8. Limits

Small fixtures, no full World.update, permissions, Agent observations, game-end,
actual window pixels or capacity. Native transient Fog delta is not yet the Python
presentation journal. Base-profile full audits and several statistics scans remain
for R4 optimization after full functional equivalence.

## 9. Raw evidence

See [compact](results/probe.summary.json), [raw](results/probe.json.gz),
[manifest](manifest.yaml), regression/build logs and SHA256SUMS.
