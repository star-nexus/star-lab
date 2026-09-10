# Analysis — 时钟与负载分开判断

## Observation / competing hypotheses

候选问题包括模拟时钟意外使用墙钟、同一5000规模的视野/接触密度不同，以及每帧Agent预算导致突发排队。

## Instrumentation

记录每帧dt、GameTime和模拟累计，wall-clock Agent deadline/queue/service，实际动作、存活与移动、编码/解码字节和耗时。
固定source；改变layout对照信息量，再只改Agent预算观察排队与帧尾的取舍。所有运行有完整raw。

## Evidence and causal interpretation

四组固定步长/board_clock guard均须由结果核验，不能仅凭设置24宣布时钟正确。
interleaved60的平均响应约1.267MB，构建18.61ms+编码6.71ms+解码6.46ms；世界16.93Hz，表明广泛接触密度的全阵营观测仍会过载。
canonical12ms达到24Hz/帧P99=36.28ms，但请求P99约0.49s。canonical18ms的60s仍24Hz，帧P99=41.10ms，请求P99约0.12s，表明增加服务预算吸收了一部分突发、也减小了帧余量。

## Sustained outcome

| 布局 / Agent预算 | 测量秒数 | 世界Hz | 帧P99 ms | 观测P99 ms | 动作排队P99 ms | 名义闭环比例 |
|---|---:|---:|---:|---:|---:|---:|
| [interleaved / 12ms](results/discovery60.json) | 60 | 16.93 | 70.90 | 25138.48 | 25091.00 | 50.98% |
| [canonical / 12ms](results/canonical60.json) | 60 | 24.00 | 36.28 | 484.15 | 488.42 | 100.41% |
| [canonical / 18ms](results/canonical18-60.json) | 60 | 24.00 | 41.10 | 123.46 | 118.56 | 100.46% |
| [canonical / 18ms](results/canonical18-300.json) | 300 | 24.00 | 44.54 | 177.97 | 170.45 | 99.74% |

完整长测指标与实际负载见README/results。各模式动态反馈轨迹不同，不能声称逐帧完全同样世界；种子和参数可复现。
