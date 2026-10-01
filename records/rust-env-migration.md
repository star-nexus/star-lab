# Rust 内核＋Python 接口迁移

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


## 最新检查点：R4e，1000-Agent当前容量验证通过（2026-09-29）

最终生产 **`7e145d169433695cd4957e186a6b2fda06813c26`** / annotated **`rust-kernel-r4e-2026-09-29`**；测量实现仍 **`5147e4d8e0c33c997bd86960d87fa4b5b3ca90c5`**，API18原二进制，本轮生产仅文档。[完整正负结果与复现](../experiments/2026-09-rust-1000-agent-validation/README.md)。

进度：`世界内核 █ 已迁移 | 1000-Agent容量 █ 已通过 | System并行 ▒ 尚未全面实现 | 兼容/平台/发布 ▒ 待收尾`（阶段状态，不是工时百分比）。按用户要求暂停5000-Agent扩展。

Mac mini M4/16GB、5000Units/1000Agents、30Hz、约30秒闭环，1线程/8ms预算，Cocoa2480×1239、minimap单位层关闭、有限GC延迟、Chrome开启。三轮独立30秒预热＋300秒测量：整帧P99 **29.800 / 29.275 / 29.470ms**；观测响应P99 **45.872 / 47.783 / 44.798ms**；动作排队P99 **35.293 / 35.601 / 34.744ms**，均30Hz，所有guard通过。5000全部存活，实际同时移动峰值171/177/173；不包含Hub/真实LLM，不代表5000同时移动或高密度战斗。

原生产Python6a970dea与规范化Python5147e4d的同条件60秒短测均因排队失败。原Python→Rust平均观测service **7.822→2.741ms（约2.85倍）**；整帧P99 **31.800→26.453ms（降低16.8%）**。这是各一次实际闭环对照，接纳时间和状态轨迹不同，不是纯语言/同输入加速比；不能把排队减少34倍称为计算加速34倍。规范化Python对照及全部负结果同时归档。

4线程重放第三轮长测40994请求/9880tick/9880展示，响应、事件和最终状态一致；18Lab测试通过，raw全量指标重算一致。2217生产回归属于R4d历史证据，本轮未重复执行。无新增规则GAP，G008/G009/R001/R002继续开放。更新Frontier当前API18范围；未merge/push，默认Python/1线程，保留49处原删除。

公共信息共享在Python和Rust已有；当前Lab逐请求入口尚未接入跨请求批次。世界step仍显式顺序推进，System并行需要读写集、事件依赖及确定提交审计，见[专门说明](rust-system-parallel-status.md)。后续继续应用接入/兼容审计与平台发布；不盲目扩大5000-Agent压力或把保留Python的产品层视为遗漏迁移。


## 当前优先级调整（2026-09-28）

用户要求先验证 **5000 Units＋1000 Agents**，暂停5000-Agent扩展压力测试。下一阶段优先对最新版R4d/API18执行30Hz、约30秒闭环、30秒预热＋300秒测量×3，并补原生产Python同条件对照；不以跨历史窗口/调度/源码的数字拼出语言加速比。主要世界计算已经迁入Rust，但不代表System并行调度、应用接入、兼容审计和发布已全部完成。

公共观测共享在Python P3及Rust只读批次中均已存在；实际闭环跨请求共享仍有接入缺口。先核验1000-Agent容量与成本，System并行需明确组件/资源/事件的读写依赖及提交顺序，不能仅凭少import判断独立。5000-Agent旧证据保留，不继续其容量调参。历史计划（已由上方R4e完成）：上轮R4d短测/历史R4c长测结论仍各自绑定原版本。

## 最新检查点：R4d，Rust观测JSON直传与5000-Agent诊断（2026-09-27）

最终生产 **`72ea765bf3fc962fdea185d0311db2970ed422bd`** / annotated **`rust-kernel-r4d-2026-09-27`**；实现/测试/测量 **`5147e4d8e0c33c997bd86960d87fa4b5b3ca90c5`**，最终仅文档。[阶段报告、完整正负结果与复现](../experiments/2026-09-rust-5000-agents/README.md)。

进度：`世界内核 █ 已迁移 | 观测传递 █ 本轮优化 | 5000-Agent容量 ▒ 未通过 | 兼容/平台/发布 ▒ 待收尾`（阶段状态，不是工时百分比）。**新增Python `get_faction_state_json` 正式接口，直接传递Rust已编码观测，省去服务端decode/encode；原字典API、客户端完整decode、权限/规则/时钟/约30秒闭环不变。** 不将Python SDK/策略/UI重写Rust；网络host没有自动接入新路径，G009仍OPEN。

固定旧实际输入19929请求/2679tick/2679展示：传统边界平均3.223ms→直传1线程1.774ms（约省45%），4线程1.750ms；所有响应、事件、最终状态一致。新窗口12ms预算实际轨迹另以4线程重放31706请求/2676tick/2676展示，全部一致。新增22契约、2217完整Python回归、18Lab测试通过。Rust源码和二进制未改，复用API18/schema5/oracle及SHA `324454a00ab8bd3559c9229e6c6c9644242d65c488585eba7d29a63b39d29405`；本轮没有重复构建/Cargo测试。GAP台账记录接口兼容范围，无已确认新增玩法GAP；G008/G009/R001/R002继续开放。

**窗口诊断均30秒预热＋60秒测量，不是正式300秒×3验收。** M4、Chrome开启、5000Units存活、Cocoa2480×1239、Fog/canonical/minimap单位层关闭/有限GC延迟，native1线程。5000Agents每人1Unit；1000Agents约每人5Units。实际同时移动峰值68–172，不是5000同时移动。

