# 10K / 100% moving / 30 Hz — 恢复入口

## 独立Rust并行任务恢复入口（2026-09-30）

当前新任务见 [rust-ecs-parallel.md](rust-ecs-parallel.md)，工作树
`/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main`，分支 `codex/rust-ecs-parallel`，
从R4e annotated tag创建。P0完成读写依赖表及可关闭逐System计时探针；归因与冻结输入1/2/4线程核验已通过，checkpoint c058d75 / annotated rust-parallel-p0-attribution-2026-09-30。首个实际优化候选为已接纳连续查询的编码批次；先审计接纳顺序，尚未实施收益。
进度：`恢复 █ | 依赖表 █ | 归因 █ | 并行实现 ░ | 容量 ░`。
目标仍5000Units/1000Agents，5000Agents暂缓。原49删除、两个冻结测量目录和历史负结果保留。
此任务当前状态优先于下方旧“下一步”；没有新的容量/发布或默认切换结论。


新Session开展Rust并行工作，先读[专门交接入口](rust-parallel-handoff.md)（2026-09-30，含设计演变、负结果、代码/测试入口和冻结起点）。

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

更新：2026-09-23。当前阶段：P0 已完成；跳过 P1/P2；P3 第二轮只读批次共享已集成；主目标恢复闭环Agent，用户接受24Hz大规模运行，详见最新确认。
本文件是唯一活动恢复入口，已从 STAR 的 `docs/dev/` 迁至 STAR Lab。
先读本文件即可恢复目标、边界和下一步；执行时再按下方链接读取对应证据。

## 当前实施：Rust 内核＋Python 接口迁移（2026-09-11）

## 当前检查点与下一步（2026-09-23）

