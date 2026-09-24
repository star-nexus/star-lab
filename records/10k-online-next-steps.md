# 10K 后续工作优先级

## 当前方向与检查点：R3k1，继续Rust世界执行（2026-09-24）

**用户最新范围：只迁移Rust负责高效执行世界的部分。** 本节取代上一条“先接网络host”的工作优先级；网络连接、ACK/通知、BOT策略、UI与报告保留Python并单列集成，不作为下一步Rust重写任务。

最终 **`d5a1d5cfc0096a632019a6cc7d94929b77238db7`** / annotated tag **`rust-kernel-r3k1-2026-09-24`**；构建 `7460cd9`、测试/测量 `8dd16f4`（Rust代码一致，精确SHA见manifest）。[阶段报告](../experiments/2026-09-rust-kernel-targets/README.md)。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 内核补齐中 | R4 ░ | R5 ░`。本轮补迁Python已有的attackable空间局部筛选；复用Rust占用索引，按Fog可见集合过滤，再走原Combat判定与ID排序。巨大射程回退列表，AP不足提前结束，不采用近似或跨帧缓存。

2112完整回归（新增133）、163针对性、3Rust/fmt/Clippy、旧六场景510节点重放通过。8组500/5000Units前后初始状态及完整响应一致；500档4组另对照Python。5000Units/100己方查询/2500可见敌军的单查询射程1为468.45→42.50ms、射程3为465.20→44.01ms；这是1预热+5样本中位数，含JSON编码、不含世界/展示/排队，**不是30Hz容量结果**。射程80略慢的负对照和setup-error均保留。

API13/schema5 release，扩展SHA `8671e69b5ac586762d45c8f174370bc8e72ec528e1b88a7b408bcfd1b0d9607a`；活动生产venv与完整目录 **`runs/star-rust-kernel-targets`** 已装新wheel。旧API12目录不动；49处原删除保留；main仍6a970dea，无merge/push，Python默认，无新并行。

[GAP台账](../../star-main/docs/native-benchmark-gaps.md)记录性能迁移遗漏及规则未变的实测范围；G008/G009仍是Python应用集成未完成项，R001/R002不笼统关闭。下一步继续审计Rust公共观测事实、空间/实体索引及批量装配成本，再按证据推进只读并行；用户在本轮再次要求继续此方向。首个5000Units+1000Agents/30Hz闭环验收与5000Agents扩展尚未完成。

以下记录保留为历史，当前范围以上文为准。

## 最新检查点：R3d4a，Rust宿主权威接口（2026-09-24）

最终 **`5ce4b3f02a5fb676e11c8bc240e86513d3e00b25`** / annotated tag **`rust-kernel-r3d4a-2026-09-24`**；运行实现/构建 `97f45b1c8fb1c6054d22ab9c970541955ea528c8`，测试/测量 `343ced3809f0ddf57c53036613abea2f9280daf5`（只改测试起始阵营，运行代码一致）；最终只改文档。[报告与复现](../experiments/2026-09-rust-r3-host-authority/README.md)。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 功能迁移中 | R4 ░ | R5 ░`（非工时百分比）。继续采用Rust性能内核＋Python易用接口/生态边界；5000Agents是独立扩展目标，不等于5000Units或已验收容量。

新增API12 `host_status`、`record_message`、`turn_start_context`：Rust提供当前回合/结束状态、消息计数及通知候选；Python连接、ACK重试与通知编排保持上层职责。离线结算已读取四字段Rust权威状态，避免依赖Python展示缓存；60墙钟秒等待与一次完整报告导出保持原状。回合候选仍O(注册Agents)，本轮没有端到端性能收益数字。

1979完整回归（Native1057、新增44），50针对性、3Rust/fmt/Clippy通过；9配置45次消息状态、18次通知顺序与Python一致；旧/新六场景510节点及新进程重放通过，6JSON/CSV和4PNG归档。保留两个setup-error日志但不作正式因果证据。**没有真实联网、ACK重试、并行或新容量结论。**

[主GAP台账](../../star-main/docs/native-benchmark-gaps.md)已更新：单条与批次计消息时点不同，未注册先增加个人计数再报错；重新注册保留旧阵营registry行；通知set顺序随Python hash seed可能跨进程变化。均为保留的旧机制，不能静默修正或宣称跨进程网络顺序已确定。**G009仍OPEN**，G008/R001/R002也未关闭。

