# 并行观测第一版：实施与验证记录

更新：2026-09-11。用户已授权实现第一版并新开Git分支。
生产分支`codex/parallel-observation-v1`，起点`6a970deaee7d9b8d3939edd102973f2377edd6ac`。
本记录随验证结果更新；不表示已合并或获得容量认证。

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

下一步：固定版本并完成正式冻结对照。若复制/还原抵消并行收益，本阶段保留分支和证据，不合并main、不宣称24/30Hz提升；后续先讨论/验证更便宜的快照边界。
