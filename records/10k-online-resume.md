# 10K / 100% moving / 30 Hz — 恢复入口

更新：2026-09-09。当前阶段：P0 已完成；跳过 P1/P2；P3 第一轮观测优化已集成，千 Agent 容量目标未达成。
本文件是唯一活动恢复入口，已从 STAR 的 `docs/dev/` 迁至 STAR Lab。
先读本文件即可恢复目标、边界和下一步；执行时再按下方链接读取对应证据。

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


## 最新检查点：P3 第一轮收尾（2026-09-09）

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

## 第二轮实施中：只读批次共享

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