活动生产venv与完整试玩目录 **`runs/star-rust-r3-host-authority`** 为API12/schema5 release，扩展SHA `dd583a3adcb9064e3d4320e3e5a5eb9f12c032247d93356398c65c75c1a44cda`；旧API11目录/tag未动。main仍6a970dea、无merge/push、Python默认，1/2/4仍串行Mutex，原49处Agent/font删除保留。

**下一步：接通G009的Python owner线程消息宿主**，复用Rust权威接口，验证真实可信身份/单条与批次计数、回合ACK/重试/断连、结束通知/上报等待及错误关闭。VLM必须在显示owner线程完成；成功end_turn→读取通知上下文之间不得接纳其他写入（当前独立API不是跨调用事务）。随后BOT策略桥接G008及动态冷组件R002审计；完整R3后才R4并行和R5容量/跨平台。首个正式关卡仍5000Units＋1000Agents/30Hz/约30秒闭环，Agent思考期不轮询。

以下记录为历史节点，当前状态以上文为准。

## 用户补充的长期语言边界（2026-09-23）

采用类似PyTorch的产品组织：**Rust承担性能关键执行，Python承担易用接口与生态。** 迁移完成不以Rust代码占比或消灭Python为标准。四层架构不变；权威状态/玩法推进/观测计算及批处理在Rust，Python保留Agent/ENV SDK、配置与场景编写、启动、模型接入、实验、UI和社区扩展。扩展通过配置和明确命令接入，不能恢复一套可写的Python权威世界。

用户特别指出需支持5000 Agents：把它作为架构扩展目标，必须与5000 Units区分。原5000Units＋1000Agents＋30Hz＋约30秒闭环继续作为首个验收关卡；5000Agents的配套Units、节奏、payload和硬件须在后续容量矩阵明确，尚无通过结论。

接下来的host/BOT迁移应按职责划分：Python可保留连接/ACK/模型或BOT策略编排，Rust提供权威执行；不要求因为R3需要“接通”就把这些上层工作全部改写Rust。高频路由、序列化、批量策略计算或显示数据处理如实测成为瓶颈，再下沉其计算部分，维持Python使用界面。不逐Unit跨语言调用、不逐Agent全世界复制、不在Rust热循环回调Python，也不让Agent思考期按世界频率轮询。玩法/权限/观测和动作次序差异继续入GAP台账。

[生产语言边界说明](../../star-main/docs/native-runtime.md)。本次只补文档，功能检查点仍为下述R3d3c/API11，不改验收数据或tag。

## 最新检查点：R3d3c，VLM本地图像接口已迁移（2026-09-23）

生产最终节点 **`30c4b76c152857c98ff45fc7952af9ceb758059e`** / annotated tag **`rust-kernel-r3d3c-2026-09-23`**；构建/测量 `173410ad603121bfe97c028e6d121c7bd9a8e232`，最终只改两份文档，代码/测试一致。[完整报告与复现](../experiments/2026-09-rust-r3-vlm/README.md)。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 功能迁移中 | R4 ░ | R5 ░`（█完成、▒进行中、░待实施/验收；非工时百分比）。每阶段继续附进度条并更新[主GAP台账](../../star-main/docs/native-benchmark-gaps.md)，修复保留反例和版本历史。

**G007关闭限本地公开Python接口**：Rust执行原鉴权/阵营状态投影，Python附加原RenderEngine画面；默认动作集不变，需MatchRules显式启用VLM。完整批次预校验并冻结参数，在VLM处截图后再执行后续动作；普通查询继续共享。step/reset/close等不能穿过未完成的截图；截图错误仍保留结构化响应。无内核热循环Python回调。

1935完整回归（Native1013，新增VLM38），62针对性/3Rust/fmt/Clippy通过。54组已启用VLM由全未实现→响应和状态全一致；真实Cocoa两模式×魏蜀显示视角四组与Python图像字节相同；36组Player及旧/新场景各510节点重放通过。74个归档文件SHA256已核验。**没有新容量或并行结论。**

**必须保留的视觉历史边界**：当前全局画面不随请求阵营切换，不强制重绘到最新tick；无screen和1×1 headless行为不变。实际TGA却标PNG；透明像素编码还可能改变RGB，旧/新独立3像素及原始TGA包均复现。初版原始RGB等价guard失败已作为有效中间诊断归档，最终以原Python实际编码字节比较。它们不归为Rust新增差异，也未借迁移修改规则/输入；真实多模态模型接收和历史评分影响未验证。

活动生产venv与完整试玩目录 **`runs/star-rust-r3-vlm`** 均为API11/schema5 release，扩展SHA `29e256d91e80337731050164c1fc20b9fb02fbc5ae14d1d49065a90e84c5515b`。旧API10目录/tag保留；main仍6a970dea，未merge/push，Python默认；1/2/4仍串行；原49处Agent/font删除未动。

**下一步：继续R3的网络host/回合ACK/结束投递（G009），结合动态冷组件写入覆盖审计（R002），随后BOT（G008）。** R001宽松转换风险仍开放。网络host需把真实截图安排在应用显示owner线程，不能把单runtime admission锁误当成全局窗口线程安全；不重调BOT难度、不取消移动力弱化。完整R3后才R4真并行和R5容量/跨平台安装及最终tag+squash/default切换。

以下旧记录按原节点保留；当前状态以上文为准。

## 最新检查点：R3d3b，Benchmark文字兼容修复（2026-09-23）

生产最终节点 **`24215823c74a79774d38cc0b354b6e3d091a3b86`** / annotated tag **`rust-kernel-r3d3b-2026-09-23`**；构建/测量 `11aefce1fb498cd6b388b1dcf498dbd8529eafb0`，最终仅更新GAP台账，代码/测试一致。[完整报告与复现](../experiments/2026-09-rust-r3-text-order/README.md)。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 功能迁移中 | R4 ░ | R5 ░`（█完成、▒进行中、░待实施/验收；非工时百分比）。每次阶段报告继续附进度条，并维护[主GAP台账](../../star-main/docs/native-benchmark-gaps.md)，修复不删除历史。

