## E8 census 已收敛为正式默认实现（2026-10-09，当前）

用户明确授权正式采用并推送GitHub。产品提交 `b2aae3d2b47cf58b8aeddac56be1a9feaae8ecf9`，分支 `codex/rust-ecs-parallel` 已推送并设置origin上游。Rust普通人口统计直接使用借用键累积/拥有键发布，删除三模式控制与未采用EntityRef分支。API18/schema5、规则/观测内容/ID及动作顺序、native默认1保持；默认游戏后端仍Python，普通宿主读段缓存未启用，E6/E7等研究默认不变。活动工作树已安装新release扩展 `1921d2`；原目录49删除和冻结Rust/Python两个HEAD保持。

115项观测/边界契约、6Rust测试、fmt/Clippy/release通过，安装后2个生命周期冒烟通过。独立旧c6默认baseline与新二进制各重放同一短规范输入：12148请求/2617tick/3010观测/17382操作，逐操作响应、完整wire、全部展示增量/事件、消费命令及最终完整状态一致；另16个native1/4缺组件/Fog边界投影与全部计数一致。此前完整长P2仍只属于旧源；本轮没有重跑长性能矩阵/新live/native4完整宿主/像素/生产网络。

采用依据是已测局部service收益（普通宿主旧源8c2：9.2258%、CI正、P99包络通过）、移除冗余分配的有界改动、回归和用户明确授权。旧完整帧改善1.3256%、CI跨零的预注册门槛仍未通过，旧结论和raw不改判；没有将新源码宣称为新性能测量。这是后续局部采用决策，不是整帧/容量/Frontier/G009验收。GAP保持、5000Agents暂缓，产品分支尚未合并main或发布wheel版本。

恢复先读本实验README第9节、decision第9节、results/census-adoption.json与census-adoption-artifact-integrity.json。原始包 `artifacts/e8-census-adoption-20261009-raw.zip`（97793a9785c04e46dadbe935f52408c9b576d0ff261f94cbbd2b909d8f509e9a，2862889 bytes，25项内SHA），含wheel、源码增量bundle/patch、全部回归/重放和测试工具。compact与外SHA另列。持久目录 `/Users/liyang/Developer/star-lab-runs/e8-census-adoption-20261009`。新测试中曾有两个错误预期（鉴权与缺Position）和一次driver录制字段假设错误，已纠正且日志分类保留，不是生产行为差异或性能证据；不重启已完成重放。

进度：`正式收敛 █████ | 回归/安装 █████ | 短重放 █████ | 原始证据 █████ | 产品默认 已采用 | GitHub产品已推送`。

## E8 census 普通宿主确认完成（2026-10-09，采用前历史）

源 `8c2afd7153ebc8ec6c80dd9f3a1406be440405e0`／隔离扩展 `c6a60a`，测量工具节点 `1c9e5fe9af7450f2c7946e244bc070b995e5ec7b`。用户授权的一轮 ABBA 四次已全部完成，四次均使用普通 single 观测、段缓存关闭，仅切换 baseline/borrowed_census。每次30秒预热＋60秒测量，5000 Units＋1000 Agents、native1、Cocoa 2480×1235、普通展示、Fog和原队列/预算/Session消费保持。

| 指标 | baseline 两次均值 | census 两次均值 | 本轮结果 |
|---|---:|---:|---|
| 完整观测 service | 2.6908ms | 2.4425ms | 改善9.2258%；改善95%区间0.2060–0.2911ms，服务门槛通过 |
| 完整帧 work（不含FPS等待） | 19.2530ms | 18.9978ms | 改善1.3256%；改善95%区间−0.1730–0.6852ms，跨零，未通过 |
| frame P99 最差运行 | 26.6741ms | 26.3266ms | 未回退，低于33.33ms |
| service P99 最差运行 | 3.3113ms | 3.0030ms | 未回退 |

四次正式各1800帧，观测1943/1944/1944/1942条；含预热每次3011条。原运行guards全部通过，世界30Hz、5000 Units存活；压力全normal，无暂停/kill/超时/强制预算。第四次最终有1条逾期约1.034ms，在既定≤100ms积压guard内，未添加“零逾期”门槛。全部预热和慢尾保留；帧max分别28.3794/29.1312/30.5002/29.3192ms，不称所有尾部改善。

独立 nearest-rank 统计及非配对100帧分块/10000次bootstrap/seed42复算通过；实时轨迹随时序不同，不能称同输入配对因果加速或三轮稳定性。确认服务收益可出现在普通路径，无需依赖未采用的段缓存；完整帧净收益仍未确认。保留研究候选、默认关闭，不补跑择优、不继续扩矩阵。G009/既有GAP仍OPEN，native4完整宿主/生产网络未覆盖，容量/Frontier和5000 Agents暂缓保持。

恢复先读本实验 README、analysis/decision、results/census-host-complete.json、census-host-integrity.json 和 census-host-boundaries.json。原始包 `artifacts/e8-census-host-20261009-raw.zip` SHA `4aa198064c41336d1f0fdd6f014dbc45448e43cb4e1a6ace005bd0333a6927b1`，3870984 bytes，52个内部成员逐项核验；compact包含全部门槛数值与raw引用，外部SHA另列。持久目录 `/Users/liyang/Developer/star-lab-runs/e8-census-host-20261009` 最终progress为complete，父/子进程已退出，不重新启动。活动源、安装3e0ebb扩展、原49删除和两个冻结HEAD保持。只提交Lab记录；不push/merge。

进度：`工具/边界 █████ | 宿主ABBA █████ 4/4 | 独立复算/归档 █████ | 服务门槛 通过 | 整帧门槛 未通过 | 默认 关闭`。

## E8 观测服务专项首轮完成（2026-10-09，当前）

活动源 `8c2afd7153ebc8ec6c80dd9f3a1406be440405e0`，研究开关默认 baseline；entity_ref 和 borrowed_census 互斥。原49项删除、两个冻结目录及历史标签、已安装3e0ebb扩展保持，不push/merge。

完成成本诊断和两个独立短筛选，不重跑长P2或补跑择优。最终131项契约通过；每个因子12148请求/2617 tick/3010观测、四持续World、同二进制ABBA/BAAB，全部响应wire/增量/事件/消费命令/最终状态与原输入或四侧一致。新源码验证范围仅此次契约和短轨迹，不自动继承旧11d9927全9880-tick/native4宿主/像素范围。

- entity_ref：服务+2.773%，改善区间跨零，总工作−3.138%；不采用。
- borrowed_census：服务2.3733→2.1560ms，减少9.1569%，改善区间0.1561–0.2884ms；服务P99 3.4066→3.0226ms。总工作减少1.6956%，区间−0.0598–0.1878ms跨零，组合门槛未过，默认关闭。小诊断census0.3795→0.1717ms仅支持归因，不是宿主收益。

恢复先读 `experiments/2026-10-rust-observation-service/README.md`、analysis/decision、results/complete.json、census-analysis.json 和 portable-integrity.json。原始包 `artifacts/e8-service-20261008-09-raw.zip` SHA `975774d1fb3d28b6cd6de2e57d6891b154a51d8f6cd3cd543c6ac9cb933a48ed`，38个内部成员及外部校验通过；含原始样本、wheel、增量源bundle和冻结工具。规范输入/11d9927父源继续引用原E8包，不重复归档。

所有测试和监督进程已结束，不从progress最后running checkpoint重启。持久目录 `/Users/liyang/Developer/star-lab-runs/e8-service-20261008`。此轮停止于组合门槛；保留census服务候选供有界总成本/宿主研究，不自动重跑、叠加或加矩阵。默认/G009及既有GAP/容量/Frontier保持；5000Agents暂缓。

进度：`诊断 █████ 100% | 原型 █████ 100% | 相关正确性 █████ 100% | 两项筛选 █████ 100% | 采用门槛 未通过`。

以下为此前 E8 源码与阶段的历史记录，以各自 source SHA 为适用范围。

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

以下为历史执行记录，以上述完成结论为当前入口。

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

以下为历史恢复快照，不表示当前活跃测试。

## E8 精简候选校验（2026-10-08，当前）

规范 encoded 候选完整通过；targeted/实际接纳待完成。恢复先读 `/Users/liyang/Developer/star-lab-runs/e8-p2-streamlined-20261008/candidate-progress.json`、`encoded-t1.progress.json`、`encoded-t1.monitor.json` 与 `parent.log`。普通完整轨迹两次结果已归档，不重跑；no_reuse 冗长组按用户精简要求取消，未完成前缀保留而不算通过。候选复用独立旧二进制的已核验完整状态指纹，仍检查每个写入/step、单条或段末全状态、全部响应/展示及逐查询计数。本阶段仅规范轨迹候选，targeted 与实际接纳校验仍待完成；P2不宣称完成，P3/默认未启动。不因压力自动暂停/终止；不关闭GAP，不改容量/Frontier/5000Agents暂缓。

进度：`普通完整参考 █ | encoded候选 ▓ | targeted/实际接纳 ░ | P3 ░ | 默认 ░`。

## E8 有界后续执行（2026-10-08，当前）

接纳/边界检查已归档；等待现有规范候选后只做一次服务收益筛选。优先读 `/Users/liyang/Developer/star-lab-runs/e8-p3-single-screen-20261008/progress.json`、`parent.log`、`screen.json` 和 `screen.monitor.json`，不要重启任何已开始的测试。等待原规范候选父任务退出后核验原始哈希，复用真实接纳与16个边界/故障检查；仅做一轮native1完整90秒录制输入的服务ABBA筛选，不自动加轮或进入正式窗口。筛选包括cache开关、wire/bytes、decode与固定消费，排除实时heap扫描及显示apply/render/submit，不是完整宿主收益门槛；计时受压力干扰则inconclusive，不自动补跑。默认/GAP/容量/Frontier不变。

