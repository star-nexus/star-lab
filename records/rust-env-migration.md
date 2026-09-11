# Rust 内核＋Python 接口迁移

更新：2026-09-11。用户已批准完整迁移方案。状态：R0/R1 已完成；R2 实施中；Rust 尚不可运行完整游戏。

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
| R2 | 实时 move/attack/观测、恢复/Fog/死亡/认领权限闭环 | 实施中 |
| R3 | 回合、完整当前玩法、BOT/结算、Python 窗口增量展示 | 未开始 |
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
Fog保留各Unit贡献、阵营union/探索、LOS、LRU、dirty；统计保留战斗/移动记录、普通/窗口差异和采样中途reset。bootstrap同时保留GameStats动态注册字段。所有数据Rust持有，墙钟只是统计元数据，CD仍用模拟时间。
仍缺可信Agent接口、完整观测/权限、Realtime/Turn生命周期、战斗窗口实体与Fog展示增量。R2未完成、尚不可完整游戏、无性能结论。下一步完成注册/认领和观测/动作边界，再全世界重放及合成Agent闭环。现存无关Agent/font删除未提交；正式checkout在`runs/star-rust-r2-vision-stats`。没有main合并、推送或默认切换。

## R0b补充规范化（2026-09-12）

迁移完整观测时发现R0漏掉多技能set输出排序，已独立修正并归档旧版反例：新oracle `17b17766923ce4db05efb17aaf023818cf69cdf6` / `rust-python-oracle-r0b-2026-09-12`，1047完整回归通过。[证据/复现](../experiments/2026-09-rust-r0b-skill-order/README.md)。旧R0/早期重放保留，不能再描述成覆盖全部可选多技能状态。后续native规则标识改为`python-r0b-17b1776`，显式拒绝混用旧版扩展。

活动R2c代码已加入typed TeamCoordination（认领反向索引/原队列maxlen）、只读批次 faction projection，并通过28项新增契约。尚未完成正式身份认证/注册分发与完整Agent闭环；私有probe不能接Agent。目前仍在开发，待完整回归和差分trace归档后固定检查点。
