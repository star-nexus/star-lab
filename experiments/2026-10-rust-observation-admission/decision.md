## E8 本轮完成（2026-10-08，当前）

修订后的native1 P2通过：40994请求、9880 tick、11007观测及计数、46807完整权威检查点；全部响应、展示增量、事件及最终状态一致。真实接纳轨迹12148请求/2617 tick/750段及12个release边界、4个锁定依赖诊断故障检查已复用，不再运行。native4完整接纳验收暂缓，诊断注错不等于release wheel注错或一般内存安全证明。

唯一native1 ABBA/BAAB服务筛选完成且计时资源有效：观测服务均值3.068→2.765ms，改善9.882%，P99 4.199→4.101ms；所测总工作均值4.625→4.367ms，改善5.584%，P99 12.307→11.621ms。改善95%区间分别0.211–0.388ms、0.112–0.408ms。保留全部2617 tick/3010观测和慢尾，最大值分别111.36→123.34ms、116.23→142.73ms，最大值并非本轮门槛但不能称所有尾部都改善。

结论：有继续验证完整宿主链路的价值；本轮只证明请求/cache服务筛选收益，未计入实时heap扫描与显示apply/render/submit，不构成整帧提速、稳定多轮收益或上线验收。默认关闭，正式宿主/窗口未启动，无自动补跑/加轮。G009及其他GAP、容量、Frontier和5000Agents暂缓保持。

进度：`完整参考 █ | 规范候选 █ | 接纳/边界 █ | 一轮收益筛选 █ | 正式宿主/默认 ░`。

恢复先读实验results/p2-native1-complete.json、p3-single-service-screen.json、completion-integrity-20261008.json及records/rust-observation-admission-status.json。两父任务与子进程已退出；旧逐组progress可能保留最后running checkpoint，以完成报告和最终raw为准，不重启历史运行。

以下为历史阶段记录，当前状态以上述完成记录为准。

> 当前有界执行：真实接纳native1 17382节点（54.23秒）、12个release短边界及4个锁依赖诊断故障测试通过。规范候选继续同PID；通过后仅一次90秒录制输入ABBA服务筛选，排除live heap/显示链，不称正式全宿主采用。见[证据](results/p2-targeted-admission.json)和[唯一筛选预注册](results/p3-single-service-screen-preregister.json)。

> 2026-10-08 精简修订：普通完整参考两次已通过，不再重跑。旧no_reuse完整组按用户要求取消，7543节点前缀只归档不计通过。当前仅执行规范encoded候选并复用已核验的旧扩展完整指纹；targeted/实际接纳仍待完成。见[预注册](results/p2-streamlined-preregister-20261008.json)。早期矩阵描述为历史计划，已被本修订覆盖。

# Decision — E8

**Status:** proposed; P0 complete, P1 authorized

## Decision

Proceed to a minimal owned-cache prototype because about 57% of measured queries have eligible continuous segments and repeated census/public builds are demonstrated. Do not claim speedup from profiled handler batching. First prove no_reuse equivalent to single, then encoded equivalence and a short non-diagnostic service screen.

## Resource policy

Latest user explicitly authorizes continuing under memory warning. E8 now uses telemetry only: no automatic pause, kill or runtime timeout. Pressure evidence still governs formal timing validity; no silently accepting interfered performance samples.

## Limits and revisit

Original window operational guards failed; P0 is diagnosis. Existing GAPs/capacity/Frontier unchanged; 5000 Agents deferred; default research off. Later implementation/benefit gates govern P2–P4 and adoption.

## Provenance

[Results](results/p0-complete.json), [Integrity](results/p0-integrity.json), [Raw](artifacts/e8-p0-20261007-raw.zip).

## P1 decision

小型契约及独立旧扩展短宿主对照通过；公共build下降且代表service未明显恶化，允许进入P2。单次screen不是正式收益，candidate普通路径对旧扩展的未配对回退保留，不隐藏。P2以固定6ec8e05、同wheel和独立旧扩展比较。只正确性校验，不进入P3或默认；targeted全部通过后才宣布P2完成。

## Accounting correction decision

发现null==null断言后不把旧计数检查称通过；原始证据完整保留并单独勘误。允许当前普通全状态轨迹自然结束，身份门槛阻止旧诊断进一步进入cached模式。隔离修正wheel、修正oracle新预注册后按序继续，不因本缺陷杀掉正在执行的有效ordinary轨迹，不启动P3。
