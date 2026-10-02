# Rust ECS parallel task recovery (2026-09-30)

## E6 展示数据与 ECS 缓存研究完成（2026-10-02）

验证节点 `068c1ecd17988ac6d884984e904aea924968e0ae` / `rust-parallel-e6-presentation-cache-2026-10-02`；测量0a297a8，执行代码相同，native扩展838c693保持。
2385回归、native1/4完整40994请求/9880tick的响应、权威、展示、查询和像素契约通过。
reuse_typed六轮apply改善44.26–45.62%、完整链14.66–15.53%、总工作10.78–11.61%，
均值/P99/区间门槛通过；native4单实例确认通过。reuse_constructed apply慢2.11–2.71%，不选择。
候选三轮窗口guards通过，但baseline第二轮帧/队列超限，六次整体window gate未全通过。
研究默认关闭，不声称容量或Frontier提升，既有GAP不关闭，5000Agents暂缓。

先读[E6 README](../experiments/2026-10-rust-presentation-cache/README.md)、
[成本/完整结果](../experiments/2026-10-rust-presentation-cache/analysis.md)、
[决策](../experiments/2026-10-rust-presentation-cache/decision.md)。原始样本/失败控制、完整重生成delta、
wheel、source bundle和校验链均保留。像素契约固定游戏墙钟及地形构建条目配额；
正式性能/实时窗口仍采用原时间预算，产品未因此修改。
下一项：显示链路准备成本，先拆真实窗口约3.184ms未归因update和3.349ms RMS分项，并追踪baseline尾延迟。
进度：`归因 █ | 契约/实现 █ | 等价 █ | 三轮收益/确认 █ | 窗口结论 █ | 证据/恢复 █`。
原49删除/冻结目录/E2–E5标签保留，不push/merge。

## 整体性能评估完成：建议优先展示与观测（2026-10-02，未实施）

进度：`运行链路 █ | canonical复算 █ | 源码/已有机制 █ | 投入排序 █ | 恢复/边界 █`。
先读[整体评估与候选排序](rust-performance-optimization-assessment.md)、[精确结果/校验](rust-performance-optimization-assessment.json)，再按其引用下钻E2/R4e/E3/E5。此处是新的投入建议，E5的执行/验收结论仍保留；没有启动优化实施或重新测量当前binary live。

审查源码3b167b1；最新完整窗口仍为E2 native4/source2bc57d5三轮，平均world step0.260–0.264ms（约整帧1.25%）、显示Systems8.491–8.748ms、展示应用2.693–2.748ms。约5.114–5.164ms update尚未分项，不归因为render/GC。不同分母、P99和跨输入结果不可相加或当因果收益。

建议首项：展示路径细分归因＋Python消费已有组件字段更新，减少deepcopy/组件重建/缓存失效；随后接已有合法read-batch。纯ENV优先观测公共工作、Statistics历史结构、Vision集合/Fog提交表示。已有裁剪/批量blit/缓存/typed编码/JSON直传/E2并行应继承；不重做whole-World快照进程池。Statistics kernel∥Movement的2/4诊断零开销上限约5%，不是净收益。

[复算工具](../tools/rust_migration/assess_optimization_priorities.py)校验E2/E3 canonical整体及6个所用member、14个源码SHA，结果可字节复算。此阶段是规划记录，无新加速比/live/容量/Frontier、生产执行变更或GAP关闭。默认1/API18/schema5、规则/观测/动作/确定性/Python生态、原49删除/冻结目录/历史标签保留，5000Agents暂缓，未push/merge。


## E5 研究完成：Movement∥Visuals真实重叠，默认不接入（2026-10-02）

进度：`依赖/窄接口 █ | 四模式/等价 █ | 主门槛/敏感性 █ | 条件停止/决策 █ | canonical归档/恢复 █`。
恢复先读[E5正式包](../experiments/2026-10-rust-movement-visuals-parallel/README.md)，再读analysis/decision/manifest、源码native-movement-visuals-parallel与GAP；E4/E3/E2/E1历史保留。

