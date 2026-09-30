# Rust 并行工作：新 Session 交接入口

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

## 独立Rust并行任务：E1 ECS方案探索完成（2026-09-30）

按用户最新指示，活动任务转向**System之间及System内部并行**，详见
[恢复入口](rust-ecs-parallel.md)及[E1正式方案/机制包](../experiments/2026-09-rust-ecs-parallel-design/README.md)。
工作树 `/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main`，分支
`codex/rust-ecs-parallel`，从R4e tag隔离；最新设计commit **be3867b3ad65749e0e34efd245359c4123189031**，
annotated **rust-parallel-e1-design-2026-09-30**。P0完整依赖表/成本/等价性保留。
进度：`恢复 █ | 归因 █ | ECS方案/机制 █ | 生产并行原型 ░ | 新容量 ░`。

拆窄访问后Recovery/Lifecycle/Vision是System间候选；P0理想零开销重叠节省mean3.883µs。
锁定Bevy0.19.1机制探针1/2/4验证窄组件重叠、冲突串行、100/5000活动子集；
已有池2/4验证5000有序结果，空dispatch median9.125/7.084µs。这些不是实际游戏并行/净收益。
**下一阶段E2：Statistics当前批次纯计算＋有序提交，先1线程拆分/分项归因，再决定2/4。**
P0跨请求批次候选暂缓、原证据不改；不直接把全部System入池。

目标仍5000Units/1000Agents，5000Agents暂缓；生产执行/API/schema/oracle/默认1线程未改。
G008/G009/R001/R002原状态保留，无新已确认玩法GAP。原49删除、两个冻结测量目录和负结果保留。
此状态优先于下方历史下一步；无新的容量/Frontier/发布或push/merge结论。


更新时间：2026-09-30。本文面向从本次Rust迁移工作中独立出来的**Rust并行优化任务**。不需要先读完整聊天，也不需要一次性打开所有历史报告。按下列顺序恢复；当前状态优先于旧报告中的“下一步”和进度条。

## 1. 先固定起点，避免从原 Python main 开始

2026-09-30核验：

- 生产仓库：`/Users/liyang/Developer/star-main`，分支 `codex/rust-env-migration`。
- 当前生产HEAD：`7e145d169433695cd4957e186a6b2fda06813c26`；annotated tag：`rust-kernel-r4e-2026-09-29`。
- 当前实际测量/实现源码：`5147e4d8e0c33c997bd86960d87fa4b5b3ca90c5`。上面的最终HEAD仅追加文档。
- 生产main仍为原Python `6a970deaee7d9b8d3939edd102973f2377edd6ac`，尚未合并Rust迁移。
- Lab：`/Users/liyang/Developer/star-lab`，分支main，R4e证据提交 `2a2b09cc1731e2b43840fc56e1fa233693ca656f`（本交接文档是其后新增）。
- 生产工作区有49处既有用户删除：`rotk_agent/`下文件及`rotk_env/assets/fonts/sh.otf`。不要恢复、删除或顺手提交；不要`git add -A`。
- API18 / schema5 / oracle `python-r0c-3cc4ffe`。扩展SHA256：`324454a00ab8bd3559c9229e6c6c9644242d65c488585eba7d29a63b39d29405`。API号相同不保证二进制相同，仍须核对源码和扩展hash。

新并行分支应从上述R4e tag创建，例如`codex/rust-ecs-parallel`，而不是默认main。先检查任务附件/工作树和Git状态；若需要隔离，使用managed worktree并显式指定R4e ref。保留已有冻结测量目录，不将它们改成开发目录：

- `/Users/liyang/.codex/worktrees/rust-wire-observation/star-main`：5147e4d，完整资源，当前Rust测量环境。
- `/Users/liyang/.codex/worktrees/python-capacity-baseline/star-main`：6a970dea，原Python对照。

这些是本机定位提示；可迁移的复现依据是commit/tag、wheel、manifest及checksum。今后合并只允许squash merge，合并前annotated tag固定节点。本阶段未push/merge，默认Python、native threads=1。

## 2. 第一轮必读：当前事实与不可改变的边界

