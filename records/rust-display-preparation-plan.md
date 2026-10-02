# E7：显示链路与绘制准备优化方案（2026-10-02）

状态：已有证据复核、代码边界审查与研究方案完成；**尚未实施 E7 原型或启动新性能实验**。
进度：`恢复/计量审计 █ | 代码边界/方案 █ | 新分项诊断 ░ | 单点原型 ░ | 正确性/收益 ░ | 条件窗口/归档 ░`。

目标仍为 5000 Units＋1000 Agents。沿用活动独立工作树、默认关闭的研究策略；不降低画质、文字、Fog 或更新频率。Rust 负责权威执行，Python 保留 UI、接口与生态。

## 1. 起点与恢复顺序

1. 本方案和[计量审计结果](rust-display-preparation-budget.json)。
2. [E6 README](../experiments/2026-10-rust-presentation-cache/README.md)、[analysis](../experiments/2026-10-rust-presentation-cache/analysis.md)、[decision](../experiments/2026-10-rust-presentation-cache/decision.md)。继承展示与像素契约、完整 delta 和失败控制。
3. [整体优化评估](rust-performance-optimization-assessment.md)第二项、[Lab PROTOCOL](../PROTOCOL.md)。旧评估的 E2 数字属于历史快照，本方案采用 E6 当前证据。
4. 产品的 `docs/native-presentation-cache-research.md`、`docs/native-state-boundaries.md`、`docs/native-benchmark-gaps.md`，再读下述代码边界。

规划执行基线为 `068c1ecd17988ac6d884984e904aea924968e0ae`，annotated tag `rust-parallel-e6-presentation-cache-2026-10-02`；活动目录 `/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main`、分支 `codex/rust-ecs-parallel`。E6 主测量源码 `0a297a868f589dd49eb514f3c73402142df05e2c`，与该基线的执行代码相同。后续仅规划/GAP文档提交不改变这个执行起点。

本次检查前 Lab 为 `ccc3edade4c3886224e7af32d125ff3c3002c24c`，工作区干净。原目录 `/Users/liyang/Developer/star-main` 仍为 `7e145d169433695cd4957e186a6b2fda06813c26`，保留 49 项原有删除；冻结 Rust `5147e4d8e0c33c997bd86960d87fa4b5b3ca90c5` 和 Python `6a970deaee7d9b8d3939edd102973f2377edd6ac` 干净，均不作为开发目录。E2–E6 标签不移动。

当前 native wheel SHA256 `2a853d7f8d1ca9701d7ffcb39522d2c25d0824562d8ca436424f8c790cfd0e30`，扩展 SHA256 `838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544`，API18/schema5。纯 Python 显示研究复用该扩展，不以重新构建或更换依赖引入第二个变量。

## 2. 先纠正旧残差，再确定投入边界

对 E6 canonical live diagnostic 原始 1800 个测量帧重新复算，30 秒预热＋60 秒诊断、native4、普通 apply、Cocoa 2480×1239。这里全部是**带诊断的均值，不是无诊断基线或加速预测**。

| 范围 | 当前均值 ms/帧 | 正确解释 |
|---|---:|---|
| display Systems | 8.355460 | 包括 Map/Unit/UI/Effects 等；其中可能有即时 Surface 绘制，并非全部是准备 |
| RenderEngine/RMS | 3.348679 | 排序、打包、实际 blit/几何绘制、清理及计时开销；必须继续拆分 |
| display.flip | 1.476814 | 平台呈现调用墙钟，可能含等待；与 Python 准备分开 |
| Agent 工作 | 3.076589 | 属于请求服务；已经包含在外层 update_work 中 |
| 旧 update 残差 | 3.184213 | 外层 update_work 减五个 core 区间，**尚未扣除 Agent** |
| 扣除 Agent 后残差 | **0.107625** | 仍含 harness census、记录、包装等，未证明是产品绘制成本 |
| screen.fill | 0.279762 | 清屏实耗，单列，不隐藏在准备或平台提交中 |
| native 世界 step | 0.255415 | 不含观测；本项不以继续并行 step 为首选 |