- 1000Agents旧字典/8ms：整帧P99 **28.900ms**、观测 **121.462ms**、动作排队 **128.913ms**；帧通过但排队未过。
- 1000Agents直传/8ms：**27.385 / 40.641 / 32.818ms**，30Hz，全部短测guard通过。
- 5000Agents旧字典/8ms：帧26.354ms但观测排队约26.6秒、完成比例0.550；旧18ms预算仍失败，帧39.710ms/Hz28.517。
- 5000Agents直传/8ms：帧26.325ms、观测7.747秒、比例0.744；12ms预算：帧**33.124ms**、观测**1075.260ms**；14ms预算：帧**35.300ms**、观测**409.486ms**。12/14完成比例约1，但都未满足排队门槛；不能只看FPS或吞吐量。

**5000-Agent容量仍未通过，不更新Frontier。** R4c/API17三轮通过仍绑定原tag及2480×1243窗口；不能把本轮单次API18短测当作API回归或正式更新容量。全部慢帧、负结果、完整输入、raw/compact及成员hash保留，详见报告。原生产main仍6a970dea，未merge/push，49处原删除保留，默认Python/1线程。

完整新测量checkout：**`/Users/liyang/.codex/worktrees/rust-wire-observation/star-main`**，保持实现SHA和API18 wheel；旧 `runs/star-rust-integer-limit` 保持07bdb2e，不改写旧重放身份。窗口工具旧19c99a3/新4fcc2fa；固定流归因c9e15ac；末尾227a180仅保持Lab内部请求计数（不改变已测量的接口或调度），全部完整SHA在manifest。

**下一步优先：让已到达且连续的只读查询利用Rust现有批次的公共事实共享，减少每Agent重建；先固定输入验证，再完整窗口测量。** 不跨动作写入、不等未来请求凑批、不引入TTL/思考轮询；保持权限、顺序和批次实际返回延迟。5000-Agent初步守住所有短测门槛后再跑300秒×3；其后补高接触密度/24Hz/10000Units、兼容边界和平台安装矩阵。Python网络/BOT集成仍是独立应用接入工作。

以下保留历史；当前状态以上文为准。

## 最新检查点：R3d5，R4c后的数值兼容性补审（2026-09-27）

最终 **`257ebf11372fe82ed368bdbba2c3760a6450d110`** / annotated **`rust-kernel-r3d5-2026-09-27`**；实现/构建/测试 **`07bdb2e89c69959c2b8cb8e61329536c032f187e`**，最终仅文档。[阶段报告与复现](../experiments/2026-09-rust-integer-limit/README.md)。

进度：`R0 █ | R1 █ | R2/R3 ▒ 兼容性补审 | R4 ▒ 首关已过 | R5 ░`（阶段覆盖，不是工时百分比）。**发现并修复G014**：默认4300位限制下，超长十进制字符串首次上报保留，第二次累计旧Rust为3/Python为2（负号版本1/2），动作响应仍一致。20组公开入口前后审计，旧版4组完整状态不同，新版20组全部响应/权威状态一致。只在跨运行辅助检查中归零GameTime三个创建墙钟，配对完整状态比较不排除任何字段；raw保留全部原值。

Python仅在统计请求接纳时携带当前解释器限制，Rust执行转换；可信元数据不受Agent parameters覆盖。默认4300、640/5000及0关闭限制、修改设置、批次/reset、全部11个累计字段都有契约；不改Python原规则，不把统计转换移回Python。录制器记录请求的限制，4线程CLI重放恢复相同设置。

新增24契约，2195完整Python回归、177针对性、4Rust/fmt/Clippy、15Lab、旧6场景510节点通过。[GAP台账](../../star-main/docs/native-benchmark-gaps.md)永久保留G014历史反例并标记本范围CLOSED；R001其余输入边界、R002动态展示、G008/G009应用接入仍开放。

**API18/schema5**，oracle不变，扩展SHA **`324454a00ab8bd3559c9229e6c6c9644242d65c488585eba7d29a63b39d29405`**。生产venv及完整测量目录 **`runs/star-rust-integer-limit`** 已安装；该目录保持构建SHA便于重放，旧R4c/API17目录/wheel保留。main仍6a970dea、未merge/push、49原删除保留，默认Python/1线程不变。原始状态、日志、wheel和compact双包均有checksum；manifest含全部源码/tool身份。

**本轮没有重测容量**。R4c三轮5000Units/1000Agents、30Hz通过结果仍严格绑定原tag/API17，不改写成API18测量。下一步继续R001其他转换/错误边界、R002权威写入及实际消费者审计；按既定计划补高接触密度/24Hz/10000Units/独立5000Agents诊断与平台安装矩阵。Python网络、BOT策略、UI保留原边界。

以下保留历史；当前状态以上文为准。

## 最新检查点：R4c，Rust展示编码与真实窗口容量首关（2026-09-25）

