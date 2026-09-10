# 10K / 100% moving / 30 Hz — 恢复入口

更新：2026-09-10。当前阶段：P0 已完成；跳过 P1/P2；P3 第二轮只读批次共享已集成；主目标恢复闭环Agent，用户接受24Hz大规模运行，详见最新确认。
本文件是唯一活动恢复入口，已从 STAR 的 `docs/dev/` 迁至 STAR Lab。
先读本文件即可恢复目标、边界和下一步；执行时再按下方链接读取对应证据。

## 最新结果：24Hz随机闭环实验已完成（2026-09-10）

- 生产source仍为906386312d70d77af25e4b4da883f6dd5b0fe5ef，未修改生产代码或默认FPS；本轮仅扩展Lab运行参数与Agent调度。
- [报告/复现命令](../experiments/2026-09-p3-clock24/README.md)、[分析](../experiments/2026-09-p3-clock24/analysis.md)、[决策](../experiments/2026-09-p3-clock24/decision.md)。4个完整运行，10个archive artifacts（4raw/4compact/2fixture），已解包重算并核验SHA。
- 确认ENV固定dt=1/24，GameTime累计与delta相同；外部Agent思考用墙钟。24帧=1模拟秒，机器慢时模拟秒可以落后墙钟，不以墙钟补偿CD。
- 5000 Units/1000 Agents，canonical阵营集结布局，逐Unit move50%/attack25%/wait25%，无合法目标则等待；观测后立即提交动作，然后等待截断正态N(30,5²)墙钟秒（15–45秒），初次请求uniform(0,30秒)。无思考期轮询。
- 30s预热+300s测量、Agent每帧18ms预算：平均24Hz，7200帧=300模拟秒；frameP99=44.54ms（7.60%帧超过41.667ms，max48.94ms）；观测P99=177.97ms、动作排队P99=170.45ms，期末最老排队30.18ms，名义闭环完成99.74%。
- 测量期接受24770次move、957次attack；5000Units全部存活，同时移动采样平均120.38/最大181。不能写成5000Units持续同时移动。
- 结论：指定canonical负载可持续达到平均24Hz并无持续大队列；严格frame与100ms请求P99仍有越线。不是旧所有guard都通过的四trace容量认证。
- 负对照：interleaved全地图高接触密度，平均观测1.267MB，世界16.93Hz、观测P99=25.14s，不能承载目标。不能只报5000/1000而省略布局、动作频率和信息量。
- 9个生产时钟测试、12个Lab调度/分析测试通过。Protocol/Hub、真实LLM、并行架构均未接入；并行化继续暂停。
- 后续以本节结果为准，不重复本轮实验、不自动扩大优化范围；以前“必须保持墙钟游戏推进”的表述已作废。

## 2026-09-10 已完成实验的执行记录：24Hz固定模拟时钟＋随机闭环

最新用户要求优先：ENV每帧推进1/FPS模拟秒，CD/恢复依赖模拟时间；外部Agent以墙钟等待。
生产capped模式和GameTime/ResourceRecovery已经满足这一边界；此前Lab使用uncapped墙钟delta，本次选择fixed模式，不修改生产默认FPS。
固定源码906386312d70d77af25e4b4da883f6dd5b0fe5ef，detached worktree `runs/star-p3-clock24`。
5000 Units/1000 Agents；每Agent平均控制5个Units；初始请求uniform(0,30s)错开。
每轮观测→逐Unit随机尝试move50%/attack25%/wait25%→立即提交本轮动作→墙钟等待截断正态N(30,5²)，范围15–45s→下一轮观测。
无合法目标则等待，不重抽动作。随机动作与时序使用独立seed42派生流；不声称该分布已经由真实玩家数据验证。
采用single查询保留观测/动作交错次序；当前共享批次不能跨越新产生的即时动作。
interleaved布局确保有非空战斗机会；Fog ON、selected面板、stdlib JSON编解码、12ms Agent预算、realtime_defer、真实窗口，Chrome保留。
先30s预热＋60s测量；根据结果继续300s观察，若通过再补独立60s重复。24Hz预算41.667ms，世界≥23.76Hz，观测/动作排队/期末积压≤100ms，名义闭环完成≥95%。
战斗允许死亡，但记录实际存活/移动与接受动作；容量判断要求测量存活≥初始95%，防止负载消失造成假通过。
每帧验证dt=1/24，并对照GameTime累计与模拟delta累计。模拟时间可能在性能不足时落后墙钟，这是固定步长语义，不用墙钟追赶CD。
本次先实现Lab工具并核验，不自动启动并行架构。