按顺序读：

1. [本交接文档](rust-parallel-handoff.md)：先理解设计演变和新任务边界。
2. [实验记录协议](../PROTOCOL.md)：生产/Lab分工、证据链、负结果、源码与工具SHA、归档规则。
3. [Rust System并行现状](rust-system-parallel-status.md)：当前已经并行什么、没有并行什么，以及为什么。
4. [权威状态与只读边界](../../star-main/docs/native-state-boundaries.md)：谁能写什么、缓存与展示消费者、只读任务生命周期。审计有版本和范围，不能当作覆盖所有未来写入的证明。
5. [运行接口与语言边界](../../star-main/docs/native-runtime.md)：重点读Product boundary、R4a/R4b、R4d、R4e和安装说明。
6. [Benchmark GAP台账](../../star-main/docs/native-benchmark-gaps.md)：保留历史差异、已修复项和未决风险。重点G001–G003、G008/G009、R001/R002；不要把开放风险当作已证实规则差异，也不要因并行测试通过就自动关闭。
7. [R4e最新容量报告](../experiments/2026-09-rust-1000-agent-validation/README.md)及同目录[analysis.md](../experiments/2026-09-rust-1000-agent-validation/analysis.md)、[decision.md](../experiments/2026-09-rust-1000-agent-validation/decision.md)：这是当前性能起点；commands/manifest/raw是复现依据。

完整时间线在[rust-env-migration.md](rust-env-migration.md)，全局恢复入口在[10k-online-resume.md](10k-online-resume.md)，活动优先级在[10k-online-next-steps.md](10k-online-next-steps.md)。它们保留了旧阶段，读顶部最新状态后按问题下钻，不能执行每一段历史“下一步”。2026-09-13的可视化迁移地图也属于历史快照。

## 3. 本 Session 的关键认识变化

| 早期想法/现象 | 实验或审计后的认识 | 对新并行任务的要求 |
|---|---|---|
| 1000Agent每秒观测可代表真实负载 | 用户最终选择观测→动作→墙钟思考约30秒→下一轮，思考期间不轮询 | 不以旧1Hz/Agent压力口径替代当前闭环；世界CD仍用模拟时钟 |
| 同阵营公共信息可反复复用 | Python已实现同只读批次共享，Rust也已有；不同阵营可共享底层事实，但各自做Fog投影和权限装配 | 先接已有批次能力，不能声称这是全新算法；不能跨写入、TTL或返回旧帧 |
| 把Python观测丢到多个进程可能很快 | v1每请求冻结/导出/IPC/还原的成本超过串行构建，实测更慢 | 避免逐Agent复制整个动态世界；不重复该设计而不先量成本 |
| Rust迁移意味着尽量移除Python | 用户明确采用类似PyTorch的边界：Rust高效执行世界，Python保持易用接口与生态 | SDK/策略/配置/UI/网络编排留Python；热点下沉但保留Python接口 |
| 多线程能直接解决观测慢 | R4a大面板有收益，小子集可能变慢；公共JSON树构建/复制/释放是另一瓶颈 | 分别测公共构建、面板、调度、编码、跨语言及客户端decode，不能只加worker |
| 把事实缓存起来就足够 | R3k4共享不可变编码事实，R4b改typed直接编码，R4d省服务端decode再encode，才明显减少成本 | 先减少重复工作、分配与复制；完整输出仍有按payload增长的成本 |
| ECS的System彼此少import，所以天然独立 | 它们共享组件、空间索引、事件、活动集合和随机数顺序；当前step仍顺序调用advance_* | 写出完整读写集和业务先后关系，再选择System间或System内部并行 |
| “性能迁移完成”意味着性能工作结束 | 主要计算已迁Rust，不等于System全面并行、应用集成或平台发布完成 | 分开报告计算归属、并行覆盖、容量、兼容和发布，不能混为一个百分比 |
| CPU空闲很多，世界step应优先并行 | R4e第一轮step平均0.295ms，显示系统8.679ms，展示应用2.768ms；step不含观测 | 基于实测热点选择并行对象；不承诺仅并行step就成倍加速整帧 |
| 5000Units/5000Agents是下一步 | 用户暂停5000Agents，先验1000Agents；当前已经三轮长测通过 | 保持5000Units/1000Agents主目标，未经新指示不恢复5000Agent调参 |

