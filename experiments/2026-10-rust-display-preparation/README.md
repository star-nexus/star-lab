
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
