## E8 本轮完成（2026-10-08，当前）

修订后的native1 P2通过：40994请求、9880 tick、11007观测及计数、46807完整权威检查点；全部响应、展示增量、事件及最终状态一致。真实接纳轨迹12148请求/2617 tick/750段及12个release边界、4个锁定依赖诊断故障检查已复用，不再运行。native4完整接纳验收暂缓，诊断注错不等于release wheel注错或一般内存安全证明。

唯一native1 ABBA/BAAB服务筛选完成且计时资源有效：观测服务均值3.068→2.765ms，改善9.882%，P99 4.199→4.101ms；所测总工作均值4.625→4.367ms，改善5.584%，P99 12.307→11.621ms。改善95%区间分别0.211–0.388ms、0.112–0.408ms。保留全部2617 tick/3010观测和慢尾，最大值分别111.36→123.34ms、116.23→142.73ms，最大值并非本轮门槛但不能称所有尾部都改善。

结论：有继续验证完整宿主链路的价值；本轮只证明请求/cache服务筛选收益，未计入实时heap扫描与显示apply/render/submit，不构成整帧提速、稳定多轮收益或上线验收。默认关闭，正式宿主/窗口未启动，无自动补跑/加轮。G009及其他GAP、容量、Frontier和5000Agents暂缓保持。

进度：`完整参考 █ | 规范候选 █ | 接纳/边界 █ | 一轮收益筛选 █ | 正式宿主/默认 ░`。

恢复先读实验results/p2-native1-complete.json、p3-single-service-screen.json、completion-integrity-20261008.json及records/rust-observation-admission-status.json。两父任务与子进程已退出；旧逐组progress可能保留最后running checkpoint，以完成报告和最终raw为准，不重启历史运行。

以下为历史阶段记录，当前状态以上述完成记录为准。

> 当前有界执行：真实接纳native1 17382节点（54.23秒）、12个release短边界及4个锁依赖诊断故障测试通过。规范候选继续同PID；通过后仅一次90秒录制输入ABBA服务筛选，排除live heap/显示链，不称正式全宿主采用。见[证据](results/p2-targeted-admission.json)和[唯一筛选预注册](results/p3-single-service-screen-preregister.json)。

> 2026-10-08 精简修订：普通完整参考两次已通过，不再重跑。旧no_reuse完整组按用户要求取消，7543节点前缀只归档不计通过。当前仅执行规范encoded候选并复用已核验的旧扩展完整指纹；targeted/实际接纳仍待完成。见[预注册](results/p2-streamlined-preregister-20261008.json)。早期矩阵描述为历史计划，已被本修订覆盖。

> 2026-10-08恢复：原普通校验同PID继续，旧监督器/旧v2队列已退出；优先读[恢复记录](results/p2-supervisor-recovery-20261008.json)和[恢复预注册](results/p2-recovery-preregister-20261008.json)。新遥测和恢复父任务等待原组完成，无重跑。

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
