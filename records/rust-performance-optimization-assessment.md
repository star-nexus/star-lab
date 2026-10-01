# STAR 整体性能优化评估（2026-10-02）

状态：已有证据复核与源码审查完成；下列优化是候选与投入建议，未实施、未获得新加速比。
进度：`运行链路 █ | 既有证据复算 █ | 源码/已有机制 █ | 投入排序 █ | 恢复/边界记录 █`。

目标保持5000 Units＋1000 Agents，5000 Agents暂缓。Rust执行权威世界，Python保留接口、策略、配置、UI和生态。游戏规则、观测内容、动作/RNG顺序、固定模拟dt和确定性保持。

## 1. 身份与证据口径

- 审查源码：`3b167b151c3bc32e1d54f6015d0f15d2c3dd6a74`，活动独立工作树、`codex/rust-ecs-parallel`；E5 validated节点，API18/schema5。随后GAP说明文档节点为`4657dd474c3b69eb849e11d30f32587ebb21bb70`；执行代码未改变。
- 最近完整窗口：E2 `2bc57d5f2241a578f61d71bb5774e7063a03ec25`，native4，30秒预热＋300秒测量×3；这是上海2026-10-01凌晨的旧快照，**不是E5当前二进制的新live测量**。
- 分项诊断：E3 `6d4018cc0c607a51a3783428867ba9259bb43f43`；固定规范输入、9880 tick，含预热与诊断时钟。E3普通路径、E4/E5契约与完整重放的等价证据仍归原实验。
- 机器：上述实验Apple M4／10物理及10逻辑核／16GB，Cocoa2480×1239，Chrome保持开启；native默认1，显式4不是默认切换。
- [复算结果](rust-performance-optimization-assessment.json)包含来源SHA、14个被审查源码文件的内容SHA、canonical ZIP与所用member SHA、公式和全部轮次。
- [E2正式包](../experiments/2026-09-rust-statistics-compute/README.md)、[R4e](../experiments/2026-09-rust-1000-agent-validation/README.md)、[E3](../experiments/2026-10-rust-internal-system-candidates/README.md)、[E5](../experiments/2026-10-rust-movement-visuals-parallel/README.md)保留完整raw/wheel/源码恢复链；本文不复制或改写这些历史证据。

每帧成本、每请求服务与每请求排队的分母不同，不能直接相加。各阶段P99不能相加/相减预测整帧P99。不同live轨迹之间的变化不能当作同输入因果收益。归档数据支持投入排序，但尚未把显示8ms的内部成本归因到某个绘制函数。

## 2. 最近窗口说明应把时间投入到哪里

E2三轮同一工作口径的均值范围：

| 指标 | 耗时 | 解读 |
|---|---:|---|
| 整帧工作 | 20.866–21.146ms/帧 | 不含限帧等待；含应用与Agent服务 |
| native世界step | 0.260–0.264ms/帧 | 不含Agent观测；整帧均值约1.24–1.26% |
| 展示增量提取 | 0.691–0.701ms/帧 | 已直接编码dirty组件引用；不是未优化的全World导出 |
| Python展示增量应用 | 2.693–2.748ms/帧 | 约整帧均值13%；有具体的对象/缓存失效优化候选 |
| Python显示Systems合计 | 8.491–8.748ms/帧 | 约整帧均值41%；需继续拆分归因 |
| Agent工作合计 | 3.447–3.539ms/帧 | 包含到期请求服务等；不与下面每请求行相加 |
| 观察实际服务 | 2.880–2.953ms/请求 | build1.760–1.804、外层encode0.075–0.078、client decode1.030–1.057ms |
| 观察排队 | 16.508–16.659ms/请求 | 不是构建耗时；需区分frame接纳边界与服务积压 |
| 动作排队 | 9.439–9.479ms/请求 | 单纯缩短某个step并不能保证消除此等待 |

从raw每帧复算，update中另有平均5.114–5.164ms没有分配到上述记录阶段。它可能包含调用链中尚未单独计时的工作，**不能直接命名为render、SDL、GC或allocator成本**。新的细分归因应覆盖它，并区分嵌套区间。

仅作算术示例：若世界step耗时减半，每帧约省0.13ms；若展示应用耗时减半，每帧约省1.35ms。两者都不是已实现的收益预测，但能说明投入尺度。无窗口headless ENV的排序不同：没有绘制时，观测服务、Statistics和Vision更重要。

## 3. 候选排序

优先级表示值得先验证，不能解释为已获准改变生产策略。工作量采用相对小/中/大，实际排期在首次拆分后调整。

