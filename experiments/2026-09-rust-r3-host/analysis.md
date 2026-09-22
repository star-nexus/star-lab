# Analysis — 离线 Rust host 接入

## 1. Observation

前置API7探针完成注册后，strategy_ping、report_llm_stats、retrieve_game_status均返回unknown action；CLI不识别backend选项。新版API8同条件全部成功。六场景生成结算并退出，逐操作重放510节点通过，四CLI独立进程固定dt/资源释放通过。

## 2. Competing hypotheses

- H1：完整结算可以直接消费HUD副本。HUD只提供小表与战报增量，缺少完整统计历史；因此不足以生成旧报告。
- H2：需要每帧同步完整世界才能让旧报告工作。报告只在结束等待后构建，一次导出即可获得权威完整数据；无须每帧开销。
- H3：初版场景重放失败来自Rust非确定性。修正仅涉及Lab时间记录，生产SHA/扩展不变；故障注入定位到外部墙钟字段。

## 3. Instrumentation

生产新增契约将Python真实handler与Rust完整响应及权威状态逐项对照。结算契约在HUD初始单位计数字段被清空后仍验证报告真实初始数量，并计数export调用：等待中0次、到期1次、后续0次。场景工具记录完整初始状态及每次step/control/turn/end-plan/display增量，渲染前后断言权威不变。独立进程重放序列化轨迹，比较完整状态、结果和展示增量。

## 4. Evidence

- 1738回归通过，79新增契约分别覆盖统计66、结算6、场景7；另3Rust/fmt/Clippy通过。
- 66统计契约覆盖多Agent同阵营累加/重复上报/注册与连接数不同/鉴权顺序/大整数/比例舍入/结束目标选择/旧epoch拒绝。
- 六场景237更新、510操作、6初始快照；158为窗口配置，79为同Cocoa引擎中的headless配置。四CLI另验证真实dummy/Cocoa驱动各两进程，总52帧。
- 六份JSON/CSV报告对应ID、模式、地图、单位数相同；两种模式都通过退出/订阅清理。无Agent场景结合含Agent数据的完整报告契约；不能代替联网集成。
- 记录器故障注入输出第一差异为 `$.entities[227].components.UnitObservation.last_seen_time`；expected等于记录的注入wall_time，actual为重放进程真实时间。

## 5. Root cause / causal chain

前置缺少应用host边界，导致已有Rust模拟不能进入普通应用入口；派生HUD又不具备结算所需完整历史。新增单一权威世界的场景编排，加结束时一次独立数据导出，补齐离线生命周期。没有挂回Python玩法system。

初版重放失败的链条是：NativeSession显式传wall_time=None → Lab使用setdefault未替换None → 记录器运行时被patch的time.time提供注入值 → 重放时None重新读取真实时间 → 时间戳字段不同。显式记录注入值修复问题；没有采用浮点容差或忽略字段。

## 6. Rejected explanations / limits

无需给Rust换随机算法来解决这个记录器问题；无需将HUD改成每帧全量镜像。未做后端FPS A/B，初始化、轨迹、截图、完整状态断言使场景探针无法用于容量推论。1/2/4配置依然串行。报告格式/输出仍在Python，游戏状态和规则统计在Rust。VLM、BOT、网络投递、动态冷组件覆盖、并行与安装验收仍待继续。

原始证据与版本均见 [manifest](manifest.yaml)、[复现](README.md) 和 results/；此前API7历史证据保持原路径。
