## E8 完整Lab宿主筛选结束（2026-10-08，当前）

4/4次ABBA完整结束，全部原运行guards通过且全部pressure normal；每次正式1800帧，观测1944/1943/1944/1944条。所有预热、正式样本、慢尾、失败冒烟guard记录均保留，116项归档/内外哈希及非配对100帧bootstrap统计独立复算通过。源11d9927、9bb2fa隔离扩展与d475e23工具节点固定；活动/冻结HEAD、原49删除及安装扩展3e0ebb均保留。

| 指标 | baseline两次均值 | cache两次均值 | 本轮运行观察 |
|---|---:|---:|---|
| 观测完整service | 2.6785ms | 2.4637ms | 减少8.0198%；均值改善区间0.1680–0.2622ms |
| 完整帧work（除FPS等待） | 18.8541ms | 18.5816ms | 减少1.4449%；改善区间−0.1164–0.6688ms，跨零 |
| Agent pump/帧 | 3.1003ms | 2.8642ms | 粗阶段观察，含真实队列和消费 |
| frame P99最差运行 | 26.1553ms | 25.2535ms | 均低于33.33ms；本轮未回退 |
| service P99最差运行 | 3.2002ms | 3.2391ms | 回退0.03896ms（约1.22%），未过筛选门槛 |

四次世界均30Hz，5000 Units存活，负载完成约100.15–100.21%，Fog/合法移动与攻击/积压/观测与动作队列guards全过；观测response和queue与这里的service是不同指标。实时session和队列随执行速度产生不同轨迹，因此这些不是同输入配对因果加速比，也不是三轮稳定性/生产网络验收。当前Cocoa窗口2480×1235，区别于历史1239高，四次尺寸相同。

判断：缓存服务收益在真实宿主中仍可见，但完整帧净收益未达到确认门槛；默认关闭，不上线、不补跑择优。Agent pump约占baseline帧16.44%，当前服务节省折算量级约0.232ms/帧，与完整帧观察差异同一量级；显示与其他工作保留，不能期望8%服务直接成为8%帧收益。下一步若继续投入，优先针对未复用单条/段首和P99的准备、编码与消费成本做有界归因，再选择一次单因素原型；不继续扩大长测试量，也不预先改变缓存参数。E8结果不修改容量/Frontier或关闭G009/既有GAP，5000Agents暂缓。

恢复读 results/full-host-screen.json、full-host-integrity.json、full-host-screen-preregister.json 与本实验analysis/decision；原始包artifacts/e8-full-host-screen-20261008-raw.zip SHA7413142c2c5d16462db3ca6e80814c8f9433127b0224aa0e1c67a47a34caa0f8，ZIP成员校验通过。父任务32566已退出；本轮任务已结束，不从旧progress重启。

进度：`P2 █ | 服务筛选 █ | 完整Lab宿主 █ 4/4 | 采用门槛 未通过 | 默认/生产网络 ░`。

以下为历史预注册与阶段证据。

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
