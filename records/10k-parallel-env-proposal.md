# Parallel ENV：单写世界、并行观测设计建议

2026-09-10。用户在了解18ms本地Agent调度预算后提出“It is time to consider parallel ENV”。
此前“并行暂停”更新为进入设计评估；本次只形成方案，无生产改动、无新性能测试或容量结论。
生产基线6a970deaee7d9b8d3939edd102973f2377edd6ac，证据来自[text-render-cache案例](../experiments/2026-09-text-render-cache/README.md)中的最终live诊断。以下均值用于选择验证方向，不是新增容量认证。

## 判断

现在值得验证并行收益，但18ms是Lab单线程仿真控制器的自定预算，不是ENV/Protocol固有吞吐上限，不能把它单独作为必须拆所有ECS系统的证据。
当前实测单次观测平均：build6.2446ms、encode0.9375ms、decode0.9461ms。
单帧Agent pump平均14.0969ms，ENV更新+render/present平均14.5847ms，说明两类工作确实串行占用同一个frame。
这些均为当前canonical5000U/1000A/30秒闭环的测量，不能直接外推10K或推导2倍收益。

## 建议的第一条并行边界

保留四层架构。ENV内部划分执行职责，不新增架构层，也不提前接入Protocol/Hub。

| 执行者 | 职责 | 世界写权限 |
| --- | --- | --- |
| ENV owner进程/线程 | 固定1/FPS推进、动作校验和提交、移动/战斗/CD/Fog更新、查询身份校验与快照绑定 | 唯一写入者 |
| 观测worker进程池，先2个 | 在纯数据只读快照上计算阵营视图、逐Unit面板/合法动作和JSON编码 | 无 |
| Lab合成Agent进程 | JSON解码、合成决策、墙钟思考、发送下个请求 | 无，只提交命令 |

第一轮保持现有窗口/渲染在owner侧，避免同时改GUI归属、ECS写入和观测三条边界。后续若render仍挤占世界预算，再单独评估展示进程。

## 为什么不直接把各System塞进线程池

World.update当前按systems顺序同步执行，共享组件、空间索引及事件衍生数据。模块之间少import不能证明内存读写独立。
移动改变位置后会影响占用、Vision/Fog、后续攻击合法性；并行修改必须额外定义冲突和提交次序，可能改变Benchmark语义。
当前Python3.13.12实际GIL开启，Py_GIL_DISABLED=0；普通线程不是此类Python CPU任务的默认多核方案。首轮选择多进程，明确计入IPC与序列化成本。
参考：[Python threading](https://docs.python.org/3.13/library/threading.html)、[multiprocessing](https://docs.python.org/3/library/multiprocessing.html)。

## 关键正确性边界

1. Worker不能读取正在变化的World，也不能复用现有ObservationBatchContext里的活组件引用；现有批次入口明确要求owner线程同步只读，不能直接放进executor。
2. 观测在owner接纳它的确定位置绑定不可变版本，至少包含tick与同帧写入序号。不能仅依赖update边界的World.revision来标识同一帧内多个动作的先后；版本设计必须覆盖所有会影响观测的写入。
3. 动作M → 查询Q → 动作N：Q必须包含M、不能混入N。owner冻结Q所需数据后，N可继续推进，worker完成的是Q当时的世界，不是任意旧缓存。不同Agent响应可以因计算耗时不同而先后返回，每个Agent的请求链和动作提交顺序仍受明确约束。
4. 默认不把请求自动降为“上一帧”观测，不跨若干帧TTL复用。若未来考虑“最新完成帧”语义，必须作为显式Benchmark设置讨论，不能暗中放宽原只读批次规则。
5. 身份/阵营/认领权限在owner侧确定；worker只输出该Agent允许的投影，跨阵营不能泄露私有信息。动作执行时重新对当前World校验所有权、资源、占用和目标合法性，不能把快照的reachable当执行许可证。
6. 已绑定的快照不能被覆盖。按在途请求引用保留版本并设置有界队列；队列满要明确背压/拒绝，不能静默换新快照、丢旧请求或重置原deadline。worker失败不得重复提交动作。
7. ENV模拟秒继续每帧1/FPS推进；外部Agent思考用墙钟。并行化不改变这两个时钟。

## 按阶段验证

### A：澄清客户端与ENV成本

只把Lab合成Agent解码/动作选择/墙钟调度放入独立进程，仍由owner执行现有业务入口；IPC只替代本地调用，不引入Hub。
对照现有baseline，记录JSON编码/解码、IPC排队和owner服务时间。预期只移除客户端部分，不能宣称移除了6.24ms观测构建。

### B：冻结状态的观测worker原型

从owner导出当前观测所需的纯数据依赖，不复制pygame/锁/整个World。静态地图在worker初始化一次；动态位置、资源、所有权、Fog等按版本提供。
先在完全冻结场景上运行1/2/4 worker，对照生产single路径逐字段/列表顺序/错误响应；包括非空reachable/attackable、敌军过滤与跨owner权限。
必须分别计量导出、复制/IPC、worker构建、JSON编码/解码和版本内存。不能只计worker运行时间，也不能把主进程已经造好完整JSON后的并行编码称为“观测并行”。
先明确导出成本；没有可靠的组件变更账本前，不承诺动态导出O(active)。若全量冻结本身成为新瓶颈，再评估有界的增量镜像，不能依赖不完整World.revision偷偷跨写入复用。

### C：动态闭环

固定帧内接纳/动作提交顺序，对固定命令回放检查串行与并行的观测版本、World状态和错误结果一致。
再测canonical5000U/1000A/30秒墙钟闭环，24Hz基线、30Hz目标，先2 worker；有效后再扩至4 worker和更大规模。
记录完整世界frameP99/Hz、请求排队+服务P99、snapshot age、快照导出与IPC成本、CPU/RSS、队列增长、实际move/attack/存活/同时移动数及每Agent完成分布。
场景/响应大小改变会影响成本，不能省略布局。随机动态反馈的轨迹随服务速度而变，不声称跨实现随机运行逐帧相同。

## 成功与停止条件

世界推进和观测尾延迟同时改善，快照一致性/权限/动作顺序通过，版本队列和内存保持有界，才值得集成。
如导出+传输抵消并行收益，保留负结果并重新选择边界；如仅客户端拆分有效，单独报告其收益，避免过度改动生产。
18ms预算不会因为改成进程就自动消失：owner仍需要有界的请求接纳和动作提交策略，只是将大量只读计算移出这段临界路径。
所有性能实验串行；这里的“串行实验”指同机不并跑不同实验，不妨碍单个实验内部的多个worker并行。
原始/compact证据与进度留Lab；生产改动放新codex分支，先tag再squash。P1/P2仍跳过，真实LLM和Protocol/Hub仍不在首轮范围内。
