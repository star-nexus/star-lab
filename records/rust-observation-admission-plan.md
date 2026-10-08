> 2026-10-08 测试量修订（用户要求合理安排）：ordinary完整证据复用；仅保留当前规范encoded正确性。真实接纳native1和16个边界/故障检查已通过，范围见实验results/p2-targeted-admission.json。候选通过后只做一次native1移动世界服务筛选，使用现有完整90秒接纳输入（2617tick）。筛选排除live heap与显示链，不满足原正式全宿主验收或默认采用；无收益停止，干扰inconclusive，有收益才补足正式三轮。native4/300秒窗口不自动展开。

# E8：已接纳观测请求的只读段复用算法方案（2026-10-07）

当前执行：P0/P1已归档，P2串行完整轨迹校验执行中、targeted待完成；默认关闭、无正式收益结论。以下算法保留原预注册边界。对应[整体评估](rust-performance-optimization-assessment.md)第三项。目标保持5000 Units＋1000 Agents；5000 Agents暂缓。

进度：`源码/历史证据 █ | 算法/契约 █ | P0接纳诊断 █ | P1最小原型 █ | P2正确性 ▓ | P3收益 ░ | 条件窗口/默认接入 ░`。

## 1. 选择与范围

首版采用**逐请求执行与返回、只读段内复用已有编码事实**。Python继续负责接纳、预算、时钟、客户端解码和策略消费；Rust复用已有ObservationBatch中的census、阵营公共编码、Unit基础面板、敌军和地形事实。每条请求仍经过原有身份与权限检查、独立组装完整响应、提交原有统计，然后返回调用者。

不把多个请求直接交给现有execute_actions_json作为宿主接入方案：该入口先解码整组，连续查询先计算响应、释放ObservationBatch后按序提交计数；Python包装还会解码整份report。这是既有batch API的合法契约，却不能自动等同于真实host逐请求的错误前缀、返回/回调时点和JSON直传成本。

首版不减少跨语言调用次数、不新增worker、不改变观测算法本身；主要变量是重复公共工作是否能在真实连续请求之间复用。后续整体合批调用或生产网络接入需要独立证据，不能捆绑为本轮收益。

E7的empty_territory已经在本轮收益门槛下不采用，E6/E7默认研究开关继续关闭。E8从活动工作树5b9658bc668b7d13f801351162f255f30622b32a开始，路径/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main、分支codex/rust-ecs-parallel。普通step、默认native1、API18/schema5、Python字典接口和已有Statistics策略保持。

当前Lab HEAD为4370070；原仓库7e145d169433695cd4957e186a6b2fda06813c26的49项删除、冻结Rust5147e4d8e0c33c997bd86960d87fa4b5b3ca90c5和Python6a970deaee7d9b8d3939edd102973f2377edd6ac均已核对，保持不动。身份和文件SHA见[rust-observation-admission-plan.json](rust-observation-admission-plan.json)。本次只写Lab方案，不修改产品源码、probe或历史工具。

## 2. 已有能力与接入缺口

源码通过原仓库CodeGraph读取；native.py、observation.rs、actions.rs及llm_system.py与活动工作树逐字节相同，因此这些结构证据适用于当前起点。Lab调用链使用其独立归档工具源码审查。

| 位置 | 已有行为 | 本轮含义 |
|---|---|---|
| native/rotk/src/observation.rs::ObservationBatch | runtime只读借用；按需构建census，按阵营保存public encoded；panel/enemy/tile为独占map中的不可变编码事实 | 复用现有构建算法，将缓存所有权与短暂Runtime借用分离，不复制World |
| 同文件faction_state | 每条参数/阵营/unit_ids检查；各请求独立捕获owner/commandable；输出持有Arc编码片段 | 不能复用完整最终响应或授权结论；保留unit_ids去重/原序/死亡过滤 |
| actions.rs::execute_requests | 整组wall metadata检查；连续query共享ObservationBatch；后续按序提交wall_time与action计数 | 不直接拿它替换逐请求host语义 |
| native/python/src/lib.rs | 单条和整组分别serde解码/编码，with_runtime锁住当前实例 | 新缓存只能保存owned事实，不让World/ECS引用跨出一次借用 |
| RustRuntime.get_faction_state_json | 已有可信身份、admission lock、拥有完整JSON的直传路径 | 三个研究模式保持同样的完整JSON/客户端decode边界 |
| RustRuntime.execute_actions_diagnostic | report在Python解码，VLM先全组校验再切分/截图 | 不能通过额外server decode/encode来冒充相同成本边界 |
| Lab tools/p3_runtime.py、p3_local_agents.py | Rust仅接受single；native-wire也仅接受single，post-action闭环拒绝旧Python batch模式；gate在Rust路径为空 | 需要新增独立研究适配入口，不能只开启已有Python batch-on开关 |
| LocalAgents._consume_observation | 消费响应、按原序使用策略RNG、更新本地会话并排队下一动作；不直接执行世界动作 | 可作为首个待证明的可信消费边界；其执行点仍在每条返回之后 |
| LLMSystem.on_message及R3d4a记录 | single消息统计在行动后，action_batch统计在行动前；响应/连接/ACK编排留Python | 真实网络host与Lab local边界不同；G009继续OPEN，不声称已接入生产网络 |