## 最新用户确认：闭环Agent，24Hz可接受，30Hz为更高目标

本节优先于下方历史计划中的独立轮询要求。用户原话是“观测从1Hz/Agent建立基线，再测5、10、30Hz”，没有明确要求LLM思考期间持续轮询；助手将其解释为独立周期观测，随后错误地归因为用户的明确要求。现予更正。

- 主要交互方式：获取一次观测 → 模拟LLM思考（例如30秒）→ 提交动作 → 获取下一次观测。思考期间不额外轮询，不替换当前决策快照。
- 独立1/5/10/30Hz结果保留为额外压力测试，不再作为真实LLM闭环必须达到的主要容量标准。不能据这些压力测试失败断言闭环千Agent不可用。
- 用户接受5000 Units/1000 Agents、30秒闭环已有300秒测试的实际表现：平均世界30Hz、整帧P99=34.5907ms、观测P99=35.6697ms、动作排队P99=28.4315ms、名义闭环负载完成99.9%。旧33.333ms严格门槛失败的历史标签不改写；这组数据可作为用户接受的工程使用基线。
- 大规模评测允许世界24Hz（每步约41.667ms），30Hz保留为更高目标。既有34.5907ms低于24Hz对应预算，支持可行性判断，但不是已运行24Hz的直接验证。旧证据源于第一轮版本，不能标为最新源码的24Hz认证。
- 5000 Units为驻留/受控规模，不表示5000个单位始终同时移动。Protocol/Hub未计入，不能写成完整网络千人在线认证。
- 后续恢复工作时优先核验最新版5000/1000、30秒闭环、24Hz，再视结果评估30Hz。这一历史表述已由顶部2026-09-10时钟确认取代：ENV固定模拟步长，Agent使用墙钟。
- 并行架构继续暂停；暂不因独立轮询压力测试失败扩大优化范围。本次仅更新活动记录，未改生产运行频率、未启动新性能实验。更强硬件改善30Hz是合理假设，尤其取决于单核性能，仍需实测。

## 当前操作节点（第二轮收尾）

- STAR main：`906386312d70d77af25e4b4da883f6dd5b0fe5ef`，仅以 squash 集成；前置 main `08c857e5df39f671c5a13bf04b9af9aac0800e78`。
- 开发分支 `codex/p3-shared-observation` 保留于 `runs/star-p3-batch-dev`，tip `626d3a8db900fc18599bc96206bc76b960826999`。
- 合并前 annotated tag `p3-read-batch-pre-squash-2026-09-09` → 开发 tip；实际测量 source `72e36414de7129a1046ce36861de18eb25b2d180`（之后仅测试/文档）。
- [第二轮报告](../experiments/2026-09-p3-read-batch/README.md)、[分析](../experiments/2026-09-p3-read-batch/analysis.md)、[决策](../experiments/2026-09-p3-read-batch/decision.md)。30组诊断、65个archive artifacts，全部raw解包重算与SHA验证。
- 899生产回归、10Lab测试、跨源冻结JSON oracle通过；规则未改变。
- 同源batch-off→batch-on：3000/1000/1Hz完成11.89%→21.06%；5000/1000为8.81%→14.03%；10K不稳定获益。
- 仅15s诊断，目标规模全部未达标；无300s+3×60s容量认证、无新增Frontier。
- 原第二轮后续优化建议已被文件顶部最新用户确认取代；后续先核验最新版闭环5000/1000，不自动扩大优化范围。

## 读取顺序