最终 **`b05c1465e551072bced220ae12c2474ec7e81e85`** / annotated **`rust-kernel-r4c-2026-09-25`**；构建/测量 **`e85e3067b1d2aed5cf08be9dbe35b1deed91dba1`**，最终仅文档。[阶段报告与复现](../experiments/2026-09-rust-rendered-loop/README.md)。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ | R4 ▒ 首关容量通过 | R5 ░`（阶段覆盖，不是工时百分比）。Rust展示增量直接编码借用组件，省去中间JSON树；Python接口、绘制与规则不变。固定实际输入2000tick/9296请求：完整delta、字节长度、响应与最终状态相同；编码平均1.613→0.177ms，P99 2.349→0.434ms，Python解码未改善。2171完整回归、108针对性、14Lab、4Rust/fmt/Clippy和旧6场景510节点通过。

**本机M4、canonical窗口5000Units＋1000Agents、30Hz、约30秒闭环，30秒预热＋300秒测量×3全部guard通过。** 整帧P99 **32.479/32.613/32.405ms**；观测响应 **85.990/82.840/87.093ms**、动作排队 **94.090/93.040/94.272ms**，均30Hz。单线程内核，Lab每帧事件预算8ms；全程5000存活，同时移动峰值171/173/178。不是5000同时移动或5000Agents。窗口2480×1243、Fog开启、canonical minimap单位层关闭、有限测量内GC延迟维护、Chrome开启，Hub/LLM不计入。

旧版18ms预算短测和8ms预算300秒失败均保留（后者35.561ms）；所有慢帧保留，新版个别30秒块仍超33.33ms，不能外推无限时长或任意配置。第三轮实际轨迹4线程重放40741请求/9878tick/9878展示事件，响应及最终状态一致。仅首关性能通过，完整迁移/R5未完成，默认Python/1线程不变。

API17/schema5/oracle不变，扩展SHA **`8c74d05d89f1037c0157ad25e32ed4c6852bad7d316694cb056faa8c72f2d2e2`**。生产venv已安装；**`runs/star-rust-presentation-encoding`保持测量SHA**用于严格重放，旧`runs/star-rust-public-facts`及旧wheel保留。main仍6a970dea、未merge/push、49原删除保留。raw/compact双包、逐成员hash、commands/环境/全部工具SHA见报告；解包后可重算。

[GAP台账](../../star-main/docs/native-benchmark-gaps.md)无已确认新增玩法差异。**下一步优先：R001宽松输入转换边界与R002剩余权威写入/展示消费者审计；按计划补高接触密度、24Hz、10000Units和独立5000Agents诊断、平台wheel矩阵。** G008/G009作为Python应用接入保留，不把网络/BOT策略/UI重写Rust；满足剩余功能/安装要求后再考虑默认切换和squash merge。

以下保留历史；当前状态以上文为准。

## 最新检查点：R4b，公共事实直接编码（2026-09-25）

最终 **`90481f985bc66f30d8ed7627afe0ee37aec1aa75`** / annotated tag **`rust-kernel-r4b-2026-09-25`**；构建 **`290de0a7c7dde1255b3d7556552fc6acddac6fbe`**，测量/测试 **`94f7b0c41f88d9012600556b123552ced9d48b69`**（仅测试预期变化），最终仅文档。[阶段报告与复现](../experiments/2026-09-rust-public-facts/README.md)。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 内核补齐中 | R4 ▒ 并行与数据装配优化 | R5 ░`（非工时百分比）。公共敌军/地形直接编码，消除临时JSON树/深复制；同只读段跨阵营共享，字段/Fog/权限/顺序/写入边界不变。新增opt-in分段诊断，普通路径不读计时墙钟；不影响CD。Python继续保留SDK、策略、网络/ACK、UI和报告。

2171完整回归、89针对性、4Rust/fmt/Clippy、旧6场景510节点通过。54handler+30真实动作入口对照，完整响应/状态/字节长度/原工作计数相同（worker利用数可变）。5000Units/MP6单线程查询5Units中位19.189→2.547ms；100Units可信单请求23.899→6.439ms、8请求26.511→8.742ms。分段确认公共构建/释放减少。**查询微测不是30Hz整帧/排队/5000Agents容量验收。**

API17/schema5/oracle不变；扩展SHA **`90fe642f549c2d3a1bebc05e14e0db013f7a105959a2340afc2f7accc922c1f3`**，生产venv与 **`runs/star-rust-public-facts`** 已安装；旧API16及仅计时API17目录/wheel保留。main未动、未merge/push，49原删除保留，默认Python/1线程。工具/源码SHA、全部raw/compact、环境与checksum见报告。

[GAP台账](../../star-main/docs/native-benchmark-gaps.md)记录无已确认新增机制差异、zeroID测试预期修正和计时边界；G008/G009、R001/R002仍开放。**下一步回到完整合成Agent闭环容量诊断，核验新版Rust下世界/展示/排队预算；按证据处理剩余内核热点。** 首关5000Units+1000Agents/30Hz、5000Agents扩展未验收；Python集成可单列，不把其代码重写当Rust迁移。

以下保留历史；当前状态以上文为准。

## 最新检查点：R4a，只读Unit面板真并行（2026-09-25）

最终 **`45bd11cca09a88fb4c757feecc234a4efe932dae`** / annotated tag **`rust-kernel-r4a-2026-09-25`**；实现/构建/测量 **`ddb084e42e07fdb359c511b8727f888ff3a5a38b`**，最终仅文档变化。[阶段报告与复现](../experiments/2026-09-rust-read-parallel/README.md)。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 内核补齐中 | R4 ▒ 只读并行首版 | R5 ░`（非工时百分比）。2/4配置现已使用固定线程池，在同一稳定只读段计算缺失Unit面板；按输入序合并、写前join、reset复用、close释放。世界/权限/公共投影/最终输出仍串行，默认Python/1线程不变。Python保留SDK、策略、网络/ACK、UI与报告。

2165完整回归、83针对性、4Rust/fmt/Clippy、旧6场景510节点通过；30案例×旧单线程/新1/2/4共120组完整Agent响应/初始最终状态/原工作计数一致。MP6留空格诊断保持5000存活Units、返回966可达格；单请求1/2/4中位25.0/20.9/21.3ms，小查询有回退。1预热+5样本、仅查询+编码，**不是30Hz/排队/5000Agents容量结论**。

API16/schema5/oracle不变；扩展SHA **`353320733d25979d2213d70d9fc08ed933a2b1b5c5c079199e85e42633fa2141`**，生产venv与完整目录 **`runs/star-rust-read-parallel`** 已安装。旧API15目录保留；main仍6a970dea、未merge/push、49处原删除未动。完整raw/compact/命令/toolSHA/环境/checksum见报告。

[GAP台账](../../star-main/docs/native-benchmark-gaps.md)无已确认新增规则差异；[状态边界审计](../../star-main/docs/native-state-boundaries.md)明确typed权威数据与Python派生展示。G008/G009及R001/R002仍开放。下一步拆分公共投影/面板调度/最终编码成本，扩展实际Agent子集负载，再做30Hz完整闭环验收；不把Python应用层重写当Rust迁移。首关5000Units+1000Agents与5000Agents扩展均未验收。

以下保留历史；当前状态以上文为准。

## 最新检查点：R3k4，Rust只读批次编码共享（2026-09-24）

**当前范围仍是Rust高效执行世界**；Python保留SDK、策略、网络/ACK、UI与报告。最终 **`3892f95af6638e213f1b842fd9c0fe4b7b3dab80`** / annotated tag **`rust-kernel-r3k4-2026-09-24`**；实现/构建/测量 **`f37ae76785f05dd9dc9ac3009731267117bbda90`**，最终仅文档变化。[完整阶段报告](../experiments/2026-09-rust-kernel-encoded/README.md)。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 内核补齐中 | R4 ░ | R5 ░`（非工时百分比）。同只读段阵营公共字段和Unit基础面板各编码一次、不可变共享，每请求分别捕获owner/commandable；单动作/可信批次/probe均接入。写入结束共享段，旧响应保留旧事实；无TTL、字段删减或新增线程。