进度：`完整参考 █ | 规范候选 ▓ | 接纳/边界 █ | 一轮收益筛选 ░ | 正式宿主/默认 ░`。

## E8 精简候选校验（2026-10-08，当前）

普通完整参考已归档复用；仅运行规范 encoded 候选，targeted/实际接纳待完成。恢复先读 `/Users/liyang/Developer/star-lab-runs/e8-p2-streamlined-20261008/candidate-progress.json`、`encoded-t1.progress.json`、`encoded-t1.monitor.json` 与 `parent.log`。普通完整轨迹两次结果已归档，不重跑；no_reuse 冗长组按用户精简要求取消，未完成前缀保留而不算通过。候选复用独立旧二进制的已核验完整状态指纹，仍检查每个写入/step、单条或段末全状态、全部响应/展示及逐查询计数。本阶段仅规范轨迹候选，targeted 与实际接纳校验仍待完成；P2不宣称完成，P3/默认未启动。不因压力自动暂停/终止；不关闭GAP，不改容量/Frontier/5000Agents暂缓。

进度：`普通完整参考 █ | encoded候选 ▓ | targeted/实际接纳 ░ | P3 ░ | 默认 ░`。

## E8 监督器恢复（2026-10-08，最新）

当前普通全轨迹子进程57758始终保留，未重启/暂停；旧监督器已退出，旧monitor/progress的running状态可能过期。接续监督器日志明确有ENOSPC写入失败，原监督器实际退出原因未捕获；当前磁盘余量约9GiB。incident结果p2-supervisor-recovery-20261008.json保存日志/哈希和事实范围。

新遥测PID18628接管同一活PID；恢复父任务PID19105使用独立recover_observation_admission_p2.py与p2-recovery-preregister-20261008.json。优先读/Users/liyang/Developer/star-lab-runs/e8-p2-recovery-20261008/p2-progress.json、parent.log及ordinary-adopted.monitor.json；当前实际节点进度仍由旧目录canonical-single-t1.progress.json与checks.jsonl给出。原v2队列已退出但旧progress仍waiting，不要据此认为它活着。

当前组完成后验证所有60754节点、raw哈希和报告，再归档。adopted PID的OS退出码无法回收，必须明确unknown，不能伪造原guard passed。完整oracle结果/原始流独立验证才能接受其正确性范围，不计性能。后续5组规格保持原预注册；用户尚未选择精简方案，不擅自缩减。P2 targeted未完成，P3/默认未启动。源/原probe/冻结oracles与monitor保持，不改变既有GAP/容量/Frontier或5000Agents暂缓。

进度：`当前普通组 接近完成 | 监督恢复 █ | v2五组 等待 | targeted ░ | P3 ░`。

## E8 计数诊断修订与继续运行（2026-10-07，最新）

原计数诊断及其expected helper取了不存在的单数字段，两侧比较null不能证明逐请求计数。已保留旧包并用p1-accounting-erratum.json纠正范围；完整wire、全authority、展示/事件及队列RNG证明保持其原适用范围。源码11d9927只修正私有诊断字段和加强测试；旧扩展非空计数回归失败、修正扩展88项通过，代表诊断有真实整数计数且响应/命令/状态不变。

已运行的v1 canonical-single-t1保留同PID/同3e0ebb扩展继续跑；不修改其冻结oracle或监测器。源码身份门槛使v1在当前组完成后不再启动cached组，之后的prelaunch source失败属于预期修订。v2入口run_observation_admission_p2_v2.py与oracle v2使用隔离9bb2fa扩展；先等旧parent和child全退出，不重复/并发运行轨迹，再按p2-v2-preregister.json校验。先读/Users/liyang/Developer/star-lab-runs/e8-p2-v2-20261007/p2-progress.json及旧runs/p2-progress.json/当前组progress/monitor；若v2仍waiting，实际进度看旧canonical-single-t1。

内存只遥测，无自动暂停/kill/超时。P2 targeted仍pending，不进入P3/默认，不关闭GAP或改容量/Frontier。

进度：`P0 █ | P1修订 █ | P2普通完整轨迹 ▓ | v2矩阵 等待 | targeted ░ | P3 ░`。

## E8 P1已归档、P2串行校验（2026-10-07）

P1 source `6ec8e05d68c82d2731a382e00411bd58f2ed6f56`、88项契约通过，代表段完整响应/消费命令/最终状态一致；独立旧扩展短宿主轨迹全节点核验通过。小屏幕计时仅筛选，不作正式提速；ordinary与旧扩展单次未配对差异已保留。P2恢复先读 `/Users/liyang/Developer/star-lab-runs/e8-p2-20261007/p2-progress.json`、当前组 `.progress.json` 和 `.monitor.json`。只串行校验，不启动P3；不得重复启动活进程。

压力仅监测，不自动暂停/终止/超时；所有尝试保留，不重跑择优。P2轨迹全通过后仍须完成targeted错误/故障/VLM检查，不能把轨迹矩阵通过称全部P2完成。

进度：`P0 █ | P1 █ | P2轨迹 ▓ | P2 targeted ░ | P3 ░ | 默认 ░`。既有GAP、容量、Frontier及5000Agents暂缓保持。

# Rust 并行工作：新 Session 交接入口

## E8 P0 完成、P1 下一步（2026-10-07，最新）

1943 条测量观测约 57% 有合法连续段；全 17382 项操作重放一致。先进入 owned cache/no_reuse 契约原型；不开默认。证据：`experiments/2026-10-rust-observation-admission/results/p0-complete.json`。用户新授权覆盖旧压力暂停：今后只监测，不自动暂停/kill/超时，正式计时有效性仍单列。

进度：`P0 █████ | P1 ▰▱▱▱▱ | P2/P3/P4 ▱`；原49删除、冻结树、历史标签和 GAP/容量/Frontier不变。

## E8 P0 执行入口（2026-10-07，最新）

用户已授权开始执行 E8。P0 探针契约通过，5000/1000 短诊断下一步；产品仍固定 5b9658b。证据入口：`experiments/2026-10-rust-observation-admission/results/p0-preregister.json`；持久目录 `/Users/liyang/Developer/star-lab-runs/e8-p0-20261007`。

进度：`P0 ▰▰▱▱▱ | P1/P2/P3/P4 ▱`。已有 GAP 不关闭，E7 不采用，不 push/merge。

## E8 已接纳观测只读段算法方案（2026-10-07，当前下一项）

E7 P3已归档4370070，empty_territory不采用。按整体评估第三项推进请求接入，算法方案records/rust-observation-admission-plan.md与身份/阶段台账已完成；本次仅方案，没有实施、测试或后台进程启动。

选择逐请求执行/返回＋owner-scoped owned ObservationBatch缓存：保留原时钟、预算检查、权限、计数、JSON直传/client decode/消费与回调顺序；已接纳连续query段最少2、最多4，不等待未来、不按阵营重排、不跨动作/step/VLM/未知回调/owner yield复用。private token绑定实例/epoch/owner/generation，所有非段native入口先失效；自定义action kind不是query回到原路径。single/segment_no_reuse/segment_encoded分开调度机制与缓存收益；首版不减少FFI次数、不改观测算法，不把execute_actions_json的整组解码/延后计数当单条host等价。

先P0真实合法段/成本诊断，再小型no_reuse/encoded契约和无诊断收益筛选；通过才做完整正确性与native1三轮正式收益，之后单列native4和条件窗口。当前Rust Lab/post-action/native-wire仅支持single，需要研究适配；真实网络G009仍OPEN，不能称生产已接通。研究开关默认关闭、5000/1000目标、既有GAP/容量/Frontier保持，5000Agents暂缓。产品仍5b9658b、原49删除/冻结目录/历史标签保持，不push/merge。

进度：`源码/边界 █ | 算法方案 █ | P0 ░ | P1 ░ | P2 ░ | P3 ░ | 窗口/默认 ░`。恢复先读方案及records/rust-observation-admission-status.json；以下E7段落为已完成的前一项与历史证据。

## E7 P3 完成、独立复核与决策（2026-10-07，当前）

原24次全部执行结束（14:59:44 Asia/Shanghai），23次正式有效、1次压力暂停无效；全部raw/四侧9880样本及工作量、40994请求、流/最终指纹、ZIP内外SHA与冻结身份核验通过，23次原统计门槛独立复算一致。候选empty_territory的D+Q均值变化-1.668%～+0.614%，全部有效运行均未达到5%改善门槛。四个ordinary主分层三轮均未通过；typed三个完整分层未通过，typed/native1/static只有两轮有效、inconclusive。7个已评估未通过、1个证据不足，不采用，不自动补跑，不进入单实例确认/Cocoa窗口/默认接入。

当前证据E7 results/p3-complete.json、p3-integrity-review.json、p3-decision-summary.json、p3-valid-round-metrics.csv；原第11次完整raw无效保留且从收益分析排除，历史p3-interruption不是活跃失败。两个监督器/测试均已退出，e7-p2已PAUSED。源码仍5b9658b、原49删除/冻结目录/标签保留，产品GAP暂缓，既有GAP/容量/Frontier不改，5000Agents继续暂缓、不push/merge。P2完整4/4只说明正确性，P3没有稳定净收益；结果只覆盖本候选与固定dummy重放，不扩展为所有显示方案无价值或一般无泄漏证明。

进度：`P2 █ 4/4 | P3执行 ██████████ 24/24 | 正式有效 23/24 | 独立核验/归档 █ | 采用 0/8 | 确认/窗口/默认 未启动`。

### 以下为历史记录；后续恢复请以上述当前结论及决策级汇总为入口

## E7 P3阶段收尾（2026-10-07）