一worker计算owned Visuals、caller执行Movement，join后原序提交实体操作/状态；只读Position存在性与next-ID，不复制World，复用实例pool，区域最多两个执行参与者。四模式按次私有，新接口_movement_visuals_step_json；E4的Vision未实施模式仍明确拒绝。普通step/default1/API18/schema5/E2 Statistics128、观测/动作/RNG/规则和Python生态不变。

native2三轮mean改善0.593/0.688/−0.023%，native4 −0.747/−0.273/0.742%，各仅1/3轮通过完整mean/P99/CI95门槛。0/4/16六组单轮敏感性全部CI跨零。诊断3772候选tick的计时区间交叠下界均值16.917/15.769µs，支持机制但不是无诊断收益。保留私有原型、普通step不启用；4线程未过前置门槛，未进入单实例确认或live窗口，不新增容量/Frontier。5000Units/1000Agents目标保持，5000Agents暂缓，既有GAP OPEN/RISK不关闭。

测量94913a4f836a3c106e08a1334cb81971cfd728c3；validated 3b167b151c3bc32e1d54f6015d0f15d2c3dd6a74（仅补文档/测试，native代码相同）；annotated rust-parallel-e5-movement-visuals-2026-10-02；扩展838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544。source.bundle需要E4 72bf05a；新空repo由原main及E2→E3→E4→E5 bundle完整恢复已验证。

2345Python/6Rust/fmt/Clippy/release通过，含多段移动/GameOver后Vision、ID耗尽、effect/Capture/Statistics错误前缀、混合实体、reset/close/多实例和两侧fault join。27完整报告、90 world重放各40994request/9880tick/展示完整校验；13合同变体各13case/377step完整state/error/delta/reset字节一致，canonical载荷单存＋13别名。所有预热和慢尾保留。

raw SHA a3593da48438e7c96c9e9c003b8374d4d8b393d45a806d1a2582a2d12e3c4f07（15916081 bytes），compact SHA 2b53b12dadc326ef04a4e43cd115b1e7c71c9dab473f71efdf9ccae4fe3bef65（21057 bytes）。原始全部step/timing/wheel/准确工具版本/检验链保存；canonical analysis与诊断成本复算字节一致，E4/E3/R4e输入和wheel恢复只写新目录。原49删除、两冻结HEAD/扩展、E2/E3/E4标签均保留；活动工作树clean，未push/merge，迁移发布未完成。


## E4 System 之间并行研究完成：派发筛选负结果（2026-10-02）

进度：`边界/理想预算 █ | scoped负对照 █ | 完整ABBA █ | 等价/决策 █ | canonical归档/复算 █`。
先读[E4正式包](../experiments/2026-10-rust-between-system-parallel/README.md)、analysis/decision/manifest，再读E3/E2/E1历史。当前结论优先于旧下一步。

只完成私有baseline/empty_fork。当前同二进制相邻配对诊断8020/9880候选tick，2/4成本均值9.512/9.048µs，当前理想预算7.098/7.769µs；成本减预算95%区间[0.456,5.385]/[0.256,2.421]µs。含计时/bookkeeping和固定先后效应，按收益优先保守停止；不是无诊断严格负收益或所有System并行无价值的证明。无诊断三轮ABBA有矛盾结果，全部保存，没有实际Vision并行净收益。

split_serial/parallel未进入且明确拒绝，真实窗口未进入，普通step未接入。实例池最多一worker＋caller；默认1/E2 Statistics128门槛/API18/schema5/oracle及Python生态不变。目标5000Units/1000Agents，5000Agents暂缓。

