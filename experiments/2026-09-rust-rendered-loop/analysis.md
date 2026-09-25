# Evidence and limits

## Observation

R4b在真实Cocoa窗口中5000Units/1000Agents、30Hz固定dt、约30秒闭环时，18ms事件预算60秒测量：整帧P99 40.279ms，世界step P99仅0.729ms。拆分表明世界推进不是当时的主耗时；Agent处理与展示共享单帧时间。将Lab预算调为6ms、8ms的60秒诊断均通过（32.149/31.229ms），但8ms的300秒首轮失败：35.561ms，观测91.551ms、动作排队95.013ms，30Hz平均频率。仅帧门槛失败，合法移动/攻击、5000存活、负载及无积压guard通过。预定余下两轮停止，不能删除或替换该负结果。

## Hypothesis and instrumentation

展示增量编码可能有重复构造。审阅Rust代码确认每个dirty Unit先序列化为Value，再由外层json!重新装配。使用完整原始长测的前2000ticks，严格重放请求、step、presentation drain次序，把native编码和Python json.loads分开计时；原路径平均1.613/0.452ms。没有将所有展示时间归因于Rust，也没有把独立层P99相加。

## Controlled evidence

改动仅为typed借用展示行和外层直接serde编码，所有mutation先完成，随后锁内序列化。两版本9296请求、2000完整增量、输出长度、最终状态一致；tick>=900的1101样本：编码平均1.613→0.177ms（约89%减少），中位1.614→0.165ms，P99 2.349→0.434ms。Python解码均值0.452→0.490ms、P99 0.683→1.227ms；其慢样本保留，不能宣称解码改善。before/after按序执行、不是随机化重复，局部成本变化与代码移除的构造相符，数值受背景任务和运行时状态影响。

## Real-time workload limits

同一脚本的实时运行会因完成时间不同而改变接纳次序/实际轨迹；原始before在下午、after在夜间，Chrome均开启，但未控制其他系统背景任务。因此整帧差值是同配置诊断，不是严格锁步因果A/B；固定输入编码probe提供独立的成本和语义对照。before短测没有输入录制，before长测和after测量开启录制且其开销包含在frame里。

before长测10个30秒块的P99从约30.67涨至36.93ms，同时观测平均payload约176KB→248KB、可见地形约2277→3015、敌军约116→282；display和delta成本亦增长。仅据此不能断言内存泄漏、历史轨迹成本或单一组件导致全部尾延迟。blocks.json保留每个阶段的原始派生指标；residual包含呈现/框架/采样等尚未进一步归因的工作。

5000是常驻存活数量；before长测同时移动最多166。合成Agent控制各自Unit子集、非法move/attack选择会等待；不等于5000个持续移动Unit或5000Agents。minimap单位层关闭、窗口2480×1243、GC在有限测量内延迟，均为当前canonical条件。Protocol/Hub和LLM没有纳入。

## Regression and rule compatibility

2171 Python回归、108展示相关、14Lab、4Rust及fmt/Clippy、旧6场景510节点通过。Rust workspace测试曾因扩展crate的Python符号链接配置错误失败；原样保留日志并按项目的core/rotk命令通过，binding依赖wheel与Python测试。无已确认新增玩法GAP；不关闭G008/G009、R001/R002。

## Validated scoped capacity

| Run | Frame P99 ms | Observation response P99 ms | Action queue P99 ms | Hz | Max moving |
|---|---:|---:|---:|---:|---:|
| t1-after-budget8-300-r1 | 32.478751 | 85.989951 | 94.090125 | 30.0 | 171 |
| t1-after-budget8-300-r2 | 32.613375 | 82.840035 | 93.040334 | 30.0 | 173 |
| t1-after-budget8-300-r3 | 32.405167 | 87.093479 | 94.272292 | 30.0 | 178 |

三轮每轮30秒预热＋300秒测量，全部guard通过，5000Units始终存活。世界单线程、Lab预算8ms；包括真实Cocoa窗口。个别30秒分段仍超33.33ms，余量不足1ms，不保证任意窗口或所有帧均满足。详见results/blocks.json；所有慢帧保留。

第三轮原始输入在4线程内核重放：40741请求、9878tick及presentation，响应/事件/最终状态一致。输入不同的实时时序不要求最终世界彼此相同；不能把不同随机轨迹的实时测量当锁步比较。
