# Analysis — first optimization round

## Observation

At baseline, 1000 canonical units / 1000 registered Agents, three static queries return 333 own-unit panels each; build times 194.018 / 149.934 / 144.886ms. The 999 `_unit_reachable` calls total 480.729ms. No attackable targets in this fixture: attack cost cannot be inferred from it.

In the separate interleaved fixture (same source, 1000 units), baseline queries return 333 panels, 17,646 reachable cells and 87 attackable targets. Build times 265.849 / 274.762 / 263.633ms. Inclusive helper times: reachable 456.815ms, attackable 313.654ms across three queries.

## Root cause

`handle_faction_state` computes every own-unit panel/affordance even for a one-unit Agent. `reachable_hexes` rebuilds dynamic occupancy by scanning all units per mover. `_unit_attackable` tests every visible enemy per own unit. Source and inclusive helper counts agree; profiling calls are diagnostic only.

## Candidates

1. Explicit `unit_ids` projection keeps shared faction observation intact; omitted parameter preserves full payload. This is a declared scope change, not an equivalent full-payload speedup.
2. Reuse existing window `occupancy_for_mover_local` with the existing movement oracle.
3. Spatial candidate filtering + unchanged final combat oracle for attackable. Fallback remains scan-based for unindexed worlds.

## Evidence limits

Selected interleaved probes retain nonempty reachable and attackable targets. They expose visible-terrain construction and serialization as substantial residuals. Short diagnostics do not establish 30Hz runtime capacity. CPU/Chrome interference has not been used to remove samples. Positive formal repeated-window evidence is pending.


## 独立观测矩阵

均为 5s warmup +15s 完整测量，selected panels、JSON、1s 决策、12ms 帧内 pump 预算、
canonical 场景、move 策略、realtime_defer。**均为短诊断，不是正式容量点。**
响应列包含排队+构建+编码；请求完成比例按预定观测频率计算。

| Units | Agents | 观测 Hz/Agent | 世界 Hz | 整帧 P99 ms | 观测响应 P99 秒 | 请求完成比例 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 100 | 1 | 30.00 | 15.64 | 0.032 | 100.00% |
| 1000 | 1000 | 1 | 30.00 | 22.52 | 14.079 | 29.51% |
| 3000 | 1000 | 1 | 30.00 | 23.89 | 17.534 | 12.06% |
| 5000 | 1000 | 1 | 30.00 | 29.24 | 18.149 | 8.99% |
| 10000 | 1000 | 1 | 26.73 | 42.27 | 18.854 | 5.32% |
| 10000 | 5000 | 1 | 28.80 | 38.88 | 19.652 | 1.15% |
| 10000 | 10000 | 1 | 29.07 | 38.93 | 19.740 | 0.58% |
| 5000 | 1000 | 5 | 30.00 | 28.98 | 19.521 | 1.80% |
| 5000 | 1000 | 10 | 30.00 | 27.81 | 19.705 | 0.90% |
| 5000 | 1000 | 30 | 30.00 | 29.95 | 19.820 | 0.30% |

原始索引：[discovery-matrix.json](results/discovery-matrix.json)。100/100 短测通过时延与负载门槛，
但没有完成长测/重复条件。10K 各点存在零接受动作/零位置进展，亦不满足 workload guards；
这是发压排队失败，不能把“注册成功”解释为 Agent 已在战斗。

## 剩余成本与非空执行

3000/1000/1Hz：平均观测构建 2.692ms，JSON 编码 0.418ms，平均 86,799 bytes。
与无编码对照的完成比例 12.06% →14.99% 表明编码不是唯一瓶颈；
这里是反馈闭环，不声称动态执行轨迹完全一致。
带 instrumentation 的独立点 2,371 次观测中，visible terrain 合计 2,338.797ms，
visible enemies 1,202.546ms；helper 时间为 inclusive，不能与父调用简单相加。

1000 Units /100 Agents interleaved mixed 场景在准入 15s 内接受 640 次 move、258 次 attack，
拒绝 152 次动作，保留全部拒绝；全部 1000 resident 保持存活。
这个场景观测响应 P99 8.421s、负载完成 59.8%，仍然失败，只证明非空攻击业务被执行。

## 长窗口失败及趋势

`gate5000-d30-300` 是较早的顺序闭环，每 Agent 思考30s后行动再拉取观测，**不是1Hz观测**。
30s warmup 后 300s /9000 帧，世界30Hz，整帧 P99 34.591ms，2.544%帧超过33.333ms，
最长连续超时3帧；观测响应P99 35.670ms，动作排队P99 28.431ms，完成99.9% nominal load。
12,502 次接受 move，14,409 次拒绝动作，平均同时moving64.23、最大125；不是5000单位全动。
世界模拟推进299.999s。前置60s点P99 29.034ms通过，无法覆盖长测失败。

30–60s block 的平均构建/编码为4.667/0.784ms，300–330s为5.914/1.217ms；
平均响应从154,871增至228,976 bytes，visible terrain从2053增至2865，敌人从79增至214。
这是成本增长与观测内容增长的相关证据，不把增长直接归因为 Chrome，也不声称已排除其它原因。
机器值见 [long-candidate-trend.json](results/long-candidate-trend.json)。

## 证据与工具限制

- `runtime-base100` 使用早期 update-only timer 和较慢 pacing，只作排队负证据，不作整帧对照。
- 后续先修正 FPS oversleep 漂移，再包含 profiler bookkeeping；不同 timer 不能混合汇总。
- `runtime-spatial5000-d60` 的最后队列状态在清理后取样，原样保留失败；修复后未补同点正式四条验证。
- `poll5000-a1000-h10` 启动时只读 analyzer 正在修改，因此 tooling_clean=false；保留无效诊断。
  随后 `poll5000-a1000-h10-clean` 在干净工具版本重跑，矩阵采用后者，前者不删除。
- 已检查全部24个raw包的SHA256并重新计算帧/观测/动作队列指标；测试会拒绝raw和报告指标篡改。
- 因目标1Hz点已明显过载，没有拿更低频闭环补齐四条正式重复来替代用户目标。
