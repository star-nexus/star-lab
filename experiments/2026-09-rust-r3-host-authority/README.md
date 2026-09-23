# R3d4a — Rust宿主权威接口，Python保留连接编排

**VALIDATED检查点；G009网络集成及完整R3仍OPEN。** 最终 `5ce4b3f02a5fb676e11c8bc240e86513d3e00b25` / annotated tag `rust-kernel-r3d4a-2026-09-24`。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 功能迁移中 | R4 ░ | R5 ░`（非工时百分比）。

## 问题与边界

G009的下一步需要网络宿主读取当前回合、通知候选和消息计数。API11没有相应Rust宿主接口，离线结算还依赖可变Python展示GameState来判定是否结束。继续读取/修改Python ECS会恢复双重权威；每条消息导出整个世界则会增加跨语言开销。

本阶段新增 `host_status`、`record_message`、`turn_start_context`：Rust持有权威判断与统计，Python保留连接、可信身份提取、owner线程接纳、set去重、在线过滤和未来ACK/重试。离线结算已使用四字段权威状态；完整报告仍按既有60墙钟秒策略仅导出一次。没有新增轮询Agent观测、取消移动弱化或调整CD规则。

## 版本与环境

实现/构建 `97f45b1`；测试修正和测量 `343ced3809f0ddf57c53036613abea2f9280daf5`；最终仅两份文档变化。build→measure只改测试第一阵营设定，运行代码一致，manifest保存精确SHA与空diff证明。工具 `a080d3bb1853b08442efd49b58d760813ebe8a3e`。前置完整checkout `30c4b76c152857c98ff45fc7952af9ceb758059e` / API11；之后的用户边界说明提交只改文档，因此前置运行行为一致。

Mac mini M4/16GiB/macOS26.5.2、CPython3.13.12、Rust1.98.1、API12/schema5；Chrome保持开启，测试/构建/窗口实验串行。扩展SHA256 `dd583a3adcb9064e3d4320e3e5a5eb9f12c032247d93356398c65c75c1a44cda`。普通启动仍默认Python，1/2/4线程配置仍为串行Mutex，不宣称并行加速。

## 证据与结果

| 检查 | 结果 |
| --- | --- |
| 完整回归 | 1979通过；Native1057，其中新增44；50项针对性通过 |
| Rust/fmt/Clippy | 3 Rust测试、格式、全workspace Clippy通过 |
| before/after | none/dummy/window配置×1/2/4，共9组；宿主接口0/9→9/9可用 |
| 消息状态 | 45次；旧版无接口不能记录→新版45/45完整状态与错误一致 |
| 回合通知 | 18次；新版通知内容和同进程发送顺序与Python一致 |
| 旧场景轨迹 | 6场景510节点精确重放通过 |
| 新场景 | 实时/回合×headless/跳过菜单/菜单，237次更新、510节点；独立新进程再次重放通过 |
| 展示/报告 | Cocoa运行；158窗口配置更新+79同一Cocoa引擎headless配置更新，4PNG、6JSON+6CSV；未称独立dummy驱动验收 |

实际窗口采用合成SDL事件/直接菜单回调、注入墙钟推进结算等待。截图抽查可见地形、单位、坐标、移动区域和HUD。没有真实网络、LLM、物理输入或容量结论。初次测试中的起始阵营假设和一次错用旧venv均为setup-error，不纳入正式before/after因果证据。

## Benchmark兼容与复杂度

单条消息执行后计数，批次执行前计数；未注册非空sender先增加个人计数再报错，首次注册放批次可能在旧host提前失败。本阶段保留该行为，支持超过u64的原整数计数。动作计数不变。

重新注册改变stats映射，但原阵营registry条目保留。通知候选按原registry→stats顺序返回，Python逐项add入set后再过滤在线Agent，保留原同进程发送次序；Python字符串hash seed仍可能改变跨进程次序。它是原有未规范网络行为，不是本次新增玩法。不得把候选直接排序后宣称等价，或宣称历史评测排名已受/未受影响。[生产GAP台账](../../../star-main/docs/native-benchmark-gaps.md)持续记录。

`host_status`只读singleton且结果固定4字段；消息只更新计数；回合候选仍O(注册Agents)，只在交接读取，不是每帧扫描Units。这里只确认代码边界与功能，未测端到端收益。两次API调用不是事务；未来owner宿主必须在成功end_turn后、下一次写入前读取通知上下文。

## 精确复现

```sh
cd /Users/liyang/Developer/star-main
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-r3d4a 343ced3809f0ddf57c53036613abea2f9280daf5
cd /Users/liyang/Developer/star-lab/runs/repro-r3d4a
uv sync --locked
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-host-authority/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python -m pytest -q
.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/r3_host_authority_probe.py --source . --output /Users/liyang/Developer/star-lab/runs/repro-r3d4a-results --expect-supported
```

精确工具可由Lab `a080d3bb1853b08442efd49b58d760813ebe8a3e` 新建worktree取得；旧源码用 `30c4b76c152857c98ff45fc7952af9ceb758059e` 和R3d3c唯一wheel归档，probe省略`--expect-supported`。源码构建、两边probe、cargo检查和场景重放完整argv/cwd在 `results/commands.json`。旧轨迹引用R3d3c原归档，不重复复制。`SHA256SUMS`涵盖本目录全部证据（清单自身除外）。

当前完整试玩目录 `/Users/liyang/Developer/star-lab/runs/star-rust-r3-host-authority` 已切到最终tag，活动生产venv也安装API12；旧目录/wheel/tag保持原状。main未变、未merge/push，生产49处Agent/font删除保留。

## 决策与下一步

保留Rust权威接口与Python上层组织。G009仍须接通真实owner线程消息宿主、身份/计数、ACK重试、结束通知及错误/关闭路径；不能直接让websocket线程截图。随后继续G008 BOT策略桥接、R002动态冷组件审计，完整R3后才进入R4真并行和R5容量/平台安装。首关仍5000Units+1000Agents/30Hz/30秒闭环；5000Agents是单列扩展目标，未通过。
