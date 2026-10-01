# E5 分析：Movement ∥ Visuals

## Observation

E3 规范轨迹中，扣除结构操作的乐观上界约8.1–8.2µs/all tick，门槛8条件预算
约13µs，3772/9880候选tick。这是诊断上界，不是净收益。E4候选caller工作较短；
E5的Movement约31µs，可能隐藏worker唤醒/等待成本，因此没有复用E4派发成本
作为本轮停止条件。

## Hypothesis

H1：后台Visuals的实际计算能与更长的Movement重叠，完整step得到稳定净收益。
H2：准备、发布、scoped派发及调度尾延迟消耗小批次预算，或收益小于可重复性噪声。
两种解释通过同模式禁用门槛对照、split_serial对照和独立诊断区分，不把诊断
计时结果直接替代无诊断完整step。

## Instrumentation

私有四模式推进；PROFILE=false完全关闭计时和diagnostic计数。主对照为同一
parallel代码门槛8与usize::MAX，native2/4各三轮、每tick ABBA/BAAB交替，
另各三轮parallel vs split_serial。计时只包围实际native调用；请求、响应解码、
展示和校验在外部完成。每个世界独立初始化并持有独立pool，任一时刻只有一个
world调用正在推进。没有逐tick世界复制或跨实例共用可变状态。

两侧各19760个原始step用于mean/P99/max；9880个tick的两侧均值差用于100-tick
分块bootstrap，10000次、seed42，末尾80tick按实际tick数加权。不得删掉预热、
慢尾或不满足调度门槛的tick。每轮mean改善、P99不回退、改善CI95下界>0才通过。

诊断分别测prepare、compute、publish及inclusive region。若Movement+compute
时长超过region时长，差值是时间区间交叠的下界。region包含两侧，不能与它们
相加；诊断开启嵌套时钟、bookkeeping且有固定plain-first顺序，只用于机制解释。

## Evidence

主门槛，正值表示parallel更快，负值表示更慢：

| 对照 | Mean 改善 | CI95改善（µs） | P99对照 → parallel（µs） | 门槛 |
|---|---:|---:|---:|---|
| primary-t2-r1 | 0.593% | [0.553, 2.109] | 629.208 → 618.709 | PASS |
| primary-t2-r2 | 0.688% | [-0.473, 3.991] | 763.083 → 736.167 | FAIL |
| primary-t2-r3 | -0.023% | [-1.512, 1.210] | 655.166 → 690.583 | FAIL |
| primary-t4-r1 | -0.747% | [-5.423, 1.041] | 673.209 → 681.625 | FAIL |
| primary-t4-r2 | -0.273% | [-4.884, 2.474] | 753.666 → 738.208 | FAIL |
| primary-t4-r3 | 0.742% | [0.899, 2.339] | 604.583 → 582.250 | PASS |

拆分对照（均为门槛8）：

| 对照 | Mean 改善 | CI95改善（µs） | P99对照 → parallel（µs） | 门槛 |
|---|---:|---:|---:|---|
| split-control-t2-r1 | 0.994% | [0.808, 4.608] | 703.625 → 707.792 | FAIL |
| split-control-t2-r2 | 0.225% | [-0.507, 1.558] | 661.417 → 672.833 | FAIL |
| split-control-t2-r3 | 0.381% | [-0.005, 1.753] | 702.458 → 658.167 | FAIL |
| split-control-t4-r1 | 0.879% | [-0.897, 6.039] | 836.084 → 807.709 | FAIL |
| split-control-t4-r2 | 0.411% | [0.174, 1.702] | 613.166 → 666.750 | FAIL |
| split-control-t4-r3 | 0.941% | [1.429, 2.765] | 601.167 → 577.500 | PASS |

单轮敏感性（不作为生产选择）：

