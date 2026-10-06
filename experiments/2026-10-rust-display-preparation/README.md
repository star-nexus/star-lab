
## E7 P2仅第四组恢复，6GiB预算（2026-10-06，最新）

用户退出Chrome并授权重启、进一步增加单进程预算。预检内核压力normal，查询可回收余量72%；实时swap查询仍有既有交换占用，因此不记录“交换为零”结论。前三组完整证据及全部raw已验证复用，不重跑；本次只执行reuse_typed/native4/static，进程限额6144MiB（6GiB）。系统warning/critical策略、原guard代码、probe、产品HEAD5b9658b/native扩展不变。
专用入口tools/rust_migration/resume_final_display_p2.py；目录/Users/liyang/Developer/star-lab-runs/e7-p2-20261006-fourth-retry/runs。预注册E7 results/p2-fourth-retry.json，冻结工具display-preparation-p2-fourth-retry-tools.zip。已验证三组原始证据、第四组单独派发及预算传递的控制；不把mock方法控制视为正确性通过。完成后finalize_display_correctness.py显式核验各组2500/2500/5120/6144MiB，不冒充统一资源预算或性能结果。
历史第四组中断3500里程碑和全部失败证据保留；新完整重放从头开始，成功才计入4/4。若再资源/校验失败，保留并停止，不自动反复重启。自动收尾只到P2，不启动P3或普通默认，不push/merge；既有GAP、容量/Frontier和5000Agents暂缓边界不变。
进度：`P2完整通过 3/4 ███████░░░ | 第四组专用恢复/预算核验 █ | 第四组重放 ▒ | P2最终归档 ░ | P3/窗口/默认接入 ░`。


## E7 P2第四组系统压力中断（2026-10-06，最新）

完整通过保持3/4；三组完整40994请求/9880tick及权威/展示/命令/像素/raw SHA再次核验。第四组reuse_typed/native4/static于20:32（Asia/Shanghai）运行4940.27秒后，由4932.417/4937.432秒两次system warning样本停止（SIGINT，child_exit=-2），最后正式进度3500tick；之后frames3600仅为render debug，不能据此补计完整tick。
峰值RSS1706868736 bytes（约1.59GiB）、采样footprint1288490188 bytes（约1.20GiB），均低于本轮5120MiB；停止原因仍是独立系统压力策略。堆栈在显示后权威JSON导出比较，错误为KeyboardInterrupt而不是AssertionError，日志未报告等价失败；中断不能计作通过，也不能据此证明内存耗尽或缓存泄漏。
证据E7 results/p2-fourth-interruption.json；守护、完整子/父日志、执行状态与启动身份已归档并核验内外SHA。当前测试/收尾均已退出，e7-p2已PAUSED，不自动反复重启、不修改冻结工具或进一步放宽守护。下一步保留三组成功，仅在明确新的运行条件或系统压力策略后受控重跑第四组；不能用现有恢复工具原样重复第三组。
进度：`P2完整通过 3/4 ███████░░░ | 第四组中断归档 █ | P2最终完成 ░ | P3/窗口/默认接入 ░`。产品HEAD5b9658b及probe/native/guard保持、既有GAP不关闭、容量/Frontier不更新、不push/merge。


## E7 P2第三组完整通过，第四组运行（2026-10-06，最新）

reuse_typed/native1/exercise已完整通过40994请求/9880tick：完整权威19760、展示投影19760、命令19760、像素19760及完整冷World99检查。流与最终权威指纹、全部raw SHA、固定源码/probe/扩展/输入身份与前两组一致；5120MiB守护passed，系统压力采样均normal。原始样本、权威/像素指纹、guard与日志已归档，内外SHA核验。证据E7 results/p2-typed-t1-exercise-completed.json。
第四组reuse_typed/native4/static已由原父任务自动启动，初次核对到500/9880tick；继续等待，不重复启动、不修改冻结执行工具。完整通过现在3/4，尚未完成P2，不代表性能收益或一般无泄漏结论；预算前两组2500MiB、本组5120MiB分别记录。
进度：`P2完整通过 3/4 ███████░░░ | 第三组证据/校验 █ | 第四组 ▒ | P2最终归档 ░ | P3/窗口/默认接入 ░`。产品HEAD5b9658b、49删除、冻结目录与GAP/容量/Frontier保持，不进入P3、不启用默认、不push/merge。