P3 original 24 jobs executed; resource-invalid strata remain inconclusive；完整计时通过资源有效性核验的组数23/24。原始样本、慢尾、失败尝试全部保留；门槛和分析见E7 results/p3-complete.json。P2完整正确性4/4保持，不启用默认、不进入单实例确认或窗口，不改容量/Frontier或关闭既有GAP。
进度：`P2 █ | P3 23/24 | 单实例确认/窗口/默认接入 ░`。

## E7 P3阶段收尾（2026-10-07）

P3 stopped or timing invalid; no automatic retry；完整计时通过资源有效性核验的组数10/24。原始样本、慢尾、失败尝试全部保留；门槛和分析见E7 results/p3-interruption-20261007.json。P2完整正确性4/4保持，不启用默认、不进入单实例确认或窗口，不改容量/Frontier或关闭既有GAP。
进度：`P2 █ | P3 10/24 | 单实例确认/窗口/默认接入 ░`。

## E7 P3资源干扰后继续剩余组（2026-10-07，最新）

用户看到当前仍有5GB物理空闲/约1.2GB交换，明确要求继续跑。这授权覆盖“当前受干扰完成后停止后续矩阵”规则，不改变计时有效性/收益门槛。当前前10组完整资源有效，原第11组reuse_typed/native1/static/r2在6000tick因warning保留同PID暂停约255.86秒后已恢复；不中断它，不抹掉干扰记录。
新增continuation-only入口tools/rust_migration/continue_display_preparation_p3.py，等待原parent8072及当前子进程完成、原收尾退出后，验证复用前11次完整尝试，继续原第12–24组（13组）。不并发、不重跑任何已启动组、不更改冻结原工具、driver/analyzer/产品。预注册修订及控制内外SHA见E7 results/p3-continuation-20261007.json；状态优先读持久runs/p3-continuation-progress.json、p3-continuation-analysis.json、p3-continuation-completed-evidence.json，原p3-progress.json保留历史停止。
后续压力仍只暂停不退出，normal一分钟恢复；每次完整raw归档。发生资源干扰的尝试保留并从正式收益排除，然后继续未启动组；真实正确性/child失败仍停止。正式分析只调用显式资源有效名单，禁止原glob分析器误纳第11组。该分层若缺三轮有效数据，报告inconclusive、不采用，不自动补跑或择优。原24次全部执行后分别报告executed/valid/invalid，不能把执行完成当正式24组全有效。
仅P3，单实例确认/窗口/默认接入仍不自动启动；P2完整4/4、既有GAP/容量/Frontier、5000Agents暂缓边界保持，不改产品GAP或push/merge。
第11组已经完整结束，driver正确性/stream/final通过但计时资源无效；原监督器已退出，接续parent24970已核验前11次，准备从第12组reuse_typed/native4/static/r2继续。历史停止已独立归档p3-first-resource-interruption-20261007.json，跟进保持ACTIVE并优先接续状态。
进度：`P3原任务执行 11/24 | 正式有效 10 ████░░░░░░ | 资源无效保留 1 | 剩余13组接续 ▒ | 确认/窗口/默认接入 ░`。

## E7 P3正式收益矩阵接续（2026-10-07，最新）

用户授权开启P3。P2四组完整结果/raw/身份已再次核验，不重跑。固定源码5b9658b、原性能driver/analyzer/native扩展/依赖不改；新增P3-only监督器tools/rust_migration/run_display_preparation_p3.py，持久目录/Users/liyang/Developer/star-lab-runs/e7-p3-20261007/runs。原24组矩阵（三轮×static/exercise×baseline/reuse_typed×native1/4）逐组串行，每组四个持续实例、完整9880tick、逐tick ABBA/BAAB；全部预热和慢尾保留。
正式计时关闭完整权威/像素哈希、细诊断及vmmap，保留原dummy2480×1239/1.5ms overscan wall预算和同侧GC策略。收益门槛仍是每轮render D+Q均值≥5%、chain/total均值正改善、100tick/10000bootstrap/seed42的95%下界>0及各自P99不回退；ordinary为主结论，typed独立交互，不跨层归因。
沿用用户不自动退出授权：压力仅暂停现场，6GiB仅监测参考，normal一分钟恢复。计时正式有效必须整次压力样本全部normal且无暂停/监测事件；发生干扰仍保留完整raw，该次不能用于收益，结束当前运行后停止剩余矩阵，不自动重跑或筛慢样本。只在无干扰的完整结果上复算；新的方法控制覆盖24组/三轮及无效资源事件和5%门槛，不计为速度结论。
预注册与冻结工具/控制内外SHA见E7 results/p3-preregister-20261007.json。各组完整后自动归档，全部24组后收尾结果到p3-complete.json；异常到p3-interruption-20261007.json。仅本轮P3，不自动启动单实例确认/窗口/默认接入，不关闭既有GAP或更新容量/Frontier，不改产品GAP或push/merge，5000Agents暂缓。
第一组p3-baseline-t1-static-r1已实际启动，parent PID8072/test PID8136，caffeinate -i -w8072防止空闲休眠，结束随父任务释放；临时跟进已恢复为E7 P3完成跟进。
进度：`P2 ██████████ 4/4 | P3预注册/控制 █ | P3完整计时 0/24 ▒░░░░░░░░░ | 确认/窗口/默认接入 ░`。

## E7 P2独立复核完成（2026-10-07，最新）

P2四组完整正确性全部通过并归档；自动收尾于06:46:36（Asia/Shanghai）结束。每组40994请求/9880tick，完整权威/展示投影/绘制命令/像素各19760次及冷World99次，流、最终权威和所有raw/四组ZIP内外SHA与持久目录逐字节复核通过。见E7 results/p2-complete.json、p2-integrity-review.json。
最后一组完整校验耗时14515.76秒（约4小时2分钟）；峰值RSS1855635456 bytes（约1.73GiB），采样footprint1610612736 bytes（1.50GiB）。压力采样均normal，实际暂停0秒；不把合成暂停控制当成本次真实暂停证据。第四组仅暂停监测、6GiB参考值非强制预算，前三组2500/2500/5120MiB原守护分别保留。结论是规范轨迹正确性通过，不是性能收益、统一资源预算或一般无泄漏证明。
测试/收尾均已退出；e7-p2已PAUSED。Lab README/manifest/analysis/decision/handoff/status/GAP阶段更新，历史失败attempt状态保持并链接后续完成结果。产品HEAD5b9658b/扩展/probe/锁文件与冻结工具核验，原49删除及两个冻结树保留；不改产品GAP、不关闭既有GAP、不更新容量/Frontier、不push/merge。
进度：`P2完整正确性 4/4 ██████████ | 独立证据校验/归档 █ | P3性能/窗口/默认接入 ░`。后续进入P3性能测量；本次仅完成P2，未启动P3、未启用默认，5000Agents继续暂缓。

## E7 P2完整通过（恢复运行，2026-10-07）

四组完整40994请求/9880tick校验全部通过：ordinary native1/static、ordinary native4/exercise、reuse_typed native1/exercise与native4/static。每组完整权威、展示/事件、绘制命令、像素、查询顺序及最终权威指纹通过，原始样本/指纹和内存守护全部保留。结论只覆盖P2正确性；第四组仅监测与保留现场，不代表强制资源上限验收；不代表性能收益、容量提升或一般无泄漏证明。
证据入口E7 results/p2-complete.json。已完成组的完整证据复用，缺失组新完整运行；历史不完整资源中断继续保留，未计作通过。测量源码5b9658b、原probe/扩展保持；前三组保留旧守护，第四组用户授权压力仅暂停、无自动终止；各组限额依次为2500/2500/5120/6144MiB（第四组仅监测参考值，不是强制上限），不能据此宣称统一内存预算验收。
进度：`P2完整正确性 4/4 █ | 证据与校验 █ | P3/窗口/默认接入 ░`。未启动P3、未启用默认路径、未push/merge；既有GAP、容量和Frontier保持。

## E7 P2第四组仅暂停监督器（2026-10-07，最新）

用户明确授权继续最后一组且不设置自动退出。本轮只重新执行reuse_typed/native4/static；前三组40994请求/9880tick及完整raw/守护再次核验复用。旧8500进程已退出，无法恢复，历史尝试全部保留。
新入口tools/rust_migration/resume_final_display_p2_pause.py，目录/Users/liyang/Developer/star-lab-runs/e7-p2-20261007-pause-only/runs；工具与控制已冻结，见E7 results/p2-pause-only-resume.json。warning连续两次或critical/未知信号只暂停同一进程组，normal连续60秒恢复；6144MiB仅监测参考值，不作为终止条件。监测查询失败保留进程暂停重试；监督器外部中断也保留暂停子进程，不自动杀死。没有自动运行超时或重复重启。暂停不会释放已有内存，退出/重启后仍无持久检查点。
合成控制通过同PID暂停/恢复、进度恰好一次、critical不退出及超出参考预算仍完成；首次过短合成子进程控制未观察到第二个warning样本，其完整raw保留。控制不计作P2通过。专用finalize_display_correctness_pause.py保持全部正确性与raw阈值，并显式区分前三组强制守护和第四组仅暂停监测，不宣称统一预算验收。
当前P2仍3/4，最后一组已启动（parent PID65461/test PID65533），e7-p2跟进ACTIVE；只完成P2，不进入P3、不启用默认。产品HEAD5b9658b、probe/native、历史guard与冻结runner保持；Lab阶段GAP更新，既有GAP/容量/Frontier不改，5000Agents暂缓、不push/merge。
进度：`P2完整通过 3/4 ███████░░░ | 无自动退出控制/归档 █ | 第四组运行 ▒ | P2最终归档 ░ | P3/窗口/默认接入 ░`。

## E7 P2压力策略与保留现场控制（2026-10-07，最新）