**R3d2b 已固定。** 生产 `a6bf5f381b0393b0ab93973502d9744d6b9e3713` / annotated tag `rust-kernel-r3d2b-2026-09-23`。[报告、试玩与复现](../experiments/2026-09-rust-r3-host/README.md)。离线 GameScene/菜单/CLI 已接 Rust；三种统计/状态系统动作、结束通知计划、一次权威快照结算及JSON/CSV保存通过验证。仍保留现有60墙钟秒结算等待；HUD小表不充当完整结算来源。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 功能迁移中 | R4 ░ | R5 ░`（█完成、▒进行中、░待实施/验收；不是工时百分比）。**每次阶段报告继续附此进度条。**

1738完整回归（816 Native、79新契约）、3Rust/Clippy/fmt通过。六场景237更新（158窗口配置、79同Cocoa引擎中的headless配置），510节点及6初始快照精确重放，新进程重放再次通过；4真实CLI进程52帧覆盖dummy/Cocoa与两种模式，退出后世界关闭。6JSON/6CSV、4截图已归档；合成SDL和直接菜单回调，不宣称物理输入验收或新容量结果。初版Lab记录器遗漏None墙钟值已修正，故障注入复现指向UnitObservation.last_seen_time，旧有效部分日志单列intermediate。

活动venv已安装该节点API8/schema5 release wheel，扩展SHA `f9e7169fab2f2f154baf582d5578201a9fc3a0dfb868f7cc0f72cb3851baf46c`。完整试玩/验证checkout为 `runs/star-rust-r3-host`，旧R3d2a/API7及所有历史tag/checkouts保留。生产原有49处Agent/font删除未修改，main仍 `6a970deaee7d9b8d3939edd102973f2377edd6ac`，无merge/push。

**下一步：R3d3，完善应用侧边界。** 先审查动态Player/其他冷组件的展示同步及VLM帧获取，再接网络host（可信身份/连接数、回合ACK、结束通知/重试）与BOT；完成完整应用行为对照后进入R4真实并行/成本优化，R5容量/安装。Rust当前仅支持离线，Hub/BOT/旧scale harness明确拒绝；普通启动默认Python，1/2/4仍串行Mutex。没有5000/1000/30Hz通过结论。移动力弱化等玩法保持不变，后续Agent仍为墙钟30秒闭环且思考期不轮询。

本机试玩：在 `runs/star-rust-r3-host` 执行 `.venv/bin/python -m rotk_env.main --backend rust --no-hub --skip-start --mode real_time --scenario chibi-small --seed 42`。无BOT时AI槽不自行行动；双方Human可在离线菜单配置。

## 此前检查点：R3d2a（历史安装状态）

**当前节点：R3d2a 已固定（2026-09-22）。** 生产 `91dc7688601c93192fea174c69981a315ac80ef9` / annotated tag `rust-kernel-r3d2a-2026-09-22`。[报告/复现](../experiments/2026-09-rust-r3-session/README.md)。完成 `NativeSession` 离线生命周期、初始化/输入异常与订阅清理、纯展示系统挂接；Rust提供HUD阵营小表及战报首批/追加增量。1659完整回归（737 Native、41新契约）、3Rust/Clippy/fmt通过；标准小场景真实Cocoa6配置540帧、558操作节点及新进程独立重放通过。0/10000条历史的HUD结构大小相同，仅是结构验证，**没有容量结论**。

活动 `.venv` 已安装该节点 API7/schema5 release wheel，扩展SHA `d95330879ebd9427233e8aade3bb075233fbd52ca741d197086e0ce0a01627e3`；完整checkout `runs/star-rust-r3-session`，wheel/raw/compact/6PNG和21项checksum在报告目录。旧R3d1 API6归档及checkout不变。生产仅剩原有49处Agent/font删除，未纳入提交。

**下一步：R3d2b，GameScene/菜单/CLI后端选择与host生命周期。** 先补齐结束后通知/统计输入和权威结算数据交接，再接场景与后端开关；不能拿部分HUD GameStats生成完整结算，也不能挂回Python玩法系统。随后VLM/BOT，再R4真并行与R5容量/安装。当前 `NativeSession` 仅用于开发/离线场景，Hub/BOT明确拒绝，普通启动仍是Python；**R3/R4/R5未完成、main仍6a970dea、无merge/push、1/2/4仍串行**。下一阶段要审查动态Player/其他冷组件的展示更新与场景退出后回调，避免仅凭窗口能画就宣称完整兼容。

## 此前检查点：R3d1（历史安装状态）

**当前节点：R3d1 已固定（2026-09-14）。** 生产 `c5ae37f5fab2e3563af136f8868d8fc7227c1f23` / annotated tag `rust-kernel-r3d1-2026-09-14`。[报告与复现](../experiments/2026-09-rust-r3-controls/README.md)。本地移动/攻击/等待/驻守/筑垒/Fog/工具栏命令、Python输入/面板适配已接；UI只操作派生数据，命令返回前刷新。旧controller的epoch在native锁内写前/取增量前检查，不能污染reset后的新世界。保留UI/Agent、键盘/工具栏的历史差异。1618完整回归（696 Native、114新契约）、3Rust/Clippy/fmt；144配置7128节点精确差分和重放通过；真实Cocoa4配置480帧、48个合成SDL事件与4次工具栏直接命令、16PNG归档。**不等于完整GameScene/物理鼠标/容量验收**。API6/schema5、oracle=python-r0c-3cc4ffe；活动venv安装本检查点归档release wheel，扩展SHA `527c60fcca55aec5b4d2481cd113c78663eb1c3f631c6e72d83964c37fe98842`。正式checkout `runs/star-rust-r3-controls`。

下一步 **R3d2：GameScene/后端选择与输入生命周期**，再接完整HUD/VLM、BOT和结算。R3d1本地回放显式关闭LLMSystem帧更新；post-game通知/报告收集仍必须在后续host集成中验证。**R3/R4/R5仍未完成，Python默认/main不变，1/2/4线程仍串行，无新5000容量结论。**

**此前 R3c 已固定（2026-09-14）。** 生产 `5bda51db6cd68455aa5724a6ef0eca1e66f89dda` / annotated tag `rust-kernel-r3c-2026-09-14`。[报告与复现](../experiments/2026-09-rust-r3-presentation/README.md)：1504完整回归（582 native契约）、3Rust/Clippy；144配置5184节点/4032ticks差分和独立精确重放通过。Rust战斗/弹道/飘字生命周期与ID已接，资源/领地/Fog使用变化队列；Python消费展示增量，复用旧绘制缓存。真实Cocoa近战/远程、实时/回合制、选中/普通视图共960帧通过，24张截图归档；不是鼠标键盘或完整GameScene验收。API/schema=5、oracle=python-r0c-3cc4ffe；活动venv已安装本检查点归档release wheel。正式checkout `runs/star-rust-r3-presentation`，45个证据checksum通过。

**此前 R3b：** 生产 `d5abc70e9cda8a6820546112e6172dd9e43c1515` / `rust-kernel-r3b-2026-09-13`。[报告与复现](../experiments/2026-09-rust-r3-observations/README.md)：1443 完整回归、522 Native契约、3 Rust/Clippy；54配置4203节点/702ticks差分和精确重放通过。已补五种非图像观测与同revision缓存；有效缓存随scene导入以保留时间/from_cache；单位事实共用。保留旧 godview 非空战报属性错误。API/schema=4，活动venv已装归档release wheel。

此前 R0c `3cc4ffea091dcf6afa8691c217ec4b09e25d4b5f` / `rust-python-oracle-r0c-2026-09-13` 补两种观测坐标列表排序，1299回归；当前oracle为 `python-r0c-3cc4ffe`。旧R2/R3a重放仍必须用原tag/wheel。R3a动作/回合检查点 `7f4ad57bbd6966748c0fb49deb82f6ad43fc7aee` 保持不动。

后续R3d场景/HUD/VLM/BOT/结算范围见上方最新R3d1节点。**没有完整R3完成或新容量结论，Python默认/main不变，1/2/4线程设置仍为串行**。R3b历史checkout `runs/star-rust-r3-observations` 保留原API4 wheel；无关49处Agent/font删除不动。[阶段地图](visuals/rust-migration-map-2026-09-13/map.html) 是R3a冻结视图，当前进度以本文和阶段记录最新节为准。

用户已批准完整方案；[阶段记录与恢复说明](rust-env-migration.md)。已从生产main `6a970deaee7d9b8d3939edd102973f2377edd6ac` 创建 `codex/rust-env-migration` 并用起始annotated tag固定。R0已完成：生产oracle `78cc8da3a03ffedaea58642abae8fcb710db997d`，tag `rust-python-oracle-r0-2026-09-11`，919回归和六组跨hashseed重放通过。R1也已完成：`92a6812beeaee71f4dd3650f5e7cc30f808c7895` / `rust-runtime-r1-2026-09-11`，952回归、2 Rust测试、GIL/随机兼容及本机3.13 release wheel通过。当前R2：typed玩法组件与实时闭环；尚未提供可玩的Rust后端。旧并行观测v1及负结果保留。
切换门槛为M4上5000Units/1000Agents/30Hz，30秒闭环；完整行为兼容及macOS ARM/Linux安装验收。Python在全部gate通过前保持默认。P1/P2仍跳过；Protocol/Hub性能仍暂缓。本轮进度以阶段记录为准，不将原型或编译成功视为迁移完成。

R2中间检查点已固定：`d1f5838496b38b97907d31cd0439d3dae53b0eb4` / `rust-kernel-r2a-2026-09-11`，1032回归、3 Rust测试及360操作差分通过。[报告/raw/compact/复现](../experiments/2026-09-rust-r2-kernel/README.md)。范围为移动/恢复/规则模式战斗子集，**完整R2仍未完成**；下一步Fog/统计/权限/观测。活动目录的 `rotk_agent/*` 和字体删除不属于本轮，已保留并询问；正式验证在Lab干净checkout。不要把这些删除带入迁移提交。

R2b已固定：`062141d97fd6c8122c93e3dd1bc0b94736442e1e` / `rust-kernel-r2b-2026-09-12`，1046回归（127 native契约）、3 Rust测试和284操作差分通过。[Fog/统计报告与证据](../experiments/2026-09-rust-r2-vision-stats/README.md)。共享视野、探索历史、LOS/LRU、统计记录和窗口分帧采样状态已迁移；**完整R2仍未完成**。下一步可信Agent注册/认领、完整观测及动作接口，随后完整世界重放。活动目录无关删除继续保留；生产main未变。

R0b补充：已发现并修正多技能列表的hash顺序遗漏。新Python oracle `17b17766923ce4db05efb17aaf023818cf69cdf6` / `rust-python-oracle-r0b-2026-09-12`，1047完整回归；[旧版反例/新版证据](../experiments/2026-09-rust-r0b-skill-order/README.md)。后续Rust对照此基线；旧R0/R2a/R2b的tag与原始证据保持不动。活动代码正实现team认领和只读批次观测，未接正式Agent。

最新R2c检查点：`582dbdab6e7b060c2589096cd41bc45ee96a474f` / `rust-kernel-r2c-2026-09-12`；1075完整回归、3Rust/Clippy、252查询/60节点差分通过。[team/批次观测报告](../experiments/2026-09-rust-r2-projection/README.md)。已迁移组件级认领/FIFO与handler级Faction观测；正式注册/身份认证/动作分发未接，下一步从该边界继续。完整R2与容量验收仍未完成；Python默认、main不变。

最新R2d：`02ac380d631b7391bdf0f583084aee8d13d5de0a` / `rust-kernel-r2d-2026-09-12`。1115完整回归、195native、3Rust/Clippy；18配置678请求差分通过。[可信动作/批次报告](../experiments/2026-09-rust-r2-actions/README.md)。公开本地注册/认领/动作/查询接口已接，连续查询共享借用、写入立即断开。仍缺完整World.update生命周期/窗口/余下动作，R2与容量未完成；下一步接Realtime/Turn和完整世界重放。Python默认/main不变，无关49个删除保留。正式checkout `runs/star-rust-r2-actions`。

最新R2e：`2c83c001780ddf103b94905df81e8a1bc469af6e` / `rust-kernel-r2e-2026-09-12`，1152回归、394节点/360ticks小场景差分。[世界生命周期/5000闭环报告](../experiments/2026-09-rust-r2-lifecycle/README.md)。5000U/1000合成Agent在无窗口规则模式跑60秒，2007轮、4017move/64attack，全部存活；8151请求/1779ticks可精确重放。**没有窗口容量通过**：诊断循环P99=41.93ms、29.635Hz、观测/动作P99=119.21/120.65ms，未达到主验收。下一步回合handoff/余下R3动作和窗口；完整迁移仍未完成、默认Python/main不变。

早期R3活动记录（已由R3a检查点取代）：回合handoff/reset/统计与人工结束回合已实现，14新契约、246Native测试通过；仍在开发，未做完整R3归档。新适配层/API版本2、scene schema2会显式拒绝混入旧R2扩展/scene。旧R2e5000诊断重放务必用其原tag与归档wheel。接下来补其余动作和窗口。

## 最新调研：主流并行 ECS 与候选路线（2026-09-11）

用户要求探索其他方案，尤其是主流游戏技术。已完成[Unity/Mass/Flecs/Bevy 调研与 STAR 候选比较](10k-parallel-ecs-alternatives.md)。主候选是局部紧凑观测数据＋原生 Job：先验证单线程数据维护与热点内核，再测按数据块并行；最小一致性方案为只读阶段屏障。常驻增量 worker、共享内存和 free-threaded Python 保留为各有前提的备选，尚未实施或验证收益。
不要将 ECS 自动等同于并行调度、将共享内存等同于不可变快照，或假定每帧有千 Agent 可共同摊销快照。当前30秒闭环名义约33次观测/秒，24Hz约1.4次/帧；请求间动作仍保留顺序。生产状态及已归档负结果保持不变；本轮只更新 Lab 调研记录，没有新容量结论。

## 最新完成：并行观测v1原型，性能负结果（2026-09-11）

用户已授权实现并新建分支。生产`codex/parallel-observation-v1`从6a970deaee7d9b8d3939edd102973f2377edd6ac起步；见[实施记录](10k-parallel-env-v1.md)。
开发tip3c4fba1a40fccee7bfc06575ade338c30a4b784e，已用annotated tag `p3-parallel-observation-v1-prototype-2026-09-11`固定。936项回归通过；主探针960次输出等价、所有guard通过。
[报告/复现](../experiments/2026-09-parallel-observation-v1/README.md)：5000Units/1000注册Agent冻结探针，串行约141次/秒，2worker51–52、4worker约62。逐请求完整快照导出/还原抵消并行收益，保留开发分支，不合并main，不进入该实现的动态闭环，无24/30Hz容量结论。
主工具57343ce1b18f457b745391b5352081f547e40b45；raw/compact与前轮辅助负结果均归档核验。下一候选先降低快照成本（同只读批次摊薄或完整写入覆盖的增量镜像），尚未实施；Lab客户端独立与动态验证仍待后续。main仍6a970deaee7d9b8d3939edd102973f2377edd6ac，当前代码checkout为开发分支。本轮未推送。

## 最新方向：已确认先做观测并行（2026-09-10）

用户提出“It is time to consider parallel ENV”后，明确同意先做观测并行，并要求补充方案；此前“并行继续暂停”不再适用于这一方向。
[设计建议](10k-parallel-env-proposal.md)：优先单写世界＋不可变观测快照＋小规模worker池；先区分Lab客户端开销与ENV观测构建，不直接拆所有ECS系统。
18ms是Lab调度参数而非ENV固有上限。当前阶段只形成设计，未实施进程拆分、未启动新性能测试，生产仍6a970deaee7d9b8d3939edd102973f2377edd6ac。
先评估客户端隔离与快照导出成本，再验证冻结观测等价和动态顺序/权限；不默认改成上一帧/TTL观测。四层架构、固定模拟时钟、墙钟Agent思考、P1/P2跳过及Protocol/Hub暂缓等要求保留。
方案已补充ECS读写依赖解释、静态/世界/阵营/Agent数据复用边界、请求与快照生命周期、三组性能对照和异常契约。当前完成的是文档补充，尚未启动实现。

## 最新完成：文字缓存修复（2026-09-10）

用户已授权解决伤害数字/CRIT/坐标卡顿并尽量降低复杂度。
已实现固定坐标视图O(1)检查/提交、变更视图O(可见格)、飘字O(活动数)并缓存各实体文字，像素提交仍依赖视口面积；912回归/94结构契约通过。
分支`codex/cached-combat-coordinate-text`位于`runs/star-text-cache-dev`，测量tip5f13218ea1b6cf563e94b61e30a1609f01c2a138；工具b93139777ef65d3abf5f7aae41a99e180930b81c。
已先创建annotated tag `p3-text-cache-pre-squash-2026-09-10`→5f13218，再squash集成生产main **6a970deaee7d9b8d3939edd102973f2377edd6ac**，唯一parent9063863，树与tag相同。
[工作记录](10k-text-render-fix.md)、[报告/复现](../experiments/2026-09-text-render-cache/README.md)、[分析](../experiments/2026-09-text-render-cache/analysis.md)。
重新固定地图缓存后base/fixed各1600帧，guard全通过；zoom0.5坐标整帧P99 736.38→15.52ms，连续平移779.10→23.53ms。1000条可见飘字准备P99 2.54→0.97ms，屏幕外2.93→0.36ms；6个坐标冷打开样本最大37.08ms，4个zoom0.5冷样本仍超过30Hz预算，不宣称任意帧30Hz。
修复版自然24Hz/5000U/1000A，30s预热+60s：平均24Hz，整帧P99=41.33ms，5000全部存活，接受4930move/111attack，同时移动平均120/最大167。100ms观测/动作排队guard仍失败，无新容量认证/Frontier。
3raw+3compact ZIP已归档、解包重算和SHA核验；fixture引用上一轮唯一canonical副本。没有改变博弈规则、按键、移动弱化或启动并行/Protocol/Hub；生产运行方式不变。

## 最新诊断：坐标与伤害/CRIT飘字（2026-09-10）

- 用户要求分析两种视觉功能对P99的影响；本轮仅Lab诊断，生产仍906386312d70d77af25e4b4da883f6dd5b0fe5ef，未实施修复。
- [报告/复现](../experiments/2026-09-text-render-probe/README.md)、[归因及限制](../experiments/2026-09-text-render-probe/analysis.md)、[决策](../experiments/2026-09-text-render-probe/decision.md)。工具测量SHA f23266d83fd4dff099eb8cb3501aab37fc85b8e3。
- 冻结5000Unit世界/1000注册Agent，13条件×2轮×100帧：zoom1下577格，坐标OFF/ON的frameP99为18.14/181.02ms；zoom0.5下2379格为21.43/743.94ms，坐标路径P99分别171.49/726.78ms。逐格每帧创建Font、渲染文字5次是已确认重复开销。
- 既有大规模实验zoom0.15低于0.3阈值，坐标直接跳过，不能据此解释历史44.54ms。
- 1000条飘字的文字准备P99=2.61ms，屏幕外1000条仍2.98ms；字体已有预热，但surface每帧重建、没有提前裁剪。
- 自然24Hz闭环30s预热+60s：5000Units全部存活，接受4906move/115attack；最多11条飘字，文字准备P99=0.054ms；整帧P99=43.08ms。最慢1%帧的文字准备平均0.039ms、占总work约0.086%，不是本canonical负载的主要瓶颈。该口径不含文字最终统一blit。
- 诊断限制：replay每条件10帧预热未保证地图缓存稳定，保留全部早期慢帧，不从飘字ON/OFF的整帧P99差推算净收益；live不是密集混战或用户手动攻击现场的复现，也不是新的容量认证。
- 2份raw+2份compact ZIP全部解包重算与SHA验证，fixture引用上一轮canonical ZIP，未重复存储。不新增Frontier。若用户安排修复，优先字体/坐标标签surface缓存；并行架构继续暂停。

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

## 2026-09-10 已完成实验的执行记录：24Hz固定模拟时钟＋随机闭环

最新用户要求优先：ENV每帧推进1/FPS模拟秒，CD/恢复依赖模拟时间；外部Agent以墙钟等待。
生产capped模式和GameTime/ResourceRecovery已经满足这一边界；此前Lab使用uncapped墙钟delta，本次选择fixed模式，不修改生产默认FPS。
固定源码906386312d70d77af25e4b4da883f6dd5b0fe5ef，detached worktree `runs/star-p3-clock24`。
5000 Units/1000 Agents；每Agent平均控制5个Units；初始请求uniform(0,30s)错开。
每轮观测→逐Unit随机尝试move50%/attack25%/wait25%→立即提交本轮动作→墙钟等待截断正态N(30,5²)，范围15–45s→下一轮观测。
无合法目标则等待，不重抽动作。随机动作与时序使用独立seed42派生流；不声称该分布已经由真实玩家数据验证。
采用single查询保留观测/动作交错次序；当前共享批次不能跨越新产生的即时动作。
interleaved布局确保有非空战斗机会；Fog ON、selected面板、stdlib JSON编解码、12ms Agent预算、realtime_defer、真实窗口，Chrome保留。
先30s预热＋60s测量；根据结果继续300s观察，若通过再补独立60s重复。24Hz预算41.667ms，世界≥23.76Hz，观测/动作排队/期末积压≤100ms，名义闭环完成≥95%。
战斗允许死亡，但记录实际存活/移动与接受动作；容量判断要求测量存活≥初始95%，防止负载消失造成假通过。
每帧验证dt=1/24，并对照GameTime累计与模拟delta累计。模拟时间可能在性能不足时落后墙钟，这是固定步长语义，不用墙钟追赶CD。
本次先实现Lab工具并核验，不自动启动并行架构。

## 最新用户确认：闭环Agent，24Hz可接受，30Hz为更高目标

本节优先于下方历史计划中的独立轮询要求。用户原话是“观测从1Hz/Agent建立基线，再测5、10、30Hz”，没有明确要求LLM思考期间持续轮询；助手将其解释为独立周期观测，随后错误地归因为用户的明确要求。现予更正。

- 主要交互方式：获取一次观测 → 模拟LLM思考（例如30秒）→ 提交动作 → 获取下一次观测。思考期间不额外轮询，不替换当前决策快照。
- 独立1/5/10/30Hz结果保留为额外压力测试，不再作为真实LLM闭环必须达到的主要容量标准。不能据这些压力测试失败断言闭环千Agent不可用。
- 用户接受5000 Units/1000 Agents、30秒闭环已有300秒测试的实际表现：平均世界30Hz、整帧P99=34.5907ms、观测P99=35.6697ms、动作排队P99=28.4315ms、名义闭环负载完成99.9%。旧33.333ms严格门槛失败的历史标签不改写；这组数据可作为用户接受的工程使用基线。
- 大规模评测允许世界24Hz（每步约41.667ms），30Hz保留为更高目标。既有34.5907ms低于24Hz对应预算，支持可行性判断，但不是已运行24Hz的直接验证。旧证据源于第一轮版本，不能标为最新源码的24Hz认证。
- 5000 Units为驻留/受控规模，不表示5000个单位始终同时移动。Protocol/Hub未计入，不能写成完整网络千人在线认证。
- 后续恢复工作时优先核验最新版5000/1000、30秒闭环、24Hz，再视结果评估30Hz。这一历史表述已由顶部2026-09-10时钟确认取代：ENV固定模拟步长，Agent使用墙钟。
- 并行架构继续暂停；暂不因独立轮询压力测试失败扩大优化范围。本次仅更新活动记录，未改生产运行频率、未启动新性能实验。更强硬件改善30Hz是合理假设，尤其取决于单核性能，仍需实测。

## 当前操作节点（第二轮收尾）

- STAR main：`906386312d70d77af25e4b4da883f6dd5b0fe5ef`，仅以 squash 集成；前置 main `08c857e5df39f671c5a13bf04b9af9aac0800e78`。
- 开发分支 `codex/p3-shared-observation` 保留于 `runs/star-p3-batch-dev`，tip `626d3a8db900fc18599bc96206bc76b960826999`。
- 合并前 annotated tag `p3-read-batch-pre-squash-2026-09-09` → 开发 tip；实际测量 source `72e36414de7129a1046ce36861de18eb25b2d180`（之后仅测试/文档）。
- [第二轮报告](../experiments/2026-09-p3-read-batch/README.md)、[分析](../experiments/2026-09-p3-read-batch/analysis.md)、[决策](../experiments/2026-09-p3-read-batch/decision.md)。30组诊断、65个archive artifacts，全部raw解包重算与SHA验证。
- 899生产回归、10Lab测试、跨源冻结JSON oracle通过；规则未改变。
- 同源batch-off→batch-on：3000/1000/1Hz完成11.89%→21.06%；5000/1000为8.81%→14.03%；10K不稳定获益。
- 仅15s诊断，目标规模全部未达标；无300s+3×60s容量认证、无新增Frontier。
- 原第二轮后续优化建议已被文件顶部最新用户确认取代；后续先核验最新版闭环5000/1000，不自动扩大优化范围。

## 读取顺序

1. 本文件及 [下一步优先级](10k-online-next-steps.md)。
2. [P0 归档与恢复方法](../archives/2026-09-10k-p0/README.md)。
3. [E8 正式案例](../experiments/2026-09-10k-e8-volume/README.md)：raw、manifest、SHA256、分析和负结果。
4. 需要调查历史时再读 [冻结 E8 工作记录](../archives/2026-09-10k-p0/workspace/docs/dev/10k-online-e8-volume-progress.md)
   和 [roadmap](../archives/2026-09-10k-p0/workspace/docs/dev/10k-online-roadmap.md)。冻结记录中的旧分支、路径和 local 状态不是当前操作指令。

## 目标与当前证据

10,000 resident / 100% moving / Fog ON，seed 与 phase seed 42，staggered；
12-step route planning 在测量前，execution pathfinding OFF；真实 Animation、
position commits、Vision ON，realtime_defer，uncapped，MiniMap 动态单位 OFF，
屏蔽 gameplay input。生产仍是单线程 Core ENV，无提交、动画或 Fog 延后。

继承 E6-1：`e7ba18b31870577110b591104ef8fa7b4713e43c`。
验证 runtime：`9581084835633e10d80aac849925939bc59b9138`，保留 E8-1/2/3/4。
里程碑：`scale-10k-100pct-30hz-sustained-e8`，不可移动至清理提交。
E8 Lab 初始归档：`2dfbb09b4c2fc556bcbe05dadaa1b1fe46c6de89`。

| 完整准入 trace | 秒 | 帧数 | controlled P99 ms |
| --- | ---: | ---: | ---: |
| Continuous | 305.447501 | 10240 | 32.430227 |
| Repeat 1 | 65.285074 | 2389 | 28.984507 |
| Repeat 2 | 65.301032 | 2342 | 30.026299 |
| Repeat 3 | 65.271297 | 2336 | 29.162605 |

以上完整 trace 的 controlled-work P99 <=33.33ms，所有 workload guards 和
16 个完整 30 秒 block 通过，position/Vision 约 20000 次/秒。
并非每个 5 秒窗口通过：300s 末窗 34.745ms，repeat2 末窗 37.231ms；
300s frame-body P99 34.033ms。负结果完整保留，不能宣称每帧、任意短窗口、
完整交互、60Hz 或 10K online Agents 达标。Chrome 保持开启，没有据此删帧。

保留优化消除重复 texture preparation、UI roster 查询、component-row 查询及
movement reference 查询；组件引用版本与同步回调失效契约继续受生产测试保护。
P0 只移除实验代码/材料、snapshot 的离线专用 correlation 字段，更新用户文档与
回归集合；已验证 hot path 不变。生产主分支已集成并推送：`02d0fc1b598c54a172e1122ac9ea4c1e2f46ec15`。
详见 [P0 closeout](../archives/2026-09-10k-p0/closeout.md)。

## P0 完成状态

- STAR 与 Lab 均在 `main`；源码、原始证据、归档和里程碑 tag 已保存至远端。
- STAR 已移走 57 个实验/生成文件和 1394 个结果文件（原目录约 387 MiB）。
- 已删除 29 个本地、34 个远端 10K/phase5 工作分支；无关分支及里程碑保留。
- 归档覆盖的 63 个引用 / 40 个不同提交在独立空仓库恢复通过；1451 个迁移文件定位均通过 SHA256 校验。
- 当前生产回归 869 passed，结构契约 81 passed，历史 E8 工具 9 passed，compileall 通过。
- 活动恢复和后续计划归 Lab；冻结历史记录保留旧路径/旧发布状态，勿作为当前指令。
- 清理结果和生产 SHA 见 closeout；Lab 当前收尾提交可用 `git log -1 -- records/10k-online-resume.md` 定位，避免自引用提交 SHA。

## 当前工作：P3 本地合成 Agent + ENV

用户于 2026-09-08 授权直接执行 P3，跳过 P1/P2；Protocol/Hub 与 P4 全链路暂缓。
世界目标 30Hz；观测独立以 1Hz/Agent 建立基线，再测 5/10/30Hz。LLM 决策延迟独立为 1–60 秒。早期工具错误地将观测与决策周期绑定；既有结果只代表低频闭环，不能替代用户要求的观测扫点。
活动契约、阶段检查点、复现与下一步见 [P3 工作记录](10k-online-p3-progress.md)。

生产起点 `02d0fc1b598c54a172e1122ac9ea4c1e2f46ec15`；Lab 起点
`85d142e897194264810ab94ddeab0c6f63fd9e9a`。开始时两仓库 clean main，远端一致。
开发分支 `codex/p3-agent-observation` 位于 Lab `runs/star-p3-dev`；
对照 detached worktree 为 `runs/star-p3-base`。正式测量使用固定 SHA detached worktree。

star-main 集成只允许 `git merge --squash`：合并前创建 annotated tag 固定开发 tip，
同时记录 main 前置 SHA、开发 tip/tag、squash 后 main SHA。已发布 tag 不移动。
所有实验工具、夹具、raw、分析和记录留 Lab；STAR 留生产代码、必要契约测试和用户文档。
Chrome 保持开启；性能任务不并发，不因怀疑系统干扰删慢帧。


## 历史检查点：P3 第一轮收尾（2026-09-09）

优先阅读 [P3 第一轮报告](../experiments/2026-09-p3-local-agents/README.md)、
[分析](../experiments/2026-09-p3-local-agents/analysis.md) 和
[决策/下一步](../experiments/2026-09-p3-local-agents/decision.md)。

- STAR main：`08c857e5df39f671c5a13bf04b9af9aac0800e78`。
- 合并前 annotated tag：`p3-observation-pre-squash-2026-09-09` → `c9737451de97f1b1903123377a1514227c3ffdf5`。
- 性能测量实现：`e8b48c0568fb8830055bf053a724acc2b4e5c04c`；tag tip 仅追加文档/注释。
- 按 `git merge --squash` 集成，main 单 parent，树与 tag 一致；881 回归、81 性能契约、7 Lab 测试通过。
- 独立1Hz观测：3000 Units/1000 Agents完成12.06%请求，5000/1000为8.99%，10000/10000为0.58%。
- 5/10/30Hz已在5000/1000分别扫点。所有规模数据是15s诊断，不能发布容量。
- 较早5000/1000/30s顺序闭环，60s通过但300s整帧P99=34.591ms失败；所有负证据保留。
- 24组运行compact/raw ZIP已归档、SHA256核验、解包重算；fixture按hash单份保存。
- 不新增Frontier，不移动E8里程碑；P3容量目标OPEN，Protocol/Hub继续暂缓。

**下一项**：在保持共享视野和实时合法性的前提下，设计显式只读批次，复用同一快照的阵营共享观测构建。
先做共享部分与Agent私有owner/commandable/affordance的成本拆分、失效契约与对照，
再按独立1Hz验证3000/1000，不能改回低频决策闭环作为替代。
共享批次 API 正在第二轮开发分支验证；生产 main 尚未包含它，P3 容量仍 OPEN。

生产 main 与 pre-squash annotated tag 已原子推送且远端 SHA 核验通过；本轮 Lab 归档提交及其祖先一并保存至 origin/main。

## 第二轮：只读批次共享（已集成，以下保留阶段记录）

已形成 [只读批次共享实施方案](10k-online-p3-read-batch-plan.md)。用户已授权实施；新分支 `codex/p3-shared-observation` 位于 `runs/star-p3-batch-dev`，起点为生产 main `08c857e5df39f671c5a13bf04b9af9aac0800e78`。
采用保序短批次、按需构建、批次结束释放；跨阵营复用基础事实，阵营分别筛选情报，逐Agent判断权限。
完全叠格方案已放弃。用户认同取消兵力导致的移动力弱化，该规则调整单独处理，不混入本轮观测性能A/B。


第二轮阶段 A/B 已实现：同步保序前缀 API、32 请求上限、预算、异常释放、
批次内全场 census/阵营公共视图/逐 Unit 面板/跨阵营地块与组件查询复用，权限逐请求。
生产回归 888 passed；Lab 三路调度及分析测试 10 passed。
阶段 C 下一步：固定源码和工具提交，串行运行 single / batch-off / batch-on 的 3000U/1000A/1Hz 诊断。
三路均包含 JSON 编码与客户端解码；与第一轮工具相比新增解码开销，不能当作完全相同的历史基线。
原始堆序号、过期请求和读写屏障保留；周期性过期请求重排边界也有契约测试。
本检查点尚无新性能结果，不作容量或加速倍数结论。

首版 source `3017547a87360a667b6b6cb13def21d63b528399`、tooling `64cc1697f1c90bbfa5baa0f06b2e44eecc38191d`
完成 14 个诊断点（含 stdout 未落盘的首个 single，不用于受控对照）。
3000/1000/1Hz：single 11.69%、batch-off 11.91%、batch-on 19.55%；均为 15s、非容量验证。
10K 首版 batches=requests=494，说明首张快照已耗尽批次预算，不能获得复用收益。
检查发现 census 预取了所有位置和 AP，已调整为按组件类型索引、位置按需读取、AP 只统计所查阵营。
891 生产回归和 10 Lab 测试通过。下一步固定新 source，对首版负结果做同配置重测；不得删掉首版。

修正版 source `72e36414de7129a1046ce36861de18eb25b2d180` 完成 15 个重测点。
同 source 的 batch-off→batch-on：3000/1000 完成 11.89%→21.06%，5000/1000 8.81%→14.03%。
10K/1000 为 3.48%→2.95%，仍不能有效摊薄首张快照；不宣称全规模提升。
30s 决策且独立 1Hz 的3000/1000为34.25%；5/10/30Hz和非空战斗均保留。
全部目标规模仍有严重积压，故不进入容量认证长测，不新增 Frontier。
另以当前生产 main 和修正版独立进程生成冻结世界 JSON oracle，3状态×10请求，逐字节相同；
修正版每个状态内部同时验证 single / batch-off / batch-on 解析后逐字段等价。
下一步：补全冷构建/命中计时诊断，归档与重算，然后按预先 tag + squash 流程集成。

第二轮最终状态：已归档、已 squash 集成；阶段记录中的“下一步/尚未”只描述当时检查点，以文件顶部当前操作节点为准。

STAR main、`codex/p3-shared-observation` 和 `p3-read-batch-pre-squash-2026-09-09` 已原子推送，远端SHA已核验。Lab本轮归档与恢复记录由当前收尾提交发布；可用 `git log -1 -- records/10k-online-resume.md` 定位，避免自引用SHA。

2026-09-10 首个60s interleaved结果（source9063863/tool359d267）：时钟guard全通过，5000单位全部存活，接受2511次move和960次attack；世界16.93Hz，frameP99=70.90ms，观测P99=25.14s，完成50.98%名义闭环量。每次观测平均1.267MB，构建18.61ms/编码6.71ms/解码6.46ms。该高接触密度布局不能承载目标，不改写负结果。
接下来仅改layout为canonical（与此前5000/1000低频闭环相同），其余参数不变，30s预热+60s对照；若通过，继续300s及独立重复。并行化不启动，不改变动作概率或思考分布。

canonical/12ms的60s对照：世界24Hz、frameP99=36.28ms、move/attack与模拟时钟guard通过；观测/动作排队P99约484/488ms，短时突发尚有积压，名义闭环完成100.41%（零服务时间参考过程与实际过程的测量窗边界不同，可略大于100%，不是重复执行）。
下一次保持全部参数，只将Agent每帧预算12ms→18ms，验证是否能以41.667ms帧预算内余量吸收突发。先60s，再300s；不删去12ms结果。

canonical/18ms的60s对照：世界24Hz、frameP99=41.10ms，观测P99=123.46ms、动作排队P99=118.56ms，期末积压≤100ms，名义完成100.46%。相比12ms尾延迟改善，帧余量缩小；未通过旧100ms请求P99严格门槛，但不据此称工程不可用。
下一步固定18ms参数运行30s预热+300s持续观察；不继续调参，不因短测的轻微SLO越线扩大架构改动。这是长期实用性诊断，不自动升级成旧门槛全部通过的容量认证。