`tools/p3_runtime.py` 的包装 update 在 `agents.pump` 之前开始计时，之后才调用原 `GameEngine._update`；五个 core 区间来自原 `_update`。因此旧残差的 **96.620054%** 是 Agent 工作。不能把约 3.18ms 解释成未知渲染热点，也不能把 Agent 再加到 update_work 上。历史 E6 结果不改写，由本审计解释原口径。

```text
update_work = Agent + 原 GameEngine._update 五个 core 区间 + harness 残差
scene_update 包含 inputs、native step、delta、apply、display Systems
work 包含上述包装 update 和帧循环外围工作；限帧等待单列排除
```

复算入口（只读已有 archive，无需启动游戏）：

```bash
cd /Users/liyang/Developer/star-lab
python3 tools/rust_migration/audit_display_budget.py --output /tmp/star-e7-display-budget.json
cmp /tmp/star-e7-display-budget.json records/rust-display-preparation-budget.json
```

审计校验 canonical ZIP SHA256 `accdac58f19704c943083006be4f15d1fc44bb88fb1d6a91ec75bce791d6e620`、raw member `raw/live-diagnostic-baseline.raw.json` SHA256 `794a98934b65c57db9161c87b488e85e219cc32e210ae507feff6491aecba854`，及 metadata member SHA。筛选 `30.0 <= t < 90.0`，原数组零基索引 883–2682；逐帧计算残差再取均值，精确复现原已公布数字。完整定位、工具 SHA、source/tooling/workload 在 JSON 中。原始数据只交叉引用，不复制。

## 3. 代码边界与已有机制

本轮先用原仓库 CodeGraph 做结构审查；`framework/engine`、`rotk_env/systems` 在原 `7e145d1` 与活动 `068c1ec` 之间无差异，故索引对应当前显示实现。具体证据入口：

| 入口 | 当前行为与约束 |
|---|---|
| `framework/engine/game_engine.py::_update` | 清屏→事件处理→scene update→RMS update→flip，均在调用线程 |
| `rotk_env/runtime/session.py::_update_systems` | display 使用展示 World，按启用 System 原序推进；保留 revision 与控制输入顺序 |
| `rotk_env/systems/window_unit_render_system.py::_get_visible_units` | 已有空间分桶、world 坐标 bounds 与 Fog 筛选；不能把新增 culling 当新成果 |
| `rotk_env/systems/window_render_systems_base.py::UnitRenderSystem` | ≤20 个可见单位走丰富展示，更多单位每帧分静态 hex groups 与动画列表；静态组先绘制，动画后绘制 |
| `rotk_env/systems/unit_render_system.py::_render_unit_group_optimized` | hex→world→screen，单实体/多实体布局原序，叠格布局及当前显示数量保持 |
| `framework/engine/renders.py::RenderEngine` | 按 layer 排序，同层保持命令顺序；连续 plain blit 已使用 `Surface.blits`，Command 已有 `__slots__` |
| 同文件 `draw/update/clear` | draw 构造 BlitCommand；update 再扫描并构造 `(surface,dest)` 批次；成功末尾清队列，错误路径契约须保留 |
| `framework/tests/test_render_blit_batching.py`、`test_render_engine_profile_breakdown.py` | 已有批量与区间闭合契约，作为回归入口；本规划未运行或修改测试 |

继承静态 terrain 缓存、opaque overscan、Fog surface/journal patch、纹理、字体及标签缓存。新的缓存必须说明哪些结果当前已经被缓存、哪些仍重复准备，不笼统重做“批量绘制/纹理缓存”。SDL/Pygame 绘制、窗口与事件调用仍在主线程，不新建显示线程池。

## 4. P0：完整分项成本与缓存契约

先以当前源码、原显示模式重新诊断 canonical 9880 tick，另做真实窗口短诊断。普通 apply 与 E6 reuse_typed 分层记录，不合并均值。正式性能运行关闭细粒度探针；先验证探针不会改命令、状态或渲染工作量。