**G006关闭**：输入对象在解析、存储、导出/reset中保留插入顺序；普通/嵌套策略依据和第二次上报的provider/model标签恢复Python文字。**新发现并关闭G013**：Unicode不可打印字符的嵌套repr转义原来不一致；使用CPython3.13/Unicode15.1固定713范围，顶层字符串继续原样保留。没有修改移动/战斗/CD/时钟或取消移动力弱化。

1897完整回归（Native975，新增文字契约45），188针对性/3Rust/fmt/Clippy/生成表核验通过。7组定向输入前后状态相等3/7→7/7；36组Player投影权威与展示均一致；旧场景510节点重放通过，新六场景237次更新、510节点及新进程重放通过。51个归档文件已核验SHA256。不是5000/1000/30Hz容量结果，也不是并行验收。

活动生产venv与完整试玩目录 **`runs/star-rust-r3-text-order`** 均为API10/schema5 release，扩展SHA `214b864f854a6fda64b0c56226bac15f9e8babc2ded28cea9195184311001d77`；旧API9目录/tag保留。main仍6a970dea，未merge/push；Python默认；1/2/4设置仍串行；原49处Agent/font删除未动。

**下一步：继续R3应用侧迁移，优先G007 VLM帧获取和动态冷组件写入覆盖审计，再网络host/回合ACK/结束投递（G009）与BOT（G008）。** 宽松转换R001和派生数据覆盖R002仍是风险，关闭两个具体文字GAP不等于所有类型兼容。完整R3后才R4真正并行/R5容量与macOS/Linux及Python3.14安装验收；不得提前切默认后端或合并main。历史真实LLM日志是否触发文字差异尚未审计。

以下旧记录按原节点保留；当前状态以上文为准。

## 最新检查点：R3d3a 与 Benchmark GAP 台账（2026-09-23）