用户要求解释warning并不要从头运行。macOS压力由可用内存、交换速率、wired和文件缓存等综合反映，warning不是OOM；内核公开说明也将其定义为开始出现压力。旧guard的“连续两次warning终止”是Lab主动采用的保守策略。此次运行停止未触达6GiB限额；旧日志未保存当时完整vm_stat或交换速率，不能确定具体系统触发原因，也不能用现在的3GiB空闲/1.4GiB交换反推停止时状态。
第四组旧进程已经SIGINT退出并关闭native世界/显示实例，probe只在完整结束时写校验raw；8500tick仅进度日志，不是可恢复检查点。本轮未启动完整轨迹、不重跑前三组。P2仍3/4，e7-p2保持PAUSED。
新增独立guard_display_preparation_resumable.py：两次warning暂停同一进程组，normal持续60秒后原PID恢复，critical/未知信号或6GiB预算仍终止。暂停事件原子落盘，记录最后日志进度及vm_stat/swap/query快照。暂停保留内存，不释放世界；不支持退出/重启后恢复，仅限正确性运行，不用于性能计时。旧guard、冻结runner、probe和产品HEAD5b9658b未改，新guard尚未接入P2 runner。
独立合成控制验证同PID恢复、暂停期间进度不变、40条进度恰好一次、暂停中critical清理、预算/未知信号终止及默认60秒策略。控制源码与完整raw已归档并核验ZIP内外SHA；它不计作E7正确性通过。见E7 results/p2-pause-guard-control.json。复现：python3 tools/rust_migration/test_resumable_display_guard.py --output <不存在的新目录>。
进度：`P2完整通过 3/4 ███████░░░ | 活进程暂停控制 █ | 旧8500现场恢复不可用 × | 新完整重放未启动 ░ | P3/窗口/默认接入 ░`。Lab阶段GAP更新，产品GAP暂缓；既有GAP不关闭、容量/Frontier不更新、5000Agents继续暂缓、不push/merge。

## E7 P2第四组6GiB重试中断（2026-10-07，最新）

P2完整通过仍3/4；三组完整40994请求/9880tick和全部raw、权威/展示/命令/像素及对应2500/2500/5120MiB守护再次核验。第四组重试于01:46:47（Asia/Shanghai）运行12749.64秒后，被12742.667/12747.683秒连续两个system warning样本停止（SIGINT，child_exit=-2），最后正式进度8500/9880tick。当前测试和收尾均已退出。
本轮峰值RSS1693810688 bytes（约1.58GiB），采样footprint1503238553 bytes（约1.40GiB），没有达到6144MiB限额。退出Chrome后本次运行更久，但没有控制证据把差异归因于Chrome；5→6GiB进程预算并未改变独立warning停止条件。日志未报告状态/命令/像素不一致，KeyboardInterrupt不是AssertionError，中断不算通过，不证明实际内存耗尽或产品泄漏。
证据E7 results/p2-fourth-retry-interruption.json；守护、完整父/子日志、状态和启动身份已归档并验证内外SHA，原源码/probe/native/guard及本次冻结执行工具未修改。e7-p2已PAUSED，不反复自动重启。下一步应核查内核压力信号与活动监视器的口径以及guard warning策略有效性，再考虑新的第四组单独重放；不能继续只加进程预算并原样重试。
进度：`P2完整通过 3/4 ███████░░░ | 第四组8500后中断归档 █ | P2最终完成 ░ | P3/窗口/默认接入 ░`。产品HEAD5b9658b、既有GAP/容量/Frontier、5000Agents暂缓保持，不进入P3、不启用默认、不push/merge。

## E7 P2仅第四组恢复，6GiB预算（2026-10-06，最新）

用户退出Chrome并授权重启、进一步增加单进程预算。预检内核压力normal，查询可回收余量72%；实时swap查询仍有既有交换占用，因此不记录“交换为零”结论。前三组完整证据及全部raw已验证复用，不重跑；本次只执行reuse_typed/native4/static，进程限额6144MiB（6GiB）。系统warning/critical策略、原guard代码、probe、产品HEAD5b9658b/native扩展不变。
专用入口tools/rust_migration/resume_final_display_p2.py；目录/Users/liyang/Developer/star-lab-runs/e7-p2-20261006-fourth-retry/runs。预注册E7 results/p2-fourth-retry.json，冻结工具display-preparation-p2-fourth-retry-tools.zip。已验证三组原始证据、第四组单独派发及预算传递的控制；不把mock方法控制视为正确性通过。完成后finalize_display_correctness.py显式核验各组2500/2500/5120/6144MiB，不冒充统一资源预算或性能结果。
历史第四组中断3500里程碑和全部失败证据保留；新完整重放从头开始，成功才计入4/4。若再资源/校验失败，保留并停止，不自动反复重启。自动收尾只到P2，不启动P3或普通默认，不push/merge；既有GAP、容量/Frontier和5000Agents暂缓边界不变。
进度：`P2完整通过 3/4 ███████░░░ | 第四组专用恢复/预算核验 █ | 第四组重放 ▒ | P2最终归档 ░ | P3/窗口/默认接入 ░`。

## E7 P2第四组系统压力中断（2026-10-06，最新）

完整通过保持3/4；三组完整40994请求/9880tick及权威/展示/命令/像素/raw SHA再次核验。第四组reuse_typed/native4/static于20:32（Asia/Shanghai）运行4940.27秒后，由4932.417/4937.432秒两次system warning样本停止（SIGINT，child_exit=-2），最后正式进度3500tick；之后frames3600仅为render debug，不能据此补计完整tick。
峰值RSS1706868736 bytes（约1.59GiB）、采样footprint1288490188 bytes（约1.20GiB），均低于本轮5120MiB；停止原因仍是独立系统压力策略。堆栈在显示后权威JSON导出比较，错误为KeyboardInterrupt而不是AssertionError，日志未报告等价失败；中断不能计作通过，也不能据此证明内存耗尽或缓存泄漏。
证据E7 results/p2-fourth-interruption.json；守护、完整子/父日志、执行状态与启动身份已归档并核验内外SHA。当前测试/收尾均已退出，e7-p2已PAUSED，不自动反复重启、不修改冻结工具或进一步放宽守护。下一步保留三组成功，仅在明确新的运行条件或系统压力策略后受控重跑第四组；不能用现有恢复工具原样重复第三组。
进度：`P2完整通过 3/4 ███████░░░ | 第四组中断归档 █ | P2最终完成 ░ | P3/窗口/默认接入 ░`。产品HEAD5b9658b及probe/native/guard保持、既有GAP不关闭、容量/Frontier不更新、不push/merge。

## E7 P2第三组完整通过，第四组运行（2026-10-06，最新）

reuse_typed/native1/exercise已完整通过40994请求/9880tick：完整权威19760、展示投影19760、命令19760、像素19760及完整冷World99检查。流与最终权威指纹、全部raw SHA、固定源码/probe/扩展/输入身份与前两组一致；5120MiB守护passed，系统压力采样均normal。原始样本、权威/像素指纹、guard与日志已归档，内外SHA核验。证据E7 results/p2-typed-t1-exercise-completed.json。
第四组reuse_typed/native4/static已由原父任务自动启动，初次核对到500/9880tick；继续等待，不重复启动、不修改冻结执行工具。完整通过现在3/4，尚未完成P2，不代表性能收益或一般无泄漏结论；预算前两组2500MiB、本组5120MiB分别记录。
进度：`P2完整通过 3/4 ███████░░░ | 第三组证据/校验 █ | 第四组 ▒ | P2最终归档 ░ | P3/窗口/默认接入 ░`。产品HEAD5b9658b、49删除、冻结目录与GAP/容量/Frontier保持，不进入P3、不启用默认、不push/merge。

## E7 P2提高单进程预算并恢复（2026-10-06，最新）

用户重启并授权再次运行、显著放宽2500MiB单进程限额。预检内核压力normal；查询可回收余量78%。剩余两组串行采用5120MiB（5GiB），系统warning/critical保护保持；原probe、产品源码5b9658b和native扩展未改。提高进程限额不解决此前warning触发，若再触发仍停止并保留证据，不自动循环重启。
前两组完整证据与全部raw已核验复用，不重复运行；历史49删除及两个冻结工作树保持。新持久目录/Users/liyang/Developer/star-lab-runs/e7-p2-20261006/runs，输入及继承证据仍引用Oct5持久目录。预注册E7 results/p2-budget-resume.json，冻结工具display-preparation-p2-budget-tools.zip；原守护代码只通过既有--limit-mib参数改变预算，包装与收尾接口新增显式预算/日期，核验错误预算和中断不会算通过。
完成后需四组完整40994请求/9880tick、全部权威/展示/事件/命令/像素检查与SHA；报告明确前两组2500MiB、后两组5120MiB，不冒充统一内存预算、一般无泄漏或性能收益结论。自动收尾只完成P2；不启动P3、默认路径、不push/merge，容量/Frontier和既有GAP不变。
进度：`P2完整通过 2/4 ▓ | 提高预算/身份核验 █ | 剩余两组恢复 ▒ | P2收尾 ░ | P3/窗口/默认接入 ░`。

## E7 P2重启尝试再次资源中断（2026-10-05，最新）