1. 本文件及 [下一步优先级](10k-online-next-steps.md)。
2. [P0 归档与恢复方法](../archives/2026-09-10k-p0/README.md)。
3. [E8 正式案例](../experiments/2026-09-10k-e8-volume/README.md)：raw、manifest、SHA256、分析和负结果。
4. 需要调查历史时再读 [冻结 E8 工作记录](../archives/2026-09-10k-p0/workspace/docs/dev/10k-online-e8-volume-progress.md)
   和 [roadmap](../archives/2026-09-10k-p0/workspace/docs/dev/10k-online-roadmap.md)。冻结记录中的旧分支、路径和 local 状态不是当前操作指令。

## 目标与当前证据

10,000 resident / 100% moving / Fog ON，seed 与 phase seed 42，staggered；
12-step route planning 在测量前，execution pathfinding OFF；真实 Animation、
position commits、Vision ON，realtime_defer，uncapped，MiniMap 动态单位 OFF，
屏蔽 gameplay input。生产仍是单线程 Core ENV，无提交、动画或 Fog 延后。

继承 E6-1：`e7ba18b31870577110b591104ef8fa7b4713e43c`。
验证 runtime：`9581084835633e10d80aac849925939bc59b9138`，保留 E8-1/2/3/4。
里程碑：`scale-10k-100pct-30hz-sustained-e8`，不可移动至清理提交。
E8 Lab 初始归档：`2dfbb09b4c2fc556bcbe05dadaa1b1fe46c6de89`。

| 完整准入 trace | 秒 | 帧数 | controlled P99 ms |
| --- | ---: | ---: | ---: |
| Continuous | 305.447501 | 10240 | 32.430227 |
| Repeat 1 | 65.285074 | 2389 | 28.984507 |
| Repeat 2 | 65.301032 | 2342 | 30.026299 |
| Repeat 3 | 65.271297 | 2336 | 29.162605 |

以上完整 trace 的 controlled-work P99 <=33.33ms，所有 workload guards 和
16 个完整 30 秒 block 通过，position/Vision 约 20000 次/秒。
并非每个 5 秒窗口通过：300s 末窗 34.745ms，repeat2 末窗 37.231ms；
300s frame-body P99 34.033ms。负结果完整保留，不能宣称每帧、任意短窗口、
完整交互、60Hz 或 10K online Agents 达标。Chrome 保持开启，没有据此删帧。

保留优化消除重复 texture preparation、UI roster 查询、component-row 查询及
movement reference 查询；组件引用版本与同步回调失效契约继续受生产测试保护。
P0 只移除实验代码/材料、snapshot 的离线专用 correlation 字段，更新用户文档与
回归集合；已验证 hot path 不变。生产主分支已集成并推送：`02d0fc1b598c54a172e1122ac9ea4c1e2f46ec15`。
详见 [P0 closeout](../archives/2026-09-10k-p0/closeout.md)。

## P0 完成状态

- STAR 与 Lab 均在 `main`；源码、原始证据、归档和里程碑 tag 已保存至远端。
- STAR 已移走 57 个实验/生成文件和 1394 个结果文件（原目录约 387 MiB）。
- 已删除 29 个本地、34 个远端 10K/phase5 工作分支；无关分支及里程碑保留。
- 归档覆盖的 63 个引用 / 40 个不同提交在独立空仓库恢复通过；1451 个迁移文件定位均通过 SHA256 校验。
- 当前生产回归 869 passed，结构契约 81 passed，历史 E8 工具 9 passed，compileall 通过。
- 活动恢复和后续计划归 Lab；冻结历史记录保留旧路径/旧发布状态，勿作为当前指令。
- 清理结果和生产 SHA 见 closeout；Lab 当前收尾提交可用 `git log -1 -- records/10k-online-resume.md` 定位，避免自引用提交 SHA。

## 当前工作：P3 本地合成 Agent + ENV

用户于 2026-09-08 授权直接执行 P3，跳过 P1/P2；Protocol/Hub 与 P4 全链路暂缓。
世界目标 30Hz；观测独立以 1Hz/Agent 建立基线，再测 5/10/30Hz。LLM 决策延迟独立为 1–60 秒。早期工具错误地将观测与决策周期绑定；既有结果只代表低频闭环，不能替代用户要求的观测扫点。
活动契约、阶段检查点、复现与下一步见 [P3 工作记录](10k-online-p3-progress.md)。

