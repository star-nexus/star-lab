# 并行观测第一版：实施与验证记录

更新：2026-09-11。用户已授权实现第一版并新开Git分支。
生产分支`codex/parallel-observation-v1`，起点`6a970deaee7d9b8d3939edd102973f2377edd6ac`。
本阶段已完成：功能原型和冻结成本门槛验证，结论为性能负结果；未合并、无容量认证。

## 已实现的边界

- 新增本地可选ParallelObservationService：spawn进程池、显式warmup、有界在途请求、每Agent最多一个在途观测。
- 通过原LLMSystem身份/阵营/模式门禁，owner执行prepare_faction_state；worker复用build_faction_state、移动/攻击合法性规则。
- 每次接纳在owner同步pickle成独立bytes，再交给进程池；禁止后台pickle活组件。snapshot_id为service UUID、World.revision及接纳序号，每次重新冻结，不依赖revision覆盖所有就地写入。
- 仅导出全Unit核心字段、所选Unit面板字段、请求方Fog、最近三条BattleLog、GameState/Winner和占用索引。静态地图/规则在worker启动时加载。
- Worker只还原窄只读接口，无真实World/渲染/网络/事件订阅。局部派生缓存属于worker，不跨任务复用动态事实。
- world reset、地图替换/显式失效、规则变化使旧service和结果交付失效。Future显式暴露worker异常；无自动动作重试。
- 生产默认调用方式不变，未接Hub，未修改模拟时钟和Agent思考策略。

## 验证顺序调整

方案A/B/C的最终对照口径保留，但本轮先实现B的快照等价与冻结成本探针，再决定是否投入A的客户端隔离和C动态闭环。这是因为导出成本本身就能否决本次实现，不应先为它搭建完整异步仿真客户端。

当前版本每请求一份动态快照，没有实现连续只读请求共享版本，也没有增量镜像。复杂度仍O(全部Units+所选面板+观测方Fog+占用)。这是待测成本，不是O(active)实现。

两次带dirty标记的冒烟只用于排除实现问题，不作为正式证据。第一种具名字段打包成本较高，已改为紧凑字段元组和worker按需还原。正式对照将使用固定干净source/tooling SHA，串行执行0/1/2/4 worker冻结探针，保留所有字段等价检查、导出/还原/IPC成本和负结果。

## 完成结果

- 功能source/开发tip：`3c4fba1a40fccee7bfc06575ade338c30a4b784e`，936项全量回归通过，其中24项新增并行契约。
- annotated tag：`p3-parallel-observation-v1-prototype-2026-09-11`，对象7427d5bc4337f44af06eff701ff2a92ccdc74cd0；仅标记原型和负性能证据，不标记实时达标。
- 主测量工具：`57343ce1b18f457b745391b5352081f547e40b45`；两轮0/1/2/4 worker，每组120查询，共960次输出等价且guard全通过。前一轮工具734f5c21dc29757501cf39859fa06a54077d0141的960次结果同样保留。
- 5000存活Units、1000注册Agent、三个阵营轮转查询120个Agent，冻结世界且最多4个在途请求。串行141.12–141.65次/秒；2worker51.25–52.18；4worker62.31–62.65。不是动态闭环，不是1000Agent同时请求。
- 2worker时owner每查询导出均值8.52–8.54ms，worker还原11.44–11.69ms，超过串行构建均值5.52–5.55ms。按需组件还原的一部分计在worker build，不能简单当作纯业务耗时。
- 决策：保留分支，不合并main，不启动该实现的独立客户端/动态闭环，不宣称24/30Hz改善。下一候选为同一只读批次摊薄导出或覆盖完整写入的增量镜像；尚未实施。

[报告与复现](../experiments/2026-09-parallel-observation-v1/README.md)、[分析](../experiments/2026-09-parallel-observation-v1/analysis.md)、[决策](../experiments/2026-09-parallel-observation-v1/decision.md)。Raw/compact均已归档、从raw重算和校验；fixture引用已有canonical归档。

生产main仍6a970deaee7d9b8d3939edd102973f2377edd6ac。当前工作目录位于开发分支，普通运行入口仍同步；并行需要显式使用`docs/parallel-observation.md`中的本地API。本轮分支、tag与Lab提交均仅在本地，未推送。