完整通过仍为2/4，本轮重新核验前两组完整40994请求/9880tick及全部raw SHA、权威/展示/命令/像素检查与守护。重启后的第三组reuse_typed/native1/exercise在运行180.95秒后，被175.160/180.166秒连续两个system warning样本停止（SIGINT，child_exit=-2）；第四组未启动，无运行中的测试或收尾进程。没有tick里程碑输出，不能推算已完成tick数；日志未报告等价错误，中断也不能计作通过。
测试进程峰值RSS为1371127808 bytes（约1307.6MiB），最新采样footprint为1001494937 bytes（约955.1MiB），均未达到2500MiB限额。实际触发的是系统整体压力；中断堆栈位于完整权威JSON导出，不证明该位置是根因，也不证明E7缓存泄漏或Chrome是原因。
证据：[E7本轮中断](../experiments/2026-10-rust-display-preparation/results/p2-reboot-interruption.json)，原日志、守护、父进程状态、输入恢复身份全部归档并核验内外SHA256。e7-p2已PAUSED，不反复自动重启、不放宽守护。下一步先审查持续系统压力与正确性harness资源成本，再决定新的受控恢复；本轮未修改测量源码/probe/守护。
进度：`P2完整通过 2/4 ▓ | 本次中断归档 █ | 剩余两组受资源阻碍 ▒ | P3/窗口/默认接入 ░`。产品HEAD固定5b9658b，既有GAP不关闭、容量/Frontier不更新、不push/merge。

## E7 P2重启恢复（2026-10-05，最新）

用户已重启机器并授权全力完成P2。系统压力normal、可回收余量60%，固定源码5b9658b及native扩展/原probe保持。原临时目录已被重启清除；从R4e canonical归档恢复输入，从E7 canonical ZIP恢复两组完整结果，内外SHA均验证。历史49删除、冻结工作树保持。
本轮持久目录/Users/liyang/Developer/star-lab-runs/e7-p2-20261005，inputs、inherited与runs分开。入口tools/rust_migration/run_remaining_display_p2.py，串行只重跑剩余两组并保留原2.5GiB/system pressure守护；全部通过后调用finalize_display_correctness.py自动核验/归档/更新Lab阶段记录。
恢复记录E7 results/p2-reboot-resume.json。实时状态runs/resume-progress.json，收尾状态runs/p2-finalization.json。自动跟进e7-p2需恢复并使用新持久路径；未变化保持安静，失败需处理或四组全部完成时报告、停用，不自动反复重启。
进度：`输入/完成证据恢复 █ | P2完整通过 2/4 ▓ | 剩余两组 ▒ | P2最终归档 ░ | P3/默认接入 ░`。不启动P3，不修改产品源码，不push/merge，不更新容量或Frontier、关闭既有GAP。

## E7 P2最新核对：未完成，重复资源中断

完整通过仍为2/4。第三组reuse_typed/native1/exercise的恢复尝试在最后记录3500tick后，被两次system warning压力样本停止（SIGINT，非已报告的等价错误）；第四组未启动，当前无测试进程。最新证据E7 results/p2-recovery-interruption.json。当前压力normal只证明检查时状态，不能外推整组数小时安全。
临时automation e7-p2已PAUSED，按既定规则不反复自动重启或放宽保护。下一步先解决持续运行的资源条件或审查正确性harness资源成本，保留两组完整结果与两次不完整尝试，再重跑剩余两组；不进入P3或默认接入。
进度：`P2完整通过 2/4 ▓ | 剩余两组受资源阻碍 ▒ | P3/窗口/默认接入 ░`。既有GAP不关闭，容量/Frontier不更新，产品测量HEAD5b9658b不变。

## E7 P2资源中断与剩余恢复（最新）

第三组reuse_typed/native1/exercise在最后记录8500tick后被系统warning压力保护停止，不能计作通过；并非已检测到等价错误。完整事件归档E7 results/p2-warning-interruption.json。两组完整通过仍有效，旧P3/确认/窗口监督器均已随上游停止。
新恢复入口E7 results/p2-recovery.json及tools/rust_migration/resume_remaining_display_correctness.py，输出/private/tmp/star-e7-20261004-p2-recovery。复用两组经哈希验证的完成结果，只重跑剩余两组；压力normal连续一分钟才开始，原probe源码和2.5GiB守护不变。失败仍停止，保留全部尝试；本恢复工具只完成P2。
压力已恢复normal，第三组正在从头重放。临时线程跟进automation e7-p2每小时检查同一个任务，不重复启动；第三组完成时归档，四组完成时核验/归档/报告并停用。资源或校验失败需处理时报告并停用，不自动反复重启。
进度：`P2完整通过 2/4 ▓ | normal恢复 █ | 剩余完整校验 ▒ | P3/窗口 ░`。默认接入尚未获门槛通过，产品HEAD5b9658b固定，既有GAP/容量/Frontier边界保持。

## E7继续与条件默认接入授权（2026-10-04）

native1/static与native4/exercise两组完整40994请求/9880tick正确性通过，结果归档E7 results/p2-t1-static-completed.json及p2-t4-exercise-completed.json。其余两组仍顺序执行，之后24组性能对照及有条件的8次单实例确认。continue_display_preparation_live.py等待确认通过后串行六次Cocoa窗口（AB/BA/AB；30+300秒），无诊断，保留全部失败和慢尾；live-progress.json为下一阶段入口。
用户最新授权收益验证通过后默认接入，替代此前“本轮仅保留研究开关”的限制；测量期间旧默认保持，先满足完整P2/P3/确认/六窗口门槛，默认native1也必须获稳定正收益，再验证默认接入并归档。默认接入补丁及独立dispatch合同见E7 results/default-patch-preparation.json：只准备、未应用，完整回归和默认路径验证留待收益门槛通过后。授权详见E7 results/default-adoption-authorization.json，不包含push/merge或容量/Frontier更新。
进度：`P0 █ | P1 █ | P2 2/4 ▓ | P3 ░ | 确认 ░ | 窗口 ░ | 条件默认接入 ░`。

## E7恢复执行（2026-10-04）

用户已清理系统内存并明确授权继续，归因于Chrome/编辑器占用；历史事件保留，不据此断言产品存在或不存在泄漏。系统压力正常、可回收余量72%。带完整权威导出的100tick冒烟通过，footprint约0.75–0.78GB，压力始终normal。
活动执行源码5b9658bc668b7d13f801351162f255f30622b32a（相对原型6730832仅GAP文档差异）。四组完整正确性在/private/tmp/star-e7-20261004顺序从头重放，每组由独立2.5GiB RSS/footprint及系统压力保护；之后24组无细探针性能对照顺序执行，性能阶段不用vmmap。
恢复预注册与完整工具快照见E7 results/preregister-resume.json及artifacts/display-preparation-resume-tools.zip。恢复工具tools/rust_migration/resume_display_preparation.py；实时进度resume-progress.json、各组guard.json/supervisor.log。失败立即停止，保留全部记录；通过P3后仍需条件单实例/窗口决策，尚无正式收益结论。普通路径和研究默认关闭、所有GAP/容量/Frontier边界保持。
进度：`P0 █ | 原型/小型契约 █ | 恢复冒烟 █ | 全轨迹 ▒ | 正式收益 ░ | 条件窗口/最终归档 ░`。

## E7：内存不足事件，重型校验与自动性能任务已停止

2026-10-02 14:49用户报告macOS应用内存不足，ChatGPT/Codex组约8GB；四个完整权威校验进程并发、GC延迟。全部测试进程与等待性能矩阵已停止，没有完整正确性或正式收益通过结论。
事件证据见[E7内存事件](../experiments/2026-10-rust-display-preparation/results/memory-exhaustion-incident.json)。停止前swap已用约10GB；停止后空闲内存约49MB→3GB。不能由RSS或此截图直接证明优化缓存泄漏，也不能用1200小型坐标缓存循环代表完整链路内存安全。
下一步先串行、限额、带进程footprint/压缩/交换与GC保留诊断，隔离baseline/candidate、完整导出及测试实例数量；在原因与安全边界确认前不重启全轨迹或性能矩阵。自动性能入口已有事件阻断。
原型源码6730832、GAP文档节点5d31d35；原型默认关闭，2389回归及补充边界对照仅证明各自范围。四个未完成全轨迹运行均不可用作完整验收。
进度：`归因 █ | 原型 █ | 小型契约 █ | 完整正确性/内存失败 ▒ | 收益 ░ | 窗口 ░`。
原49删除、冻结目录、既有GAP、5000Agents暂缓、容量/Frontier/no push/merge约束保持。

## E6 展示数据与 ECS 缓存研究完成（2026-10-02）

验证节点 `068c1ecd17988ac6d884984e904aea924968e0ae` / `rust-parallel-e6-presentation-cache-2026-10-02`；测量0a297a8，执行代码相同，native扩展838c693保持。
2385回归、native1/4完整40994请求/9880tick的响应、权威、展示、查询和像素契约通过。
reuse_typed六轮apply改善44.26–45.62%、完整链14.66–15.53%、总工作10.78–11.61%，
均值/P99/区间门槛通过；native4单实例确认通过。reuse_constructed apply慢2.11–2.71%，不选择。
候选三轮窗口guards通过，但baseline第二轮帧/队列超限，六次整体window gate未全通过。
研究默认关闭，不声称容量或Frontier提升，既有GAP不关闭，5000Agents暂缓。

先读[E6 README](../experiments/2026-10-rust-presentation-cache/README.md)、
[成本/完整结果](../experiments/2026-10-rust-presentation-cache/analysis.md)、
[决策](../experiments/2026-10-rust-presentation-cache/decision.md)。原始样本/失败控制、完整重生成delta、
wheel、source bundle和校验链均保留。像素契约固定游戏墙钟及地形构建条目配额；
正式性能/实时窗口仍采用原时间预算，产品未因此修改。
下一项：显示链路准备成本，先拆真实窗口约3.184ms未归因update和3.349ms RMS分项，并追踪baseline尾延迟。
进度：`归因 █ | 契约/实现 █ | 等价 █ | 三轮收益/确认 █ | 窗口结论 █ | 证据/恢复 █`。
原49删除/冻结目录/E2–E5标签保留，不push/merge。

## 整体性能评估完成：建议优先展示与观测（2026-10-02，未实施）

