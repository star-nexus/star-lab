# Decision — E1 ECS parallelism exploration

**Status:** accepted — design/prototype choice, no shipped parallel runtime

**Decision date:** 2026-09-30

**Validated STAR design commit:** `be3867b3ad65749e0e34efd245359c4123189031`

**Validated design tag:** `rust-parallel-e1-design-2026-09-30`

## 1. Decision

下一阶段E2先拆Statistics**当前调度批次**的独立计算和按原行序提交，使用1线程
建立严格等价及gather/compute/JSON/commit/trim分项归因；仅对证据支持的纯计算
接已有每实例ReadPool2/4线程。System间Recovery/Lifecycle/Vision保留为可行的
窄访问重构路线，当前不作为首个吞吐优化点。P0跨请求共享作为独立暂缓候选保留。

## 2. Decision drivers

- 保持5000/1000、完整信息/规则/动作顺序/确定性及Python接口生态。
- Statistics成本最大，但可并行占比未知；不将整个0.167ms当可并行时间。
- 三个无规则边小System目前理想重叠mean3.883µs，调度成本量级不能忽略。
- 活动/到期/统计当前batch索引继续限定工作，不以全扫描制造并行收益。

## 3. Measured alternatives

| Option | Causal evidence | Decision |
|---|---|---|
| 窄Query/独立Resource的持久Bevy Schedule | 锁定探针disjoint2、conflict/exclusive1 | 可行路线；要解耦Runtime资源、错误gate和全局池所有权，后置 |
| scoped纯计算＋有序提交 | 已有池5000有序结果相等，dispatch7–9µs量级 | 首个内部原型路线；先串行拆分和分项测量 |
| 活动子集par_iter_many_unique_mut | 5000中仅100变化 | 保留给稀疏组件更新；不依赖迭代顺序/结构写入 |
| Recovery/Lifecycle/Vision立即并行 | P0理想上限mean3.883µs | 当前成本优先级较低；可单独做依赖验证 |
| 整体Runtime锁/独占World包装 | 冲突探针全串行 | 拒绝作为并行实现 |

## 4. Why this option

Statistics是最大的已归因世界阶段。小范围提取当前batch的纯叶子能先揭示真正
独立计算，而不引入全局Schedule/资源大改或第二套权威世界。首个阶段的成功
标准是串行拆分等价性和成本解释，之后才是净并行收益。
候选行按原ordinal返回Result，提交精确成功前缀，再抛相同首错；不能全量预验证
回滚或让后来行先改状态。cycle.take/错误状态、缺Observation插入、旧Fog、
history retention、phase cadence和JSON可见顺序也必须相同。

## 5. Why not the alternatives

全System线程池无法消除真实旧状态/结构依赖。全世界快照或帧末提交会重复复制
成本或改变即时生效。小System虽然语义上最容易拆，但当前理想节省与机制开销
不支持先做默认调度替换。直接par_iter_mut＋worker事件/索引写入不能保证顺序。

## 6. Headroom and scaling rationale

本阶段没有测得最小有效worker数或并行crossover，默认Python/native1线程不变。
统计batch_size128等参数不变。净收益门槛应来自同输入当前batch的完整调用、
小/空批次负结果以及真实窗口帧与排队，不能取合成大批次最佳值作为默认。
全局ComputeTaskPool与每实例ReadPool必须选择一种预算所有者，避免每实例池再
叠加自动全局池/嵌套阻塞；混合实例/reset/close是后续原型必验项。

## 7. Risks / trade-offs and gates

生产设计第6节列出E2具体gates：none/dummy/window、各统计phase、零count首/中/末行
部分错误、缺组件、周期完成、Fog旧/新边界、worker错误/reset/close；串行完整对象
对照后再1/2/4全40994请求/9880tick/9880展示重放。最后同条件5000/1000实际窗口，
高active/highdirty作为独立控制组。真实规则/观测/事件/RNG不因性能收益让步。
本阶段G008/G009/R001/R002继续开放；未确认新增GAP，也未关闭任何已有GAP。

## 8. Revisit when

- Statistics独立计算比例不足，串行构建/trim/提交才是热点。
- 高dirty/高active真实目标使Vision或Movement独立计算超过净调度成本。
- 新写入点、导入组件组合、缓存容量或错误行为改变当前候选读写集。
- 应用集成目标重新要求跨请求共享；独立恢复P0候选，不混同System调度。

## 9. Provenance

[Reproduction](README.md)、[Manifest](manifest.yaml)、[Analysis](analysis.md)、
[Decision-grade metrics](results/comparison.json)、[Package hashes](results/packages.json)。
E1只为设计/机制检查点，真实容量起点仍R4e；无push/merge或Frontier更新。
