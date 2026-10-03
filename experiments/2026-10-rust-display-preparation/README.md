> 2026-10-04用户清理内存并授权恢复；100tick守护冒烟通过，四组完整正确性正顺序重跑，随后自动进入24组顺序性能对照。实时恢复入口见records/rust-parallel-handoff.md，既有中断数据保留。

> 内存事件更新：2026-10-02 14:49系统应用内存不足，所有重型测试和自动性能矩阵已停止。完整轨迹验证未完成，无正式收益结论。恢复先读[事件](results/memory-exhaustion-incident.json)；此前小型缓存检查不代表整条链路内存安全。

# E7：显示链路与绘制准备

状态：P0完成；C候选原型完成，完整正确性正在执行。尚无正式加速比。
进度：`恢复 █ | 归因 █ | 原型 █ | 正确性 ▒ | 收益 ░ | 条件窗口/归档 ░`。

先读[分析](analysis.md)、[P0成本原始汇总](results/p0-costs.json)、[P1预注册](results/preregister-p1.json)、[原方案](../../records/rust-display-preparation-plan.md)。
执行源码67308329c3096119d65870d400bf4624f74803df；E6执行基线068c1ec。普通路径保持原样、研究默认关闭、复用原native扩展。临时完整raw位于/private/tmp/star-e7-20261002，正式归档待阶段完成。

复现命令见每次metadata的argv；Python使用活动源码.venv。完整正确性：display_preparation_probe.py --task correctness --full-authority --overscan-clock items；正式收益：--task paired --candidate empty_territory --overscan-clock wall，native1/4、baseline/reuse_typed、static/exercise各三轮。源SHA、输入SHA和扩展SHA由驱动强制校验。

P0两次真实诊断的失败guards保留，不代表容量通过。已有E6窗口失败与所有GAP保留，不更新Frontier，不push/merge。
