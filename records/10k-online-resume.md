# 10K / 100% moving / 30 Hz — 恢复入口

更新：2026-09-08。当前阶段：P0 已完成；P1 尚未开始。
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

## 下一项工作：P1 采样能力，然后长测

先设计并验证有界、低开销、可完整保存的 30–60 分钟 recorder，做采样开销对照。
旧 E8 recorder 容量 20000 帧，不能只把 duration 改成一小时；生产 profiler
仍是约 5 秒/4096 样本，不能靠扩大生产窗口获取长测结果。
记录存活状态/队列/缓存、GC 安全点、分段成本趋势及正常世界进度；RSS 不等于泄漏。
所有新实验工具、夹具、结果和进度记录放 Lab；STAR 只保留必要生产改动与契约测试。

开始前检查两仓库状态与远端同步，并按 exact SHA 使用 Lab 工作目录下的 detached
worktree。不要并发性能任务，不因怀疑 Chrome 或 OS 干扰删除准入慢帧。先
Instrument → Attribute → Optimize → Controlled A/B → Regression；无新证据
不重开 Cull/slots 或架构重写。P2/P3/P4 的范围和验收条件见优先级文档。