生产最终节点 `a11c2b125cae451bcac6e3c3332bcbd65af24409` / annotated tag `rust-kernel-r3d3a-2026-09-23`。修复、构建、测量节点 `5e086be1160d49d148d09cfa6f3ee1743a3b8a1c`；最终仅更新台账验证状态，代码/测试完全相同。[报告与精确复现](../experiments/2026-09-rust-r3-player-gaps/README.md)。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 功能迁移中 | R4 ░ | R5 ░`（█完成、▒进行中、░待实施/验收；非工时百分比）。

**用户新增持续要求：每阶段记录迁移产生的规则/机制/Benchmark GAP。** 主台账 [star-main/docs/native-benchmark-gaps.md](../../star-main/docs/native-benchmark-gaps.md) 已建立，不能只记未解决项；修复保留历史、精确版本、两边行为、Benchmark影响及复现。R0原版→oracle排序变化、未完成能力、已确认GAP、未验证风险和保留的原机制分开记录。

本轮修复G004：死亡后展示Player.units过期，36配置展示一致性0/36→36/36，权威始终36/36；初次全量Player基线、后续死亡成员ID补丁。修复G005：Python接受的全角/其他Nd数字在Rust策略分/统计计数解析中失配；反例策略分0.5，以及12+2得到14次/14.29%已精确恢复，68组680数字及非法边界有契约。1852完整回归（930 Native、新增114）、3Rust/fmt/Clippy、六场景510节点独立重放通过。没有容量结论。

**仍开放G006：对象转文字的键顺序改变**；本例evidence输入z,a，Rust存成a,z。响应相同也可能状态文本不同；after审计继续保留这一有效负结果，不能关闭或忽略。尚未审计旧真实LLM评测输入是否触发，不能推断排名已变或未变。主分支未合并Rust。

当前活动venv为API9/schema5 release扩展，SHA `60a6a30e7e267e08140173e821a53b52fcde02222124ce3382a94d2fba153070`；完整试玩checkout `runs/star-rust-r3-player-gaps`，旧R3d2b/API8保留。生产原有49处Agent/font删除未动，main仍6a970dea，未merge/push；Python默认，1/2/4仍串行。

**下一步优先G006及宽松类型转换兼容审计**，随后继续VLM、其他动态冷组件、网络host/回合ACK/结束投递与BOT。它们仍是完整R3的必需范围；之后才R4真并行和R5容量/安装。每次阶段报告附进度条，并同步更新主GAP台账与此恢复入口。已确认规则保持不变；取消移动弱化仍单独处理。

以下为历史记录；最新节点与安装状态以上文为准。

## 当前检查点与下一步（2026-09-23）

**R3d2b 已固定。** 生产 `a6bf5f381b0393b0ab93973502d9744d6b9e3713` / annotated tag `rust-kernel-r3d2b-2026-09-23`。[报告、试玩与复现](../experiments/2026-09-rust-r3-host/README.md)。离线 GameScene/菜单/CLI 已接 Rust；三种统计/状态系统动作、结束通知计划、一次权威快照结算及JSON/CSV保存通过验证。仍保留现有60墙钟秒结算等待；HUD小表不充当完整结算来源。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 功能迁移中 | R4 ░ | R5 ░`（█完成、▒进行中、░待实施/验收；不是工时百分比）。**每次阶段报告继续附此进度条。**

1738完整回归（816 Native、79新契约）、3Rust/Clippy/fmt通过。六场景237更新（158窗口配置、79同Cocoa引擎中的headless配置），510节点及6初始快照精确重放，新进程重放再次通过；4真实CLI进程52帧覆盖dummy/Cocoa与两种模式，退出后世界关闭。6JSON/6CSV、4截图已归档；合成SDL和直接菜单回调，不宣称物理输入验收或新容量结果。初版Lab记录器遗漏None墙钟值已修正，故障注入复现指向UnitObservation.last_seen_time，旧有效部分日志单列intermediate。

活动venv已安装该节点API8/schema5 release wheel，扩展SHA `f9e7169fab2f2f154baf582d5578201a9fc3a0dfb868f7cc0f72cb3851baf46c`。完整试玩/验证checkout为 `runs/star-rust-r3-host`，旧R3d2a/API7及所有历史tag/checkouts保留。生产原有49处Agent/font删除未修改，main仍 `6a970deaee7d9b8d3939edd102973f2377edd6ac`，无merge/push。

**下一步：R3d3，完善应用侧边界。** 先审查动态Player/其他冷组件的展示同步及VLM帧获取，再接网络host（可信身份/连接数、回合ACK、结束通知/重试）与BOT；完成完整应用行为对照后进入R4真实并行/成本优化，R5容量/安装。Rust当前仅支持离线，Hub/BOT/旧scale harness明确拒绝；普通启动默认Python，1/2/4仍串行Mutex。没有5000/1000/30Hz通过结论。移动力弱化等玩法保持不变，后续Agent仍为墙钟30秒闭环且思考期不轮询。

本机试玩：在 `runs/star-rust-r3-host` 执行 `.venv/bin/python -m rotk_env.main --backend rust --no-hub --skip-start --mode real_time --scenario chibi-small --seed 42`。无BOT时AI槽不自行行动；双方Human可在离线菜单配置。

以下为历史检查点，安装与优先级以最新节为准。

## 当前检查点与下一步（2026-09-22）