历史P0规范轨迹中64.475%查询位于长度2–5的query段，同阵营重复14.573%、无重复panel。这只是请求轨迹的乐观候选分布，不证明当前预算/回调/接纳后仍有等量合法批次，更不能换算为提速。R3k4/R4b的encoded facts与Python旧read batch是继承能力；旧1Hz过载试验不作为当前30秒闭环目标。

## 3. 严格保序的段构造

定义只读段为：同一Runtime实例、epoch与owner执行上下文内，**已经接纳**、当前队首连续的get_faction_state请求，且当前导入action spec的kind确为query；段内没有会改变缓存依赖的写入、未知回调或owner让出。自定义spec把该动作标为写时，保留execute_request的revision变化并走旧路径，不能仅按名字认定只读。首版最少2条、最多4条；单条走旧路径。4为研究上限，不是生产策略，2/8只作为后续敏感性诊断，不能择优替换正式参数。

对Lab heap，顺序由原(due, serial)决定。首个正常dequeue时冻结当前ready cutoff以及最多4条连续队首的身份，扫描遇到动作/未来请求立即停止；仅查看队首有界前缀，不按阵营排序、不跳过错误/动作、不弹出整个前缀、不提前分配后续request_id。真实owner队列若被审计，使用其已有接纳序号，不移植heap规则。

随后每条仍执行原流程：

```text
原pump预算检查 → 队首/截止/段身份检查 → 单条dequeue
  → 在原调用位置取得wall_time、身份和request_id
  → 原单条解码/有限wall校验/时钟写入/统计初始化/鉴权
  → ObservationBatch构建或复用事实 → 完整响应组装
  → 原动作计数与revision处理 → JSON编码 → 返回拥有的JSON
  → 原客户端decode/消费/RNG/回调/下一动作排队
  → 再做原pump预算检查 → 决定下一条能否继续该段
```

消费或回调后必须重新检查真实队首。新插入事件即使是query，也不属于已冻结段；若它成为新队首，立即结束旧段并按原队列处理，不绕过它执行原前缀。未来请求不等待、不拉入。预算耗尽即关闭缓存；未消费后缀从未被移出队列，保留原deadline/serial和统计。没有为凑批增加等待窗，也没有一次性执行4条越过原逐请求预算检查。

固定输入oracle使用明确记录的请求、写入、回调与时钟序列；真实窗口因运行速度变化可能出现不同到期时间和轨迹，窗口结果只用于运行验收，不能冒充同输入因果比较。

## 4. Rust缓存生命周期与私有接口

把ObservationBatch独占的owned缓存字段抽为私有ReadSegmentCache：census、faction facts、panel/enemy/tile编码map及必要诊断计数。已有事实构造逻辑保持，缓存通过move转移；不可持有World、ECS组件引用、MutexGuard或借用的参数。不得clone整个世界、Fog或缓存，不保存历史请求/历史完整响应。

建议研究接口形状（名称在实现时锁定）：

```python
with runtime._admitted_observation_segment(mode, max_requests=4) as segment:
    # Python仍逐条按原pump取请求；不预执行其余请求。
    payload = segment.get_faction_state_json(...原参数与wall_time...)
    # payload拥有完整结果；原消费随后执行。
```

