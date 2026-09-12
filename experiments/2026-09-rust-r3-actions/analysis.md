# Analysis — R3a动作和回合兼容

## 1. 实际观察

R2e在注册并启用rest后抛出未实现错误；R3a返回休息成功。1298完整回归、27配置1524逐操作节点及独立Rust重放通过。每一节点都比较完整导入世界、解码响应和事件顺序，不能由“最终结果看起来相同”替代。

## 2. 为什么按Python实际行为迁移

合理猜测的玩法可能与现有代码不同。直接把技能实现为可用、把休息实现为回血、统一人工与Agent回合重置时机，都会破坏oracle一致性。测试显示应保留以下差异，另开规则变更时再处理：

- rest只增加wait_turns；连续两次清除enum CONFUSION，不扣AP、不恢复SP。raw字符串confusion不是enum，不被清除。
- Agent occupy立即占领当前/相邻位置；Framework start_capture必须站在目标格，创建CaptureAction，在后续tick完成。城市task记录cost=2，原实际AP消费仍是1。
- realtime fortify检查AP/CP但不消费；turn模式各消费1。成功响应再减1AP，因此报告值比真实状态低1。工事始终建立level1，已fortified不能升级，没有新增距离检查。
- 技能helper返回success，handler读取result，合法地形也会“Skill execution failed”，不进入AP/SP/CD写入分支。迁移保持这个问题，没有实现注释里描述的隐藏、落石伤害或闪避效果。
- 捕获Unit消失：销毁计时实体但不清除格子的being_captured；Unit移开：取消标记再销毁任务。禁用TerritorySystem只停止update，不禁止直接调用动作。
- Agent end_turn仅round回到首阵营时重置；人工end-turn先重置再判结束。事件/统计记录在round递增前，GameTime的round在下一tick同步。回合时长float sum保持CPython3.13的补偿求和规则。

这些不是新规则，也不代表推荐继续保留全部历史行为。用户已要求迁移时保持现有玩法，因此本轮只记录、测试，不擅自修正。

## 3. 联动与复杂度

TerritoryControl/ConstructionPoints/CaptureAction转成Rust权威组件，领地攻防加成接入既有战斗计算。初始化/reset时建立unfinished capture ID有序集合；每步只遍历活动任务，按外部ID提交变化。地图lookup和Player表复用先前建立的数据，不每帧全量排序。此处O(active)是代码结构结论，不是测量到的P99收益。

R3a新增schema/API3，拒绝R2与早期R3接口被误配。规则oracle标识仍是R0b，版本拒绝针对接口/导入契约，未改变玩法。

## 4. 证据范围

动作族840节点；回合族684节点；实际重新执行全部1524节点并核验归档对应响应、状态、事件与不同线程配置摘要。132新增动作契约另覆盖缺失组件、参数类型/权限顺序、不同地形、技能两套CD门槛、攻击与领地、捕获者死亡等；14回合契约覆盖轮转、终局和人工重置先后。

局限：小场景、无真实窗口/LLM/Hub，未验证真实窗口攻击特效实体生命周期；没有5000规模测量。1/2/4仍由同一互斥写入路径执行，不构成并行加速证据。极端非规范组件值/Python特有非JSON参数不是本轮新增全覆盖承诺。

## 5. 原始证据

见[raw](results/probe.json.gz)、[compact](results/probe.summary.json)、[replay](results/replay.json)、[回归日志](results/full-regression.log)。source/tool/wheel精确身份与hash见[manifest](manifest.yaml)。