| 顺序 | 层次/候选 | 已有依据与具体操作 | 成本/风险 | 第一验收 |
|---|---|---|---|---|
| 1 | 展示消费：字段更新与缓存失效 | 当前dirty Unit行包含9类组件；`WorldPresentation.apply`逐类deepcopy、重建对象、add_component。World对每次对象替换都使相关查询/引用缓存失效。先区分成员增删、引用替换和字段写入，尝试更新现有组件并保留空间索引更新 | 中；派生引用、Enum/path转换和字段删除语义须完整覆盖 | 同输入完整展示state/events；应用时间、对象构造次数、缓存eviction/引用版本与整帧A/B |
| 2 | 显示链路：减少每帧重新准备 | aggregate约8.5–8.7ms且有未归因update。先分Unit cull/分组/命令构建、UI、Fog patch/rebuild、RenderQueue pack/submit与平台边界；再试跨帧保留不变准备结果、复用命令/分组缓冲和必要小计算的native批量入口 | 归因小、针对改造中；画家顺序/像素/镜头变化必须一致 | 先获得完整归因，再单变量完整窗口A/B及截图；不降低图层/文字/Fog/频率 |
| 3 | 请求接入：复用已有encoded read batch | P0规范轨迹64.475%查询位于2–5请求只读段，同阵营重复仅14.573%、无重复panel。ObservationBatch/权限捕获/事实编码共享都已存在；接入已接纳连续读，不等待未来请求 | 中；请求/回调接纳与写入栅栏是关键 | 先证实接纳队列有合法批次；完整M→Q→N/错误/VLM状态，再single与batch净收益 |
| 4 | Statistics历史结构与表示 | 当前window history每批`Vec<Value>::drain`保留固定上限；E3全9880tick trim诊断均值34.408/40.919/42.818µs。比较环形缓冲/分段历史，随后考虑typed记录与按边界编码 | 中到大；裁剪包含被移除Value析构，换容器并不会消灭析构成本 | 稳态history相同上限/顺序、错误成功前缀、完整export/reset；区分memmove、构建、drop、提交 |
| 5 | Vision集合、Fog提交表示 | E3整阶段约43µs，纯几何约0.55–0.60µs，commit约27–28µs。当前代码克隆旧Vision/visibility集合、构造difference临时BTreeSet、再复制到状态与组件；先减少重复集合和临时分配，再比较表示 | 中；有序输出、LRU/refcount、离图格、阵营变化、移除不能改变 | 完整每步Fog/Vision/export/展示；A→B→A缓存反例、冷/热分层、普通stepA/B |
| 6 | 观测算法：减少全场重复统计/编码 | 每个ObservationBatch重建census，并对每阵营公共敌军投影遍历unit_entities。在先用已有batch后，审计增量总数/存活/AP可行动计数与更窄的投影候选；稳定terrain片段可按确切terrain revision复用 | 中到大；必须覆盖全部死亡/恢复/turn/import/terrain写入，不能用粗TTL | 整体完整响应与旧基线逐步相等；census/entitiesvisited、build/drop、缓存失效成本 |
| 7 | 客户端decode与真实host直传 | client decode约1.0ms/请求。Lab已native-wire，dict API仍易用；真实网络host尚未自动接入直传。先保持已编码bytes贯通和边界只解码一次，实测有必要时再评估兼容的decode/惰性访问路径 | 中；SDK数据所有权、数字/Unicode/插入顺序契约；G009未关闭 | 正确性+真实消费端服务时间；完整观测内容和结果生命周期；不拿只编码微测代替容量 |
| 8 | 调度架构：权威owner与显示解耦 | 请求等待明显大于单次服务，single-loop受每帧接纳边界影响。若前面工作后仍受显示阻塞，可研究单一权威owner执行器＋UI消费有序增量 | 大；VLM/输入/停止/reset/背压和事件一次性语义 | 先证明等待成因；固定dt、录制接纳顺序、完整增量不丢、生命周期与frame/queue/hz一起验证 |
| 条件 | 局部地图数据布局/查找与scratch复用 | 当前Spatial已动态占用+局部筛选，寻路/reachable会构造heap/hash临时状态，OrderedWorld ID查找为BTreeMap。仅在真实归因确认占比后，试cell→dense index、generation-stamped scratch或更快内部lookup | 中；稀疏/离图坐标、ID间隙、A*邻居和平局路径严格不变 | 真实路径和顺序相等，稀疏/密集分开；收益不能从大图虚拟推断 |

这份表同时覆盖架构、算法、数据结构和代码实现：窗口首先改善派生数据与重复准备；ENV首先复用请求公共工作；native再改善历史和集合表示。保留typed ECS和热/冷边界，按热点缩小数据接触面，而非以Rust代码比例或System线程数为目标。

## 4. 已有优化必须继承

