# Decision — cache unchanged text, retain gameplay and visuals

**Status:** validated implementation  
**Date:** 2026-09-10  
**Measured STAR:** `5f13218ea1b6cf563e94b61e30a1609f01c2a138`

## Decision

采用当前坐标overlay和活动飘字缓存实现，按先annotated tag后squash的流程集成。
坐标问题的大开销已被受控前后对照消除；伤害/CRIT重复栅格化与屏幕外绘制消除，不将所有攻击时卡顿都归因或承诺由本修复消失。

## Why this design

只有两处既有renderer路径变化和cull不可变集合契约，没有新的架构层/系统/调度器。
静止视图无需逐格工作；变化视图复用未改变标签；飘字仅管理活动集合。缓存自然按当前视图/活动组件有界，不需要任意TTL、全场定期清理或猜测容量上限。
像素对照和生命周期契约保障相机锚点、边缘裁剪、独立淡出以及失效语义。

## Rejected alternatives

- 关闭伤害/CRIT或坐标：改变用户反馈且不必要。
- 为整张地图所有缩放档预计算标签：加载慢且内存随地图/字号增长，当前视图缓存即可达到目标。
- 只缓存Font、仍每帧逐格font.render：仍有可避免的重复文字工作和大量提交。
- 所有CRIT共用一个可变alpha surface：会让不同年龄的效果在延迟绘制队列里互相覆盖透明度。
- 复制或异步处理世界：不是本问题所需，并行方案继续暂停。

## Headroom and remaining limits

当前固定视图/平移整帧P99均低于24Hz预算；6个冷开启样本最大37.081ms，也在24Hz预算内。不是保证任意机器/任意战斗每帧都低于预算；zoom0.5冷样本有4个超过30Hz预算，明确保留。
1000活动文字仍需O(Aactive)更新位置、alpha和提交，无法免费。UI像素提交仍有成本，Agent pump、观测编码和其他世界系统也可造成慢帧。

## Revisit

真实用户不同缩放/窗口/战斗密度出现新慢帧时，继续逐系统归因；若修改cull集合契约、坐标样式、字体生命周期或多次同帧渲染调用，重跑像素与缓存失效契约。
本修复不新增Performance Frontier。精确source/tag/squash节点和raw/compact SHA见manifest，归档后可从恢复入口继续。
