# Decision — first optimization round retained; capacity goal OPEN

保留并集成有明确因果证据和等价性契约的改动：

1. `get_faction_state(unit_ids=...)` 明确投影自身单位面板；省略时保持兼容，共享视野完全保留。
2. 重用已维护空间索引生成 reachable、筛选 attackable 候选；最终合法性仍由原有 oracle 判定。
3. move 目标占用与路径阻挡重用空间索引；不改变友军穿越/任意阵营目标占用规则。
4. 请求内只做一次实时阵营统计；不缓存会失效的 AP/存活/阵营值。
5. ENV action catalog 和参考 Agent JSON schema 支持 integer array，用户文档同步。

静态 interleaved 相同 selected scope 的原始字节数、可达/可攻击输出保持一致；
selected scope 相比 full faction 是显式投影，不包装成等载荷加速。
所有生产变更保持原四层。Lab 不进入生产依赖；生产没有实验工具/fixture/raw。

## 集成回执

- main before: `02d0fc1b598c54a172e1122ac9ea4c1e2f46ec15`
- timed implementation: `e8b48c0568fb8830055bf053a724acc2b4e5c04c`
- development tip: `c9737451de97f1b1903123377a1514227c3ffdf5`（最后一提交仅注释和文档）
- annotated pre-merge tag: `p3-observation-pre-squash-2026-09-09`
- integration: `git merge --squash codex/p3-agent-observation`
- main after: `08c857e5df39f671c5a13bf04b9af9aac0800e78`
- 集成树与 tagged developer tree 完全一致；主提交只有一个 parent。
- 集成后回归、compileall、diff 检查见 [integration-validation.json](results/integration-validation.json)。
- 881 production tests、81 performance contracts、7 Lab scheduling/archive tests通过；这些集合存在重叠，不相加。

## 未完成与下一项工程

千 Agent /3000–5000 Units /1Hz观测仍未达到要求；10K Agent也未达到。
P3容量目标保持OPEN；本轮只关闭局部复杂度优化和测量基线工作，不声明整个P3完成。
P1/P2跳过；网络/Hub、长时soak、100%移动+Agent观测组合容量均未验证。
不新增性能 Frontier，也不将 pre-squash tag 命名为容量达标 tag。

下一项在相同1Hz负载上设计并测量**同一世界快照下按阵营共享观测构建**：
共享地形/可见敌人/阵营统计与每Agent的owner/commandable/所控Unit affordance分开。
首先确定显式只读批次和失效边界，覆盖位置、Fog、AP/MP、阵营、所有权、死亡/替换，
再比较批次构建与JSON分发成本；不复用跨世界写入的过期合法性，不通过丢观测或改变Fog语义达标。
此设计尚未实现；其生产接口和契约需要下一轮代码/性能证据，不在本次已合并修改中。

如基线通过，再扩大到5/10/30Hz和高密度场景，并按原先1×300s+3×60s条件验证候选。
