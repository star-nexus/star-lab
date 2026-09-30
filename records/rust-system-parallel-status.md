# Rust System并行：当前状态与边界（2026-09-29）

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


当前验收目标收回到5000 Units＋1000 Agents；5000-Agent扩展暂缓。用户Python接口、策略、窗口和网络编排继续保留Python。

## 已有能力与缺口

- Python时期已实现同步只读批次共享，测量节点72e36414、集成9063863。原生产main6a970dea已包含它。
- Rust的ObservationBatch也已实现只读段公共事实和Unit面板复用；R4a另加入2/4线程Unit面板计算。
- 当前Lab post-action闭环逐请求调用single入口，因此没有利用跨请求只读批次。这是已有能力的接入缺口，不是一个新的共享算法。
- R4d的get_faction_state_json省去服务端重复JSON往返，仍是逐请求入口。
- 当前Runtime::step显式顺序调用各推进阶段；不是由Bevy Schedule分配所有System到多个核心。主要世界计算已在Rust，不等于System并行、容量或发布全部完成。

代码锚点：生产 `native/rotk/src/runtime.rs:341`、`native/rotk/src/movement.rs:259`、`native/rotk/src/vision.rs:395`、`native/rotk/src/observation.rs:412`。核验源码5147e4d8e0c33c997bd86960d87fa4b5b3ca90c5（R4d实现；72ea765仅追加文档）。

## ECS为什么适合并行，又为什么不是自动并行

ECS把状态与逻辑分开，使System可以显式声明读写组件和资源。这正适合依赖调度。System之间不直接调用仍可能共同访问同一数据，或通过事件形成生产/消费关系。

当前真实例子：advance_movement写Position、Movement、spatial，跨格时写vision_dirty；advance_vision随后消费新位置及dirty事实。若把二者直接并行，可能读到本tick移动前状态，改变Fog及Agent可见信息。事件替代函数调用后仍需要明确哪些事件本tick生效、消费顺序是什么。

Bevy支持让没有冲突的System并行，但冲突的组件/整个World访问会阻止并行：[官方schedule文档](https://docs.rs/bevy_ecs/0.19.1/bevy_ecs/schedule/index.html)。当前多个advance_*方法取得整体&mut Runtime，接口没有把最小读写集交给调度器。需要分解借用与共享资源访问，而不是只打开multi_threaded开关。

## 合理的后续实现方式

1. 列出每个阶段读取/写入的组件、空间索引、活动集合、事件和随机数；标记依赖及原执行顺序。
2. 让只读或读写互不冲突的System通过明确参数接入Schedule；独立实体计算可以在System内部并行。
3. 空间占用、死亡/生命周期、统计、共享集合及随机数消费的提交保持规定顺序；必要时每个任务生成独立结果，再有序合并。
4. 同一录制输入的1/2/4线程完整状态、响应和事件必须一致；随后再测真实窗口整帧与排队收益。

这里没有宣称任何尚未审计的System对已经可安全并行；不能先把全部System放上线程池，再靠锁随机决定次序。

## 优先级依据

R4e第一轮长测世界step平均0.295ms/P990.758ms，整帧P9929.800ms。这个step不包含全部Agent观测、Python展示和呈现；其耗时不能代表整个ENV处理量。System并行值得保留为R4工程项，但针对当前负载，不能仅靠加速这段亚毫秒step得到数倍整帧提升。

R4e已完成当前1000-Agent三轮长测及原生产/规范化Python同条件短测，见[报告](../experiments/2026-09-rust-1000-agent-validation/README.md)。将世界计算已迁移、并行覆盖程度、容量验收、Python上层接入和发布分别报告，不再笼统称“性能迁移全部完成”。
