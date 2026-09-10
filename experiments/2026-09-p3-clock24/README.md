# P3 — 24Hz 固定模拟时钟与随机闭环 Agents

**Status:** measured engineering workload; see actual metrics below, not a claim that every strict gate passed.  
**STAR repository:** star-nexus/star  
**Measured / validated source:** `906386312d70d77af25e4b4da883f6dd5b0fe5ef`  
**Existing source tag:** `p3-read-batch-pre-squash-2026-09-09` has the same tree as measured main. No new production change/tag in this experiment.

## 1. Problem and user intent

用户要求ENV每帧按1/FPS推进模拟秒，CD/恢复使用模拟时间；外部Agent用墙钟思考，期间不轮询。
之前助手强调保持墙钟推进与用户意图不同，现已纠正；旧独立轮询仅保留为压力测试。

## 2. Implementation and clock boundary

生产capped模式已经使用固定delta，GameTime累计delta，ResourceRecovery读取GameTime；无需重写生产时钟。
Lab新增 --fps / --clock-mode / --cycle-mode / --jitter-seconds；本次fixed模式不传--uncapped。
每帧验证dt=1/24，且GameTime累计等于delta累计。墙钟用于Agent等待、请求延迟、帧限速和测量，不能驱动CD追赶。
若实际运行不足24Hz，模拟时间会落后墙钟。这是明确选择的固定步长语义，报告同时记录两种时间。

## 3. Workload

5000初始Units、1000Agents，平均每Agent5个Units，全部真实注册和认领；不连接真实LLM或Protocol/Hub。
每轮get_faction_state→逐Unit随机move50%/attack25%/wait25%→立即提交动作→等待→下一轮。没有合法目标则等待，不重复抽签。
首次请求uniform(0,30s)，每轮等待为截断正态N(30,5²)，范围15–45s；动作与时序随机流独立且seed可复现。
这是一种合成到达模型，不声称已拟合真实玩家数据。并非5000Units始终同时移动。
Fog ON，selected面板，stdlib JSON编码/客户端解码均计时；single入口保持读写次序（不能将即时动作之后的读提前凑批）。
Chrome保持开启，真实窗口，性能进程串行，realtime_defer只代表本次有限实验epoch。
初始interleaved分散交错布局作为高接触密度负对照；canonical为此前低频5000/1000实验使用的阵营集结布局。

## 4. Reproduction

Lab工具精确SHA与全部参数见每个result的tooling/workload；四组之间的代码不变，仅记录提交与参数不同。

```bash
cd /Users/liyang/Developer/star-lab
mkdir -p runs/reproduce-clock24
git -C /Users/liyang/Developer/star-main worktree add --detach /Users/liyang/Developer/star-lab/runs/reproduce-clock24-source 906386312d70d77af25e4b4da883f6dd5b0fe5ef
/Users/liyang/Developer/star-main/.venv/bin/python tools/p3_runtime.py --source /Users/liyang/Developer/star-lab/runs/reproduce-clock24-source --fps 24 --clock-mode fixed --cycle-mode post-action --jitter-seconds 5 --units 5000 --agents 1000 --delay 30 --observation-mode single --scope selected --layout canonical --policy stochastic --seconds 300 --warmup 30 --budget-ms 18 --gc-policy realtime_defer --output runs/reproduce-clock24/run.json > runs/reproduce-clock24/run.log 2>&1
```

采用Lab worktree，fixture和结果均不写入生产checkout。暂停本次实验不影响生产默认FPS。

## 5. Results

| 布局 / Agent预算 | 测量秒数 | 世界Hz | 帧P99 ms | 观测P99 ms | 动作排队P99 ms | 名义闭环比例 |
|---|---:|---:|---:|---:|---:|---:|
| [interleaved / 12ms](results/discovery60.json) | 60 | 16.93 | 70.90 | 25138.48 | 25091.00 | 50.98% |
| [canonical / 12ms](results/canonical60.json) | 60 | 24.00 | 36.28 | 484.15 | 488.42 | 100.41% |
| [canonical / 18ms](results/canonical18-60.json) | 60 | 24.00 | 41.10 | 123.46 | 118.56 | 100.46% |
| [canonical / 18ms](results/canonical18-300.json) | 300 | 24.00 | 44.54 | 177.97 | 170.45 | 99.74% |

300s窗口实际接受 **24770 moves / 957 attacks**，拒绝动作106次。
存活Units最少5000；采样同时移动平均120.38、最大181。
测量窗口delta累计300.000000模拟秒；窗口墙钟300秒。完整census中的GameTime也逐项核验。
12ms→18ms是看到随机突发排队后预先记录的单参数对照；首版负结果未删除。

300s窗口内5000个Units全部存活；采样同时移动平均120.38、最大181。实际思考等待均值29.9965秒，范围15.0651–44.7335秒。
整帧超过41.667ms的比例约7.60%，最大48.94ms；平均24Hz不等于每帧都在预算内。期末最老排队30.18ms。

## 6. Interpretation and limits

必须分别报告世界Hz、帧尾耗时、Agent尾延迟和实载。不要仅以一个100ms请求SLO越线把可运行配置描述为完全不可用，也不要隐藏越线。
旧严格guard仍逐项保留；这次是用户认可24Hz背景下的工程运行评估，没有完成300s+3×60s全部严格guard通过的容量认证。
名义闭环比例以同一随机等待序列、零服务时间的参考过程计算；服务导致事件跨测量窗边界，比例可略高于100%，不表示重复请求。
初始5000Units是已验证规模。战斗可能合法致死，故另要求测量存活≥初始95%，并保留实际数量，防止负载消失造成假通过。
不能推广到广泛混战布局、不同Agent等待分布、真实网络、100%持续移动或任意机器。

## 7. Evidence and verification

4组compact/raw ZIP；2个按hash单份保存的fixture ZIP。所有raw解包重算、SHA/size验证；见manifest与SHA256SUMS。
9个生产时钟测试、12个Lab调度/分析测试通过。生产源未修改。
参见[分析](analysis.md)、[决策](decision.md)、[恢复入口](../../records/10k-online-resume.md)。