进度：`运行链路 █ | canonical复算 █ | 源码/已有机制 █ | 投入排序 █ | 恢复/边界 █`。
先读[整体评估与候选排序](rust-performance-optimization-assessment.md)、[精确结果/校验](rust-performance-optimization-assessment.json)，再按其引用下钻E2/R4e/E3/E5。此处是新的投入建议，E5的执行/验收结论仍保留；没有启动优化实施或重新测量当前binary live。

审查源码3b167b1；最新完整窗口仍为E2 native4/source2bc57d5三轮，平均world step0.260–0.264ms（约整帧1.25%）、显示Systems8.491–8.748ms、展示应用2.693–2.748ms。约5.114–5.164ms update尚未分项，不归因为render/GC。不同分母、P99和跨输入结果不可相加或当因果收益。

建议首项：展示路径细分归因＋Python消费已有组件字段更新，减少deepcopy/组件重建/缓存失效；随后接已有合法read-batch。纯ENV优先观测公共工作、Statistics历史结构、Vision集合/Fog提交表示。已有裁剪/批量blit/缓存/typed编码/JSON直传/E2并行应继承；不重做whole-World快照进程池。Statistics kernel∥Movement的2/4诊断零开销上限约5%，不是净收益。

[复算工具](../tools/rust_migration/assess_optimization_priorities.py)校验E2/E3 canonical整体及6个所用member、14个源码SHA，结果可字节复算。此阶段是规划记录，无新加速比/live/容量/Frontier、生产执行变更或GAP关闭。默认1/API18/schema5、规则/观测/动作/确定性/Python生态、原49删除/冻结目录/历史标签保留，5000Agents暂缓，未push/merge。


## E5 研究完成：Movement∥Visuals真实重叠，默认不接入（2026-10-02）

进度：`依赖/窄接口 █ | 四模式/等价 █ | 主门槛/敏感性 █ | 条件停止/决策 █ | canonical归档/恢复 █`。
恢复先读[E5正式包](../experiments/2026-10-rust-movement-visuals-parallel/README.md)，再读analysis/decision/manifest、源码native-movement-visuals-parallel与GAP；E4/E3/E2/E1历史保留。

一worker计算owned Visuals、caller执行Movement，join后原序提交实体操作/状态；只读Position存在性与next-ID，不复制World，复用实例pool，区域最多两个执行参与者。四模式按次私有，新接口_movement_visuals_step_json；E4的Vision未实施模式仍明确拒绝。普通step/default1/API18/schema5/E2 Statistics128、观测/动作/RNG/规则和Python生态不变。

native2三轮mean改善0.593/0.688/−0.023%，native4 −0.747/−0.273/0.742%，各仅1/3轮通过完整mean/P99/CI95门槛。0/4/16六组单轮敏感性全部CI跨零。诊断3772候选tick的计时区间交叠下界均值16.917/15.769µs，支持机制但不是无诊断收益。保留私有原型、普通step不启用；4线程未过前置门槛，未进入单实例确认或live窗口，不新增容量/Frontier。5000Units/1000Agents目标保持，5000Agents暂缓，既有GAP OPEN/RISK不关闭。

测量94913a4f836a3c106e08a1334cb81971cfd728c3；validated 3b167b151c3bc32e1d54f6015d0f15d2c3dd6a74（仅补文档/测试，native代码相同）；annotated rust-parallel-e5-movement-visuals-2026-10-02；扩展838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544。source.bundle需要E4 72bf05a；新空repo由原main及E2→E3→E4→E5 bundle完整恢复已验证。

2345Python/6Rust/fmt/Clippy/release通过，含多段移动/GameOver后Vision、ID耗尽、effect/Capture/Statistics错误前缀、混合实体、reset/close/多实例和两侧fault join。27完整报告、90 world重放各40994request/9880tick/展示完整校验；13合同变体各13case/377step完整state/error/delta/reset字节一致，canonical载荷单存＋13别名。所有预热和慢尾保留。

raw SHA a3593da48438e7c96c9e9c003b8374d4d8b393d45a806d1a2582a2d12e3c4f07（15916081 bytes），compact SHA 2b53b12dadc326ef04a4e43cd115b1e7c71c9dab473f71efdf9ccae4fe3bef65（21057 bytes）。原始全部step/timing/wheel/准确工具版本/检验链保存；canonical analysis与诊断成本复算字节一致，E4/E3/R4e输入和wheel恢复只写新目录。原49删除、两冻结HEAD/扩展、E2/E3/E4标签均保留；活动工作树clean，未push/merge，迁移发布未完成。


## E4 System 之间并行研究完成：派发筛选负结果（2026-10-02）

进度：`边界/理想预算 █ | scoped负对照 █ | 完整ABBA █ | 等价/决策 █ | canonical归档/复算 █`。
先读[E4正式包](../experiments/2026-10-rust-between-system-parallel/README.md)、analysis/decision/manifest，再读E3/E2/E1历史。当前结论优先于旧下一步。

只完成私有baseline/empty_fork。当前同二进制相邻配对诊断8020/9880候选tick，2/4成本均值9.512/9.048µs，当前理想预算7.098/7.769µs；成本减预算95%区间[0.456,5.385]/[0.256,2.421]µs。含计时/bookkeeping和固定先后效应，按收益优先保守停止；不是无诊断严格负收益或所有System并行无价值的证明。无诊断三轮ABBA有矛盾结果，全部保存，没有实际Vision并行净收益。

split_serial/parallel未进入且明确拒绝，真实窗口未进入，普通step未接入。实例池最多一worker＋caller；默认1/E2 Statistics128门槛/API18/schema5/oracle及Python生态不变。目标5000Units/1000Agents，5000Agents暂缓。

测量 **dede5ca0ca3472abdb1d24589878e6a72d812f88**；validated **a7508bce4b900ccf8465e761291adb7e7e2ce98d**；最终文档 **72bf05a2f6ec6d1d15ffad7914226c0c3e16b9cf**（native代码相同）；annotated **rust-parallel-e4-dispatch-screen-2026-10-02**。扩展 **9c7eebe03257d1d6941e67b5e31a947e4c6cedf32db6979e624629fd5cf5dd91**。source.bundle需要E3 ad02b75。

28次完整run报告（24无诊断＋4诊断twins）全部录制响应/事件/最终hash核对，四组twins完整对象一致；7合同变体各36case/174step字节等于canonical；2330Python/5Rust/fmt/Clippy/release通过。raw **c15f4476ce9a7582fd0a33313cf5f8a21670c709d033f75746df2d1011131f4a**；脚本版本/全部tick/慢尾/wheel/日志/校验链保存，canonical复算、只读恢复、bundle验证通过。原49删除、两冻结HEAD/扩展保留；G001–G003历史、G008/G009 OPEN、R001/R002 RISK保留，无新确认玩法GAP、live容量/Frontier、push/merge或发布结论。



## E3 其他 System 内部候选研究完成（2026-10-01）

进度：`边界审计 █ | 分项归因 █ | 完整等价 █ | 条件排序 █ | canonical归档/复算 █`。
先读[E3正式报告](../experiments/2026-10-rust-internal-system-candidates/README.md)、analysis/decision/manifest与[生产成本/依赖表](/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main/docs/native-internal-system-candidates.md)，再读E2/E1/P0历史。此状态优先于下面旧“下一候选”。

活动工作树仍`/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main`、`codex/rust-ecs-parallel`。测量/validated **6d4018cc0c607a51a3783428867ba9259bb43f43**；最终文档 **ad02b75f2b83f97fe0bef4c1c9eee5742b1610fb**（执行代码/测试相同）；annotated **rust-parallel-e3-internal-attribution-2026-10-01**指测量节点。Release扩展SHA **e0f46cfbffd8542c08cd2b2e6b4a26c000da05ecb9bffd3466d77fa859a9834d**。仅增加按次私有归因，**没有启用其他System新并行**；E2 Statistics策略/128门槛、API18/schema5/oracle、默认1、Python接口生态不变。

当前规范轨迹Vision诊断均值约43µs，但几何仅0.553–0.599µs/tick，占1.27–1.37%，提交约27–28µs。Movement行处理乐观上界5.36–5.45µs/tick（含写入/计时），活动平均122.47/峰186。Visuals四阶段循环合计约8µs，上界不能跨栅栏合并；damage平均6.66/峰28行。Recovery平均2.81/峰24到期项，最大阶段是首次5007新ID审计，到期0；Capture无活动样本。

**当前目标没有足够证据启动另一项并行执行。**条件roadmap：先测Vision大批冷几何/合法更大视距，再测更多同时移动单位的Movement、Visuals大批同阶段更新。先串行拆分和分项成本，再决定scoped计算；保持LRU A→B→A、逐段空间写入、新箭同tick推进、ID/错误前缀/事件原序。不得复制世界或全部System入池。当前目标进一步优化可先研究Vision串行提交/表示；其收益仍待单独验证。

旧E2与新1/2/4共4轮每轮40994请求/9880tick/展示完全核对；4个36场景/174step契约输出字节相同；2315Python/4Rust/fmt/Clippy/release通过。原始包SHA **c3e347b145fcc5edfda304bb35030d3d3d9320861f116a5507d2b92cbd9b6abd**，全部逐tick/慢样本/wheel/日志保存；相同输入/合同引用R4e/E2 canonical。恢复bundle需要E2 0aa28ac2；复算只读canonical ZIP，索引/校验/完整argv见正式包。E2的原live容量仍指2bc57d5/23dc7e4，**E3没有新live/Frontier/加速比**。

无新确认玩法GAP；G001–G003历史、G008/G009 OPEN和R001/R002 RISK保留，5000Agents暂缓。原49删除、两冻结HEAD/扩展hash核验一致；未push/merge，发布未完成。