**当前节点：R3d2a 已固定（2026-09-22）。** 生产 `91dc7688601c93192fea174c69981a315ac80ef9` / annotated tag `rust-kernel-r3d2a-2026-09-22`。[报告/复现](../experiments/2026-09-rust-r3-session/README.md)。完成 `NativeSession` 离线生命周期、初始化/输入异常与订阅清理、纯展示系统挂接；Rust提供HUD阵营小表及战报首批/追加增量。1659完整回归（737 Native、41新契约）、3Rust/Clippy/fmt通过；标准小场景真实Cocoa6配置540帧、558操作节点及新进程独立重放通过。0/10000条历史的HUD结构大小相同，仅是结构验证，**没有容量结论**。

活动 `.venv` 已安装该节点 API7/schema5 release wheel，扩展SHA `d95330879ebd9427233e8aade3bb075233fbd52ca741d197086e0ce0a01627e3`；完整checkout `runs/star-rust-r3-session`，wheel/raw/compact/6PNG和21项checksum在报告目录。旧R3d1 API6归档及checkout不变。生产仅剩原有49处Agent/font删除，未纳入提交。

**下一步：R3d2b，GameScene/菜单/CLI后端选择与host生命周期。** 先补齐结束后通知/统计输入和权威结算数据交接，再接场景与后端开关；不能拿部分HUD GameStats生成完整结算，也不能挂回Python玩法系统。随后VLM/BOT，再R4真并行与R5容量/安装。当前 `NativeSession` 仅用于开发/离线场景，Hub/BOT明确拒绝，普通启动仍是Python；**R3/R4/R5未完成、main仍6a970dea、无merge/push、1/2/4仍串行**。下一阶段要审查动态Player/其他冷组件的展示更新与场景退出后回调，避免仅凭窗口能画就宣称完整兼容。

以下为历史阶段记录；当前安装状态与优先级以上文及恢复入口为准。

## 最新检查点：R3d1 本地输入（2026-09-14）

**当前节点：R3d1 已固定（2026-09-14）。** 生产 `c5ae37f5fab2e3563af136f8868d8fc7227c1f23` / annotated tag `rust-kernel-r3d1-2026-09-14`。[报告与复现](../experiments/2026-09-rust-r3-controls/README.md)。本地移动/攻击/等待/驻守/筑垒/Fog/工具栏命令、Python输入/面板适配已接；UI只操作派生数据，命令返回前刷新。旧controller的epoch在native锁内写前/取增量前检查，不能污染reset后的新世界。保留UI/Agent、键盘/工具栏的历史差异。1618完整回归（696 Native、114新契约）、3Rust/Clippy/fmt；144配置7128节点精确差分和重放通过；真实Cocoa4配置480帧、48个合成SDL事件与4次工具栏直接命令、16PNG归档。**不等于完整GameScene/物理鼠标/容量验收**。API6/schema5、oracle=python-r0c-3cc4ffe；活动venv安装本检查点归档release wheel，扩展SHA `527c60fcca55aec5b4d2481cd113c78663eb1c3f631c6e72d83964c37fe98842`。正式checkout `runs/star-rust-r3-controls`。

下一步 **R3d2：GameScene/后端选择与输入生命周期**，再接完整HUD/VLM、BOT和结算。R3d1本地回放显式关闭LLMSystem帧更新；post-game通知/报告收集仍必须在后续host集成中验证。**R3/R4/R5仍未完成，Python默认/main不变，1/2/4线程仍串行，无新5000容量结论。**


更新：2026-09-14。当前执行已获授权的Rust内核＋Python接口完整迁移；P1/P2仍跳过。没有新增容量通过结论。
恢复入口：[`10k-online-resume.md`](10k-online-resume.md)。

## 当前路线：Rust迁移（优先于下方历史候选）

R3c已固定于生产 `5bda51db6cd68455aa5724a6ef0eca1e66f89dda` / `rust-kernel-r3c-2026-09-14`；
[阶段记录](rust-env-migration.md)、[验证报告](../experiments/2026-09-rust-r3-presentation/README.md)。
1504全回归、5184节点/4032ticks差分与精确重放、真实窗口960帧通过；API/schema=5。
移动/战斗临时ID和生命周期在Rust，Python已有资源/领地/Fog/特效增量消费者。完整可玩入口尚未接。

1. R3d：GameScene生命周期、后端选择和输入命令；不允许Python展示组件修改Rust权威状态。
2. 完整HUD与VLM帧获取、BOT输入、结算数据/事件；覆盖实时/回合制和none/dummy/window完整运行与reset。
3. 完成单线程等价后进入R4只读观测并行和成本优化。现有1/2/4只验证一致性，没有worker加速。
4. R5按既定5000U/1000Agent/30Hz闭环门槛与平台wheel要求验收；通过后才tag+squash/default Rust。

