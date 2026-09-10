# Decision — 坐标与飘字

**Status:** analysis complete; optimization proposed  
**Decision date:** 2026-09-10  
**Measured STAR commit:** `906386312d70d77af25e4b4da883f6dd5b0fe5ef`  
**Fix / validated tag:** N/A；没有修改生产。

## 1. Decision

将坐标文字的重复构建列为已确认瓶颈。若用户安排修复，优先缓存字体及合成后的坐标标签surface，按字体大小/文字/样式复用，在视图范围和变更时维护有界缓存。这不改变ENV博弈规则、Agent信息或时钟。
当前canonical千Agent闭环中，伤害/CRIT文字准备不是首要P99来源；不以关闭战斗反馈作为容量方案，不启动并行架构。

## 2. Decision drivers

两轮坐标ON/OFF的路径与整帧量级差异稳定；实际自然战斗存在115次attack和1410个有飘字的测量帧，文字准备仍不足0.1ms。

## 3. Measured alternatives

| 选项 | 证据 | 决策 |
| --- | --- | --- |
| 坐标ON | zoom1/0.5坐标路径P99 171/727ms | 确認重复构建瓶颈 |
| 0.15下坐标ON/OFF | 均因阈值跳过 | 不能解释历史大规模实验P99 |
| 1000飘字只禁止绘制 | 生命周期仍运行；text准备消失 | 仅归因，未作产品改变 |
| 1000屏幕外飘字 | 文字准备仍约3ms | 后续可考虑提前裁剪 |
| 自然闭环飘字 | 最多11条，准备P99 0.054ms | 不列为当前主要瓶颈 |

## 4. Why this option / rejected shortcuts

不直接移除坐标或攻击反馈；前者是有用的调试功能，后者是玩家反馈。重复静态文字构建可在保留视觉的前提下减少。
不把Font预热描述为缺失；标准战斗字体已经预热。下一步若做飘字优化，应针对surface复用和屏幕外裁剪。
不从不同条件的整帧P99简单相减预测收益；短预热未隔离地图缓存过渡。后续修复A/B应记录缓存完成状态或在相同已稳定视图内切换开关。

## 5. Headroom / risks / revisit

无新运行默认值和容量门槛。若战斗密度大幅增加、长寿命/更多种文字、不同窗口缩放或用户实际攻击现场仍出现明显卡顿，补该场景的逐系统计时；不要将本canonical结果泛化。
问题状态不是CLOSED：本次只完成诊断，修复/回归/性能A/B尚未执行。

## 6. Provenance

[README](README.md)、[manifest](manifest.yaml)、[analysis](analysis.md)、[results](results/)。
