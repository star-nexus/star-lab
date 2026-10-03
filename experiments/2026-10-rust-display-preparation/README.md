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