| 范围 | 需拆开的成本 | 工作量/失效计数 |
|---|---|---|
| Unit | bucket/bounds/Fog 筛选、动画位置、hex 分组、屏幕坐标/布局、样式与文字、命令入队 | candidates/visible、静态/动画数量、groups、坐标转换、lookup、命令数量、组/样式命中与重建 |
| Map/Fog | 当前 viewport 与已有地形缓存准备、overlay、Fog patch/full rebuild、即时 Surface 绘制、入队 | 缓存命中、准备/完成条目、待办、journal/epoch、patch/rebuild原因、Surface像素/字节 |
| UI/Panel/Effects/MiniMap | 数据读取、layout、文字/Surface准备、即时绘制、入队 | 静态/动态字段、font/Surface命中、选中/阵营变化、事件触发重建 |
| RMS | enqueue/命令构造、layer准备、run扫描、batch参数构造、实际blits、scalar/custom/area/flags执行、clear/释放 | 总命令、对象/tuple/list构造、run数/长度、barriers、实际绘制数量与像素工作量 |
| 平台与外层 | 清屏、event pump/get/dispatch、flip、Agent、census、记录/帧统计与剩余开销 | wall/process CPU边界、慢帧时间轴、输入事件、GC策略及观测/队列关联 |

每个区间给出 inclusive/self 关系；同一帧可加的 exclusive 分项才能相加，阶段 P99 不相加。enqueue 已嵌在 producer/display 中，不能再把它加到 display 总耗时。RMS 内实际绘制、Map 内即时绘制不得误归为纯 Python 准备。探针和原 profiler 包装开销单列评估；正式对照维持同样的统计配置。

缓存契约清单覆盖 entity 生命周期、组件字段、动画位置、空间记录、Fog journal/epoch、相机、缩放、viewport、阵营、选择、纹理/字体版本及规则配置。E6 保留对象引用不等于保留计算结果有效；不能只靠 reference_version。若使用专用 revision，需先证明所有写入路径和 reset/import 都更新它；每帧 World revision 本身也可能使缓存永远失效。

输出成本表、命中/失效表、绘制顺序契约与候选可移除成本。按**可消除工作减新增准备/失效/发布成本**排序，再锁定一个原型和诊断准备区间。该区间按两侧共有的exclusive语义定义，如入队/打包/清理，不能按候选已删函数计时。派生上限仅用于筛选，不预报整帧收益。原型前把区间、世界输入SHA、镜头脚本SHA、模式、初始缓存状态、两侧相同预备过程和验收门槛写入预注册记录；正式收益分母固定为下述完整显示段，不按候选数据调整。

## 5. P1：收益优先的单点候选

首选研究候选为 **有序绘制命令缓冲，减少对象构造与重复打包**；只有 P0 确认 enqueue/pack/clear 是可测热点才进入。它改变准备表示，实际 `blits`/draw 的工作量和画家顺序保持。

| 顺序 | 候选 | 最小试验与转入条件 |
|---|---|---|
| A，首选 | RMS 普通 blit 准备 | 先保留原命令、复用 frame scratch batch，隔离列表分配；再试入队直接记录有序 plain-blit run，减少 BlitCommand＋二次扫描/tuple准备。两步独立消融，不把已存在的 blits 计为新收益 |
| B | Unit 分组/布局准备 | 若 Unit 静态重复准备更大，先复用不变 hex/world 坐标、组拓扑和布局参数；动态动画、健康/状态、Fog、选择、屏幕坐标按当前输入计算。不跨帧复用完整最终绘制结果 |
| C | UI/Map/Fog 重复准备 | 仅对 P0 实测的失效/重建热点做准确键控；静态 layout/内容与动态字段分开，继承已有字体/标签和 journal patch，不降低刷新频率 |
| 条件 | 小计算 native 批量 | 只有上述消除重复工作后仍有显著纯计算热点才审查窄数组入口；不复制 World、不把 SDL 调用放 worker，精度/舍入与原序需逐项证明 |

A 的私有研究模式暂定 `baseline`、`reuse_batches`、`record_runs`；不支持的命令/消费者保留原表示。模式只作用于指定渲染上下文/当帧，普通窗口默认 baseline。RMS 是全局 singleton，不能由某个 World 设置持久全局模式污染其他实例；比较时需要隔离队列/屏幕上下文，恢复逻辑要覆盖异常与退出。无效模式在任何入队/绘制前拒绝。

必须保留 layer 顺序与同层 painter order；geometry/custom/area/special_flags 是顺序栅栏。不能按纹理全局重排或跨栅栏合批。Surface、Rect/list dest 是执行时仍可变的引用：不得提前截图/冻结坐标，不能只比较入队时值。custom 在执行时修改 Surface/dest、追加命令、切换图层和抛错均需审查；无法证明等价的上下文走原路径。保持单命令与多命令路径、已执行错误前缀和旧队列清理语义。

