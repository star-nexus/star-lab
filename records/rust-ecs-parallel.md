# Rust ECS parallel task recovery (2026-09-30)

Active worktree `/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main`, branch
`codex/rust-ecs-parallel`, rooted at annotated R4e tag / 7e145d169433695cd4957e186a6b2fda06813c26.
P0 implementation `2ac2b29a7a3bf09d92370a0352dcf0fd47f741e5`; Lab probe tool
`31c93a3fc294df55810f384b2e3e36b72c507cb3`. Read this current status before historical next steps.

Progress: `recovery █ | dependency audit █ | attribution █ | parallel fix ░ | capacity ░`.
Target 5000 Units + 1000 Agents; 5000 Agents paused. Preserve rules, observations,
accepted action order, simulation clock and deterministic RNG. Rust executes world;
Python keeps interface/ecosystem. Default Python/native threads=1 unchanged.

## Read order

1. [Original handoff](rust-parallel-handoff.md) and [PROTOCOL](../PROTOCOL.md).
2. [P0 attribution package](../experiments/2026-09-rust-system-attribution/README.md), analysis and decision.
3. Active source [System dependency/cost table](/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main/docs/native-system-dependencies.md).
4. Active source GAP ledger / state boundaries / runtime docs in that SAME worktree.
5. R4e canonical evidence; don't overwrite frozen measurement or older negative controls.

## Restored decisions and failures

Python observation process pool v1 per-request export/IPC/restore was slower than
serial construction; do not repeat whole-world copying per Agent. Read batches
already share public facts in Python and Rust; this is an integration gap, not a
new algorithm. R4a only parallelizes missing Unit panels and may lose on tiny
queries. R3k4/R4b/R4d reduced encoding/representation/boundary work without changing
information. Arc is ownership, not multithreading. Immediate action/death/turn and
RNG commits cannot become arbitrary completion order or frame-end command buffers.
Keep movement loss weakening and historical skill/territory quirks. G001–G003
remain oracle-version changes, G008/G009 remain OPEN, R001/R002 remain scoped risks.

R4e validated three canonical 5000/1000 300s windows with one native thread, not
all movers/high density/5000 Agents/Hub/real LLM. World step mean 0.295ms is much
smaller than display work. Per-System cost was unknown; P0 adds opt-in attribution
before picking a parallel world kernel. No System pair is approved for reordering.

## Isolation

Original production head 7e145d1 on codex/rust-env-migration retains 49 user deletions.
Lab started clean main d777f3319140eb5f883447125dc0899d9f8fd87c.
Frozen Rust 5147e4d and Python 6a970dea worktrees remain unchanged. New worktree
has complete tracked assets; it does not restore deleted files in original checkout.
No push/merge. Subsequent merge only squash, with annotated milestone first.

## P0 checkpoint and selected next stage

Final documentation commit `c058d75c0ad67a7c340c2a6ac74a9d5bc2888adf`, annotated
`rust-parallel-p0-attribution-2026-09-30`. Measured implementation remains2ac2b29.
Analyzer tool commit622c9e7441757c12d75cdf0d083cde4a7c6fd8dd; probe31c93a3.

Frozen R4e and candidate1/2/4 match all40994 requests/9880ticks/9880complete deltas
in output-stream/final-state hashes; candidate ordinary/profiled paths compare
complete decoded responses/deltas and final full state. All gates pass. Raw
per-tick phase durations, wheel and test evidence are archived with compact/raw
hashes and sizes, see results/packages.json. No new live capacity or Frontier.

T1 diagnostic mean: stats0.167297ms, vision0.045143ms, movement0.027429ms,
visuals0.010109ms, recovery0.003624ms; native total0.256917ms. Including recorded
warmup, headless paired replay; not a live/threads/overhead A-B.

11007queries,6938segments; multi-query queries7097(64.48%),same-faction repeats1604
(14.57%),panel repeats0. P1 SELECTED: ordered encoded read-batch ingress for
already-admitted adjacent faction queries. First audit admission/callback order;
then avoid server dict decode/re-encode, reuse existing ObservationBatch facts.
Do not wait/reorder/cross any write or tick/display/reset/VLM boundary. If queue
cannot supply the boundary, record a negative feasibility result, not a fabricated
batch. This is a candidate, not an implemented speedup. Cost/small-negative and
complete response/state checks precede a new real-window1000-Agent gate.

## Current stage

P0 profiler/contract tests committed; 2239 Python regressions (22 new), 4 Rust
contracts, fmt/Clippy and release wheel pass. New extension SHA256
`a73c477263d792cd0c4f71e3ab6001a36223cf0afd7136f8e8975f16b584731f`.
API18/schema5/oracle unchanged; additive private method requires this new wheel.
Frozen extension remains `324454a00ab8bd3559c9229e6c6c9644242d65c488585eba7d29a63b39d29405`.
Attribution uses exact R4e r3 trace, includes recorded warmup, runs serially.
Complete decoded responses/deltas and final state compare profiled vs ordinary
candidate; frozen binary independently supplies full-output-stream hashes. Timing
probe changes wall execution speed; this is not a live closed-loop/capacity rerun.

P0 is complete; follow the selected P1 admission audit and gates above. Do
not restore 5000-Agent tuning or assume all new cost is parallelizable. Keep
release/integration/frontier status separate from instrumentation correctness.