保留规则：休息/工事/技能中的历史行为暂不修正，MP弱化仍单独处理；ENV固定模拟dt，Agent按墙钟思考且不轮询；Chrome保持开启，性能实验串行。生产main6a970dea和旧实验负结果不变，无关49处删除不纳入迁移。

## 最新调研与候选优先级（2026-09-11）

见[主流并行 ECS 调研](10k-parallel-ecs-alternatives.md)。用户本轮要求探索方案，未自动启动新的实现。
建议顺序：定位观测热点及最小依赖 → 单线程紧凑数据维护对照 → 单线程原生内核 → 同内核2/4 worker分块 → 有净收益再做动态闭环。原生 Job＋只读阶段屏障为主候选；需要世界/观测重叠时再比较常驻增量副本和带版本共享内存；free-threaded Python先验证扩展兼容性和真实GIL状态。
这些均未测量。保留v1完整快照负结果，不将并行调度、帧末统一提交或模拟LOD偷偷变成博弈规则变更。

## 最新完成：并行观测v1原型，性能负结果（2026-09-11）

用户已授权实现并新建分支。生产`codex/parallel-observation-v1`从6a970deaee7d9b8d3939edd102973f2377edd6ac起步；见[实施记录](10k-parallel-env-v1.md)。
开发tip3c4fba1a40fccee7bfc06575ade338c30a4b784e，已用annotated tag `p3-parallel-observation-v1-prototype-2026-09-11`固定。936项回归通过；主探针960次输出等价、所有guard通过。
[报告/复现](../experiments/2026-09-parallel-observation-v1/README.md)：5000Units/1000注册Agent冻结探针，串行约141次/秒，2worker51–52、4worker约62。逐请求完整快照导出/还原抵消并行收益，保留开发分支，不合并main，不进入该实现的动态闭环，无24/30Hz容量结论。
主工具57343ce1b18f457b745391b5352081f547e40b45；raw/compact与前轮辅助负结果均归档核验。下一候选先降低快照成本（同只读批次摊薄或完整写入覆盖的增量镜像），尚未实施；Lab客户端独立与动态验证仍待后续。main仍6a970deaee7d9b8d3939edd102973f2377edd6ac，当前代码checkout为开发分支。本轮未推送。

## 最新方向：已确认先做观测并行（2026-09-10）

用户已明确同意先做观测并行，并要求完善方案；旧“并行暂停”不再适用于这一方向。
见[单写世界、并行观测建议](10k-parallel-env-proposal.md)。当前只形成方案，生产未改，未运行新实验。
优先评估Lab客户端隔离→只读快照worker→动态一致性与性能，避免把18ms仿真预算误当ENV固有限制；保留四层架构和原有观测/动作顺序语义。
补充方案明确ECS数据依赖、快照与投影复用、请求生命周期、对照组与正确性用例。下一步按方案做依赖审计和原型验证，不能直接将现有System或活World放入进程池。

## 最新完成：文字缓存修复（2026-09-10）

[修复报告](../experiments/2026-09-text-render-cache/README.md)已归档。生产main6a970deaee7d9b8d3939edd102973f2377edd6ac，由tag钉死5f13218后squash集成，912回归/94结构契约通过。
zoom0.5坐标整帧P99 736.38→15.52ms；连续平移779.10→23.53ms；1000条文字准备2.54→0.97ms。首次坐标打开最大37.08ms，未改视觉反馈和博弈规则。
自然5000U/1000A/24Hz闭环60秒维持平均24Hz，整帧P99=41.33ms；100ms请求排队guard仍失败。本次没有新增容量认证/Frontier；当时并行与Protocol/Hub保持暂停，现观测并行方向以上方最新确认为准，Protocol/Hub仍暂缓。

## 历史诊断与当时候选修复（2026-09-10）

已完成[坐标/飘字P99归因](../experiments/2026-09-text-render-probe/README.md)，未改生产。
坐标在zoom1/0.5的文字路径P99约171/727ms，是明确渲染瓶颈；默认zoom0.15跳过坐标，不解释旧大规模实验P99。
自然5000U/1000A闭环最多11条飘字，文字准备P99=0.054ms，整帧P99=43.08ms；少量飘字不是当前canonical场景主瓶颈。
如安排修复，优先缓存字体/完整坐标标签surface；后续A/B须固定已稳定地图缓存，不能从本轮不同缓存过渡状态的整帧P99相减推算飘字收益。
本轮只完成用户要求的分析；未自动实施优化，不新增Frontier，不启动并行或Protocol/Hub。