| 对照 | Mean 改善 | CI95改善（µs） | P99对照 → parallel（µs） | 门槛 |
|---|---:|---:|---:|---|
| sensitivity-0-t2 | 0.381% | [-0.415, 2.511] | 668.041 → 664.167 | FAIL |
| sensitivity-0-t4 | 1.816% | [-0.306, 11.203] | 883.042 → 852.041 | FAIL |
| sensitivity-16-t2 | 0.188% | [-2.218, 4.383] | 759.750 → 779.709 | FAIL |
| sensitivity-16-t4 | 0.109% | [-3.872, 5.328] | 990.875 → 990.708 | FAIL |
| sensitivity-4-t2 | 0.868% | [-1.850, 6.267] | 749.834 → 748.000 | FAIL |
| sensitivity-4-t4 | -0.146% | [-5.869, 3.305] | 877.500 → 880.333 | FAIL |

四模式共同3772-tick掩码诊断（µs）：

| Threads / 模式 | Prepare | Movement | Visuals / Compute | Publish | Region |
|---|---:|---:|---:|---:|---:|
| 2 / baseline | 0.000 | 40.221 | 16.510 | 0.000 | 0.000 |
| 2 / empty_fork | 0.000 | 42.008 | 16.447 | 0.000 | 44.237 |
| 2 / split_serial | 0.213 | 38.082 | 15.648 | 0.466 | 0.000 |
| 2 / parallel | 0.220 | 41.095 | 19.144 | 0.499 | 43.558 |
| 4 / baseline | 0.000 | 36.384 | 16.106 | 0.000 | 0.000 |
| 4 / empty_fork | 0.000 | 37.953 | 15.037 | 0.000 | 40.560 |
| 4 / split_serial | 0.206 | 37.454 | 15.228 | 0.498 | 0.000 |
| 4 / parallel | 0.205 | 38.451 | 18.245 | 0.480 | 41.041 |

Region包含Movement和Compute，不能相加。native2/4的parallel计时区间交叠下界均值为16.917/15.769µs，3758/3761个候选tick下界>0。它包含嵌套时钟及OS时间，不是纯CPU计算收益；跨诊断run的成本差也不能解释为精确因果净收益。

完整响应、全展示增量/事件和最终state按历史canonical核验，四world直接比较
完整对象；13边界场景逐步比较完整state/error/delta/reset。此证据覆盖实际运行
轨迹与明确边界，不能代表所有未测配置或更高接触密度。

## Root cause / causal limits

已证实：窄输入和所有权计划允许两个System的计算区间安全重叠，完整规则/错误前缀等价；当前轨迹下门槛8在native2/4均只1/3主轮通过，未获得满足预设门槛的可重复完整step净收益。六组敏感性全部CI95跨零，不能找到经过确认的替代阈值。具体调度/核心/allocator噪声占比没有被隔离，因此不宣称它们是已确认根因，也不宣称无诊断并行必然负收益。

不将温度、CPU核心迁移、后台负载或allocator影响称为已证实原因。本轮没有为
这些因素提供隔离计数器。稳定门槛失败与具体OS原因属于不同判断。

## Rejected explanations

* “E4诊断成本已证明所有System之间并行无价值”：拒绝；本轮是不同依赖与实际重叠。
* “四线程就有四个参与者同时跑这两个System”：拒绝；E5区域最多一worker＋caller。
* “门槛8是生产最小充分值”：拒绝；它是预先固定的首选候选，敏感性不自动改策略。
* “逐tick四world配对足以证明实际窗口容量”：拒绝；只有通过主门槛与单实例确认后
  才允许窗口阶段；既有E2/R4e容量身份不被覆盖。

## Limits / forensic path

仅本机、R4e记录的5000Units/1000Agents、当前移动/接触密度。诊断上界和private
调用性能不是整帧改善或5000Agents容量。API18/schema5、默认1及原规则保留。
机器可读结果、所有原始step/timing、准确工具版本、wheel与检验链见manifest/results。
