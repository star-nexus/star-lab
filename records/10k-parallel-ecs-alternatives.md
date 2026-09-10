# 并行 ECS 技术调研与 STAR 候选路线

日期：2026-09-11。状态：官方资料调研与设计比较，未实施新架构、未运行新性能实验，不新增容量结论。

## 依据与版本

- 用户要求：探索其他方案，尤其是主流游戏开发技术如何并行 ECS。
- STAR main：`6a970deaee7d9b8d3939edd102973f2377edd6ac`。
- 当前开发分支 `codex/parallel-observation-v1`：`3c4fba1a40fccee7bfc06575ade338c30a4b784e`，工作区干净；原型保留，不合并 main。
- 已完成证据：[v1 冻结实验](../experiments/2026-09-parallel-observation-v1/README.md)、[成本分析](../experiments/2026-09-parallel-observation-v1/analysis.md)。主测量工具 `57343ce1b18f457b745391b5352081f547e40b45`；证据归档 Lab `15d1ff5e50305925bd000e190b14258026b8cf05`。
- 本轮核对的运行时为 Python 3.13.12，`sys._is_gil_enabled() == True`，`Py_GIL_DISABLED == 0`。没有安装或测试 free-threaded Python。
- 外部技术描述来自下列官方文档，访问日期均为 2026-09-11；STAR 适用性属于设计判断，不是这些引擎对 STAR 的性能承诺。

## 1. 主流实现真正并行的是什么

| 技术 | 官方机制 | 对 STAR 的启示 |
| --- | --- | --- |
| Unity Entities / DOTS | 相同组件组合的实体放在 chunk 中，每种组件有自己的数组；System 调度 Job；按组件读写关系建立依赖；支持 `IJobChunk.ScheduleParallel` | 一个 System 内的实体处理也可以拆成多核任务；数据布局和调度依赖共同决定收益 |
| Unreal MassEntity | Fragment 是数据，Processor 提供逻辑；按 archetype/chunk 查询批次；提供 `ParallelForEachEntityChunk`；Fragment requirement 声明访问模式 | 将整批数据交给计算任务，减少逐对象查找；具备并行 API 不代表任意 Processor 自动安全并行 |
| Flecs | 多线程 System 将匹配实体分段交给 worker；staging 延迟结构修改，sync point 再提交 | 线程池可以协作完成同一个 System，无须把 System 永久绑到一个核 |
| Bevy ECS | Schedule 并行执行访问兼容的 System，可显式声明 before/after；独占 World 访问会限制并行 | 业务顺序与读写冲突需要进入调度约束，而不是由 import 关系推导 |

