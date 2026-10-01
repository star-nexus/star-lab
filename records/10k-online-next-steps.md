# 10K 后续工作优先级

## E6 展示数据与 ECS 缓存（执行中）

起点4657dd4，私有原型5f567d3，测试checkpoint0a297a8；native源码及838c693扩展保持。
2385项Python回归通过；普通apply AST与起点一致。完整基线诊断通过40994请求/9880tick，
探针成本仅作归因。完整像素对照曾在2711tick失败，当前补充控制展示墙钟后重新验证；
在正确性完整通过前不进入性能或live。三个研究模式默认不接入普通展示。
进度：`身份/契约 █ | 原型/回归 █ | 基线归因 █ | 完整等价 ░ | 配对/条件live ░ | 归档 ░`。

[当前E6入口](../experiments/2026-10-rust-presentation-cache/README.md)与
[成本/契约](../experiments/2026-10-rust-presentation-cache/analysis.md)。
5000Units＋1000Agents；5000Agents暂缓。既有GAP及容量/Frontier状态不改，不push/merge。

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