## E7 P2提高单进程预算并恢复（2026-10-06，最新）

用户重启并授权再次运行、显著放宽2500MiB单进程限额。预检内核压力normal；查询可回收余量78%。剩余两组串行采用5120MiB（5GiB），系统warning/critical保护保持；原probe、产品源码5b9658b和native扩展未改。提高进程限额不解决此前warning触发，若再触发仍停止并保留证据，不自动循环重启。
前两组完整证据与全部raw已核验复用，不重复运行；历史49删除及两个冻结工作树保持。新持久目录/Users/liyang/Developer/star-lab-runs/e7-p2-20261006/runs，输入及继承证据仍引用Oct5持久目录。预注册E7 results/p2-budget-resume.json，冻结工具display-preparation-p2-budget-tools.zip；原守护代码只通过既有--limit-mib参数改变预算，包装与收尾接口新增显式预算/日期，核验错误预算和中断不会算通过。
完成后需四组完整40994请求/9880tick、全部权威/展示/事件/命令/像素检查与SHA；报告明确前两组2500MiB、后两组5120MiB，不冒充统一内存预算、一般无泄漏或性能收益结论。自动收尾只完成P2；不启动P3、默认路径、不push/merge，容量/Frontier和既有GAP不变。
进度：`P2完整通过 2/4 ▓ | 提高预算/身份核验 █ | 剩余两组恢复 ▒ | P2收尾 ░ | P3/窗口/默认接入 ░`。


## E7 P2重启尝试再次资源中断（2026-10-05，最新）

完整通过仍为2/4，本轮重新核验前两组完整40994请求/9880tick及全部raw SHA、权威/展示/命令/像素检查与守护。重启后的第三组reuse_typed/native1/exercise在运行180.95秒后，被175.160/180.166秒连续两个system warning样本停止（SIGINT，child_exit=-2）；第四组未启动，无运行中的测试或收尾进程。没有tick里程碑输出，不能推算已完成tick数；日志未报告等价错误，中断也不能计作通过。
测试进程峰值RSS为1371127808 bytes（约1307.6MiB），最新采样footprint为1001494937 bytes（约955.1MiB），均未达到2500MiB限额。实际触发的是系统整体压力；中断堆栈位于完整权威JSON导出，不证明该位置是根因，也不证明E7缓存泄漏或Chrome是原因。
证据：[E7本轮中断](results/p2-reboot-interruption.json)，原日志、守护、父进程状态、输入恢复身份全部归档并核验内外SHA256。e7-p2已PAUSED，不反复自动重启、不放宽守护。下一步先审查持续系统压力与正确性harness资源成本，再决定新的受控恢复；本轮未修改测量源码/probe/守护。
进度：`P2完整通过 2/4 ▓ | 本次中断归档 █ | 剩余两组受资源阻碍 ▒ | P3/窗口/默认接入 ░`。产品HEAD固定5b9658b，既有GAP不关闭、容量/Frontier不更新、不push/merge。

> 2026-10-05最新：重启后以正常内存压力重新恢复P2。持久目录/Users/liyang/Developer/star-lab-runs/e7-p2-20261005；前两组归档结果已验证复用，剩余两组串行运行并自动收尾。尚未完成P2；历史中断继续保留。

> 最新核对：P2未完成，仅2/4完整通过。恢复第三组再次被system warning守护中断；第四组未启动。e7-p2自动跟进已暂停。见results/p2-recovery-interruption.json；此前运行中状态是历史快照。

