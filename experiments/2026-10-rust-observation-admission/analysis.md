## E8 完整Lab宿主净收益筛选（2026-10-08，当前）

用户已授权先验证完整宿主净收益。一次ABBA，4个独立进程串行，各30秒预热＋60秒测量；5000 Units/1000 Agents，native1，同9bb2fa扩展/11d9927源码，仅切换single/segment_encoded。包括真实heap/逐请求预算/持久Session消费与RNG/世界/delta/普通展示/绘制/SDL flip，排除FPS等待和生产网络。当前窗口2480×1235（历史1239高），四次严格同尺寸；不与历史窗口作容量比较。

复用全部已通过P2，不重跑长正确性、不补跑择优或加矩阵。5秒target-load冒烟和新边界/统计负控通过；冒烟帧P99 37.27ms与短duration不计性能验收。真实轨迹随服务速度不同，本轮是运行净收益筛选，统计为非配对实时100帧分块，不冒充固定输入因果改善。所有原负载/队列/帧/频率guards保留；压力仅记录，非normal样本整次资源无效，不自动暂停/kill/重试。

恢复读取 results/full-host-screen-preregister.json 及 /Users/liyang/Developer/star-lab-runs/e8-full-host-screen-20261008/progress.json、各monitor与parent.log。入口 tools/rust_migration/run_admitted_host_screen.py；若活跃不要重复启动。结束自动归档，但Lab最终diff/独立校验与提交由后续审查完成。任何child或身份失败保留完整尝试并停止后续，不修改冻结工具或默认。

进度：`既有P2 █ | 服务筛选 █ | 宿主工具/控制 █ | 宿主ABBA ░ 0/4 | 正式采用 ░`。G009/既有GAP、容量/Frontier不变，5000Agents暂缓，不push/merge。

## E8 本轮完成（2026-10-08，当前）

修订后的native1 P2通过：40994请求、9880 tick、11007观测及计数、46807完整权威检查点；全部响应、展示增量、事件及最终状态一致。真实接纳轨迹12148请求/2617 tick/750段及12个release边界、4个锁定依赖诊断故障检查已复用，不再运行。native4完整接纳验收暂缓，诊断注错不等于release wheel注错或一般内存安全证明。

唯一native1 ABBA/BAAB服务筛选完成且计时资源有效：观测服务均值3.068→2.765ms，改善9.882%，P99 4.199→4.101ms；所测总工作均值4.625→4.367ms，改善5.584%，P99 12.307→11.621ms。改善95%区间分别0.211–0.388ms、0.112–0.408ms。保留全部2617 tick/3010观测和慢尾，最大值分别111.36→123.34ms、116.23→142.73ms，最大值并非本轮门槛但不能称所有尾部都改善。

结论：有继续验证完整宿主链路的价值；本轮只证明请求/cache服务筛选收益，未计入实时heap扫描与显示apply/render/submit，不构成整帧提速、稳定多轮收益或上线验收。默认关闭，正式宿主/窗口未启动，无自动补跑/加轮。G009及其他GAP、容量、Frontier和5000Agents暂缓保持。

进度：`完整参考 █ | 规范候选 █ | 接纳/边界 █ | 一轮收益筛选 █ | 正式宿主/默认 ░`。

恢复先读实验results/p2-native1-complete.json、p3-single-service-screen.json、completion-integrity-20261008.json及records/rust-observation-admission-status.json。两父任务与子进程已退出；旧逐组progress可能保留最后running checkpoint，以完成报告和最终raw为准，不重启历史运行。

以下为历史阶段记录，当前状态以上述完成记录为准。

> 当前有界执行：真实接纳native1 17382节点（54.23秒）、12个release短边界及4个锁依赖诊断故障测试通过。规范候选继续同PID；通过后仅一次90秒录制输入ABBA服务筛选，排除live heap/显示链，不称正式全宿主采用。见[证据](results/p2-targeted-admission.json)和[唯一筛选预注册](results/p3-single-service-screen-preregister.json)。

> 2026-10-08 精简修订：普通完整参考两次已通过，不再重跑。旧no_reuse完整组按用户要求取消，7543节点前缀只归档不计通过。当前仅执行规范encoded候选并复用已核验的旧扩展完整指纹；targeted/实际接纳仍待完成。见[预注册](results/p2-streamlined-preregister-20261008.json)。早期矩阵描述为历史计划，已被本修订覆盖。