两个明确未采用的玩法改动：不放开叠格/穿透单位来静态化路径；不在本迁移中取消兵力损失导致的移动力弱化。后者用户倾向取消，但必须作为独立规则变更。并行不能借机删观测字段、近似Fog、延迟动作生效或更改事件提交时机。

## 4. 第二轮阅读：重要失败与成功，避免重走弯路

按需阅读README/analysis/decision，不先加载大raw：

- [Python并行观测v1负结果](10k-parallel-env-v1.md)：2worker导出约8.5ms、还原约11.5ms，而串行构建约5.5ms。冻结探针，不是动态闭环。
- [主流ECS候选路线调研](10k-parallel-ecs-alternatives.md)：System之间并行与System内分块的区别，延迟结构修改不等于可以改变游戏提交顺序。2026-09-11历史调研，实施时以锁定依赖源码/API为准。
- [R4a只读并行](../experiments/2026-09-rust-read-parallel/README.md)：已存在的固定线程池与大小查询的正负结果。
- [R3k4编码共享决策](../experiments/2026-09-rust-kernel-encoded/decision.md)：Arc只保证共享所有权，不代表并行；输出结果不能依赖后续世界生命周期。
- [R4b公共事实成本](../experiments/2026-09-rust-public-facts/decision.md)：优化数据表示优于仅增加worker的证据，微测不能冒充容量。
- [R4d传输边界与5000-Agent负结果](../experiments/2026-09-rust-5000-agents/README.md)：原字典往返/直接JSON传递区别，以及扩大帧内预算不能同时解决帧和排队问题。

旧[10k-parallel-env-proposal.md](10k-parallel-env-proposal.md)是Python时期的设计背景，**不是当前Rust并行实施规格**。如需恢复确定性基线，读[R0报告](../experiments/2026-09-rust-r0/README.md)及迁移记录中的R0b/R0c段。

## 5. 代码入口：按数据生命周期阅读

下列路径相对star-main，先用CodeGraph做结构定位，再阅读具体实现；不要一开始全仓库扫描。

| 顺序 | 文件 | 要回答的问题 |
|---|---|---|
| 1 | `native/rotk/src/runtime.rs` | Runtime拥有哪些状态/索引/活动集合？step、reset和导入在哪里形成写入边界？当前advance_*顺序是什么？ |
| 2 | `native/core/src/world.rs`、`native/rotk/src/components.rs` | 外部ID与Bevy Entity如何映射？哪些状态是typed，哪些仍是冷数据？ |
| 3 | `native/rotk/src/observation.rs` | ObservationBatch的只读借用、公共事实/Fog/面板/权限边界；prepare_panels如何join并按固定顺序合并？ |
| 4 | `native/core/src/read_pool.rs` | 已有1/2/4档固定池、分块、借用作用域、退出及并发测试；优先复用，避免重复线程池与过度订阅 |
| 5 | `native/python/src/lib.rs`、`rotk_env/runtime/native.py` | py.detach后实例Mutex的作用；外部操作为何仍串行；get_faction_state_json怎样省重复编解码？ |
| 6 | `native/rotk/src/actions.rs`、`team.rs`、`codec.rs` | 可信身份、动作次序、查询/写入分段、控制权限与响应所有权；不能让worker完成顺序决定可见世界 |
| 7 | `native/rotk/src/movement.rs`、`spatial.rs`、`vision.rs` | 最典型依赖：位置/占用更新→视野dirty→Fog投影；候选计算与确定顺序提交能否分离？ |
| 8 | `native/rotk/src/combat.rs`、`recovery.rs`、`lifecycle.rs`、`statistics.rs`、`turn.rs`、`territory.rs` | 战斗/死亡/资源/回合/胜负/统计的隐含共享写入和先后关系；针对候选System再深入 |
| 9 | `native/core/src/rng.rs`、`clock.rs`、`deadline.rs` | CPython随机兼容、消费次序、模拟时钟与活动deadline；并行不得改变RNG分配或dt语义 |
| 10 | `native/rotk/src/presentation.rs`、`rotk_env/runtime/` | 展示delta有drain/一次性事件语义，不是可随意并发的纯读；展示缓存不是第二套权威世界 |