2156完整回归（新增12）、74针对性、3Rust/fmt/Clippy、旧6场景510节点通过。15组Agent完整响应、初始/最终状态hash、旧计数一致；四个新增编码/引用计数仅诊断。5000Units/100Unit查询：public8请求88.366→23.552ms，single27.639→21.531ms；编码1阵营/100面板、引用8/800，仍完整约6.04MB。每项1预热+5样本，仅native处理和编码，**不含世界/绘制/排队，不是30Hz容量验收**。

API15/schema5、oracle不变；扩展SHA **`62451b1ee2844373f162e1489d40684894febbc0e8efc27167046f1c18363206`**，生产venv与完整目录 **`runs/star-rust-kernel-encoded`** 已安装。旧R3k3/API14目录/wheel保留，main仍6a970dea、未merge/push、Python默认，49处原删除未动。

[GAP台账](../../star-main/docs/native-benchmark-gaps.md)记录无已确认新增机制差异及生命周期证据；G008/G009/R001/R002仍开放。下一步继续权威状态写入/派生覆盖审计，明确只读任务输入/生命周期后推进R4真并行，不把Python上层重写Rust。5000Units+1000Agents/30Hz首关与5000Agents扩展尚未验收。

工具Lab **`c34682448d033d62c92a65e5b468cac3f5b1790a`**，原始证据/命令/环境/canonical引用/checksum均在阶段报告。以下保留历史，当前状态以上文为准。

## 最新检查点：R3k3，Rust观测JSON装配（2026-09-24）

**仍只推进Rust高效执行世界的部分**，Python保留SDK、策略、网络/ACK、UI和报告。最终 **`a3ff47b796537e2a543d42da6094aa13d64f6e63`** / annotated tag **`rust-kernel-r3k3-2026-09-24`**；实现/构建/测量 **`450bf97db4c52ead5d5ab36eda5a035a33ee4158`**，最终仅文档变化。[阶段报告与复现](../experiments/2026-09-rust-kernel-assembly/README.md)。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 内核补齐中 | R4 ░ | R5 ░`（非工时百分比）。将已拥有的观测数组/批次结果直接装入外层JSON，消除重复serialize-to-Value；必要的共享事实独立副本仍保留。无跨帧缓存、信息简化、规则变更或新并行。

2144完整回归、62针对性、3Rust/fmt/Clippy、旧6场景510节点通过；12组前后完整响应/计数/长度与初始最终状态hash一致，public批次另与逐条执行比对。5000Units/100己方Unit查询：public单请求中位52.232→30.815ms，8请求173.365→95.241ms；关闭Fog地形8请求100.544→54.464ms。每项1预热+5样本，只计native查询/批次与编码，**不是30Hz整体容量结论**；8请求大载荷仍超单帧预算。

兼容API14/schema5，规则不变；新扩展SHA **`a36e0684f4e76b7b4036e6ca20b217d1f5a78dda11929f7a9a714afd090a7c74`**，不能单靠API14区分本次性能实现。生产venv与完整目录 **`runs/star-rust-kernel-assembly`** 已安装，旧R3k2目录保持原样。main仍6a970dea，未merge/push，Python默认，49处原删除保留。

[GAP台账](../../star-main/docs/native-benchmark-gaps.md)追加本轮无已确认新增机制差异及验证边界；G008/G009/R001/R002不自动关闭。下一步拆分剩余公共事实复制/编码成本，核验稳定只读上下文的响应表示与生命周期，继续权威状态写入审计后推进R4真并行；Pythonhost/BOT策略不当作Rust重写任务。5000Units+1000Agents首关与5000Agents扩展均未验收。

工具Lab **`864f01ad2764aa387b3b472a096e3572cd070911`**；完整raw、commands、环境、canonical引用和checksum见报告。下方历史记录保留，当前状态以上文为准。

## 最新检查点：R3k2，Rust公共观测索引（2026-09-24）

**当前范围只迁移Rust负责高效执行世界的部分。** Python保留SDK、策略、网络/ACK、UI和报告；下方旧“先接网络host”优先级已被覆盖。

最终 **`67e35deaacef22ed1754f39245d771c3af887888`** / annotated tag **`rust-kernel-r3k2-2026-09-24`**；实现/构建/测量 **`0e912d85c18027e77125fd770500bdd123c30d75`**，最终只改文档。[完整阶段报告](../experiments/2026-09-rust-kernel-catalog/README.md)。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 内核补齐中 | R4 ░ | R5 ░`（非工时百分比）。Unit索引减少地块/特效扫描，Fog地形按较小集合精确投影；死亡/reset/特效销毁同步成员。不改规则、不跨帧缓存，尚无真并行。