# Analysis — E8

## Hypothesis

已接纳连续只读请求可以共享 census、公共事实编码与重复 panel，且逐请求执行/返回/计数顺序保持。

## Instrumentation

仅包装冻结单请求 pump 的原 heappop，读取最多四个堆前缀；不批量弹出、不执行额外查询。诊断探针和 300 组前缀及插入事件契约检查已通过。正式性能须关闭诊断。

## Evidence / limits

P0已完成。历史相邻查询不是当前接纳证据。

## P0 measured diagnosis

1943 measured observations; 1106 (56.92%) belonged to legal 2–4 query candidate segments. No batching was executed. Full 12148 requests, 2617 ticks and 2617 presentation events replayed identically, including final authority. 19 pressure samples were normal; peak RSS 695.9 MiB.

| Kind | Samples | Individual fact build ms | Shared fact build ms | Individual/shared panel builds |
|---|---:|---:|---:|---:|
| 1-same | 10 | 1.181 | 0.986 | 5/5 |
| 2-mixed | 10 | 2.377 | 1.659 | 10/10 |
| 2-same | 10 | 2.499 | 0.968 | 10/10 |
| 3-mixed | 10 | 3.645 | 1.752 | 15/15 |
| 3-same | 10 | 3.814 | 1.082 | 15/15 |
| 4-mixed | 10 | 4.228 | 1.790 | 20/20 |
| 4-same | 1 | 4.734 | 0.955 | 20/20 |

Faction timings include census and public encoding; never add nested times. Singles-before-shared is warm-biased: singleton difference demonstrates noise. These are removable-build screening data, not authenticated service improvement. No repeated panels were found in sampled segments. P0 window Hz/queue guards failed; diagnostic overhead/slow samples all retained, no capacity validation. Actual cache residency remains to be measured in P1. The failed normalization probe and resource-interrupted smoke remain archived; neither counts as workload pass.

## P1 owned-cache and short contracts

候选6ec8e05新增私有scope/token，每条仍保留decode、鉴权、wall、accounting、输出及消费顺序。owned缓存move，无World/Fog/完整缓存clone，不增加worker。所有普通native入口在访问Runtime前失效缓存。缓存事实不依赖query的wall/action计数；Unit panel的available_skills只读取冷UnitSkills、排序输出，不读取计数或wall。权限owner/commandable每请求重新获取。

88项Python契约通过；独立旧扩展短宿主轨迹2392请求/153tick/153展示全部通过，含2545个全权威节点、200个完整观测wire、完整展示增量和事件。模拟pump的预算切断/新队首/错误cleanup与原队列、RNG、消费命令一致。这不是生产网络验收，G009仍OPEN。

| 单次代表screen | Queries | Service mean ms |
|---|---:|---:|
| candidate single | 570 | 2.579 |
| candidate no_reuse | 570 | 2.662 |
| candidate encoded | 570 | 2.006 |
| independent old single | 570 | 2.393 |

全部完整wire、消费命令和最终权威状态hash一致。上述运行未配对，状态静态、无host扫描，不能用于5%正式门槛；candidate ordinary单次比旧扩展慢约7.8%，完整保留并待正式控制漂移。独立诊断显示census每段构建一次；记录编码backing字节峰值836382，仅表示片段字节，不是完整分配/RSS或一般无泄漏证明。普通和复用完整固定轨迹等价尚在P2校验。

## P2 scope

三模式native1规范轨迹各40994请求/9880tick/9880展示；实际接纳录制的encoded native1/4另重放。逐节点全authority导出成本使每个完整规范模式需数小时，按流比较，不保存全World历史。两种输入分别证明world语义与实际已接纳段，不把旧规范相邻query说成真实host eligibility。targeted故障/编码/VLM/revision验收仍pending；P3未开始。

## Accounting oracle correction

P1原diagnostic/helper错用单数计数字段，非空回归在原3e0ebb扩展上失败（None对1），因此撤回其逐请求计数验证声明。原完整响应与全authority对照不受此诊断键错误影响。11d9927与v2 oracle使用实际复数字段，注册Agent计数必须为整数；88契约重新通过，代表诊断/完整状态/消费命令/wire保持一致。原普通全轨迹仍用旧已加载二进制跑完；v2矩阵等待旧child/parent退出，旧冻结工具不改。
