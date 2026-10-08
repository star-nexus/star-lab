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