生产起点 `02d0fc1b598c54a172e1122ac9ea4c1e2f46ec15`；Lab 起点
`85d142e897194264810ab94ddeab0c6f63fd9e9a`。开始时两仓库 clean main，远端一致。
开发分支 `codex/p3-agent-observation` 位于 Lab `runs/star-p3-dev`；
对照 detached worktree 为 `runs/star-p3-base`。正式测量使用固定 SHA detached worktree。

star-main 集成只允许 `git merge --squash`：合并前创建 annotated tag 固定开发 tip，
同时记录 main 前置 SHA、开发 tip/tag、squash 后 main SHA。已发布 tag 不移动。
所有实验工具、夹具、raw、分析和记录留 Lab；STAR 留生产代码、必要契约测试和用户文档。
Chrome 保持开启；性能任务不并发，不因怀疑系统干扰删慢帧。


## 历史检查点：P3 第一轮收尾（2026-09-09）

优先阅读 [P3 第一轮报告](../experiments/2026-09-p3-local-agents/README.md)、
[分析](../experiments/2026-09-p3-local-agents/analysis.md) 和
[决策/下一步](../experiments/2026-09-p3-local-agents/decision.md)。

- STAR main：`08c857e5df39f671c5a13bf04b9af9aac0800e78`。
- 合并前 annotated tag：`p3-observation-pre-squash-2026-09-09` → `c9737451de97f1b1903123377a1514227c3ffdf5`。
- 性能测量实现：`e8b48c0568fb8830055bf053a724acc2b4e5c04c`；tag tip 仅追加文档/注释。
- 按 `git merge --squash` 集成，main 单 parent，树与 tag 一致；881 回归、81 性能契约、7 Lab 测试通过。
- 独立1Hz观测：3000 Units/1000 Agents完成12.06%请求，5000/1000为8.99%，10000/10000为0.58%。
- 5/10/30Hz已在5000/1000分别扫点。所有规模数据是15s诊断，不能发布容量。
- 较早5000/1000/30s顺序闭环，60s通过但300s整帧P99=34.591ms失败；所有负证据保留。
- 24组运行compact/raw ZIP已归档、SHA256核验、解包重算；fixture按hash单份保存。
- 不新增Frontier，不移动E8里程碑；P3容量目标OPEN，Protocol/Hub继续暂缓。

**下一项**：在保持共享视野和实时合法性的前提下，设计显式只读批次，复用同一快照的阵营共享观测构建。
先做共享部分与Agent私有owner/commandable/affordance的成本拆分、失效契约与对照，
再按独立1Hz验证3000/1000，不能改回低频决策闭环作为替代。
共享批次 API 正在第二轮开发分支验证；生产 main 尚未包含它，P3 容量仍 OPEN。

生产 main 与 pre-squash annotated tag 已原子推送且远端 SHA 核验通过；本轮 Lab 归档提交及其祖先一并保存至 origin/main。

## 第二轮：只读批次共享（已集成，以下保留阶段记录）

已形成 [只读批次共享实施方案](10k-online-p3-read-batch-plan.md)。用户已授权实施；新分支 `codex/p3-shared-observation` 位于 `runs/star-p3-batch-dev`，起点为生产 main `08c857e5df39f671c5a13bf04b9af9aac0800e78`。
采用保序短批次、按需构建、批次结束释放；跨阵营复用基础事实，阵营分别筛选情报，逐Agent判断权限。
完全叠格方案已放弃。用户认同取消兵力导致的移动力弱化，该规则调整单独处理，不混入本轮观测性能A/B。