内部token绑定(instance_nonce, epoch, owner_thread, segment_generation)，同实例最多一个活动token；跨实例/线程/旧epoch/nested/token关闭均不能借用旧缓存。开段本身不提前检查后续Agent权限、不写世界时钟或计数。每条调用短暂借用Runtime，将owned缓存move入ObservationBatch，生成拥有编码片段的响应，结束借用后按原点提交该请求统计/revision，再编码完整JSON；将仍有效缓存move回私有槽。时钟写入、ensure_action_stats及错误提前返回保持execute_request原顺序，不能以这张简化流程覆盖真实错误分支。

可疑native入口在访问或修改Runtime前先失效缓存并递增段generation，不能只依赖Python包装。默认所有非本段观测入口都是屏障，只有逐项证明无依赖影响的入口才可列入例外。合法动作仍执行，不能为了缓存而拒绝动作。旧token后的下一观测由Python私有适配层在**尚无该请求副作用时**转回原single路径；已开始执行的请求失败不得重放，避免重复计数和响应。

正常返回/预算到期/段末、异常、panic、reset、close、场景切换都销毁或归还缓存所有权；沿用既有native故障边界，禁止继续使用poisoned上下文。关闭一个旧token不能误清理另一段的新token。响应的不可变编码片段/完整字符串可独立存活至客户端消费；可变Python结果容器仍独立，不改变输入参数。

缓存驻留至多一个有界段、最多4个请求的事实并集。字节上限若需要，必须在P0根据实际数据预注册：只能在请求完成后清空缓存、下一条按single继续，不能删字段、拒绝原本合法的大响应或更改错误行为。未实施前不猜测统一MiB预算。

## 5. 读依赖、权限与屏障

| 可复用内容 | 依赖 | 不能随之共享的内容 |
|---|---|---|
| census | Unit所属阵营、Headcount存活、ActionPoints可行动、实体集合 | 请求身份、动作/消息计数、错误时间 |
| faction public encoded | census、GameState/Winner/BattleLog、阵营Fog视野、敌军Position/类型/存活、terrain/rules | 其他阵营的权限投影、完整响应、缺失/无效参数判定 |
| Unit基础panel | Unit/属性/AP/技能/CD/位置，当前occupancy与terrain，当前阵营可见敌军 | owner/commandable；每条仍新捕获，不复用授权通过结论 |
| enemy/tile encoded facts | 对应实体/格的事实字段；返回哪些事实由当前阵营投影决定 | 把同一敌军/地形事实可共享解释成跨阵营可见性可共享 |

query自身的action accounting确实是写入。已有execute_requests允许先构造连续query的事实，再提交action计数；E8须针对当前代码证明这些计数字段不影响上表、鉴权或后续query错误。依赖相关字段若改变，必须失效/重读；若每条都必须失效，接受没有收益，不能放宽一致性。

首版以下事件结束段：move/attack/rest/occupy/fortify/skill、claim/release/re-register、回合/时钟/世界step、状态导入/reset/close、Fog/terrain/rules变更、展示delta drain、VLM截图、所有其他动作与未知native调用、native故障/不可信回调/owner yield。record_message、ACK/重试/连接/断开亦先作为host屏障；它们的统计/时序若要跨越，需独立依赖证明。

首个可调度消费边界只允许审计过的LocalAgents流程：在原点消费完整响应、使用原策略RNG、排队未来动作；payload_callback/录制器也要逐项证明没有读取后续已提交统计或重入世界。未证明者按屏障。任何消费callback直接执行写入时，native入口先失效，写入成功后下一query读取新世界；不能把未知callback延迟到整批末尾。

每条仍校验可信Agent ID、注册阵营、请求faction、unit_ids存在性/归属/类型/顺序，独立捕获owner/commandable。跨写入/TTL/旧世界帧不复用；epoch只是reset边界，不能代替每次写入的段失效。缓存无法让不同Agent少输出字段：最终完整JSON仍按每请求发出，O(总响应字节数)不可消除。

## 6. 三模式与归因

新增Lab私有研究模式，不复用旧Pythonobservation-mode开关，不改变普通CLI/SDK默认。

无效模式/限额在token创建及任何世界时钟/统计写入之前拒绝；普通业务参数仍按原请求位置校验，不提前审判后续请求。

| 模式 | 行为 | 对照用途 |
|---|---|---|
| single | 原native-wire逐请求路径 | 当前基线 |
| segment_no_reuse | 同样的段识别/token/逐请求接口；每条前清空所有跨请求census/faction/panel/enemy/tile缓存 | 隔离段管理、适配与缓存所有权拆分成本 |
| segment_encoded | 同一段内保留上述owned缓存，逐请求返回/统计/消费不变 | 复用效果 |