2144完整回归（新增32）、165针对性、3Rust/fmt/Clippy和旧6场景510节点通过。100Units、5Unit查询、6211/60919地块×3种Fog共6组初始状态和完整响应相同；小地图3组另对照Python。大地图局部7格视野中位1.224→0.125ms，空视野0.842→0.084ms；关闭Fog294.697→296.953ms负对照保留。每组1预热+5样本，仅native查询+编码，**不是30Hz整帧/Agent容量结论**。

API14/schema5，扩展SHA `8358eecb5adfd2b7de7b020003aafa546280926bb7c9e4fa3e7e42f2f99fe02d`；生产venv及完整目录 **`runs/star-rust-kernel-catalog`** 已安装。旧API13目录保持原样；49处原删除保留，main仍6a970dea，未merge/push，Python默认。

[GAP台账](../../star-main/docs/native-benchmark-gaps.md)记录本轮无已确认新增机制差异及索引生命周期责任；G008/G009仍为Python应用集成事项，R001/R002未笼统关闭。下一步审计Rust公共数据装配/编码/批次边界及权威状态写入，随后再推进R4只读并行。5000Units+1000Agents/30Hz首关和5000Agents扩展均未验收。复现工具Lab `b395de44a4c08cbf08841195a5fd5f49dea0f5d7`，raw/compact/commands/环境/checksum见报告。

以下历史记录保留，当前状态以上文为准。

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


更新：2026-09-14。用户已批准完整迁移方案。状态：R0/R1 已完成；R2规则模式闭环已验证；R3a/b/c检查点已固定，战场展示增量已接，完整GameScene/输入等仍待迁移；Rust尚不可运行完整游戏。

## 固定节点与边界

- 起始生产 main：`6a970deaee7d9b8d3939edd102973f2377edd6ac`。
- 开发分支：`codex/rust-env-migration`；起始 annotated tag：`rust-migration-origin-2026-09-11`。
- 并行观测 v1 分支及负结果保留；不继承其逐查询完整快照进程池实现。
- 四层架构保留。Rust 持有权威世界与模拟计算；Python 保留加载、界面、协议、Agent。Protocol/Hub 性能与真实 LLM 暂缓。
- 移动力弱化不在本次迁移修改范围。默认后端在全部验收通过前仍为 Python。

## 用户已确认的决策

1. 完整实时／回合制、窗口／dummy／规则模式分阶段迁移。
2. 先规范 Python 无序容器引起的顺序，再冻结新 oracle；Rust 与该基线严格重放一致。旧实验用原 tag 复现。
3. 保留域种子、CPython 随机算法、f64、取整、动作/事件顺序；权威状态、事件与解码响应含列表顺序一致。
4. Rust＋独立 bevy_ecs＋PyO3＋maturin；三个 crate；运行计算释放 GIL，无逐 Unit Python 回调。计划锁定版本须由实际发行源验证。
5. 单写、只读阶段、1/2/4线程。缓存仅在无写入批次共享；不增加思考期轮询或过期观测。
6. macOS ARM64、Linux x86_64/ARM64；普通 CPython 3.13/3.14 安装验证。
7. 验收后 Rust 默认；Python 冻结作对照/回退，不长期重复开发双内核。

## 阶段与状态

| 阶段 | 交付 | 状态 |
| --- | --- | --- |
| R0 | 明确有序遍历、响应与事件顺序；Lab 重放/差分；完整回归；annotated oracle tag | 已完成 |
| R1 | 工具链、三个 crate、稳定实体 ID、场景导入、生命周期、时钟和随机兼容 | 已完成 |
| R2 | 实时 move/attack/观测、恢复/Fog/死亡/认领权限闭环 | 规则模式闭环和窗口战斗内核已验证；完整应用接入依赖R3 |
| R3 | 回合、完整当前玩法、BOT/结算、Python 窗口增量展示 | R3a回合/动作、R3b观测、R3c战场展示已固定；输入/场景/HUD/VLM/BOT/结算待补 |
| R4 | 等价基础上的并行、活动集合、数据维护与调度成本对照 | 未开始 |
| R5 | 容量、平台安装、tag/squash、默认切换 | 未开始 |

## 验收

本机 M4，5000 Units/1000 Agents/30Hz；Agent 初次 uniform(0,30秒)，每轮观测→逐 Unit move/attack/wait=50/25/25（非法等待、不重抽）→截断 N(30,5²) 墙钟等待15–45秒。期间不轮询。
60秒诊断后，30秒预热＋300秒测量独立3次。每次 frame work P99≤33.33ms、世界≥29.7Hz、观测/动作排队≤100ms，并保留原响应/期末积压/完成率/存活 guard。包含接入、模拟、Python展示及present，不含主动限帧等待。Chrome保留，性能实验串行，无删慢帧。
另报24Hz、高接触负对照、10K扩展。未通过不得默认切换或登记容量通过。

## 记录方式

生产代码、契约测试、用户文档在 star-main；驱动/重放/性能工具及 raw/compact 在 Lab。每阶段记录精确源码/工具 SHA、环境、命令、结果和 checksum，更新恢复入口。所有 main 集成只允许预先 annotated tag 固定节点后的 squash merge。

## 本轮开始

两个仓库起始干净，已创建分支及起始tag。正在安装计划指定 Rust 工具链并实现有界有序查询缓存。没有执行新的性能测量或发布。

## R0 已完成