并行线程开关不是把Runtime整体放到多个线程上。当前`with_runtime`锁住整个实例，再执行`&mut Runtime`闭包；只读面板workers在内部借稳定数据，返回前join。当前不是多Agent外部调用并发，也不是Bevy Schedule自动并行世界Systems。

依赖和安装读取根`Cargo.toml`、`Cargo.lock`、`rust-toolchain.toml`及`native/python/pyproject.toml`，以实际文件为准，不从早期方案猜版本。性能实验使用release，勿拿debug库比较。

## 6. 测试和实验入口

生产契约优先：

- `rotk_env/tests/test_native_parallel_observation.py`
- `rotk_env/tests/test_native_request_batch.py`
- `rotk_env/tests/test_native_encoded_observation.py`
- `rotk_env/tests/test_native_public_facts.py`
- `rotk_env/tests/test_native_wire_observation.py`
- `rotk_env/tests/test_native_movement.py`、`test_native_vision.py`、`test_native_combat.py`
- `rotk_env/tests/test_native_presentation_delta.py`、`test_native_r1.py`

变更触及哪些生命周期、资源或身份路径，再补相应既有契约；不能只比较速度或最终hash。比较完整解码响应、列表顺序、游戏事件和权威状态。保留M→Q→N：Q必须包含M、不含N。录制/注入墙钟元数据，不能用种子推导真实LLM响应时间。1/2/4线程的工作结果应一致，线程利用率诊断计数可以不同。

Lab入口：`tools/p3_runtime.py`、`tools/p3_local_agents.py`；轨迹与核验：`tools/rust_migration/native_loop_trace.py`、`replay_rendered_loop.py`、`analyze_1000_gate.py`；归档：`package_agent_capacity.py`。具体运行参数用R4e `results/commands.json`，不要靠摘要重新拼出另一个负载。

当前R4e：M4/16GB，5000活Units/1000合成Agents，30Hz固定dt，1线程/8ms接入预算，Cocoa2480×1239，Fog开、minimap单位层关、有限运行GC延迟、Chrome开。Agent首次请求错开0–30秒，逐Unit move/attack/wait=50/25/25，非法等待，不重抽；思考截断正态30±5秒、15–45秒，期间不轮询。

三轮30秒预热+300秒测量：帧P99为29.800/29.275/29.470ms，观测响应45.872/47.783/44.798ms，动作排队35.293/35.601/34.744ms；各30Hz，所有guard通过，5000存活、峰值同时移动171/177/173。包含Python展示/呈现，不包含限帧等待、Hub和真实LLM。不是全5000同时移动/高接触密度容量。

第三轮实际输入的4线程重放40994请求/9880tick/9880展示全部一致；不代表4线程性能达标。原生产Python与当前Rust各一次同条件60秒短测：观测service7.822→2.741ms（约2.85倍），整帧P9931.800→26.453ms（降低16.8%）；不是固定输入的纯语言比较，排队下降也不是计算加速34倍。原版、规范化Python两个负对照都保留。

## 7. 建议新 Session 的首个交付

先提交一张**读写依赖与成本表**，列出组件、索引、冷数据、活动集合、事件、随机流、展示变化队列的读写及先后约束；区分System间并行、System内并行、跨请求只读共享三个不同问题。基于现有计时选择一个候选，不先承诺把所有System并行化。

随后选一个收益可测、规则无变化的小步实现；与冻结单线程同输入对照，再做实际闭环测试。不得为凑批次跨越动作或等待更多Agent。活动集合优先O(active)，Bevy Changed不自动意味着只遍历活动实体。

进度报告附阶段状态条；生产代码/契约/用户文档在star-main，实验工具/结果/复现在star-lab。任何Benchmark相关差异写GAP台账。每阶段更新恢复入口；通过一个阶段不代表切换默认后端或整个迁移发布。