第二轮阶段 A/B 已实现：同步保序前缀 API、32 请求上限、预算、异常释放、
批次内全场 census/阵营公共视图/逐 Unit 面板/跨阵营地块与组件查询复用，权限逐请求。
生产回归 888 passed；Lab 三路调度及分析测试 10 passed。
阶段 C 下一步：固定源码和工具提交，串行运行 single / batch-off / batch-on 的 3000U/1000A/1Hz 诊断。
三路均包含 JSON 编码与客户端解码；与第一轮工具相比新增解码开销，不能当作完全相同的历史基线。
原始堆序号、过期请求和读写屏障保留；周期性过期请求重排边界也有契约测试。
本检查点尚无新性能结果，不作容量或加速倍数结论。

首版 source `3017547a87360a667b6b6cb13def21d63b528399`、tooling `64cc1697f1c90bbfa5baa0f06b2e44eecc38191d`
完成 14 个诊断点（含 stdout 未落盘的首个 single，不用于受控对照）。
3000/1000/1Hz：single 11.69%、batch-off 11.91%、batch-on 19.55%；均为 15s、非容量验证。
10K 首版 batches=requests=494，说明首张快照已耗尽批次预算，不能获得复用收益。
检查发现 census 预取了所有位置和 AP，已调整为按组件类型索引、位置按需读取、AP 只统计所查阵营。
891 生产回归和 10 Lab 测试通过。下一步固定新 source，对首版负结果做同配置重测；不得删掉首版。

修正版 source `72e36414de7129a1046ce36861de18eb25b2d180` 完成 15 个重测点。
同 source 的 batch-off→batch-on：3000/1000 完成 11.89%→21.06%，5000/1000 8.81%→14.03%。
10K/1000 为 3.48%→2.95%，仍不能有效摊薄首张快照；不宣称全规模提升。
30s 决策且独立 1Hz 的3000/1000为34.25%；5/10/30Hz和非空战斗均保留。
全部目标规模仍有严重积压，故不进入容量认证长测，不新增 Frontier。
另以当前生产 main 和修正版独立进程生成冻结世界 JSON oracle，3状态×10请求，逐字节相同；
修正版每个状态内部同时验证 single / batch-off / batch-on 解析后逐字段等价。
下一步：补全冷构建/命中计时诊断，归档与重算，然后按预先 tag + squash 流程集成。

第二轮最终状态：已归档、已 squash 集成；阶段记录中的“下一步/尚未”只描述当时检查点，以文件顶部当前操作节点为准。

STAR main、`codex/p3-shared-observation` 和 `p3-read-batch-pre-squash-2026-09-09` 已原子推送，远端SHA已核验。Lab本轮归档与恢复记录由当前收尾提交发布；可用 `git log -1 -- records/10k-online-resume.md` 定位，避免自引用SHA。

2026-09-10 首个60s interleaved结果（source9063863/tool359d267）：时钟guard全通过，5000单位全部存活，接受2511次move和960次attack；世界16.93Hz，frameP99=70.90ms，观测P99=25.14s，完成50.98%名义闭环量。每次观测平均1.267MB，构建18.61ms/编码6.71ms/解码6.46ms。该高接触密度布局不能承载目标，不改写负结果。
接下来仅改layout为canonical（与此前5000/1000低频闭环相同），其余参数不变，30s预热+60s对照；若通过，继续300s及独立重复。并行化不启动，不改变动作概率或思考分布。

canonical/12ms的60s对照：世界24Hz、frameP99=36.28ms、move/attack与模拟时钟guard通过；观测/动作排队P99约484/488ms，短时突发尚有积压，名义闭环完成100.41%（零服务时间参考过程与实际过程的测量窗边界不同，可略大于100%，不是重复执行）。
下一次保持全部参数，只将Agent每帧预算12ms→18ms，验证是否能以41.667ms帧预算内余量吸收突发。先60s，再300s；不删去12ms结果。

canonical/18ms的60s对照：世界24Hz、frameP99=41.10ms，观测P99=123.46ms、动作排队P99=118.56ms，期末积压≤100ms，名义完成100.46%。相比12ms尾延迟改善，帧余量缩小；未通过旧100ms请求P99严格门槛，但不据此称工程不可用。
下一步固定18ms参数运行30s预热+300s持续观察；不继续调参，不因短测的轻微SLO越线扩大架构改动。这是长期实用性诊断，不自动升级成旧门槛全部通过的容量认证。