1. 已有窗口空间分桶裁剪；不可再把“加camera culling”当新成果。当前Unit renderer从共享空间索引取viewport buckets，再精确bounds/Fog过滤。
2. 已有静态terrain presentation缓存、Fog surface与visibility journal增量patch、纹理/字体/标签缓存。新的display研究要量失效与重建频率，不能假设每帧都全重画Fog。
3. `RenderEngine`已有连续plain blit的`Surface.blits`批量提交，Command已有`__slots__`；geometry/custom/area/special flags是原序栅栏。新增工作应瞄准准备和临时对象，不能只重复批量调用。
4. R3k2已有精确attackable空间盘/敌军列表较小者筛选；Movement使用active IDs，Recovery使用deadline/pending/new-ID；不能重新扫描全部resident来凑任务。
5. R3k4/R4b已有typed直接编码、不可变encoded facts与只读段共享；R4c已有dirty组件引用直接序列化；R4d已有JSON直传，Lab已使用。公共编码缓冲与接口接入仍需审查，但不是从零新建。
6. E2已在真实当前批次≥128行、native2/4下并行JSON记录构建，原序commit；不能把E2收益重复计为下一阶段成果。

证据：[R3k4](../experiments/2026-09-rust-kernel-encoded/README.md)、[R4b](../experiments/2026-09-rust-public-facts/analysis.md)、[R4c](../experiments/2026-09-rust-rendered-loop/README.md)、[R4d](../experiments/2026-09-rust-5000-agents/README.md)、[P0](../experiments/2026-09-rust-system-attribution/decision.md)。R4d的5000-Agent历史负结果仅用于避免重走失败路线，本评估不恢复该目标。

## 5. System并行与大改造的投入判断

E4轻量组合保守停止、E5 Movement∥Visuals真实重叠未通过三轮稳定门槛。进一步候选Statistics kernel∥Movement，在E3逐tick配对复算的native2/4诊断零开销预算仅11.104/10.599µs，即5.069/5.062%。此处使用`kernel_wall_ns`，不是多worker累计`records_ns`，也不是对两个阶段均值取min。假设依赖已解除、输入准备/调度/提交/竞争为零；不是可实施或实测加速。

暂不优先投入完整Bevy Schedule迁移、全System线程池、GPU重写、全项目Rust化、全局替换BTree为Hash、逐AgentWorld快照/多进程还原。前几项没有当前热点净收益依据；后者已有明确负结果。现有Python snapshot进程池owner export约9ms、worker restore约11ms已超过原串行build约5.5ms；这不是需要更多worker的证据。[历史负结果](../experiments/2026-09-parallel-observation-v1/decision.md)。

GC策略已有realtime defer。E2保留91.9/102.4ms帧尾；尚未证明尾部来自GC、allocator或OS调度，不能先靠关闭GC或换分配器宣称解决。应用对象减少后，若尾仍回退，再做有时间轴、存活/分配、平台区间证据的独立诊断。

## 6. 建议下一项最小工作

首选为**展示路径归因＋展示组件更新原型**：先恢复当前窗口基线，把display内部与未归因update分清；选择一个field-update策略与旧replace策略同输入比较，复用当前delta/API，尽量从Python消费端小步开始。

验证有序完整权威状态、展示副本、事件/删除/混合实体、引用缓存、相机/缩放/Fog/选择/UI、reset/close；无诊断三轮同二进制或同依赖单变量对照，保留全部慢样本，检查mean/P99/CI。只有先通过完整推进/展示等价与净收益，再做30秒预热＋300秒真实窗口frame/queue/hz/load guards。新诊断须独立运行，不用diagnostic预算当收益。

若工作目标明确收窄到headless ENV，则第一项改为已接纳连续只读请求的batch可行性审查；Statistics历史结构和Vision提交作为后续native候选。该选择不要求减少任何观测字段、推迟动作、等待更多Agent、修改游戏采样batch/历史长度或思考节奏。

## 7. 复算与边界

在Lab根目录运行：

```bash
python3 tools/rust_migration/assess_optimization_priorities.py \
  --source /Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main \
  --output /tmp/star-optimization-assessment.json
cmp /tmp/star-optimization-assessment.json records/rust-performance-optimization-assessment.json
```

`--source`可换成恢复的3b167b1 checkout。工具按该commit读取14个文件并校验当前内容，canonical E2/E3 ZIP整体SHA以及所用6个raw/timing member SHA；重算全部三轮frame/phase均值、未归因update、全部9880 tick预算与trim。canonical包是复现依据，无需ignored scratch、安装wheel、修改冻结目录或重新运行游戏。

E2 ZIP SHA `62c5e73a2356334fc0fa85e3b5f4054a46f5f759ad7cb6c9fcef41dcd7b190ba`；E3 ZIP SHA `c3e347b145fcc5edfda304bb35030d3d3d9320861f116a5507d2b92cbd9b6abd`。结果记录工具自身SHA；本文是规划记录，未新增正式性能实验或validated运行节点，未发布Frontier。

G001–G003历史、G008/G009 OPEN、R001/R002 RISK保留；没有新增已确认玩法差异，没有借候选排序关闭GAP。生产执行代码、普通step/default1、观测/动作/规则/确定性和Python接口生态均不变。原49项删除、冻结目录与E2/E3/E4/E5标签保持，未push/merge。