## E2 Statistics 内部并行研究完成（2026-10-01）

正式包：[E2报告](../experiments/2026-09-rust-statistics-compute/README.md)，含analysis/decision/manifest、完整raw、逐步samples、错误/reset契约、wheel及源码恢复bundle。
活动工作树 `/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main`，分支 `codex/rust-ecs-parallel`。
实测/策略 **2bc57d5f2241a578f61d71bb5774e7063a03ec25**；最终文档 **0aa28ac2ae0267048fcdb3998f9d76175ed4d699**（执行代码相同）；
annotated **rust-parallel-e2-statistics-2026-10-01**。正式扩展SHA **23dc7e4f5425e855a780a802d889f13bd28f300577688e66378ab574b7712d55**。
串行44c3696、实验调度7ab0ac1及独立旧P0 binary均保留。
进度：`串行拆分 █ | 分项归因 █ | scoped计算 █ | 全量等价 █ | 净收益/门槛 █ | 真实容量 █ | canonical归档/复算 █`。

仅当前Statistics批次的JSON记录构建在已有实例池内部并行，主线程原序提交；实际候选行至少128且显式native2/4才调度。小/尾批inline、默认1不变，没有between-System调度器。健康算术极小，trim/visibility/factions及写入保留串行。
旧/新8种契约完整输出字节相同（36场景/174step）；20次R4e40994请求/9880tick/展示的完整流/最终状态一致，含正式普通step1/2/4。2291Python/4Rust/fmt/Clippy/release通过，多实例/reset/close覆盖。
同binary同线程只改门槛的3组完整step对照：2线程均值减少4.18–16.76%，4线程7.58–10.36%，各组P99改善。合成1–32行并行负收益；64为测得mean-positive点，64行native4 P99反而更差，128保守操作门槛。此因果对照不是旧P0到全部新实现或整帧加速。

真实5000Units/1000Agents/native4三轮30预热＋300s Cocoa全部guard通过：帧P99 28.283/28.643/28.631ms，Hz29.997/29.993/30.000。
max帧91.923/102.449/32.239ms、worst5s P99 39.837/76.037/31.794ms原样保留，不保证每帧/短窗口。alive_min5000，peak movers180/173/173；不外推全5000移动、高密度、Hub/真实LLM或5000Agents。R4e native1验收及全部历史证据不覆盖。
canonical raw SHA **62c5e73a2356334fc0fa85e3b5f4054a46f5f759ad7cb6c9fcef41dcd7b190ba**；8个完全相同contract raw只存1成员+别名；analyzer由canonical包复算而非依赖ignored loose scratch。工具checkpoint **69969a1713bb83d7e18fd4b05137276bc412cb72**，各测量工具hash/旧变体commit及完整argv/env见manifest/results。

API18/schema5/oracle/Python生态边界不变。无新确认玩法GAP；G008/G009 OPEN、R001/R002 RISK、G001–3基线变化保留，5000Agents暂缓。原49项删除和两处冻结HEAD/扩展hash均核验保留。没有push/merge，迁移/发布未完成。
下一候选E3先归因Vision uncached几何与有序缓存/Fog提交；between-System Recovery/Lifecycle/Vision保留低优先级窄接口研究（现有理想重叠小于派发成本），不直接全System入池。先读本E2包/生产native-statistics-parallel/GAP，再读E1依赖与机制、P0归因和R4e历史容量。
此状态优先于下方历史E1/P0下一步。

## 独立Rust并行任务：E1 ECS方案探索完成（2026-09-30）

按用户最新指示，活动任务转向**System之间及System内部并行**，详见
[恢复入口](rust-ecs-parallel.md)及[E1正式方案/机制包](../experiments/2026-09-rust-ecs-parallel-design/README.md)。
工作树 `/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main`，分支
`codex/rust-ecs-parallel`，从R4e tag隔离；最新设计commit **be3867b3ad65749e0e34efd245359c4123189031**，
annotated **rust-parallel-e1-design-2026-09-30**。P0完整依赖表/成本/等价性保留。
进度：`恢复 █ | 归因 █ | ECS方案/机制 █ | 生产并行原型 ░ | 新容量 ░`。

拆窄访问后Recovery/Lifecycle/Vision是System间候选；P0理想零开销重叠节省mean3.883µs。
锁定Bevy0.19.1机制探针1/2/4验证窄组件重叠、冲突串行、100/5000活动子集；
已有池2/4验证5000有序结果，空dispatch median9.125/7.084µs。这些不是实际游戏并行/净收益。
**下一阶段E2：Statistics当前批次纯计算＋有序提交，先1线程拆分/分项归因，再决定2/4。**
P0跨请求批次候选暂缓、原证据不改；不直接把全部System入池。

目标仍5000Units/1000Agents，5000Agents暂缓；生产执行/API/schema/oracle/默认1线程未改。
G008/G009/R001/R002原状态保留，无新已确认玩法GAP。原49删除、两个冻结测量目录和负结果保留。
此状态优先于下方历史下一步；无新的容量/Frontier/发布或push/merge结论。


更新时间：2026-09-30。本文面向从本次Rust迁移工作中独立出来的**Rust并行优化任务**。不需要先读完整聊天，也不需要一次性打开所有历史报告。按下列顺序恢复；当前状态优先于旧报告中的“下一步”和进度条。

## 1. 先固定起点，避免从原 Python main 开始

2026-09-30核验：

- 生产仓库：`/Users/liyang/Developer/star-main`，分支 `codex/rust-env-migration`。
- 当前生产HEAD：`7e145d169433695cd4957e186a6b2fda06813c26`；annotated tag：`rust-kernel-r4e-2026-09-29`。
- 当前实际测量/实现源码：`5147e4d8e0c33c997bd86960d87fa4b5b3ca90c5`。上面的最终HEAD仅追加文档。
- 生产main仍为原Python `6a970deaee7d9b8d3939edd102973f2377edd6ac`，尚未合并Rust迁移。
- Lab：`/Users/liyang/Developer/star-lab`，分支main，R4e证据提交 `2a2b09cc1731e2b43840fc56e1fa233693ca656f`（本交接文档是其后新增）。
- 生产工作区有49处既有用户删除：`rotk_agent/`下文件及`rotk_env/assets/fonts/sh.otf`。不要恢复、删除或顺手提交；不要`git add -A`。
- API18 / schema5 / oracle `python-r0c-3cc4ffe`。扩展SHA256：`324454a00ab8bd3559c9229e6c6c9644242d65c488585eba7d29a63b39d29405`。API号相同不保证二进制相同，仍须核对源码和扩展hash。

新并行分支应从上述R4e tag创建，例如`codex/rust-ecs-parallel`，而不是默认main。先检查任务附件/工作树和Git状态；若需要隔离，使用managed worktree并显式指定R4e ref。保留已有冻结测量目录，不将它们改成开发目录：

- `/Users/liyang/.codex/worktrees/rust-wire-observation/star-main`：5147e4d，完整资源，当前Rust测量环境。
- `/Users/liyang/.codex/worktrees/python-capacity-baseline/star-main`：6a970dea，原Python对照。

这些是本机定位提示；可迁移的复现依据是commit/tag、wheel、manifest及checksum。今后合并只允许squash merge，合并前annotated tag固定节点。本阶段未push/merge，默认Python、native threads=1。

## 2. 第一轮必读：当前事实与不可改变的边界

按顺序读：

1. [本交接文档](rust-parallel-handoff.md)：先理解设计演变和新任务边界。
2. [实验记录协议](../PROTOCOL.md)：生产/Lab分工、证据链、负结果、源码与工具SHA、归档规则。
3. [Rust System并行现状](rust-system-parallel-status.md)：当前已经并行什么、没有并行什么，以及为什么。
4. [权威状态与只读边界](../../star-main/docs/native-state-boundaries.md)：谁能写什么、缓存与展示消费者、只读任务生命周期。审计有版本和范围，不能当作覆盖所有未来写入的证明。
5. [运行接口与语言边界](../../star-main/docs/native-runtime.md)：重点读Product boundary、R4a/R4b、R4d、R4e和安装说明。
6. [Benchmark GAP台账](../../star-main/docs/native-benchmark-gaps.md)：保留历史差异、已修复项和未决风险。重点G001–G003、G008/G009、R001/R002；不要把开放风险当作已证实规则差异，也不要因并行测试通过就自动关闭。
7. [R4e最新容量报告](../experiments/2026-09-rust-1000-agent-validation/README.md)及同目录[analysis.md](../experiments/2026-09-rust-1000-agent-validation/analysis.md)、[decision.md](../experiments/2026-09-rust-1000-agent-validation/decision.md)：这是当前性能起点；commands/manifest/raw是复现依据。

完整时间线在[rust-env-migration.md](rust-env-migration.md)，全局恢复入口在[10k-online-resume.md](10k-online-resume.md)，活动优先级在[10k-online-next-steps.md](10k-online-next-steps.md)。它们保留了旧阶段，读顶部最新状态后按问题下钻，不能执行每一段历史“下一步”。2026-09-13的可视化迁移地图也属于历史快照。

## 3. 本 Session 的关键认识变化

