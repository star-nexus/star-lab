# Analysis — 批次共享的收益与边界

## 1. Observation

3000/1000：batch-off→batch-on完成11.89%→21.06%；5000/1000：8.81%→14.03%。10K/1000：3.48%→2.95%，并非所有规模加速。
所有观测队列P99仍为秒级，不能以世界Hz或缓存命中率宣称千人实时。

## 2. Competing hypotheses

H1：阵营公共事实的重复构建是显著成本，可在同一只读批次内摊薄。
H2：完整响应输出、独有Unit面板和批次第一张快照仍限制吞吐；缓存准备本身可能得不偿失。

## 3. Instrumentation / diagnostic changes

同源三路入口、原堆序号与过期deadline、32条上限、每帧12ms预算（单次不可中断工作可能超出，客户解码也计入整帧）。
所有响应可用时间不早于批次返回。消费时间、JSON编码/解码、完整帧、动作、FIFO、原始事件均记录。
缓存计数在每个批次 finally 后汇总；补充归因工具计时 cold build / hit，属于有开销的diagnostic，不混入正常矩阵。
reanalysis 的 observed_batch_size 为按请求加权批长；完整批长可由 raw 中同一 t 的 batch_size分组恢复，不能拿加权值代替每批平均。

## 4. Evidence

补充归因（包含预热，inclusive计时不能把父子项相加）：阵营公共构建789次，平均3.9771ms；命中3681次，平均0.000777ms。
这个对照支持“缓存确实消除了重复公共构建”，但不等于整个请求同倍数加速。

| Point | Build avg ms | Encode avg ms | Decode avg ms | Bytes avg | Request-weighted batch size |
|---|---:|---:|---:|---:|---:|
| lazy-3000-single | 2.977 | 0.412 | 0.388 | 86636 | 1.00 |
| lazy-3000-batch-off | 2.970 | 0.408 | 0.389 | 86701 | 3.92 |
| lazy-3000-batch-on | 1.147 | 0.432 | 0.417 | 93198 | 9.21 |
| lazy-5000-batch-on | 2.013 | 0.689 | 0.655 | 144397 | 4.81 |
| lazy-10000-batch-on-a1000 | 13.434 | 1.559 | 1.400 | 324465 | 1.00 |

## 5. Root cause

可复用的阵营公共构建得到摊薄，但每个响应仍携带完整公共内容并独立编码/解码；每Agent所控不同Unit仍计算自身reachable/attackable。批次结束即释放，没有跨帧共享，因此每批仍有首次全场统计与阵营视图构建成本。

## 6. Causal chain

同阵营多次查询 → 公共构建命中 → 平均构建减少 → 中等规模吞吐提高。
世界规模增大 → 首张完整观测接近/超过批次预算 → 批次缺少后续命中 → 准备缓存成本无法摊薄。

## 7. Rejected explanations

首版提前缓存所有位置/AP：10K/1000下494批/494请求，没有第二次查询可复用。修正版取消预取位置、仅查询阵营AP并按组件类型索引，提升中等规模效果，但仍未解除10K限制。
降低决策频率不能代替降低观测量：3000/1000、30s决策、独立1Hz观测也仅完成34.25%。
没有把慢帧归咎Chrome并删帧，也没有把成功缓存误写为容量通过。

10K/1000修正版的15s窗口内接受移动为0，position_progress门槛失败；不能把该点当作活跃对战容量。单独interleaved战斗点接受811次移动和334次攻击，说明动作路径非空，但帧与观测SLO仍失败。

## 8. Limits of the evidence

单机、15s诊断。反馈轨迹随服务速度变化；相同种子/参数并不意味着不同模式每帧世界状态相同。
首个stdout未落log点排除受控比较；attribution点单独标记。没有300s+3×60s容量认证、长期内存或Protocol/Hub结论。

## 9. Raw evidence

每个results JSON含source/tooling/workload/guards、raw ZIP定位与SHA；artifacts保存原始事件和日志；SHA256SUMS可独立验证。
