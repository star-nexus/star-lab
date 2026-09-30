# Analysis — E1 ECS parallelism exploration

## 1. Observation

Runtime step在c058d75仍顺序推进Clock→Statistics→Movement→Visuals→Recovery→
Lifecycle→Vision→Capture；所有方法取得整体可变Runtime。P0固定输入9880tick的
均值为Statistics0.167297ms、Vision0.045143ms、Movement0.027429ms。
R4e现实统计batch_size128，不是每tick扫描5000统计行。

## 2. Competing hypotheses

H1：只将原advance方法包成Schedule Systems即可并行。
H2：缩窄组件/资源访问后，部分System可重叠；部分只能内部纯计算并行、有序提交。
H3：目前最明显的无规则边System群足以值得默认线程调度。
H4：当前Statistics的最大总耗时足以证明全部0.167ms可以并行。

## 3. Instrumentation / diagnostic changes

生产只增加设计文档，无执行修改。Lab独立Rust探针使用锁定Bevy0.19.1和实际
MovePoints/Vision/OrderedWorld/ReadPool类型。原子计数＋两System会合观察最大同时
执行body数；人为2ms等待不是计时。分别测独立组件、同组件、同Resource不同字段、
独占World；内部Query对5000实体只提交100个唯一活动handle。
另用已有ReadPool验证5000有序整数结果，并在100次预热后测1000次空作业dispatch。
按每个原P0tick计算sum(Recovery,Lifecycle,Vision)-max，重算理想重叠上限。
工具、原文件和输入hash在manifest/metadata/comparison中。

## 4. Evidence

| Evidence | Result | Interpretation |
|---|---|---|
| 窄组件System最大并行body，threads1/2/4 | 1/2/2 | H2的机制部分成立；不等于真实Recovery/Vision已通过 |
| 同组件、同Resource字段、独占World | 全为1 | H1不能绕过可变访问粒度；Runtime mutex也不能产生该并行 |
| active par_iter_many_unique_mut | 5000常驻、100选中、100变化 | 支持O(active)候选实现接口；不证明实际worker参与/顺序 |
| scoped5000有序输出 | 2/4线程均等于串行整数结果 | 支持按原ordinal接回结果的机制 |
| scoped空作业median/P99 | 2线程9125/13833ns；4线程7084/10625ns | 分发/等待/结果簿记非零；不是游戏性能或净收益 |
| R/L/V理想重叠节省 | mean3882.529ns；P9913292ns；max49875ns | 当前负载缺少优先换整个Schedule的成本依据 |

源码审查识别R↔L、R↔V、L↔V在Visuals结构操作结束后拆窄访问的候选。
Statistics读旧Position/MP/Fog，不能与相应writer完整并行；Visuals会产生/删除实体。
错误会留下此前行/全局时间写入并阻止后续阶段；Schedule.after不是成功依赖。
这些规则边界在生产设计矩阵逐项列出，未以简化探针替代审查。

## 5. Root cause

当前未并行既有接口粒度原因，也有真实规则、结构和错误提交依赖。
ECS存储本身和multi_threaded特性不会自动把整体可变Runtime变成窄System。
机制证据支持窄访问调度和唯一活动子集接口，但不能证明真实System可任意换序。
尚未查明Statistics内部计算/JSON构建/提交/trim的成本比例，H4仍未证实。

## 6. Causal chain

```text
组件/资源/结构/事件读写集和旧状态采样
  -> 可重叠计算与必要有序提交边界
  -> 锁定API机制验证 + P0原始阶段成本
  -> 先Statistics串行叶子拆分/成本分项，再决定2/4并行
```

## 7. Rejected explanations / designs

- “不同System无直接调用即可并行”：Movement与Vision/Capture经新Position和索引相连。
- “同Resource不同字段等于独立”：探针中仍串行，需真实资源拆分。
- “先全部入线程池靠mutex”：总体写锁继续互斥，也无法表达先错中止。
- “统一deferred command到帧末”：改变即时死亡/结构可见性/事件顺序。
- “全世界快照后并行”：重复此前跨进程复制负结果，不能因便于实现重复引入。
- “Vision miss去重即可”：容量1、键A/B/A改变命中/eviction/stamp状态；必须精确规划
  元数据序列，只有纯LOS几何可去重计算，Fog引用计数与提交仍有序。

## 8. Limits of the evidence

本次是设计与机制验证。没有真实System并行实现，没有真实游戏等价性/首错测试，
没有并行step净收益、应用帧/排队收益、窗口容量或新的Frontier。
合成2ms会合不能当速度测试，1000次空作业不能与P0直接相减为净收益。
P0成本包含录制预热，来自headless成对重放；真实高dirty/密集战斗可能改变优先级。
不同资源行为仍需检查typed/cold状态、活动索引、事件、LRU、RNG和结构操作。
进程全局Bevy池和每实例ReadPool的预算/重置/关闭问题未实现验证。
所有旧GAP/风险保持原状态，未增加已确认规则差异。

## 9. Raw evidence

[Compact summary](results/comparison.json)、[Overlap](results/overlap-ceiling.json)、
[Package index](results/packages.json)、[Manifest](manifest.yaml)。Raw ZIP保存五次完整
输出、构建/lock日志和逐采样数据；P0timings在其规范raw包中，完整SHA链可重算。