## 最新结果：24Hz随机闭环实验已完成（2026-09-10）

- 生产source仍为906386312d70d77af25e4b4da883f6dd5b0fe5ef，未修改生产代码或默认FPS；本轮仅扩展Lab运行参数与Agent调度。
- [报告/复现命令](../experiments/2026-09-p3-clock24/README.md)、[分析](../experiments/2026-09-p3-clock24/analysis.md)、[决策](../experiments/2026-09-p3-clock24/decision.md)。4个完整运行，10个archive artifacts（4raw/4compact/2fixture），已解包重算并核验SHA。
- 确认ENV固定dt=1/24，GameTime累计与delta相同；外部Agent思考用墙钟。24帧=1模拟秒，机器慢时模拟秒可以落后墙钟，不以墙钟补偿CD。
- 5000 Units/1000 Agents，canonical阵营集结布局，逐Unit move50%/attack25%/wait25%，无合法目标则等待；观测后立即提交动作，然后等待截断正态N(30,5²)墙钟秒（15–45秒），初次请求uniform(0,30秒)。无思考期轮询。
- 30s预热+300s测量、Agent每帧18ms预算：平均24Hz，7200帧=300模拟秒；frameP99=44.54ms（7.60%帧超过41.667ms，max48.94ms）；观测P99=177.97ms、动作排队P99=170.45ms，期末最老排队30.18ms，名义闭环完成99.74%。
- 测量期接受24770次move、957次attack；5000Units全部存活，同时移动采样平均120.38/最大181。不能写成5000Units持续同时移动。
- 结论：指定canonical负载可持续达到平均24Hz并无持续大队列；严格frame与100ms请求P99仍有越线。不是旧所有guard都通过的四trace容量认证。
- 负对照：interleaved全地图高接触密度，平均观测1.267MB，世界16.93Hz、观测P99=25.14s，不能承载目标。不能只报5000/1000而省略布局、动作频率和信息量。
- 9个生产时钟测试、12个Lab调度/分析测试通过。Protocol/Hub、真实LLM、并行架构均未接入；并行化继续暂停。
- 后续以本节结果为准，不重复本轮实验、不自动扩大优化范围；以前“必须保持墙钟游戏推进”的表述已作废。

## 最新用户确认：闭环Agent，24Hz可接受，30Hz为更高目标

本节优先于下方历史计划中的独立轮询要求。用户原话是“观测从1Hz/Agent建立基线，再测5、10、30Hz”，没有明确要求LLM思考期间持续轮询；助手将其解释为独立周期观测，随后错误地归因为用户的明确要求。现予更正。

- 主要交互方式：获取一次观测 → 模拟LLM思考（例如30秒）→ 提交动作 → 获取下一次观测。思考期间不额外轮询，不替换当前决策快照。
- 独立1/5/10/30Hz结果保留为额外压力测试，不再作为真实LLM闭环必须达到的主要容量标准。不能据这些压力测试失败断言闭环千Agent不可用。
- 用户接受5000 Units/1000 Agents、30秒闭环已有300秒测试的实际表现：平均世界30Hz、整帧P99=34.5907ms、观测P99=35.6697ms、动作排队P99=28.4315ms、名义闭环负载完成99.9%。旧33.333ms严格门槛失败的历史标签不改写；这组数据可作为用户接受的工程使用基线。
- 大规模评测允许世界24Hz（每步约41.667ms），30Hz保留为更高目标。既有34.5907ms低于24Hz对应预算，支持可行性判断，但不是已运行24Hz的直接验证。旧证据源于第一轮版本，不能标为最新源码的24Hz认证。
- 5000 Units为驻留/受控规模，不表示5000个单位始终同时移动。Protocol/Hub未计入，不能写成完整网络千人在线认证。
- 后续恢复工作时优先核验最新版5000/1000、30秒闭环、24Hz，再视结果评估30Hz。保持世界每秒模拟时间、移动/恢复/冷却与30秒思考的墙钟语义；不能靠放慢游戏取得帧率。
- 并行架构继续暂停；暂不因独立轮询压力测试失败扩大优化范围。本次仅更新活动记录，未改生产运行频率、未启动新性能实验。更强硬件改善30Hz是合理假设，尤其取决于单核性能，仍需实测。

## 已有基础与验收边界