buffer 的容量和缓存都有预注册上限；成功清理释放实体、Surface、dest和callable引用，错误路径保留原语义而非随意 finally 清空。不保存历史帧命令，不用无界对象池。多实例、reset/close/resize/scene切换必须回收研究资源。

B 必须保留当前静态/动画分类条件与阈值、分组插入次序、静态组先于动画列表的提交顺序；不能仅用 is_moving 或整世界 dirty 替代真实依赖。输入变化导致缓存未命中时正常重算，并把失效维护成本计入完整链。

每轮只推进一个候选。A 收益不足就形成负结果，再按 P0 转 B；不能将多个改造一次合入后只报告合计 FPS。

## 6. P2：正确性、像素和内存先行

使用 E6 完整 ordinary native 生成的展示载荷及原请求轨迹，核对 40994 次请求、9880 tick：完整响应、事件、逐tick展示状态、查询/绘制顺序和最终完整权威export。E6这些已有校验不等于逐tick完整authority导出；E7独立正确性运行另增加逐tick完整native export比较、展示前后权威指纹验证。完整状态比较/哈希均在计时外，保存指纹流与差异快照，不把全部状态历史留在运行缓存。新增命令表示归一化后比较 layer、顺序、Surface内容/尺寸、dest、area、flags 与 custom效果，哈希/像素审查在独立正确性运行中进行。

沿用 E6 固定墙钟和地形配额方法：只冻结动画/选择等读取的游戏墙钟，perf clocks 保持真实；像素运行两侧统一 2048 条目配额、取消地形 1.5ms 截止，以控制同一缓存完成进度。**正式性能与 live 保持原 1.5ms 预算**，逐帧记录工作量/待办/完成进度；受控像素一致不能扩展为真实时间预算下每帧完成进度完全相同。若完成时序不同，明确单列，并确认没有少绘制或延后本应立即更新的内容。

固定镜头沿用 E6 脚本；P0 前另外固定切镜、平移、合法缩放、阵营、单/多选择、HUD变化、resize脚本及 SHA，分别验收稳态与失效期。补充 >20/≤20 丰富模式切换、叠格/移动插值、箭/效果/浮字、透明与裁切/flags、custom修改后续目标、空队列、错误成功前缀、暂停/时间倍率/GameOver、epoch/revision拒绝、reset/close、多实例和场景切换。

内存诊断检查当前驻留内存、tracemalloc当前保留、Surface项数/像素/字节、命令/缓冲容量、待办与弱引用生命周期。重复镜头循环和持续切镜应达到有界平台，不能只用 ru_maxrss 判断无泄漏。冷启动、冷缓存成本单列；正式轨迹预热和慢样本仍全部保留。正确性或长期保留失败即停止采用。

## 7. P3：隔离 E6 的正式收益对照

采用 2×2 分层；层内只改变 E7 显示模式，不跨层归因：

| consumer | 原显示 | E7 candidate | 用途 |
|---|---|---|---|
| ordinary apply | baseline | candidate | **默认路径主结论** |
| E6 reuse_typed | baseline | candidate | 叠加效应与交互，独立报告 |

E6 已使 display 均值改善约 5.99–6.99%，RMS 没有稳定同向收益。禁止拿 ordinary＋旧显示与 typed＋新显示计算“E7提速”。第二层失败则不宣称可叠加，不掩盖第一层结果，也不自动开启 E6。

每层 native1/native4 各三轮，持续独立实例、逐 tick ABBA/BAAB 交替；同扩展、依赖、GC策略、镜头、输入和计时口径。机制消融 `reuse_batches` 与 `record_runs` 单列，不同时调整门槛或缓存容量。保留全部 9880 tick、预热与慢尾。

正式固定重放沿用 E6 的 dummy driver 和2480×1239 Surface，不调用Cocoa flip；以下帧级边界只需共同的少量计时读取，细粒度准备探针关闭。明确公式：

```text
D = screen.fill + display Systems（其中已包含命令入队和即时绘制）
Q = RMS.update（准备、实际提交与清理全计入）
P = dummy 平台边界开销（不调用 display.flip，不代表 Cocoa 呈现耗时）
完整显示段 = D + Q
完整展示链 = decode + apply + D + Q + P
固定轨迹总工作 = request + step + delta_encode + 完整展示链
```

