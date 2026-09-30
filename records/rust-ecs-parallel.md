# Rust ECS parallel task recovery (2026-09-30)

Active worktree `/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main`, branch
`codex/rust-ecs-parallel`, rooted at annotated R4e tag / 7e145d169433695cd4957e186a6b2fda06813c26.
P0 implementation `2ac2b29a7a3bf09d92370a0352dcf0fd47f741e5`; Lab probe tool
`31c93a3fc294df55810f384b2e3e36b72c507cb3`. Read this current status before historical next steps.

Progress: `recovery █ | dependency audit █ | attribution █ | parallel fix ░ | capacity ░`.
Target 5000 Units + 1000 Agents; 5000 Agents paused. Preserve rules, observations,
accepted action order, simulation clock and deterministic RNG. Rust executes world;
Python keeps interface/ecosystem. Default Python/native threads=1 unchanged.

## E2 Statistics 内部并行研究进行中（2026-10-01）

当前任务见 [E2研究包](../experiments/2026-09-rust-statistics-compute/README.md)及
[恢复入口](rust-ecs-parallel.md)。从E1按计划进入Statistics当前批次纯计算/有序提交。
串行拆分 **44c3696814b82d7c9d92a83ef7d160ef462168af**；并行研究原型
**7ab0ac1d97f5d68b8d81c505fa505a1cb234a56c**，同一独立工作树/分支。
进度：`串行拆分 █ | 分项归因 █ | scoped原型 █ | 全量等价 █ | 净收益 ▒ | 真实容量 ░`。

旧P0二进制与新原型1/2/4的36场景/174step完整状态、错误、展示及reset输出一致；
原R4e40994请求/9880tick/9880展示的完整输出流与最终状态也一致。79项定向契约通过。
记录构建是独立热点，算术极小；裁剪及逐行提交仍串行。现有实例池不增加worker预算。
同二进制、同线程数的inline/128行策略独立交替对照正在完成，小批次阈值和真实窗口待验。
普通step当前仍串行调度，私有推进探针按调用控制实验；API18/schema5/oracle/默认1线程不变。
没有新已确认规则GAP；G008/G009 OPEN、R001/R002 RISK继续保留。5000Agents暂缓。
磁盘满中断的pytest已在仅清理本任务编译缓存后重跑通过；原删除、冻结目录和正式证据保留。
此状态优先于下方历史E1/P0下一步，不是容量或发布完成结论。

## Historical E1 checkpoint — completed design and selected E2

User's newest instruction selects ECS between-System and within-System exploration.
P0 cross-request batch candidate is deferred; preserve its immutable experiment.
E1 design commit **be3867b3ad65749e0e34efd245359c4123189031** / annotated
**rust-parallel-e1-design-2026-09-30**. Lab probe tool
5f83b060fe6fb47db6ecbe9bea0633d02f7b550f; analyzer
adf399f96db5beef6427caba4ec83c491424755e. Measurement source remains c058d75;
E1 changes production docs only. No extension rebuild or real System parallelism.

Progress: `access audit █ | locked API mechanisms █ | design choice █ | production prototype ░ | capacity ░`.
Read [E1 package](../experiments/2026-09-rust-ecs-parallel-design/README.md), analysis,
decision and [production design](/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main/docs/native-ecs-parallel-design.md)
before historical P0 next-stage suggestions.

Between Systems: after Visuals succeeds and structural changes finish, narrow
Recovery/Lifecycle/Vision access is a candidate concurrent region, with ordered
R→L→V side-effect commit. Statistics' old Position/MP/Fog sampling and partial
errors, Movement new spatial positions and Visuals spawning prevent whole-method
concurrency. These remain source-level candidates, not production-approved swaps.

Within Systems: Statistics current128-row batch pure candidates first; Vision
uncached geometry second; Movement active-unit arithmetic later. Keep cycle phases,
first-error successful prefixes, insertion/history/LRU/spatial/Fog/event/RNG order.
E2 first uses1thread serial leaf extraction + gather/compute/JSON/commit/trim attribution;
only measured independent work then uses existing2/4workers with original-ordinal outputs.
Complete response/presentation/authority/error-state equivalence precedes net performance
and a new actual5000/1000window. Don't make a full resident scan to fill workers.

All five mechanism processes pass: disjoint sample Systems max1/2/2 at1/2/4;
shared component/Resource fields/exclusive World max1; selected100/5000 all exact;
ReadPool5000ordered outputs equal. Empty dispatch median2/4=9125/7084ns;
ideal P0 R/L/V overlap mean3882.529ns/P9913292ns. Different workloads, no measured
net speedup. Compact/raw checksum chain and analyzer re-audit are archived.
No new Frontier/capacity/closed GAP. Default Python/native1 remains unchanged.

## Read order

1. [Original handoff](rust-parallel-handoff.md) and [PROTOCOL](../PROTOCOL.md).
2. [E1 design/mechanism package](../experiments/2026-09-rust-ecs-parallel-design/README.md), analysis and decision; then [P0 attribution package](../experiments/2026-09-rust-system-attribution/README.md), analysis and decision.
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

## Historical P0 checkpoint and then-selected candidate (deferred by E1)

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
(14.57%),panel repeats0. P0 THEN SELECTED P1 (now deferred): ordered encoded read-batch ingress for
already-admitted adjacent faction queries. First audit admission/callback order;
then avoid server dict decode/re-encode, reuse existing ObservationBatch facts.
Do not wait/reorder/cross any write or tick/display/reset/VLM boundary. If queue
cannot supply the boundary, record a negative feasibility result, not a fabricated
batch. This is a candidate, not an implemented speedup. Cost/small-negative and
complete response/state checks precede a new real-window1000-Agent gate.

## P0 validated implementation (historical)

P0 profiler/contract tests committed; 2239 Python regressions (22 new), 4 Rust
contracts, fmt/Clippy and release wheel pass. New extension SHA256
`a73c477263d792cd0c4f71e3ab6001a36223cf0afd7136f8e8975f16b584731f`.
API18/schema5/oracle unchanged; additive private method requires this new wheel.
Frozen extension remains `324454a00ab8bd3559c9229e6c6c9644242d65c488585eba7d29a63b39d29405`.
Attribution uses exact R4e r3 trace, includes recorded warmup, runs serially.
Complete decoded responses/deltas and final state compare profiled vs ordinary
candidate; frozen binary independently supplies full-output-stream hashes. Timing
probe changes wall execution speed; this is not a live closed-loop/capacity rerun.

P0 is complete. E1 has superseded its next-stage priority: follow current E2
Statistics serial split/cost gates at the top. Preserve the deferred P1 evidence.
Do not restore5000-Agent tuning or assume all new cost is parallelizable. Keep
release/integration/frontier status separate from design/mechanism correctness.