三模式均保持原生完整JSON输出、同样的字符串→bytes边界与一次客户端JSONdecode、同一消费脚本；不能用single直传对比batch report在Pythondecode再encode。single→no_reuse测机制成本，no_reuse→encoded测共享效果，single→encoded才是净收益。ordinary展示保持baseline，E6 typed不加入本轮第一矩阵。

若拆分owned缓存影响ordinary路径，其同二进制single必须先与独立5b9658b扩展完整等价，并记录新增ordinary成本。性能主对照只在同一候选二进制中切换研究模式，不把重编译或不同依赖当第二变量。

## 7. P0成本与候选可行性，先决定值不值得继续

先在当前Rust单条路径、原5000/1000闭环下做短独立诊断（初步30秒预热＋60秒测量，原思考约30秒、无1Hz轮询），记录真实接纳边界与可复用段。低负载/冷启动可补短样本，不能用同步全部Agent凑主结果。

| 必需指标 | 目的 |
|---|---|
| ready/accepted/dequeue序号、原deadline/请求wall_time、step/动作/回调/预算切点 | 区分历史query相邻与当前真正合法段 |
| 段长1/2/3/4、实际共享数、混合阵营/同阵营、panel重复/重叠、屏障原因 | 计算真实覆盖率，不拿64.475%当当前事实 |
| census/entities visited、public build/encode、enemy/tile/panel build、cache drop | 找到实际可消除工作及新增维护成本 |
| 参数序列化、Rust进入/鉴权、事实、输出组装/编码、server额外转换、client decode、消费 | 核对嵌套边界；正式净收益包含全部必要工作 |
| 观测service/response/queue、action queue、Agent pump/整帧work、world Hz、积压 | 短service收益不能代替排队与整帧收益 |
| 缓存项数/字节、RSS/footprint、响应字节、活跃token与段末清理 | 验证内存随当前段而不是历史增长 |

诊断关闭后才测正式性能。只读成本预算按同段逐请求轨迹累计可省build/drop减去段维护计算；没有重复panel时不计panel命中收益。混合阵营通常可共享census与底层fact片段，同阵营才进一步共享public projection；不同单位面板仍各自计算。

历史数据不能证明合法段，或者当前严格边界使大多数段变成单条、可消除成本不足，则归档有限价值/负结果，停止P1或不进入P3大矩阵。上限仅作筛选，不能单凭带诊断计时否决一个已经很小且契约安全的原型；原型是否提速最终用关闭诊断的完整服务对照判断。

## 8. 分阶段验证与收益门槛

| 阶段 | 最小工作 | 继续/停止条件 |
|---|---|---|
| P1 | owned cache拆分、private token和no_reuse；先做小型M→Q→N差分 | single与no_reuse若响应、每请求计数/时钟、队列/消费/错误前缀不等价，立即停止复用阶段 |
| P1b | encoded仅复用已证明事实；短代表批次无诊断single/no_reuse/encoded | 长度1对照与2/4、混合/重复/无重叠代表段全部保留；没有公共build下降或总service明显变慢，停止扩展，不先跑全天矩阵 |
| P2 | 规范完整轨迹＋真实接纳录制重放、targeted错误/生命周期 | 通过后才启动正式收益；不重跑E7的四组完整像素/权威测试 |
| P3 | native1主结果，第一轮完整固定接纳ABBA筛选，通过后补足三轮 | 任一轮未过原门槛保持关闭；不补跑择优。native1通过后再单列native4交互验证，不扩大到8层24组 |
| P4 | 通过固定输入门槛后，5000/1000三轮single/encoded窗口AB/BA/AB | 30秒预热＋300秒测量；原frame/queue/hz/load guards全部通过才讨论默认接入 |

P2完整校验覆盖所有40994请求/9880tick规范操作与全部响应、逐条统计/wall/权限小状态、每个世界写入/推进节点的权威状态、展示增量与事件。比较按流处理，不把全状态历史放在内存。完整authority采样位置须在预注册中明确，不能把逐请求小状态指纹说成逐请求全量export。新增接纳/回调/预算日志补足旧轨迹未保存的宿主边界；旧轨迹只做world/request等价与历史候选分布，不冒充真实accepted queue。