生产 `78cc8da3a03ffedaea58642abae8fcb710db997d`，annotated oracle tag `rust-python-oracle-r0-2026-09-11`；919项生产回归通过。Lab工具 `85c7dc8d9406e22761390eadbf80f3edbec0b873`；两种模式×三种display配置、150ticks，跨hashseed重放状态/事件/完整响应一致。窗口配置使用SDL dummy，不是视觉或容量验收。原版VisibilityTracker无序列表差异已归档。见[报告与复现](../experiments/2026-09-rust-r0/README.md)。Rust 1.98.1 已安装，下一步实现R1三个crate、初始化导入与CPython随机兼容。

## R1 已完成

生产 `92a6812beeaee71f4dd3650f5e7cc30f808c7895`，tag `rust-runtime-r1-2026-09-11`；952项Python回归（33 native契约）、2项Rust测试和Clippy通过。release macOS ARM64 CPython3.13 wheel及全量差分raw已[归档](../experiments/2026-09-rust-r1/README.md)。20组种子/域×1400混合抽样与完整MT状态一致；时钟、reset/close/GIL通过。Linux/3.14未验收。Native只具备初始化、冷数据保留、时钟及随机兼容，gameplay_ready=false；没有容量结论。

当前R2从typed组件、六边形路径/占用与移动开始，随后战斗/恢复/Fog/权限/完整观测。活动checkout检测到非本轮字体文件删除，未纳入提交或覆盖；已询问用户。正式R1验收用Lab干净detached checkout，资源完整。

## R2 中间检查点：移动、恢复、规则模式战斗

生产 `d1f5838496b38b97907d31cd0439d3dae53b0eb4`，annotated tag `rust-kernel-r2a-2026-09-11`；工具 `7af8e4cecb463d294c73fd05f1b7898c840bdd5b`。
1032项完整回归（113 native契约）、3项Rust测试及Clippy通过。三种display×两种seed的360个低层操作节点，完整导入状态/结果/事件等价；见[检查点报告](../experiments/2026-09-rust-r2-kernel/README.md)。
已迁移动态占用、A*平局、MP规则、即时/逐格移动、AP/MP/skill到期队列及规则模式伤害/暴击/死亡。枚举/字符串状态区别及正在计时的恢复队列被完整保留。
**R2未完成**：正常统计订阅、Fog、注册/认领权限、完整观测/动作入口仍未接入；窗口战斗特效实体/ID仍待迁移。私有probe不是Agent接口；Rust尚不可运行完整游戏，无容量结论。
下一步接入Fog和统计，再完成可信身份动作/观测边界、逐操作完整世界重放与小规模闭环。
活动checkout又出现非本轮 `rotk_agent/*` 删除，已询问用户，全部保留、未提交。正式R2检查点验收使用干净Lab detached checkout `runs/star-rust-r2-kernel`，不用缺失文件的活动目录作完整回归证据。

## R2b 中间检查点：Fog与统计（2026-09-12）

生产 `062141d97fd6c8122c93e3dd1bc0b94736442e1e`，tag `rust-kernel-r2b-2026-09-12`；工具 `6650a423be711878e480d50a0b9fd69b6d0f9ad9`。
1046完整回归（127 native契约）、3Rust测试/Clippy、284操作节点的完整导入状态/响应/事件等价通过；[报告](../experiments/2026-09-rust-r2-vision-stats/README.md)。
Fog保留各Unit贡献、阵营union/探索、LOS、LRU、dirty；统计保留战斗/移动记录、普通/窗口差异和采样中途reset。bootstrap新增public附加字段支持；注册映射原本就是dataclass声明字段，并不存在旧codec丢失注册字段的问题（此前说明已更正）。所有数据Rust持有，墙钟只是统计元数据，CD仍用模拟时间。
仍缺可信Agent接口、完整观测/权限、Realtime/Turn生命周期、战斗窗口实体与Fog展示增量。R2未完成、尚不可完整游戏、无性能结论。下一步完成注册/认领和观测/动作边界，再全世界重放及合成Agent闭环。现存无关Agent/font删除未提交；正式checkout在`runs/star-rust-r2-vision-stats`。没有main合并、推送或默认切换。

## R0b补充规范化（2026-09-12）

迁移完整观测时发现R0漏掉多技能set输出排序，已独立修正并归档旧版反例：新oracle `17b17766923ce4db05efb17aaf023818cf69cdf6` / `rust-python-oracle-r0b-2026-09-12`，1047完整回归通过。[证据/复现](../experiments/2026-09-rust-r0b-skill-order/README.md)。旧R0/早期重放保留，不能再描述成覆盖全部可选多技能状态。后续native规则标识改为`python-r0b-17b1776`，显式拒绝混用旧版扩展。

活动R2c代码已加入typed TeamCoordination（认领反向索引/原队列maxlen）、只读批次 faction projection，并通过28项新增契约。尚未完成正式身份认证/注册分发与完整Agent闭环；私有probe不能接Agent。目前仍在开发，待完整回归和差分trace归档后固定检查点。

## R2c检查点：team与只读批次观测（2026-09-12）

生产`582dbdab6e7b060c2589096cd41bc45ee96a474f` / `rust-kernel-r2c-2026-09-12`；工具`f02fef40c5eb2b361ab2908f5b7eac8fca5c87af`。完整回归1075（155native）、3Rust/Clippy、252查询/60操作节点等价及复用guard通过。[报告](../experiments/2026-09-rust-r2-projection/README.md)。
Typed Team维护认领反向索引，保留冲突/强转/FIFO/maxlen；ObservationBatch用Rust只读借用限制缓存生命周期，复用census/faction/panel/enemy/tile，按请求装配owner/commandable。保持unit_ids语义、Fog、reachable/attackable，reset/写后查询不沿用旧批次。当前仍会clone响应树、扫描部分候选，留给R4测量优化。
**尚未接正式Agent**：注册/可信身份校验/ActionExecutor完整分发仍缺，私有probe不能用于容量测试。下一步迁移注册、认证和动作外层返回格式，并把已有投影接入；再补Realtime/Turn生命周期、窗口战斗实体/Fog展示日志，跑完整世界差分和合成闭环。R2、R3–R5仍未完成；默认Python/main不变。正式checkout `runs/star-rust-r2-projection`，无关49个删除继续保留未提交。

