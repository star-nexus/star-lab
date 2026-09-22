# R3d2b：Rust 离线游戏入口、统计输入与结算

**VALIDATED CHECKPOINT；完整 R3/R4/R5 仍 OPEN。** 2026-09-23。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 功能迁移中 | R4 ░ | R5 ░`。
█完成、▒进行中、░待实施/验收；不是工时百分比。

- 生产仓库：`star-nexus/star`；开发分支 `codex/rust-env-migration`。
- 前置／问题节点：`91dc7688601c93192fea174c69981a315ac80ef9`（R3d2a/API7）。
- 修复／测量／验证节点：`a6bf5f381b0393b0ab93973502d9744d6b9e3713`。
- annotated tag：`rust-kernel-r3d2b-2026-09-23`。
- 场景工具：`2efdb7d6c4a2c7627f8ad033358e183b3fb23ac3`；接口/CLI工具：`2ec41bdc481259440702211ab202cf3c059d7eef`；报告/记录器诊断：`30ab6f8829095384e85662016cfb37150120869a`。最后一个工具节点包含前两工具的相同文件。

## 1. 问题与改动

R3d2a 能建立离线 NativeSession 和绘制 HUD，但普通 GameScene/菜单/命令行还不能选 Rust，统计上报和结束后的结算也未接通。HUD 的 GameStats 是部分派生副本，直接用于结算会丢失完整历史。

本检查点实现：

- `--backend python|rust`、`--native-threads 1|2|4`；显式 Rust 加载失败报错退出，普通启动仍默认 Python。
- GameScene 将本地输入、Rust 模拟、离线结算 host、Python 展示串接，菜单重启保持所选后端；重入会重置结束等待状态。退出和异常关闭会话及旧输入订阅。
- Rust 支持 `strategy_ping`、`report_llm_stats`、`retrieve_game_status`。保留鉴权、Faction计数、重复上报累加、旧限流、错误优先级和大整数统计转换；连接数来自可信入口字段，不能由 Agent 参数伪造。
- host 的 `prepare_game_end` 计算通知目标与收集状态；只产生通知计划，本阶段没有网络发送。epoch 在 native 锁内检查。
- 结束等待到期只导出一次完整权威快照，构造独立的结算视图，复用 Python 报告格式和 JSON/CSV 保存器。该临时 World 不挂模拟 systems，也不写回 Rust；不能从 HUD 小表凑报告。
- 保留当前源码的结算等待 60 墙钟秒语义，包括无 Agent 和已收齐报告的情况。本次没有采用另一历史版本的提前结算规则，也没有修改移动力弱化等玩法。

## 2. 验证与边界

| 验证 | 结果 |
| --- | --- |
| 完整回归 | 1738 passed，含816 Native契约；本阶段新增79项 |
| Rust/静态检查 | 3测试、fmt、Clippy全部通过 |
| 离线场景 | 实时/回合×headless/skip-start/menu，共6例，237次场景更新 |
| 实际显示 | 上述158次窗口场景更新，79次headless场景更新；同一Cocoa引擎进程，后者不是独立dummy驱动 |
| 精确重放 | 6初始快照、510操作节点；状态/结果/展示批次逐项相同，新进程再重放通过 |
| 实际CLI入口 | 实时/回合×headless/skip-start，4独立进程52帧；其中2个dummy、2个Cocoa；模拟dt均1/30 |
| 结算文件 | 6份JSON和6份单行CSV；模式、实验ID、地图、10个存活Unit等核验通过 |
| 截图 | 4PNG，人工检查实时skip-start与回合menu；旧面板遮挡仍存在 |

场景探针使用 chibi-small（15×15，10 Units、0 Agents）、Wei/Shu HUMAN；每场景一次成功本地move，合成SDL V坐标键、回合制SPACE，直接调用菜单/重新开始回调。headless/skip-start seed42，普通菜单沿用现有菜单生成种子，**实际种子保存在各初始快照**。实时超时临时设1模拟秒，回合上限临时设1；检测结束后注入61墙钟秒跳跃来验证等待和结算，绝不把这些计时用于性能结论。

CLI探针调用真实 `rotk_env.main.main()`、真实引擎循环和原参数解析，以chibi-small/seed42、默认human_vs_ai且不开BOT启动；第12帧发合成SDL QUIT，第13帧退出。验证一个Rust世界、固定dt、无failure、世界关闭和pygame释放。不是物理鼠标/键盘人工验收。场景绘制前后全量状态断言及录轨有额外开销，不能据此估算运行FPS。

79新契约覆盖：66统计/结束计划，6完整结算及失败/一次导出，7场景/CLI/拒绝未接host。完整报告对照保留 Python 收集器所有字段，测试跨实时/回合、none/dummy，以及多Agent同Faction、超大计数、部分上报、错误顺序、reset/关闭/旧epoch。没有宣称任意Python对象、整个网络场景和BOT全部兼容。

仍待 R3：网络host与VLM/BOT、动态Player/冷组件的展示覆盖、完整应用集成差分；R4 真并行和成本优化；R5 5000/1000/30Hz容量与跨平台安装。当前1/2/4仍串行Mutex。Chrome保持开启，实验串行。没有新增容量结论或Frontier记录；Python默认、生产main `6a970deaee7d9b8d3939edd102973f2377edd6ac` 不变，未merge/push；49处无关Agent/font删除未提交。

## 3. 源码、安装与日常使用

本机 Apple M4 / 10逻辑CPU / 16GiB / macOS26.5.2 ARM64 / CPython3.13.12。详见 `results/environment.json`。release wheel为本机CPython3.13专用；Linux和3.14仍待R5。API8/schema5，oracle `python-r0c-3cc4ffe`；扩展SHA256 `f9e7169fab2f2f154baf582d5578201a9fc3a0dfb868f7cc0f72cb3851baf46c`。

```sh
cd /Users/liyang/Developer/star-main
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-r3d2b a6bf5f381b0393b0ab93973502d9744d6b9e3713
cd /Users/liyang/Developer/star-lab/runs/repro-r3d2b
uv sync --locked
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-host/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python -m pytest -q
```

日常离线试玩（当前已准备好的完整checkout为 `runs/star-rust-r3-host`）：

```sh
cd /Users/liyang/Developer/star-lab/runs/star-rust-r3-host
.venv/bin/python -m rotk_env.main --backend rust --no-hub --skip-start --mode real_time --scenario chibi-small --seed 42
```

`--mode turn_based`选择回合制；加`--headless`使用dummy。去掉`--skip-start`可进入菜单，需在菜单选择离线控制器；菜单配置沿用现有行为。`--no-hub`不启用BOT，对手不会自动行动；需要自主双方操作可在菜单设双方Human。Rust暂拒绝Hub、`--mock-ai`和旧scale harness。活动生产目录原有字体/Agent删除不影响此完整checkout，不要为了运行覆盖这些删除。

从源码构建与Rust检查（确保固定工具链位于PATH，本次使用 `$HOME/.cargo/bin/cargo`）：

```sh
export PATH="$HOME/.cargo/bin:$PATH"
uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /Users/liyang/Developer/star-lab/runs/repro-r3d2b-wheel
cargo test -p star-core -p star-rotk --locked
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked -- -D warnings
```

## 4. 探针与预期签名

```sh
cd /Users/liyang/Developer/star-lab
git worktree add --detach runs/repro-r3d2b-tools 30ab6f8829095384e85662016cfb37150120869a
cd /Users/liyang/Developer/star-lab/runs/repro-r3d2b
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d2b-tools/tools/rust_migration/r3_scene_host_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d2b --output /Users/liyang/Developer/star-lab/runs/repro-r3d2b-window
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d2b-tools/tools/rust_migration/r3_scene_host_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d2b --output /Users/liyang/Developer/star-lab/runs/repro-r3d2b-replay --replay /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-host/results/window/trace.json.xz
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d2b-tools/tools/rust_migration/r3_host_interface_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d2b --output /Users/liyang/Developer/star-lab/runs/repro-r3d2b-after.json
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d2b-tools/tools/rust_migration/r3_host_interface_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d2b --output /Users/liyang/Developer/star-lab/runs/repro-r3d2b-cli.json --entry headless --mode real_time
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d2b-tools/tools/rust_migration/r3_host_artifact_check.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d2b --window /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-host/results/window --output /Users/liyang/Developer/star-lab/runs/repro-r3d2b-artifact-check.json
```

CLI工具将`--entry`和`--mode`依次设为headless/skip-start、real_time/turn_based执行四例，进程串行。默认capability探针无窗口，不属于容量测试。

before复现：按同样步骤创建 `91dc7688601c93192fea174c69981a315ac80ef9` 的干净worktree，`uv sync --locked`，安装相邻 `../2026-09-rust-r3-session/artifacts/` 的API7归档wheel；同一interface探针换解释器/source/output运行。已有完整checkout为 `runs/star-rust-r3-session`。预期before CLI退出2、三个系统动作均unknown、无prepare_game_end；after CLI识别rust、三个动作成功、具备完整report_context与结束计划。A/B只判断能力，不把不同初始化墙钟的状态当数值性能对照。

## 5. 证据与完整性

入口 `results/summary.json`；配置/guard见 `results/window/compact.json`；新进程结果 `results/replay.json`。压缩轨迹55564字节，解压41856116字节；压缩SHA `4cb6f2791fcfcff36b22b67983b55871e2416a7498b010ed0a8981039e142e83`，解压SHA `09405465b8f695760c67ffc8d8831210c82f86988482074b37992832909015c5`。所有正式小型数据、报告、截图、wheel及保留的中间日志均列入SHA256SUMS。

第一次六场景有效执行后，记录器把显式None的wall_time留在轨迹中，重放读到真实时间，失败且未保存轨迹；保留 `results/intermediate/recorder-missing-time.log`，仅用于追溯，不作为正式通过证据。工具旧节点963ea2b，新场景工具2efdb7d显式记录注入时间并在重放前落盘。故障注入将正式轨迹第一个step的wall_time改回None，精确定位到UnitObservation.last_seen_time差异，见 `results/artifact-check.json`。没有据此修改Rust算法或放宽差分标准。

```sh
cd /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-host
shasum -a 256 -c artifacts/SHA256SUMS
```