来源：[Unity chunk 数据布局](https://docs.unity3d.com/Packages/com.unity.entities@1.4/manual/concepts-archetypes.html)、[Unity Job 调度](https://docs.unity3d.com/Packages/com.unity.entities@1.4/manual/systems-scheduling-jobs.html)；[MassEntity 概览](https://dev.epicgames.com/documentation/unreal-engine/overview-of-mass-entity-in-unreal-engine?lang=en-US)、[并行 chunk API](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/MassEntity/FMassEntityQuery/ParallelForEachEntityChunk?lang=en-US)、[访问声明](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/MassEntity/FMassFragmentRequirements)；[Flecs Systems](https://www.flecs.dev/flecs/Systems.html)；[Bevy 官方 ECS 示例](https://github.com/bevyengine/bevy/blob/main/examples/ecs/ecs_guide.rs)。

可借鉴的共同模式是：常驻数据、按块计算、声明依赖、必要位置同步、结构修改延迟提交。线程共享底层存储，可以避免 v1 每次请求都序列化并还原完整动态对象图；这不意味着整个任务路径完全零复制、零分配。

### 两类并行应分别考虑

1. **System 之间并行**：A、B 的完整读写集合兼容，且没有业务顺序约束时可以重叠。读写集合包括索引、缓存、事件和随机数等隐含依赖。
2. **System 内部并行**：一次处理 5000 个实体的循环划为若干任务，分别读取稳定输入、写入互不重叠的输出。这通常比“一 System 一核”有更好的负载分配空间，但每项工作必须足够大以覆盖任务调度成本。

例如，若只是根据固定输入计算独立的候选位置，可以分块计算。若移动还涉及占格冲突，则候选结果仍需按规则裁决；“实体不同”不代表“共享格子、目标、资源不同”。这只是机制举例，并未审计或改造 STAR MovementSystem。

### CommandBuffer 的边界

新增/删除实体或组件可能移动存储、使迭代器失效，所以 Mass/Flecs/Unity 提供延迟提交机制。Unity 并行记录命令时，还需与线程完成顺序无关的 sort key 来稳定回放次序。[Unity ECB playback](https://docs.unity.cn/Packages/com.unity.entities@1.4/manual/systems-entity-command-buffer-playback.html)

CommandBuffer 并不自动解决“两个攻击同时扣同一个目标兵力”“移动与攻击谁先发生”。STAR 若把现有即时命令全部改为帧末提交，可能改变博弈结果，不能当作透明性能优化。Flecs 的 readonly/staging 主要限制结构修改，System 仍可修改已有组件的值，也不能直接等同于本项目的不可变观测快照。

## 2. 为什么这些技术与 v1 成本不同

STAR `framework/ecs/world.py:28` 当前以 `entity -> {component_type: component_instance}` 保存对象，并使用反向索引和查询缓存。这是清晰的 ECS 组织方式，但不等于 Unity/Mass 的连续数值数据块。

v1 每次观测：owner 导出全部 Unit 核心状态及占用 → pickle/IPC → worker 还原窄 read model → 按原业务逻辑构建响应。冻结 canonical 5000 Units / 1000 注册 Agent 主探针中：

| 路径 | 吞吐（两轮范围） | owner 导出平均 | worker 还原平均 |
| --- | --- | --- | --- |
| 原串行 | 141.12–141.65 次/秒 | — | — |
| 1 worker | 32.25–32.50 次/秒 | 8.14–8.22ms | 10.41–10.45ms |
| 2 workers | 51.25–52.18 次/秒 | 8.52–8.54ms | 11.44–11.69ms |
| 4 workers | 62.31–62.65 次/秒 | 9.31–9.61ms | 11.12–11.25ms |

原串行 build 平均仅 5.52–5.55ms。主线程为搬运数据付出的时间已高于原 build；增加 worker 无法抵消这部分串行成本。worker build 还包括惰性组件实例化，不能将它全部称为规则计算时间。以上冻结吞吐不是动态 24/30Hz 容量结果，完整方法与限制见原实验。

因此下一候选应先减少搬运和对象重建，再测增加核心的净收益。既有证据没有证明共享内存、native 或增量副本一定获益，也没有单独分离 GC、带宽争用和调度的因果影响。

## 3. STAR 的候选路线

| 路线 | 数据和执行方式 | 主要收益来源 | 主要成本/条件 | 当前判断 |
| --- | --- | --- | --- | --- |
| A. 局部紧凑数据 + 原生 Job | 观测热点依赖存为常驻数值数组/紧凑索引；Cython/C++/Rust 内核释放 GIL，线程读取同版本数据，输出各自结果 | 避免逐请求全量对象复制；降低 Python 热循环成本；同进程多核 | 需要准确提取依赖、维护数据、验证原生规则等价；Python 响应装配仍可能串行 | 最值得作为主候选，先做单线程内核对照，再测多线程 |
| B. 常驻 worker + 有序增量日志 | worker 初始建一次副本；之后接收变更和查询屏障，原业务逻辑读取已更新副本 | 避免每次完整还原，更易保留 Python 业务代码 | 必须覆盖所有写入/派生索引；每个副本都要应用变更；慢 worker 积压和版本边界复杂 | 保留 Python 的合理备选，先一个副本证明经济性 |
| C. 紧凑共享内存 + 多进程读 | 进程映射同一数据缓冲区，请求传版本与索引 | 绕过普通 Python GIL，减少大块 IPC 复制 | 共享内存不直接共享 Python 对象；需改查询访问方式；缓冲区寿命、一致性和同步是核心 | 可作为 A 的存储基础上的另一执行后端，不能只把 pickle bytes 放进共享内存后照旧还原 |
| D. free-threaded Python + 读阶段 | 在真正关闭 GIL 的解释器上，以线程读取稳定组件数据 | 减少业务代码重写和进程复制 | 扩展兼容性、读路径缓存写入、对象访问开销；所有库导入后要复查 GIL | 值得小范围可行性验证，尚不能作为已兼容的默认运行时 |
| E. 整体替换 ECS / 引擎 | 迁移至原生 Flecs/Unity/Mass 等运行时 | 可以系统性采用原生数据和任务机制 | 迁移成本、Python 边界、测试与规则一致性范围大 | 当前没有证据支持优先整体迁移 |

A 路线无须先把整个 World 改成 archetype ECS。可先只提取一个观测热点需要的紧凑数据，保留四层架构与 Python 业务编排。reachable/attackable 是候选，当前材料不足以认定其中某个函数占绝对主导，选择前应测其实际占比；不能预先保证该内核就是最佳优化点。

[Cython 官方 GIL 文档](https://docs.cython.org/en/latest/src/userguide/nogil.html)明确区分“函数可在无 GIL 下运行”与“调用时实际释放 GIL”。纯 C 级计算可并行，反复访问 Python 对象/回调会破坏该边界；单纯释放 GIL 本身不会使单线程代码更快。[NumPy 线程安全文档](https://numpy.org/doc/stable/reference/thread_safety.html)也说明很多底层操作释放 GIL，但共享数组并发修改需要同步，object dtype 不是这条捷径。

[Python shared_memory](https://docs.python.org/3/library/multiprocessing.shared_memory.html)提供跨进程内存区域，不负责 ECS 查询语义、版本一致性或 Python 对象复用。[Python free-threading](https://docs.python.org/3.14/howto/free-threading-python.html)允许 Python 线程使用多个核，但不兼容的扩展导入可能重新启用 GIL；容器内部锁也不能保证整个 World 的多字段事务一致。

## 4. 是否让世界与观测同时运行：独立于线程/进程选择

**简单模式：读阶段屏障。** 在原有顺序中的安全点暂停写入，多个任务读取同一版本，完成后继续写入。无须保留多代世界；同一只读批次可以共享输入。代价是世界仍要等最慢读任务，收益来自缩短读阶段，不能宣称世界已与观测异步重叠。即使只有一个请求，也可考虑拆其足够重的独立子任务，但任务太小会得不偿失。

**异步模式：带版本的常驻读数据。** owner 推进新状态，worker 继续读绑定版本；需要不可变块、版本保留或明确的副本查询屏障。共享内存、双缓冲和增量日志只是实现材料，不会自动保证这一点。慢读者尚未结束时，不能循环覆盖它正在读取的缓冲区。

有序日志可以让同一个 worker 按“应用到版本 V → 执行 Q → 应用下一批变更”工作，无须给该 worker 同时保留所有版本，但后续变更会在其后排队。owner 与它可以重叠；要测日志生成、应用、积压、重启重建及多个 worker 的更新扇出成本。

精确契约仍是：若接纳顺序为动作 M → 查询 Q → 动作 N，则 Q 包含 M、不包含 N。不能用上一帧替代、不用 TTL、不把 Q 偷偷移到帧末。owner 身份/认领权限绑定、Fog 过滤、reset/地图更换失效、响应字段与顺序均需保留。

## 5. O(active) 的前提与低查询频率

增量维护只有在写入源可靠记录变化时，才能减少全量扫描。当前组件支持原地字段修改，组件引用版本不是任意字段变更日志；不能仅订阅实体增删或现有少量事件，就声称覆盖全部动态状态。

成本更准确地描述为 O(变化数据 + 受影响派生数据 + 请求实际输出)，而不是固定 O(移动单位数)。Fog、资源恢复、战斗、认领、地图/规则和生命周期变化都可能扩大影响集合；密集变化时仍可能退化为 O(N)。如果每帧扫描 N 个实体比较后再标 dirty，扫描成本也必须计入。

按 1000 Agents / 约 30 秒一轮，忽略服务时间时平均约 33 次观测/秒，在 24Hz 下约 1.4 次/帧。这只是名义负载估算，实际到达有抖动，服务等待会改变周期。请求之间可能夹有动作，因此平均每个可共享只读批次的请求数还可能更小。不能假定每帧 1000 个 Agent 共同摊销一个快照，也不为了凑批次增加思考期轮询。

常驻数据的维护也不是免费：应同时比较“每秒维护成本 + 查询成本”，防止查询本来较稀疏，却为每帧全量同步付出更多工作。内核优化、数据复用、并行三者应拆开测量。

## 6. 建议的最小验证顺序

1. **选择一个热点与最小数据接口。** 在现有串行观测中分离公共投影、逐 Unit 面板/合法动作、装配和 JSON 的成本，选择有足够占比的纯计算段；确认读写、缓存和顺序依赖。
2. **单线程紧凑数据对照。** 仅为该热点构建常驻输入；静态数据预建，动态维护成本全部计入。沿用串行 oracle 比较输出；先证明没有把 v1 的全量复制转移到每帧维护中。
3. **单线程原生内核对照。** 先验证精确行为和数据转换成本，再用相同输入、相同内核测试 2/4 worker 的分块版本。这样可以区分语言/布局收益和并行收益。A 的最低复杂度模式是读阶段屏障。
4. **若目标仍需与世界重叠，再选 B 或 C。** 以一个常驻副本/版本缓冲区原型先测更新和同步，经济性通过后才扩 worker。D 可以单独作兼容性探针，不与存储重构同时混测。
5. **返回动态闭环验证。** 固定 ENV dt=1/FPS、Agent 墙钟思考，不在思考期观测。保留 canonical 与高接触负对照；先短诊断，具备收益再运行持续窗口，记录世界帧 P99、查询/动作等待、更新发布和同步耗时、进程总资源/内存与积压。

必要正确性包括：原响应字段和列表顺序、非空 reachable/attackable、动态占用、同帧 M→Q→N、Fog/权限、实体死亡增删替换、reset/地图规则切换、取消/超时/worker 失败。原生数值实现还需防止精度与排序差异改变合法动作或决策输入。

是否继续扩并行，以包含数据维护/转换/装配的净成本和动态 P99 为准；CPU 占用升高本身不是成功标准。当前没有 A/B/C/D 的实现或测量结果。

## 7. 其他游戏技术的适用边界

MassGameplay 也提供显示/模拟 LOD、按客户端相关性控制复制和 Signal 机制。[官方概览](https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-mass-gameplay-in-unreal-engine)
显示裁剪、可靠 dirty 更新、相关性索引可以借鉴；降低战斗/观测更新频率或省略可见信息会影响 Benchmark，应单独作为规则/协议选择，不能混入等价优化。

空间分区可用于邻域查询和任务拆分；把世界分成多个可独立写入的区域则还涉及跨区移动、攻击、视野及顺序，不是直接把现有 System 放上不同 CPU 核。分布式跨机器还增加通信和故障边界，当前先验证本机并行。

GPU 属于另一种原生计算后端。本轮未验证 STAR 热点的 GPU 适配、传输/同步成本或收益，不能从“GPU 空闲”推出值得迁移。待有足够大的、可批处理的热点与稳定紧凑输入后再评估。

## 决策状态

推荐优先验证 **局部紧凑观测数据 + 原生 Job**，以只读阶段作为最小一致性方案；保留常驻增量 worker 与共享内存为需要世界/观测重叠时的备选。此处是候选优先级，不替用户确认新的实施范围。
已完成官方资料调研和成本对照；v1 负结果及旧实验保持不变；生产分支/main/tag 未修改，未启动性能测试，未推送。