E8 已有固定 workload 的完整持续窗口 P99 通过证据和 505 项回归测试。
5 秒滚动窗口仍有越线；长测整帧 P99 未通过 33.33ms。不能将持续窗口
结果解释为任意短窗口、每一帧或 10K online Agents 已达标。
P0 已完成：源码主分支、tag 与 Lab 证据已推送；实验分支和项目目录已清理。
具体版本、测试及恢复验证见 [P0 closeout](../archives/2026-09-10k-p0/closeout.md)。

## 优先级与完成标志

| 优先级 | 工作 | 为什么做 | 完成标志 |
| --- | --- | --- | --- |
| P0（完成） | 评审并准备集成已验证基线，明确发布 gate 的窗口定义和重复规则；安排源码、tag、Lab 证据的远端保存 | 防止基线漂移、窗口口径混用和证据只留本机 | 版本和证据可定位；集成后的必要回归通过；发布结果明确区分持续窗口、5 秒滚动及整帧指标 |
| P1（跳过） | Core 30–60 分钟长测：内存、队列/缓存、GC 安全点、逐时间段性能趋势 | 当前最长证据约 305 秒，长期成本漂移原因尚未确立 | 有不截断、采样开销已评估的完整长测证据；无持续增长的存活状态/积压，世界进度正常；趋势及超时情况明确记录 |
| P2（跳过） | 验证 workload 和生命周期变化：0/50/100% 移动、不同 phase seed/可见密度、单位增删替换及阵营变化 | 新优化依赖组件引用版本；当前性能通过限于固定场景、种子和视口 | 正确性和引用失效行为一致；每个变体独立报告，保留固定 canonical workload 作对照 |
| P3（进行中） | Phase 6：本地合成 Agent 经 ENV 业务入口，100 → 1K → 5K → 10K sessions；Protocol/Hub 暂缓 | 10K units 容量不等于 10K Agent 容量 | 本地注册/多 Unit 认领/观测/合法 action 或等待可复现；吞吐、序列化、排队及 action 应用延迟可归因；慢 Agent 不阻塞世界进度。见 P3 活动记录 |
| P4 | Phase 9：10K Core 与 10K 合成 Agent 全链路，再做 30–60 分钟 soak | 分别通过不能证明合在一起通过 | 世界时序、协议吞吐、背压、内存和状态一致性同时满足预先定义的验收条件 |
| 条件触发 | 进一步 tail 优化、native、并行或渲染解耦 | 目前没有证据要求架构重写 | 仅在前述验证暴露明确瓶颈，或明确新增更严格的短窗口/整帧要求后启动 |

## 执行注意

- 当前实验 recorder 容量为 20,000 帧。不要直接把 duration 改成一小时，
  也不要简单放大历史保留量后假设采样成本不变。先完成有界的长测采样方案
  和开销对照，再用于正式验证。不要为长测改变生产 profiler 的 5 秒窗口。
- 保留全部准入窗口内的慢帧。Chrome 是否运行应作为明确记录的环境条件；
  如需对照，应事先定义不同条件，不能事后因怀疑 Chrome 而删帧。
- GC 安全点行为也要记录，不能仅凭 realtime_defer 临界窗口表现推断长期
  无维护成本；RSS 变化本身也不能直接证明存活对象泄漏。
- P2 的额外变体不悄悄替换 canonical workload。发生失败时明确失败的条件
  和支持的结论范围。
- 合成 Agent 使用确定性等待和合法动作，不使用 10K 次真实 LLM 调用作为
  STAR 协议容量证明。跨主机发压时分别记录负载端与服务端资源。
- 性能测量期间不并发运行其他基准或重型测试。普通 CI 继续运行确定性
  功能/结构契约；机器性能 gate 在可比的测量环境中执行。
- P3 本地驱动与首轮空间查询优化已完成并归档；下一项是显式只读批次中的共享观测构建复用。P1/P2 不作为前置条件。
- 观测独立按1Hz/Agent基线，再测5/10/30Hz；决策思考延迟独立为1–60秒。所有容量结论附实际观测/动作频率。
- star-main 只用 squash merge；合并前 annotated tag 固定开发节点，Lab 记录合并前后精确 SHA。


## P3 首轮后的优先级

首轮生产优化已 squash 集成 `08c857e5df39f671c5a13bf04b9af9aac0800e78`，
[报告与原始包](../experiments/2026-09-p3-local-agents/README.md) 已保存。
1Hz下千Agent仍严重排队；关闭JSON编码也不足以达标。优先调查同快照的共享阵营观测复用，
先明确只读批次/写入失效边界，再讨论更快编码；不能通过丢请求、缩小Fog或用30s决策替代1Hz观测改变任务。
容量验证和整个P3保持未完成，不新增Frontier。
