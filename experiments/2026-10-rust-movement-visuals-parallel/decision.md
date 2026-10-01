# E5 决策：Movement ∥ Visuals

**Status:** accepted — negative adoption result  
**Date:** 2026-10-02  
**Measurement source:** 94913a4f836a3c106e08a1334cb81971cfd728c3  
**Validated source:** 3b167b151c3bc32e1d54f6015d0f15d2c3dd6a74  
**Tag:** rust-parallel-e5-movement-visuals-2026-10-02

## Decision

完成四模式原型和研究，保留私有按次接口，普通step不启用E5。native2/4三轮主对照均仅一轮完整通过；0/4/16六个单轮敏感性均未通过。native4未通过前置门槛，因此不进入单实例ABBA确认或实际窗口验收；此停止符合预注册计划。机制验证成功，但没有稳定净收益证据，不外推所有System之间并行无价值。

四种私有模式均按次生效。普通step和默认native1维持原先System顺序，Statistics
内部纯记录并行沿用E2门槛128；没有新线程池或通用Bevy Schedule。5000Agents暂缓。

## Alternatives and threshold

* baseline：旧顺序、旧即时World操作，作为四模式基线。
* empty_fork：空worker与Movement重叠，之后旧Visuals；只是派发解释对照。
* split_serial：窄准备、原序Movement、计划Visuals、原序发布；隔离拆分成本。
* parallel：计划Visuals与Movement实际重叠；相对同模式禁用门槛判断最终净收益。

首选门槛8来自E3覆盖率与条件预算，不是生产充分值。0/4/16只做单轮敏感性，
任何有利点都需要新的预注册三轮研究，不能事后取赢家替代本轮门槛。

## Review trigger / risks

在相同规则下出现显著更多同tick Visuals工作，或已有pool的scoped派发/发布成本
显著下降时复审。先做无诊断完整step净收益，再做单实例确认，最后窗口guards。
派发策略、allocator和OS核心分配均可能影响尾部；不通过门槛就保持研究路径关闭。
混合实体、ID耗尽和失败成功前缀继续属于不可放宽的正确性边界。

本轮不会因回归或机制验证通过而关闭既有GAP、改变容量/Frontier或切换默认后端。
原49删除、E2/E3标签及两冻结实验目录保留，不push/merge。
