# R3d2a：离线场景生命周期与 HUD 增量

**VALIDATED CHECKPOINT；完整 R3/R4/R5 仍 OPEN。** 2026-09-22。
生产 `91dc7688601c93192fea174c69981a315ac80ef9`，annotated tag `rust-kernel-r3d2a-2026-09-22`。
前置 R3d1 `c5ae37f5fab2e3563af136f8868d8fc7227c1f23`。
窗口/重放工具 `ab0567f37173d8a86c2baccbfafa113580e894ea`；HUD结构探针 `f7784415a10541835424ec106bc93a8a9b3cab1d`。
后一个节点未改变窗口/重放工具，可用于复现两个探针。

## 改动与验证

Rust展示增量新增 `hud`：阵营统计小表、模拟总时间、一次战报基线和后续追加条目。`NativeSession` 完成一次场景准备、Rust导入、Python纯展示/input系统挂接和关闭；支持none/dummy/window，准备阶段禁止Hub/BOT。旧Python模拟系统及订阅退役，工具栏实体不重复分配。初始化异常清理部分订阅；Native输入异常关闭权威实例，在下一场景边界重新抛出，避免旧EventBus打印错误后继续模拟。

- 1659完整回归，其中737 Native、41新契约；3Rust测试、Clippy、fmt通过。
- 标准chibi-small/seed42、10 Units/0 Agents、window：实时/回合×1/2/4线程设置，6场景540 Cocoa帧。每场景一次成功移动、一次Fog关闭、一次等待、90 ticks。
- 移动到达、HUD数据相等、每帧绘制不改权威状态、关闭恢复订阅均有断言。
- 558操作节点及6份初始化快照，从序列化数据独立重建Rust重放；完整权威状态、结果和每批展示增量相同。新进程读取压缩trace再次通过。
- HUD结构对照：0与10000条战斗历史、各0与10000条观测历史，首批HUD均485字节、空闲HUD均102字节。这里只是小场景初始化时的结构大小，不是通用响应大小或时延结论；权威历史完整保留。

简要入口 `results/summary.json`，配置/guard/raw引用 `results/window/compact.json`。Raw `results/window/replay.json.xz` 为45704字节，解压47099306字节，SHA见manifest。6张PNG归档，检查实时统计/战报与回合制到达后的战报/坐标。沿用旧面板布局，截图仍可见面板互相遮挡；未宣称UI排版重新验收。

## 边界

这是R3d2的离线会话子检查点，GameScene/菜单/CLI后端切换、VLM、BOT、Hub host和结束后通知/报告仍待完成。展示GameStats是部分副本，不能直接用于完整结算。窗口探针直接调用可信本地命令，不含物理鼠标或合成SDL事件链；输入事件链沿用R3d1证据，本轮新增异常事件契约。1/2/4仍串行Mutex；逐配置独立重放不等于并行加速或带不同墙钟元数据的跨配置逐位一致。

没有5000/1000容量、时延门槛或跨平台安装认证。Chrome保持开启，正式负载串行。第一次工具错误地对文件Path调用JSON摘要，在第一帧截图校验失败，属于一次性工具调试，不作实验结论；正式结果为修复后完整重跑。默认Python/main、MP弱化等规则不变，49处无关删除未提交。

## 复现

```sh
cd /Users/liyang/Developer/star-main
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-r3d2a 91dc7688601c93192fea174c69981a315ac80ef9
cd /Users/liyang/Developer/star-lab/runs/repro-r3d2a
uv sync --locked
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-session/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python -m pytest -q
```

本机macOS ARM64/CPython3.13归档release wheel，扩展SHA `d95330879ebd9427233e8aade3bb075233fbd52ca741d197086e0ce0a01627e3`。
源码构建：固定工具链在PATH，运行 `uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /absolute/output` 并安装wheel。
Rust检查：`cargo fmt --all --check`、`cargo test -p star-core -p star-rotk --locked`、`cargo clippy --workspace --all-targets --locked -- -D warnings`。
完整测试使用 `runs/star-rust-r3-session`，未恢复活动目录中用户的Agent/font删除。

```sh
cd /Users/liyang/Developer/star-lab
git worktree add --detach runs/repro-r3d2-tools f7784415a10541835424ec106bc93a8a9b3cab1d
cd /Users/liyang/Developer/star-lab/runs/repro-r3d2a
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d2-tools/tools/rust_migration/r3_session_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d2a --output /Users/liyang/Developer/star-lab/runs/repro-r3d2-window --driver cocoa
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d2-tools/tools/rust_migration/r3_session_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d2a --output /Users/liyang/Developer/star-lab/runs/repro-r3d2-replay --replay /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-session/results/window/replay.json.xz
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d2-tools/tools/rust_migration/r3_hud_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d2a --output /Users/liyang/Developer/star-lab/runs/repro-r3d2-after.json
```

before探针使用同一r3_hud_probe.py，解释器/source换为R3d1完整checkout和API6归档wheel：预期无session/hud。新版预期都有；提取展示不改变权威状态。

```sh
cd /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-session
shasum -a 256 -c artifacts/SHA256SUMS
```
