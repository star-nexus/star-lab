# Decision — R3d2b 离线入口检查点

**Accepted，2026-09-23。** 生产 `a6bf5f381b0393b0ab93973502d9744d6b9e3713`，tag `rust-kernel-r3d2b-2026-09-23`。

## 1. Decision

固定离线可玩检查点：NativeSession拥有Rust权威世界，GameScene调用明确输入/step/host/展示边界；统计系统动作由Rust处理；结束时一次导出完整权威数据，Python负责既有报告格式和文件输出。保持Python默认，不合并main。

进度：`R0 █ | R1 █ | R2/R3 ▒ 功能迁移中 | R4 ░ | R5 ░`，不计工时百分比。

## 2. Alternatives and evidence

| 选项 | 依据 | 决定 |
| --- | --- | --- |
| HUD小表直接结算 | 缺少完整历史；契约主动破坏HUD仍须产生真实报告 | 拒绝 |
| 每帧导出全部权威状态 | 报告仅到期使用；一次导出契约通过，无常规帧需求 | 拒绝 |
| 临时挂回Python玩法/统计system | 会创建第二写入者，破坏迁移权威边界 | 拒绝 |
| 到期导出独立只读报告视图 | 6完整报告契约、6实际场景文件和精确轨迹通过 | 采用 |
| 弱化重放比较以忽略失败 | 故障为记录器没有保存实际墙钟；显式记录即可精确重放 | 拒绝 |

## 3. Headroom and trade-offs

没有本轮容量或线程数的最小充分值结论；操作设置仍1线程，全部线程设置仍串行Mutex。默认Python，Rust实验入口需明确选择和匹配API8扩展。结束报告会做一次全量复制，属于到期工作；最终容量测量需要明确是否覆盖结算窗口，不能隐藏成本。保留旧60秒等待与重复统计累加等现有语义。

## 4. Revisit

接入联网host时验证可信身份/连接数、game-end通知发送及重试、回合ACK、退出/故障；完成VLM/BOT和动态Player/冷组件派生覆盖后再做完整应用差分。R4测真实并行成本和确定性，R5验收5000/1000/30Hz、macOS/Linux和CPython3.13/3.14。通过全部门槛前不改变默认或合并。

依据：[README](README.md)、[analysis](analysis.md)、[manifest](manifest.yaml)、`results/summary.json`。原并行观测负结果和各历史tag保持不动。
