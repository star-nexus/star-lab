# Rust 内核＋Python 接口迁移

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