| 早期想法/现象 | 实验或审计后的认识 | 对新并行任务的要求 |
|---|---|---|
| 1000Agent每秒观测可代表真实负载 | 用户最终选择观测→动作→墙钟思考约30秒→下一轮，思考期间不轮询 | 不以旧1Hz/Agent压力口径替代当前闭环；世界CD仍用模拟时钟 |
| 同阵营公共信息可反复复用 | Python已实现同只读批次共享，Rust也已有；不同阵营可共享底层事实，但各自做Fog投影和权限装配 | 先接已有批次能力，不能声称这是全新算法；不能跨写入、TTL或返回旧帧 |
| 把Python观测丢到多个进程可能很快 | v1每请求冻结/导出/IPC/还原的成本超过串行构建，实测更慢 | 避免逐Agent复制整个动态世界；不重复该设计而不先量成本 |
| Rust迁移意味着尽量移除Python | 用户明确采用类似PyTorch的边界：Rust高效执行世界，Python保持易用接口与生态 | SDK/策略/配置/UI/网络编排留Python；热点下沉但保留Python接口 |
| 多线程能直接解决观测慢 | R4a大面板有收益，小子集可能变慢；公共JSON树构建/复制/释放是另一瓶颈 | 分别测公共构建、面板、调度、编码、跨语言及客户端decode，不能只加worker |
| 把事实缓存起来就足够 | R3k4共享不可变编码事实，R4b改typed直接编码，R4d省服务端decode再encode，才明显减少成本 | 先减少重复工作、分配与复制；完整输出仍有按payload增长的成本 |
| ECS的System彼此少import，所以天然独立 | 它们共享组件、空间索引、事件、活动集合和随机数顺序；当前step仍顺序调用advance_* | 写出完整读写集和业务先后关系，再选择System间或System内部并行 |
| “性能迁移完成”意味着性能工作结束 | 主要计算已迁Rust，不等于System全面并行、应用集成或平台发布完成 | 分开报告计算归属、并行覆盖、容量、兼容和发布，不能混为一个百分比 |
| CPU空闲很多，世界step应优先并行 | R4e第一轮step平均0.295ms，显示系统8.679ms，展示应用2.768ms；step不含观测 | 基于实测热点选择并行对象；不承诺仅并行step就成倍加速整帧 |
| 5000Units/5000Agents是下一步 | 用户暂停5000Agents，先验1000Agents；当前已经三轮长测通过 | 保持5000Units/1000Agents主目标，未经新指示不恢复5000Agent调参 |

两个明确未采用的玩法改动：不放开叠格/穿透单位来静态化路径；不在本迁移中取消兵力损失导致的移动力弱化。后者用户倾向取消，但必须作为独立规则变更。并行不能借机删观测字段、近似Fog、延迟动作生效或更改事件提交时机。

## 4. 第二轮阅读：重要失败与成功，避免重走弯路

按需阅读README/analysis/decision，不先加载大raw：

- [Python并行观测v1负结果](10k-parallel-env-v1.md)：2worker导出约8.5ms、还原约11.5ms，而串行构建约5.5ms。冻结探针，不是动态闭环。
- [主流ECS候选路线调研](10k-parallel-ecs-alternatives.md)：System之间并行与System内分块的区别，延迟结构修改不等于可以改变游戏提交顺序。2026-09-11历史调研，实施时以锁定依赖源码/API为准。
- [R4a只读并行](../experiments/2026-09-rust-read-parallel/README.md)：已存在的固定线程池与大小查询的正负结果。
- [R3k4编码共享决策](../experiments/2026-09-rust-kernel-encoded/decision.md)：Arc只保证共享所有权，不代表并行；输出结果不能依赖后续世界生命周期。
- [R4b公共事实成本](../experiments/2026-09-rust-public-facts/decision.md)：优化数据表示优于仅增加worker的证据，微测不能冒充容量。
- [R4d传输边界与5000-Agent负结果](../experiments/2026-09-rust-5000-agents/README.md)：原字典往返/直接JSON传递区别，以及扩大帧内预算不能同时解决帧和排队问题。

旧[10k-parallel-env-proposal.md](10k-parallel-env-proposal.md)是Python时期的设计背景，**不是当前Rust并行实施规格**。如需恢复确定性基线，读[R0报告](../experiments/2026-09-rust-r0/README.md)及迁移记录中的R0b/R0c段。

## 5. 代码入口：按数据生命周期阅读

下列路径相对star-main，先用CodeGraph做结构定位，再阅读具体实现；不要一开始全仓库扫描。

| 顺序 | 文件 | 要回答的问题 |
|---|---|---|
| 1 | `native/rotk/src/runtime.rs` | Runtime拥有哪些状态/索引/活动集合？step、reset和导入在哪里形成写入边界？当前advance_*顺序是什么？ |
| 2 | `native/core/src/world.rs`、`native/rotk/src/components.rs` | 外部ID与Bevy Entity如何映射？哪些状态是typed，哪些仍是冷数据？ |
| 3 | `native/rotk/src/observation.rs` | ObservationBatch的只读借用、公共事实/Fog/面板/权限边界；prepare_panels如何join并按固定顺序合并？ |
| 4 | `native/core/src/read_pool.rs` | 已有1/2/4档固定池、分块、借用作用域、退出及并发测试；优先复用，避免重复线程池与过度订阅 |
| 5 | `native/python/src/lib.rs`、`rotk_env/runtime/native.py` | py.detach后实例Mutex的作用；外部操作为何仍串行；get_faction_state_json怎样省重复编解码？ |
| 6 | `native/rotk/src/actions.rs`、`team.rs`、`codec.rs` | 可信身份、动作次序、查询/写入分段、控制权限与响应所有权；不能让worker完成顺序决定可见世界 |
| 7 | `native/rotk/src/movement.rs`、`spatial.rs`、`vision.rs` | 最典型依赖：位置/占用更新→视野dirty→Fog投影；候选计算与确定顺序提交能否分离？ |
| 8 | `native/rotk/src/combat.rs`、`recovery.rs`、`lifecycle.rs`、`statistics.rs`、`turn.rs`、`territory.rs` | 战斗/死亡/资源/回合/胜负/统计的隐含共享写入和先后关系；针对候选System再深入 |
| 9 | `native/core/src/rng.rs`、`clock.rs`、`deadline.rs` | CPython随机兼容、消费次序、模拟时钟与活动deadline；并行不得改变RNG分配或dt语义 |
| 10 | `native/rotk/src/presentation.rs`、`rotk_env/runtime/` | 展示delta有drain/一次性事件语义，不是可随意并发的纯读；展示缓存不是第二套权威世界 |

并行线程开关不是把Runtime整体放到多个线程上。当前`with_runtime`锁住整个实例，再执行`&mut Runtime`闭包；只读面板workers在内部借稳定数据，返回前join。当前不是多Agent外部调用并发，也不是Bevy Schedule自动并行世界Systems。

依赖和安装读取根`Cargo.toml`、`Cargo.lock`、`rust-toolchain.toml`及`native/python/pyproject.toml`，以实际文件为准，不从早期方案猜版本。性能实验使用release，勿拿debug库比较。

## 6. 测试和实验入口

生产契约优先：

- `rotk_env/tests/test_native_parallel_observation.py`
- `rotk_env/tests/test_native_request_batch.py`
- `rotk_env/tests/test_native_encoded_observation.py`
- `rotk_env/tests/test_native_public_facts.py`
- `rotk_env/tests/test_native_wire_observation.py`
- `rotk_env/tests/test_native_movement.py`、`test_native_vision.py`、`test_native_combat.py`
- `rotk_env/tests/test_native_presentation_delta.py`、`test_native_r1.py`

变更触及哪些生命周期、资源或身份路径，再补相应既有契约；不能只比较速度或最终hash。比较完整解码响应、列表顺序、游戏事件和权威状态。保留M→Q→N：Q必须包含M、不含N。录制/注入墙钟元数据，不能用种子推导真实LLM响应时间。1/2/4线程的工作结果应一致，线程利用率诊断计数可以不同。

Lab入口：`tools/p3_runtime.py`、`tools/p3_local_agents.py`；轨迹与核验：`tools/rust_migration/native_loop_trace.py`、`replay_rendered_loop.py`、`analyze_1000_gate.py`；归档：`package_agent_capacity.py`。具体运行参数用R4e `results/commands.json`，不要靠摘要重新拼出另一个负载。

当前R4e：M4/16GB，5000活Units/1000合成Agents，30Hz固定dt，1线程/8ms接入预算，Cocoa2480×1239，Fog开、minimap单位层关、有限运行GC延迟、Chrome开。Agent首次请求错开0–30秒，逐Unit move/attack/wait=50/25/25，非法等待，不重抽；思考截断正态30±5秒、15–45秒，期间不轮询。

三轮30秒预热+300秒测量：帧P99为29.800/29.275/29.470ms，观测响应45.872/47.783/44.798ms，动作排队35.293/35.601/34.744ms；各30Hz，所有guard通过，5000存活、峰值同时移动171/177/173。包含Python展示/呈现，不包含限帧等待、Hub和真实LLM。不是全5000同时移动/高接触密度容量。

第三轮实际输入的4线程重放40994请求/9880tick/9880展示全部一致；不代表4线程性能达标。原生产Python与当前Rust各一次同条件60秒短测：观测service7.822→2.741ms（约2.85倍），整帧P9931.800→26.453ms（降低16.8%）；不是固定输入的纯语言比较，排队下降也不是计算加速34倍。原版、规范化Python两个负对照都保留。

## 7. 建议新 Session 的首个交付

先提交一张**读写依赖与成本表**，列出组件、索引、冷数据、活动集合、事件、随机流、展示变化队列的读写及先后约束；区分System间并行、System内并行、跨请求只读共享三个不同问题。基于现有计时选择一个候选，不先承诺把所有System并行化。

随后选一个收益可测、规则无变化的小步实现；与冻结单线程同输入对照，再做实际闭环测试。不得为凑批次跨越动作或等待更多Agent。活动集合优先O(active)，Bevy Changed不自动意味着只遍历活动实体。

进度报告附阶段状态条；生产代码/契约/用户文档在star-main，实验工具/结果/复现在star-lab。任何Benchmark相关差异写GAP台账。每阶段更新恢复入口；通过一个阶段不代表切换默认后端或整个迁移发布。