重点小测试：单条与空段、Q/Q和Q/写/Q，跨阵营/重注册/claim-release、重复/乱序/空unit_ids、错误参数/非有限wall/缺身份/未知动作、自定义action spec把query标为写与revision耗尽、冷GameStats初始化、后项malformed不提前阻止前项、动作和消息计数成功前缀、编码失败前已提交的原统计、callback插入更早事件/直接写入/调用未知native入口/抛错、预算切断保留原后缀、暂停/倍率/GameOver、VLM前后World与图像引用、跨线程/跨实例/nested/过期token、reset/close/panic故障及输出在上下文结束后仍独立可用。

第一正式收益门槛：**每轮全部观测完整service均值至少改善5%，配对改善95%区间下界>0、观测service P99不回退；固定轨迹总工作均值正改善、95%下界>0、P99不回退。** 分母包含全部观测，含不能合段的单条/屏障，不能只报告命中段。action服务、段最大驻留、预算越界需单列，不能用延迟动作或多执行请求制造收益。正式主参数max_requests=4，在P0后冻结源码/接口/路径/消费/录制身份和统计工具；若需改参数，另立修订与新实验，不用已测数据择优。

三轮ABBA使用**一个实例/进程一次完整重放**，A/B/B/A各自独立进程按次串行，避免四个5000Units世界同时驻留；两侧输入/墙钟metadata/队列和预算切点相同，perf clock真实。每轮保留所有9880tick及预热/慢尾，以100tick分块、10000次bootstrap、seed42、末80tick按实际权重；service按该tick的实际请求数量加权，不能平均“每tick均值”或把无观测tick当零耗时观测。P99/max从原始完成请求与原始tick总work计算，不能相加分项P99。报告ABBA次序与漂移，不筛异常慢样本。

固定重放将接纳/预算切点作为共同录制输入，隔离同输入成本；真实窗口仍运行原动态预算和时钟。service从原dequeue开始至客户端decode/消费及本次必要段维护完成；前缀扫描/token开段必须落在首条已计时请求内，关段/drop落在末条计时内，或以明确归属计入整段服务总额，不能移到计时外。native/query完成、返回、消费完成、段清理完成分别记录，不能将cache结果建成时刻当Agent已收到；response时间以实际消费完成时点记录，不能用维护归因改变原始响应时间。response/queue用于真实窗口，固定录制逻辑时钟不能声称真实排队变快。

窗口沿用5000 Units＋1000 Agents、Fog、原镜头/2480×1239、GC realtime策略与约30秒闭环思考/合法动作配置。帧P99≤33.33ms、世界频率≥29.7Hz、观测及相关队列P99≤100ms、完整负载/积压/存活/合法动作guards均须通过；真实轨迹差异只用于运行验收。生产网络默认接入仍需单独完成可信身份、record_message、ACK/结束/错误/断开/背压契约，不能凭Lab通过关闭G009。

## 9. 资源、停止与Lab交付

2026-10-07用户新授权覆盖旧pressure pause only：只记录warning/critical/未知压力，不自动暂停、kill或设置运行超时；6GiB仅为监测参考，没有强制内存预算。正式计时发生任何压力非normal/暂停/监测事件，则该整次计时无效，raw保留，不自动补跑择优；不把后台Chrome使用与性能差异直接归因为因果。计划的有限样本/阶段完成正常退出，与资源守护自动退出不同。

采用缓存必须通过反复开关段/跨帧/写入/reset的有界驻留检查，不能只用峰值RSS证明无泄漏。失败保留具体状态和完整尝试，暂停临时跟进，不自动反复重启。创建方案时尚未执行；当前P2测试已启动，没有新增E8自动跟进，旧E7跟进保持暂停。

实施时建立experiments/2026-10-rust-observation-admission/，按PROTOCOL保存README/manifest/analysis/decision、P0成本/段分布、三个模式与每轮指标、源码/同二进制single/独立旧扩展/wheel身份、接纳与回调输入、raw与compact、工具和ZIP内外SHA。负结果同样完成研究记录。每阶段附进度条，更新恢复入口与[Lab阶段台账](rust-observation-admission-status.json)。

保持既有GAP/容量/Frontier不变、5000Agents暂缓，不push/merge。本轮默认关闭，用户随后已授权执行方案；当前实施与小型验证完成，完整正确性执行中，正式收益未开始。

方案文件完整性：从Lab根目录运行 `shasum -a 256 -c records/rust-observation-admission-SHA256SUMS`。这不是正式性能证据或采用验收。