保持E6 chain/total口径；镜头脚本施加、状态/像素哈希、诊断和文件IO在计时外，两侧同样执行。live整帧包含真实清屏、事件处理、Cocoa flip及Agent服务，限帧等待单列排除。准备分项用于独立诊断解释机制，不在正式运行逐命令加计时，也不与D重复相加。正式逐帧工作量只记两侧共有的轻量、无行为影响的计数；详细分配、hit/失效和时间轴放独立诊断。普通 profiler 配置两侧一致。

本轮选择的正式预注册门槛：**每轮完整显示段D＋Q均值至少改善5%、配对改善95%区间下界大于0、P99不回退；完整展示链和固定轨迹总工作同样要求均值改善、区间下界大于0、P99不回退**。5%作用于全部显示工作，约束收益规模；使用D＋Q也能覆盖打包成本移到producer的情况。局部准备分项不承担无诊断净收益门槛。固定镜头与切镜脚本分别通过，不仅检查 pooled 总结果。P99/max 从单次原始样本计算；100-tick分块、10000次bootstrap、seed42，末块按实际大小加权。新增其他阶段成本全部单列，不能只用局部收益掩盖成本转移。

显示段P99/max直接从每个原始帧的 `D_i + Q_i` 求分位数/最大值，不能相加D/Q各自的P99；chain/total也先构造每帧总值再统计。

若 private 模式只在某层或线程配置通过，仅报告该范围。主路径 native4 通过后，做单实例顺序ABBA确认：A/B/B/A各自以独立进程、一个持续实例重放完整轨迹，初始化与缓存预备过程相同；固定镜头和切镜脚本都满足同一均值/区间/P99门槛才进入live。未通过则停止，不补跑择优。

## 8. P4：条件窗口、尾延迟与交付

通过前置门槛后，以 ordinary apply 固定 consumer，native4 baseline/candidate 新做三轮 AB/BA/AB，每次30秒预热＋300秒测量。沿用原5000/1000、Fog、2480×1239 Cocoa、GC、Agent思考/合法动作策略和接入预算。若研究叠加组合，另立实验身份，不能混进普通 consumer 对照。

检查帧 P99≤33.33ms、世界频率≥29.7Hz、观测/相关队列 P99≤100ms，以及完整负载、积压、存活、合法 move/attack、固定模拟时间等全部 guards。全部六次 baseline/candidate 都参与整体窗口结论；真实轨迹不同，只用于运行验收，不冒充固定输入因果比较。

保留 E6 baseline-r2 的帧 P99 37.627ms/max284.162ms、观测/队列超限负结果。新的三轮不是补跑覆盖旧结果。若再次失败，保存慢帧前后事件、exclusive阶段、Agent接纳/服务、cache pending、GC/CPU/平台时间轴，区分产品、harness和平台成本，不先猜GC或强行换allocator。诊断追踪另跑，不污染正式窗口。

按 PROTOCOL 建立 `experiments/2026-10-rust-display-preparation/`（本规划尚未建立正式实验包）：README/manifest/analysis/decision、全部raw/慢样本/失败控制、工具与源码精确SHA、同一wheel或canonical引用、source bundle、内外SHA256SUMS和复算命令。候选不可用同样完整归档负结果；validated tag仅在对应阶段实际验证后创建。

每阶段报告附进度条，更新 handoff、status、活动优先级和 GAP 台账。本次只登记规划与计量审计；没有新增确认玩法GAP或关闭旧GAP。G001–G003历史、G008/G009 OPEN、R001/R002 RISK保持。API18/schema5、普通 step/native默认1、Statistics原策略、规则/观测/动作/RNG/ID顺序与确定性保持；5000Agents暂缓，不更新容量/Frontier，不push/merge。

本轮实施的第一个交付应是 **P0成本表＋缓存/绘制契约＋单一原型选择理由**，之后才做A或B。当前没有已实现的 E7 加速比。

本规划、只读审计工具与派生结果的完整性从Lab根目录验证：`shasum -a 256 -c records/rust-display-preparation-SHA256SUMS`。这不是新正式性能实验的校验清单；正式包在P0实际执行后另建。
