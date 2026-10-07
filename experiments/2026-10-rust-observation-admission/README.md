> 当前修订：先读[计数诊断勘误](results/p1-accounting-erratum.json)和[v2预注册](results/p2-v2-preregister.json)。旧逐请求计数断言已撤回；完整响应/权威/展示结果仍保留。原普通全轨迹继续同PID运行，修正矩阵等它退出后串行开始。

# E8：已接纳观测只读段复用

状态：P0/P1已归档，P2完整轨迹矩阵执行中，targeted错误/故障/VLM检查尚未完成。默认关闭。算法和门槛见[方案](../../records/rust-observation-admission-plan.md)。

进度：`P0 █ | P1 █ | P2轨迹 ▓ | P2 targeted ░ | P3 ░ | 默认 ░`。

## Reproduction

起点产品5b9658b，候选6ec8e05；精确源码、wheel/扩展、独立旧扩展及增量源码bundle校验见[完整性](results/p1-integrity.json)。源码bundle依赖旧5b9658b，先恢复引用的E7源码包。P1原始包保存三个模式、独立旧扩展的小型单次筛选、诊断、88项契约及短宿主2698节点完整oracle。诊断与单次筛选不构成正式收益。

P2入口tools/rust_migration/run_observation_admission_p2.py；[预注册](results/p2-preregister.json)固定三模式native1规范轨迹和P0实际接纳native1/4复用轨迹。规范60754节点=40994请求+9880tick+9880展示；规范相邻query不冒充host接纳证据。P0实录另提供合法段边界。逐请求/写入/推进的实际校验位置见预注册。

恢复先读/Users/liyang/Developer/star-lab-runs/e8-p2-20261007/p2-progress.json及当前组.progress.json、.monitor.json和parent.log。已有活进程时不得再次启动入口；它不会自动重试或进入P3。完成轨迹矩阵后仍有targeted验收，结果文件明确P2_complete=false。

## Evidence and limits

[P0](results/p0-complete.json)、[P1](results/p1-complete.json)及[完整性链](results/p1-integrity.json)。P1小筛选保持全部样本：候选single约2.579ms、no_reuse约2.662ms、encoded约2.006ms；旧扩展single约2.393ms。顺序执行且未配对，不能把这些均值当稳定净收益，ordinary单次回退须在后续正式旧/新对照中解释。

用户最新授权：内存仅遥测，不自动暂停/kill/超时，无强制限额。正式性能有效性仍独立判断，受压力影响的计时保留但不作为有效收益。E6/E7研究默认关闭、现有GAP和容量/Frontier不变。

在实验目录运行shasum -a 256 -c SHA256SUMS；raw ZIP内另有SHA256SUMS。大型固定输入通过路径及哈希引用，不重复存入Git。