> 2026-10-04用户清理内存并授权恢复；100tick守护冒烟通过，四组完整正确性正顺序重跑，随后自动进入24组顺序性能对照。实时恢复入口见records/rust-parallel-handoff.md，既有中断数据保留。

> 内存事件更新：2026-10-02 14:49系统应用内存不足，所有重型测试和自动性能矩阵已停止。完整轨迹验证未完成，无正式收益结论。恢复先读[事件](results/memory-exhaustion-incident.json)；此前小型缓存检查不代表整条链路内存安全。

# E7：显示链路与绘制准备

状态：P0完成；C候选原型完成，完整正确性正在执行。尚无正式加速比。
进度：`恢复 █ | 归因 █ | 原型 █ | 正确性 ▒ | 收益 ░ | 条件窗口/归档 ░`。

先读[分析](analysis.md)、[P0成本原始汇总](results/p0-costs.json)、[P1预注册](results/preregister-p1.json)、[原方案](../../records/rust-display-preparation-plan.md)。
执行源码67308329c3096119d65870d400bf4624f74803df；E6执行基线068c1ec。普通路径保持原样、研究默认关闭、复用原native扩展。临时完整raw位于/private/tmp/star-e7-20261002，正式归档待阶段完成。

复现命令见每次metadata的argv；Python使用活动源码.venv。完整正确性：display_preparation_probe.py --task correctness --full-authority --overscan-clock items；正式收益：--task paired --candidate empty_territory --overscan-clock wall，native1/4、baseline/reuse_typed、static/exercise各三轮。源SHA、输入SHA和扩展SHA由驱动强制校验。

P0两次真实诊断的失败guards保留，不代表容量通过。已有E6窗口失败与所有GAP保留，不更新Frontier，不push/merge。

## 2026-10-04 接续工具

恢复预注册见[preregister-resume](results/preregister-resume.json)，精确工具快照及全部阶段已有证据由artifacts/SHA256SUMS覆盖。当前源码固定5b9658b，测量期间不提交产品文档，GAP进度暂记录[Lab台账](results/open-gap-status-resume.json)。

P2/P3主进程运行中，不重复启动。条件监督器continue_display_preparation_confirmation.py等待resume-progress.json的P3完成状态，复算全部24组，只有普通native4两脚本各三轮通过才串行运行8个单实例完整重放；无诊断、原1.5ms预算、2.5GiB保护。确认方法控制仅为合成逻辑校验。P3或确认失败就归档负结果；确认通过后仍待三轮真实窗口对照和最终归档。

接续命令（只允许一个监督器；已有confirmation-progress.json时拒绝重复）：

```bash
/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main/.venv/bin/python tools/rust_migration/continue_display_preparation_confirmation.py --source /Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main --source-sha 5b9658bc668b7d13f801351162f255f30622b32a --trace /private/tmp/star-e7-20261002/inputs/rust-300-r3.trace.json.gz --runs /private/tmp/star-e7-20261004
```

第一组完整P2已归档并通过原始载荷校验。后续窗口接续工具continue_display_preparation_live.py及配置见[窗口预注册](results/live-preregister.json)；等待confirmation-progress.json通过后才启动六次Cocoa运行。最新[默认接入授权](results/default-adoption-authorization.json)替代此前最终保持关闭的限定；测量期间仍保持原默认。

## P2第二组与默认接入准备

native4/exercise完整40994请求/9880tick通过，见[第二组证据](results/p2-t4-exercise-completed.json)。四组仅完成两组；没有正式速度结论。

[默认接入准备](results/default-patch-preparation.json)保存精确基线、补丁及结果文件SHA。补丁仅给WindowMapRenderSystem增加默认update frame scope，保留显式baseline控制；在临时模块验证默认选择、baseline、嵌套和异常恢复通过，未修改活动产品源码。未来所有采用门槛通过后，先应用补丁，再做完整回归及真实默认路径验证；不能把这四项dispatch检查当完整像素/性能验收。
