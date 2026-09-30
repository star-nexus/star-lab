# Analysis — System attribution before parallelization

## Observation

R4e run1 world step mean0.295ms/P990.758ms excludes observations; Python display
systems mean8.679ms/application2.768ms dominate that world segment. R4a small
queries can lose from scheduling; R4b representation reduced public work. Existing
read-batch support is not connected across Lab's individual request calls.

## Hypotheses

H1: Movement/Vision dominates enough world work to justify within-System workers.
H2: Existing adjacent-query public sharing is a better current-load implementation.
H3: Systems with few imports can run together — rejected structurally: components,
spatial/Fog, LRU/deadlines, events/structural changes and business order conflict.

## Instrumentation

Opt-in step_inner profiling measures disjoint wall intervals per original phase;
normal step performs no timer reads. Paired replay uses complete decoded responses
and deltas and final state; an independent frozen replay hashes all full outputs.
Read segments end at every action, tick or presentation read. Raw includes every
9880 tick, not just the 9000 original measured frames. JSON/map/timer overhead is
outside individual phases and partly inside native total; tiny phase numbers are
not precise microbenchmarks. No actual 2/4-thread world parallelism is introduced.

## Evidence and causal interpretation

Initial t1: statistics0.167297ms, vision0.045143ms, movement0.027429ms,
visuals0.010109ms, recovery0.003624ms; remaining singleton phases below0.001ms.
Each value is a mean of9880 paired diagnostic replay samples; do not treat as new
Cocoa results or subtract its P99 from R4e frame P99. Statistics includes historical
sampling/visibility work before movement/Fog and cannot be moved after them.

11007 observations occupy6938 immutable segments: lengths1/2/3/4/5 occur
3910/2048/921/57/2 times. 7097 queries(64.475%) are in multi-query segments.
Only1604 requests(14.573%) repeat the same faction within a segment; selected
panel references never repeat. Thus64.5% is NOT a predicted savings ratio. Base
facts may share across factions, but Fog and permissions remain faction-specific;
final payload encoding and client decode still happen for each request.

## Root cause and scope

Confirmed gap: no per-System attribution before P0, and current Lab single-entry
calls cannot reuse native batch facts across consecutive requests. This does not
prove a particular callback/admission batching design is safe or faster. Profile
first; preserve scheduler accept order, same-request outputs, clocks and complete
observations. No new capacity failure or parallel fix is established here.

## Negative results and limits

All-world pooling rejected by dependency/ordering evidence, not benchmarked.
Historical per-request whole-world IPC/restore was slower and remains archived.
No higher CPU utilization or raw replay throughput is promoted to frame benefit.
Cold-writer risks and missing network/BOT integration remain independent.

## Raw evidence

results/comparison.json, per-run summaries, raw archive per-tick samples;
source identities and checksums in manifest.yaml / results/packages.json.
