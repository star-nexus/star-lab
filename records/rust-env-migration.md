# Rust 内核＋Python 接口迁移

更新：2026-09-11。用户已批准完整迁移方案。状态：R0 已完成；R1 实施中；尚未交付 Rust 运行后端。

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
| R1 | 工具链、三个 crate、稳定实体 ID、场景导入、生命周期、时钟和随机兼容 | 实施中 |
| R2 | 实时 move/attack/观测、恢复/Fog/死亡/认领权限闭环 | 未开始 |
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
