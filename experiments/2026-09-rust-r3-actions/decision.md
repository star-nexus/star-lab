# Decision — 固定R3a功能检查点，继续窗口迁移

**Status:** accepted intermediate checkpoint

**Decision date:** 2026-09-13

**Validated STAR commit:** `7f4ad57bbd6966748c0fb49deb82f6ad43fc7aee`

**Annotated tag:** `rust-kernel-r3a-2026-09-13`

## 1. 决策

保留通过差分和完整回归的回合、rest/occupy/fortify/skill接口及计时占领，继续R3余下观测、窗口、BOT与结算。Python仍为默认，main不变。阶段检查点不等于完整R3完成，不进入R5默认切换。

## 2. 依据和取舍

1524节点完整状态/响应/事件一致，1298回归通过，原轨迹可从归档初始状态和有序输入完整重放。保留既有技能返回字段等历史问题，避免把规则修复混入迁移；后续经明确规则决策单独修改Python oracle/版本，再更新对应Rust规则。

不采用统一人工/Agent重置、实时工事自动扣费、技能自动修复等改动。本轮没有对这些替代规则做性能测量，不能给出优劣容量判断。主动集合只承担计时捕获任务，未来增加动态任务/删除入口时必须同步维护集合。

## 3. 尚待完成

其他观测变体、BOT/结算与真正窗口输入/输出；战斗展示实体ID/生命周期、Fog展示增量等仍未迁移。完成单线程等价后再做R4并行/成本优化，R5执行完整5000/1000/30Hz门槛和平台wheel验证。没有选择生产默认线程数，也没有任何新的容量认证。

## 4. 复审条件与追溯

当技能/工事/占领规则获准改变、新增捕获实体生命周期命令、display路径变化、观测schema变化时重新核验对应轨迹。旧检查点/tag/wheel不覆盖。最终集成仍先annotated tag，再仅squash merge；本轮未合并或推送。

[复现](README.md) · [分析](analysis.md) · [manifest](manifest.yaml) · [raw](results/probe.json.gz)