## R2d检查点：可信请求与批次入口（2026-09-12）

生产 `02ac380d631b7391bdf0f583084aee8d13d5de0a` / `rust-kernel-r2d-2026-09-12`；工具 `d762bd1f06298a59776a554c93d3b49e3fe9a2f2`。1115完整回归（195native）、3Rust/Clippy、18配置/678请求节点差分通过；294查询、114只读段复用与权限guard通过。[报告/raw/compact/复现](../experiments/2026-09-rust-r2-actions/README.md)。

公开 `RustRuntime.execute_action/execute_actions/get_faction_state` 已接本地可信身份、注册/认领/FIFO、move/attack/查询及计数；JSON入口元数据由Python准备，Rust不回调Python。连续Faction查询共享只读借用，遇到任何其他请求结束；计数在独占锁内按序提交。验证了写入中途失败后的查询和reset身份失效。1/2/4配置结果一致，但尚无worker并行。

**完整R2仍未完成，Rust尚不可运行完整游戏**。本轮是3Unit小场景、无world ticks/真实窗口/Hub/LLM的可信本地请求验证，不能作5000/1000/30Hz容量结论；dummy/window不执行attack。下一步Realtime/Turn生命周期与完整World.update重放，再合成Agent闭环及R3展示。异常非字符串阵营、极大整数等历史边界仍待覆盖。Python默认/main未变，无merge/push；无关49个删除保留。正式checkout `runs/star-rust-r2-actions`。

## R2e检查点：世界生命周期与5000/1000规则模式闭环（2026-09-12）

生产 `2c83c001780ddf103b94905df81e8a1bc469af6e` / `rust-kernel-r2e-2026-09-12`。1152完整回归（232native）、3Rust/Clippy；394小场景操作/360核心World.update ticks的状态、响应、有序事件差分通过。[报告/raw/compact/复现](../experiments/2026-09-rust-r2-lifecycle/README.md)。存活阵营计数随死亡维护，胜负检查O(阵营数)，保留全灭优先、模拟时间超时、窗口缺位置例外、enabled与回合时钟同步。

5000Units/1000合成Agent真实注册认领后的60秒规则模式闭环跑通：2007轮，4017接受move、64attack、63拒绝move，5000全部存活、每Agent至少1轮。初始化Python世界已销毁，所有交互与tick走native。8151请求＋1779ticks逐响应digest/事件/最终状态重放一致；这不是5000规模Python差分。

**无窗口规则模式诊断，不是完整实时性验收**：move即时完成、无绘制，带逐响应hash开销且无预热排除。循环P99=41.93ms、世界29.635Hz、观测119.21ms、动作排队120.65ms；严格数值门槛已越线，无容量认证。不能写成5000持续同时移动或窗口30Hz达标。60秒raw完整保留，未进入300秒性能验收。

接下来补回合handoff/reset、R3余下动作/BOT/结算与真实窗口（攻击特效实体/Fog增量），继续扩展兼容覆盖；R4并行优化和R5平台/容量/切换仍未完成。Python默认、生产main未变；无merge/push，无关49个删除不动。正式checkout `runs/star-rust-r2-lifecycle`。工具probe/loop `db3400a09b1681559ac8aaf05652595d681d9d9c`，replay `d208e3ebffa2c38514cf1b683df66b0beec6cf65`。

## R3活动开发：回合交接与接口版本（2026-09-12）

已开始回合handoff/reset和统计顺序迁移：Agent只在round回到首阵营时重置，人工end-turn保持先重置再判胜负；TurnStartEvent/回合日志/时钟下一tick同步已接。14项新增契约和246项Native测试通过，**尚未做R3完整回归/tag/正式trace归档**。Player查找使用初始化/reset派生表，不逐动作扫描全部实体。API版本2/scene schema2显式拒绝旧R2扩展或旧scene被误用于新适配层；旧实验仍使用其固定source/wheel。补充了CPython3.13浮点sum补偿规则以保持回合时长统计一致（核对官方v3.13.12源码）。
后续继续rest/occupy/fortify/skill、其他观测、BOT/结算与真实窗口，不宣称完整R3或容量完成。

## R3a检查点：回合、剩余Unit动作与领地（2026-09-13）

生产 `7f4ad57bbd6966748c0fb49deb82f6ad43fc7aee` / annotated tag `rust-kernel-r3a-2026-09-13`；包含前期turn提交 `e3da7a072f35b76246d596660107abc37107cf11`。Lab probe/replay工具 `cb336f40a973050c2fb5eba7ec886f779042577d`。[报告/raw/compact/复现](../experiments/2026-09-rust-r3-actions/README.md)。

1298完整回归（378Native契约；新增14turn+132unit/territory）、3Rust/Clippy通过。27配置1524不同节点（762ticks）完整状态/响应/事件差分通过；归档轨迹重新执行全部1524节点一致，1/2/4配置一致但尚无worker并行。正式完整checkout `runs/star-rust-r3-actions`。

已接rest、occupy、fortify、skill既有验证与返回；Framework计时start_capture与Agent即时occupy分开，活动集合O(active)，领地攻防加成进入战斗。回合轮转、人机重置顺序、统计事件沿用oracle。保留原技能success/result字段不匹配导致技能失败、实时工事检查但不扣资源、响应AP额外减1、捕获Unit消失时tile标记残留等历史行为；不把修复这些规则问题混入迁移。

