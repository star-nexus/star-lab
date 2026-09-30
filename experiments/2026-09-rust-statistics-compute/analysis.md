# E2 analysis

## Observation

P0完整step里Statistics是最大世界阶段，但其整体不是可直接并行的计算。E1确认它在Movement前读旧Position/MP及先前Fog，存在缺组件插入、逐行history、周期phase与失败后的成功前缀。R4e窗口中世界step远小于Python显示工作，需限制整帧收益预期。

## Hypothesis

健康算术可能可并行但量太小；构建完整JSON记录可能有足够独立工作；历史裁剪可能主导而必须有序。整方法线程池可能错误改变状态与失败边界，微小批次可能调度亏损。这些是归因前的候选解释。

## Instrumentation

44c3696仅串行拆分，按当前批次收集窄借用输入，构造自有记录，再按原ID／ordinal提交。PROFILE=false不读计时钟；true分gather/health/JSON/commit/trim/visibility/factions。7ab0ac1增加已有ReadPool的scoped2/4分块，正式2bc57d5只在至少128行启用，默认1线程不建池。私有推进探针每调用覆盖门槛，false返回null，策略与timing不进入权威状态。

worker sum compute/records与调用者kernel_wall分别记录；dispatch_residual=墙钟减最大chunk，也含join/merge/计时，不称纯调度成本。完整结果与全量错误状态先对旧P0独立binary校验，之后同binary同线程数只改门槛作普通完整step交替A/B。带诊断孪生的compare run只用于归因/等价，不参与净收益。全部samples与max慢样本保留。

## Evidence

串行非空3320tick，平均125行：gather22.220µs，健康算术0.151µs，JSON154.005µs，提交21.301µs，trim107.958µs。全9880tick Statistics均值140.037µs；含录制预热。决定并行JSON记录构建，保留trim及写入顺序。

8变体完整contract的压缩字节、36场景/174step状态/单次展示/错误/reset与旧binary一致，canonical raw SHA9db82664ad15814eec53a603f0d5148ad4d431ef66a4f36871f21de38847078c。20次固定输入重放完整响应/展示流与最终状态一致；正式普通step的1/2/4也独立重放。小测试不是大轨迹的替代。完整回归2291Python/4Rust/fmt/Clippy/release通过，包括多实例并发及重置后的自有返回值。

同7ab binary/同线程的3组独立普通step控制：2线程均值降低4.18–16.76%，4线程降低7.58–10.36%，各组P99降低。该对照隔离并行门槛，不是整个串行拆分对旧P0的因果对照。独立正式普通路径亦保留，不能以一次old1/new4时序结果宣称全转换加速。

259resident/10000稳态history的合成交替控制保持当前selected batch，1–32行强制并行更慢，64平均开始正收益，128余量更大。200samples＋20warmup/每线程每点，reset不入计时；关闭动画/视野是微实验范围，不能用于替代真实容量。

真实窗口3×30预热＋300秒全部guard通过，检查记录于capacity-comparison。帧P99 28.283/28.643/28.631ms，max91.923/102.449/32.239ms，worst5s P99 39.837/76.037/31.794ms；短窗口尾延迟也原样保留。窗口维持5000Units/1000Agents/30Hz/8ms/30秒思考±5秒、Fog/权限/完整信息、原native-wire及客户端解码。实际接纳动作不同于原R4e，不能把两次窗口轨迹的平均帧差当纯并行加速。

## Root cause and rejected explanations

主要独立成本是记录JSON构建，非health算术；仅算术并行会被池开销淹没。大记录批可用有界worker缩短kernel墙钟，但有序写入/trim/visibility/factions仍串行。否决全部System直接进池、扩大游戏采样batch、全resident扫描补任务、按worker完成次序提交和删减观测。也不能从Arc/窄Schedule机制探针推导当前System真实并行收益。

Recovery/Lifecycle/Vision之间候选仍有正确性研究价值；P0理想重叠均值3.883µs小于机制空派发7–9µs，当前吞吐优先级低于E2。Vision几何下一步仍需cache miss成本归因，不能直接线程化LRU/Fog/refcount提交。

## Limits and intermediate results

原FD-capture pytest受磁盘满中断；仅清理活动checkout的可重建dev缓存，完整sys-capture suite通过。错误sampler／构建入口的setup失败未进入目标负载，不纳入正式性能点。原49项删除、冻结Rust/Python目录及历史正式证据保留。没有worker panic故障注入的全配置证明；本阶段覆盖业务错误、reset失败、close与同步有序join。

API18/schema5/oracle不变，无新已确认玩法GAP；G008/G009 OPEN、R001/R002 RISK与G001–3基线差异保留。一次M4上的64/128不代表所有payload/硬件；默认native1不变。没有全部5000单位同时移动、高密度、Hub或真实LLM验收；5000Agents继续暂缓。后续真实frame/queue报告决定本配置容量门槛，不作整帧因果收益承诺。
