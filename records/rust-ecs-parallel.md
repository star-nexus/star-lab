# Rust ECS parallel task recovery (2026-09-30)

Active worktree `/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main`, branch
`codex/rust-ecs-parallel`, rooted at annotated R4e tag / 7e145d169433695cd4957e186a6b2fda06813c26.
P0 implementation `2ac2b29a7a3bf09d92370a0352dcf0fd47f741e5`; Lab probe tool
`31c93a3fc294df55810f384b2e3e36b72c507cb3`. Read this current status before historical next steps.

Progress: `recovery █ | dependency audit █ | attribution █ | Statistics compute █ | native4 capacity █`.
Target 5000 Units + 1000 Agents; 5000 Agents paused. Preserve rules, observations,
accepted action order, simulation clock and deterministic RNG. Rust executes world;
Python keeps interface/ecosystem. Default Python/native threads=1 unchanged.

## E2 Statistics 内部并行研究完成（2026-10-01）

正式包：[E2报告](../experiments/2026-09-rust-statistics-compute/README.md)，含analysis/decision/manifest、完整raw、逐步samples、错误/reset契约、wheel及源码恢复bundle。
活动工作树 `/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main`，分支 `codex/rust-ecs-parallel`。
实测/策略 **2bc57d5f2241a578f61d71bb5774e7063a03ec25**；最终文档 **0aa28ac2ae0267048fcdb3998f9d76175ed4d699**（执行代码相同）；
annotated **rust-parallel-e2-statistics-2026-10-01**。正式扩展SHA **23dc7e4f5425e855a780a802d889f13bd28f300577688e66378ab574b7712d55**。
串行44c3696、实验调度7ab0ac1及独立旧P0 binary均保留。
进度：`串行拆分 █ | 分项归因 █ | scoped计算 █ | 全量等价 █ | 净收益/门槛 █ | 真实容量 █ | canonical归档/复算 █`。

仅当前Statistics批次的JSON记录构建在已有实例池内部并行，主线程原序提交；实际候选行至少128且显式native2/4才调度。小/尾批inline、默认1不变，没有between-System调度器。健康算术极小，trim/visibility/factions及写入保留串行。
旧/新8种契约完整输出字节相同（36场景/174step）；20次R4e40994请求/9880tick/展示的完整流/最终状态一致，含正式普通step1/2/4。2291Python/4Rust/fmt/Clippy/release通过，多实例/reset/close覆盖。
同binary同线程只改门槛的3组完整step对照：2线程均值减少4.18–16.76%，4线程7.58–10.36%，各组P99改善。合成1–32行并行负收益；64为测得mean-positive点，64行native4 P99反而更差，128保守操作门槛。此因果对照不是旧P0到全部新实现或整帧加速。

真实5000Units/1000Agents/native4三轮30预热＋300s Cocoa全部guard通过：帧P99 28.283/28.643/28.631ms，Hz29.997/29.993/30.000。
max帧91.923/102.449/32.239ms、worst5s P99 39.837/76.037/31.794ms原样保留，不保证每帧/短窗口。alive_min5000，peak movers180/173/173；不外推全5000移动、高密度、Hub/真实LLM或5000Agents。R4e native1验收及全部历史证据不覆盖。
canonical raw SHA **62c5e73a2356334fc0fa85e3b5f4054a46f5f759ad7cb6c9fcef41dcd7b190ba**；8个完全相同contract raw只存1成员+别名；analyzer由canonical包复算而非依赖ignored loose scratch。工具checkpoint **69969a1713bb83d7e18fd4b05137276bc412cb72**，各测量工具hash/旧变体commit及完整argv/env见manifest/results。

API18/schema5/oracle/Python生态边界不变。无新确认玩法GAP；G008/G009 OPEN、R001/R002 RISK、G001–3基线变化保留，5000Agents暂缓。原49项删除和两处冻结HEAD/扩展hash均核验保留。没有push/merge，迁移/发布未完成。
下一候选E3先归因Vision uncached几何与有序缓存/Fog提交；between-System Recovery/Lifecycle/Vision保留低优先级窄接口研究（现有理想重叠小于派发成本），不直接全System入池。先读本E2包/生产native-statistics-parallel/GAP，再读E1依赖与机制、P0归因和R4e历史容量。
此状态优先于下方历史E1/P0下一步。

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
2. [E2 Statistics implementation/capacity package](../experiments/2026-09-rust-statistics-compute/README.md), analysis/decision; then [E1 design/mechanism package](../experiments/2026-09-rust-ecs-parallel-design/README.md), analysis and decision; then [P0 attribution package](../experiments/2026-09-rust-system-attribution/README.md), analysis and decision.
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