API/scene现为3（e3中间版本为2，R2为1），显式拒绝旧扩展/旧scene混用。活动 `.venv` 已安装本检查点归档release wheel，extension SHA256 `987b450aa0d8df55170fe726d994a5372e76bb3e6978becc58dcea2e2049a7c3`。raw SHA256 `c465b36fc798d61368307f1f8ceb1c708e3038b73e529fcd714ad299a07c4358`，12项artifact校验通过。

**完整R3与容量验收仍未完成**：无真正绘制，display是行为配置，攻击只在none测；未运行本版5000规模，不更新Frontier。下一步补其他观测变体、窗口战斗/特效实体ID与Fog展示增量、输入命令，再BOT/结算及各入口，之后R4并行和R5正式容量/平台验证。Python默认，main仍6a970dea，无merge/push；无关49个Agent/font删除原样保留。

### R0c 补充（2026-09-13，R3b 开发前）

生产 `3cc4ffea091dcf6afa8691c217ec4b09e25d4b5f` / `rust-python-oracle-r0c-2026-09-13`，1299 完整回归。旧 `observation.visible_environment` 与 named `unit_observation.visible_terrain` 未按坐标排序；本次只补排序，不改变内容或 visible_area 的 Python set 类型。前后反例在 `experiments/2026-09-rust-r3-observations`，该实验仍在进行。后续 Rust 对照此规范化基线；旧 tag/wheel 不动。

### R3b 已固定：非图像观测（2026-09-13）

生产 `d5abc70e9cda8a6820546112e6172dd9e43c1515` / `rust-kernel-r3b-2026-09-13`；[完整报告](../experiments/2026-09-rust-r3-observations/README.md)。1443 全回归、522 Native（新增144）、3 Rust/Clippy；54 配置4203节点/702 ticks 差分及精确重放通过。工具 `f10dd87452b771f70e15af19d38a2299f4a9532c`。Raw SHA `d62735a1aee16c785bac29e1e14f326d7cf06134028747d62c750408cc6781f3`，22833971bytes。

五个非图像观测已接：observation/unit/faction/limited/godview。缓存只在同 revision 共享，导入有效缓存以保留时间/from_cache；同一份 Unit 基础信息构造供 get_faction_state 和旧观测使用。保留 godview 非空 BattleLog 的旧属性错误及各查询历史语义。API/schema=4，oracle `python-r0c-3cc4ffe`；活动 venv 已安装归档 release wheel。旧 tag/wheel 原样保留。

下一步：真实窗口战斗与展示增量/输入、VLM、BOT/结算。R3 尚未全部完成，1/2/4 仍串行，R4/R5 和新容量结论均未完成。正式 checkout `runs/star-rust-r3-observations`；main仍 `6a970deaee7d9b8d3939edd102973f2377edd6ac`；无关49处Agent/font删除保持不动。未合并或切默认。

[阶段地图](visuals/rust-migration-map-2026-09-13/map.html) 是此前 R3a 的冻结状态图；以本文最新节点恢复。

### R3c 历史开发记录（2026-09-13，已由下节固定节点取代）

R3b 归档提交 `36ca087` 后继续窗口接入。当前生产工作区正开发 `native/rotk/src/presentation.rs`：按旧顺序管理攻击动画、飞行箭矢、特效、飘字的生命周期/实体ID，并输出变更行；Python `visual_projection.py` 复用旧动画数学作派生展示。`presentation_state.py` 导入最小生命周期，API/schema 暂升5（活动venv已装对应开发wheel，旧R3b正式wheel保留）。61新增检查（含Framework ID契约）、582 native契约通过；尚未全回归/归档/真实窗口可玩。下一项为资源/场景/Fog展示增量与窗口消费者/输入。源码仍有49处无关删除，勿动。


## R3c检查点：战斗展示生命周期与派生窗口（2026-09-14）

生产 `5bda51db6cd68455aa5724a6ef0eca1e66f89dda` / `rust-kernel-r3c-2026-09-14`；
[完整证据和可执行复现](../experiments/2026-09-rust-r3-presentation/README.md)。1504完整回归（582 native）、
3Rust/Clippy/fmt；144配置5184节点 = 864请求+4032ticks+288reset，完整状态/响应/事件差分和
含展示增量的独立精确重放通过。采集工具1743d0effd96365fdfb5bf55c4486ef8e5cc82c2。
真实Cocoa1200×800、Chrome开启：两种mode×近远程×选中/普通视图960帧、24PNG；
普通视图工具079c99a73f18a7a4cae1e0a37cb1a2ae51be5610。所有帧渲染前后Rust权威状态不变。

权威临时视觉ID、弹道出生帧及计时移入Rust；Python只计算插值/旋转/相机、字体与Surface。
单位资源、领地与Fog按变化累计，多个tick后消费不会漏状态；小场景状态随delta返回。
WorldPresentation同步派生World/空间索引/Fog日志，拒绝旧epoch/revision；窗口AnimationSystem只投影相机。
仍未接完整GameScene/输入/HUD/VLM/BOT/结算，尚无可玩Rust默认入口或新容量认证。

API/schema=5、oracle=python-r0c-3cc4ffe。正式工作树 runs/star-rust-r3-presentation，
活动star-main venv同步安装归档release wheel，扩展SHA a60b227d02e47998762c735a047e10a90a225fb8b78727b41afcc0d68c1d3f89。
45个归档artifact校验通过；完整raw为194433027bytes JSON，无损XZ 189416bytes，
SHA 52fdfb03ceb4506d30d5d161b5f5cb92421298c345ab256fcae905b80d5141a5；可恢复原gzip相同SHA。
没有删节点/抽样；compact和packing记录完整身份。main仍6a970dea，49无关删除未触碰，无merge/default切换。

下一步直接R3d：把应用场景与输入接到明确命令边界，完整HUD/VLM，再处理BOT/结算与场景reset。
R4只读并行/热路径成本、R5容量和平台安装尚待；1/2/4线程设置仍为串行Mutex。