测量 **dede5ca0ca3472abdb1d24589878e6a72d812f88**；validated **a7508bce4b900ccf8465e761291adb7e7e2ce98d**；最终文档 **72bf05a2f6ec6d1d15ffad7914226c0c3e16b9cf**（native代码相同）；annotated **rust-parallel-e4-dispatch-screen-2026-10-02**。扩展 **9c7eebe03257d1d6941e67b5e31a947e4c6cedf32db6979e624629fd5cf5dd91**。source.bundle需要E3 ad02b75。

28次完整run报告（24无诊断＋4诊断twins）全部录制响应/事件/最终hash核对，四组twins完整对象一致；7合同变体各36case/174step字节等于canonical；2330Python/5Rust/fmt/Clippy/release通过。raw **c15f4476ce9a7582fd0a33313cf5f8a21670c709d033f75746df2d1011131f4a**；脚本版本/全部tick/慢尾/wheel/日志/校验链保存，canonical复算、只读恢复、bundle验证通过。原49删除、两冻结HEAD/扩展保留；G001–G003历史、G008/G009 OPEN、R001/R002 RISK保留，无新确认玩法GAP、live容量/Frontier、push/merge或发布结论。



## E3 其他 System 内部候选研究完成（2026-10-01）

进度：`边界审计 █ | 分项归因 █ | 完整等价 █ | 条件排序 █ | canonical归档/复算 █`。
先读[E3正式报告](../experiments/2026-10-rust-internal-system-candidates/README.md)、analysis/decision/manifest与[生产成本/依赖表](/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main/docs/native-internal-system-candidates.md)，再读E2/E1/P0历史。此状态优先于下面旧“下一候选”。

活动工作树仍`/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main`、`codex/rust-ecs-parallel`。测量/validated **6d4018cc0c607a51a3783428867ba9259bb43f43**；最终文档 **ad02b75f2b83f97fe0bef4c1c9eee5742b1610fb**（执行代码/测试相同）；annotated **rust-parallel-e3-internal-attribution-2026-10-01**指测量节点。Release扩展SHA **e0f46cfbffd8542c08cd2b2e6b4a26c000da05ecb9bffd3466d77fa859a9834d**。仅增加按次私有归因，**没有启用其他System新并行**；E2 Statistics策略/128门槛、API18/schema5/oracle、默认1、Python接口生态不变。

当前规范轨迹Vision诊断均值约43µs，但几何仅0.553–0.599µs/tick，占1.27–1.37%，提交约27–28µs。Movement行处理乐观上界5.36–5.45µs/tick（含写入/计时），活动平均122.47/峰186。Visuals四阶段循环合计约8µs，上界不能跨栅栏合并；damage平均6.66/峰28行。Recovery平均2.81/峰24到期项，最大阶段是首次5007新ID审计，到期0；Capture无活动样本。

**当前目标没有足够证据启动另一项并行执行。**条件roadmap：先测Vision大批冷几何/合法更大视距，再测更多同时移动单位的Movement、Visuals大批同阶段更新。先串行拆分和分项成本，再决定scoped计算；保持LRU A→B→A、逐段空间写入、新箭同tick推进、ID/错误前缀/事件原序。不得复制世界或全部System入池。当前目标进一步优化可先研究Vision串行提交/表示；其收益仍待单独验证。

旧E2与新1/2/4共4轮每轮40994请求/9880tick/展示完全核对；4个36场景/174step契约输出字节相同；2315Python/4Rust/fmt/Clippy/release通过。原始包SHA **c3e347b145fcc5edfda304bb35030d3d3d9320861f116a5507d2b92cbd9b6abd**，全部逐tick/慢样本/wheel/日志保存；相同输入/合同引用R4e/E2 canonical。恢复bundle需要E2 0aa28ac2；复算只读canonical ZIP，索引/校验/完整argv见正式包。E2的原live容量仍指2bc57d5/23dc7e4，**E3没有新live/Frontier/加速比**。

无新确认玩法GAP；G001–G003历史、G008/G009 OPEN和R001/R002 RISK保留，5000Agents暂缓。原49删除、两冻结HEAD/扩展hash核验一致；未push/merge，发布未完成。


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
