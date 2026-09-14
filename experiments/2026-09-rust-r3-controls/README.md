# R3d1：本地操作接入 Rust 内核

**VALIDATED CHECKPOINT；完整 R3/R4/R5 仍 OPEN。** 2026-09-14。
生产 `c5ae37f5fab2e3563af136f8868d8fc7227c1f23`，annotated tag `rust-kernel-r3d1-2026-09-14`。
前置 R3c `5bda51db6cd68455aa5724a6ef0eca1e66f89dda`。
差分工具 `b69ffd73ef044fb05b0e0c60380b889ed4632a81`；独立重放/窗口工具
`99cfdd6692f7e99658c8111cbcd9b073934b3ca3`。后者仅补 JSON capture 坐标解码为 tuple，未改运行内核或差分数据。

## 问题与改动

旧版已能从 Rust 生成战场展示，但 Python 输入仍直接寻找 Python Movement/Combat/TurnSystem。
旧 Runtime 没有本地命令入口（before.json 的 AttributeError）；新版同一低层移动成功且权威状态变化（after.json）。

新增可信本地 `execute_control`，复用 Rust 的移动、攻击、资源、筑垒、Fog 和回合状态。
LocalControls 在命令返回前刷新派生展示；窗口/坐标输入和动作面板保留原行为、字体缓存及命中测试。
工具栏和 UI 只初始化一次，挂接时不重新分配实体 ID。
控制器固定 epoch，Rust 持同一把锁先检查再写入/提取增量；旧回调不能操作 reset 后的新世界，不能取走新展示的首批数据。

刻意保留三种历史差异：UI wait/garrison 只扣 AP，Agent rest 另有状态效果；
实时本地筑垒沿用不消耗 AP/CP 的旧行为；工具栏结束回合只轮换 TurnManager，而键盘结束回合先重置资源并检查胜负。
没有取消严重兵力损失导致的 MP 弱化，没有静态化动态路径，没有改按键表。

## 验证结果与边界

- 1618 完整回归，其中 696 Native 契约；新增 114 项。3 Rust 测试、Clippy 和 fmt 通过。
- 144 配置（3 display × 2 mode × 2近远程 × 2死亡 × 2暴击 × 3线程设置），7128节点：
  1008 Agent请求、1440本地命令、144次定时占领、4176 ticks、288 resets、72次键盘结束回合。
  完整响应、权威状态、有序事件逐项对照 Python oracle；独立 Rust 重放另检查每一批展示增量。
- 1/2/4 线程设置结果相同，目前仍串行 Mutex，不是并行加速结果。
- Cocoa 1200×800，实时/回合 × 近战/远程共480帧；通过真实 InputSystem 分发28个合成SDL按键和20个合成SDL点击，
  包括选中、移动、点击攻击面板、目标点击、Fog/视角、坐标和键盘结束回合。
  工具栏低层命令另直接调用4次；**未宣称其按钮轮询路径通过物理鼠标点击验收**。
  16 PNG 已归档，检查了远程攻击面板、缩小后的CRIT/坐标和回合制放大视图。
  移动到达、攻击损失、CRIT/弹道出现及最终清理均有断言；每帧检查绘制前后 Rust 权威状态不变。

本轮是输入/本地命令检查点，**不是完整 GameScene/CLI 可玩版**。
完整HUD、VLM、BOT、LLMSystem结束后的通知与报告收集、场景生命周期仍待接；本地回放显式关闭LLMSystem的帧更新，
Agent查询仅通过本地可信入口。世界使用显式模拟dt，不测墙钟吞吐。
不含5000/1000容量、P99、Hub、真实LLM、真实并行或Linux/CPython3.14安装验收。Chrome保持开启，实验顺序执行。

## 环境与安装复现

M4/10逻辑CPU/16GiB，macOS26.5.2 ARM64，CPython3.13.12；环境与lock hash见 environment.json。
Rust1.98.1、maturin1.15.0，API6/schema5，oracle=`python-r0c-3cc4ffe`。
归档release扩展 SHA256：`527c60fcca55aec5b4d2481cd113c78663eb1c3f631c6e72d83964c37fe98842`。

```sh
cd /Users/liyang/Developer/star-main
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-r3d1 c5ae37f5fab2e3563af136f8868d8fc7227c1f23
cd /Users/liyang/Developer/star-lab/runs/repro-r3d1
uv sync --locked
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-controls/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python -m pytest -q
PATH=/Users/liyang/.cargo/bin:$PATH cargo test -p star-core -p star-rotk --locked
PATH=/Users/liyang/.cargo/bin:$PATH cargo clippy --workspace --all-targets --locked -- -D warnings
PATH=/Users/liyang/.cargo/bin:$PATH cargo fmt --all -- --check
```

自行重建使用以下命令，重建产物不可覆盖归档wheel；编译路径可能使二进制hash不同，精确重放使用原归档wheel。

```sh
PATH=/Users/liyang/.cargo/bin:$PATH uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /Users/liyang/Developer/star-lab/runs/repro-r3d1-wheel
```

## 前后对照、差分和窗口复现

在新checkout执行 interface-repro；旧版在R3c checkout和该阶段归档API5 wheel中执行同一脚本。
禁止把新版Python适配器与旧wheel混用。旧结果应为AttributeError且state_changed=false；新版move success=true、state_changed=true。

```sh
PYTHONPATH=. .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-controls/artifacts/interface-repro.py
.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/r3_controls_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d1 --output /Users/liyang/Developer/star-lab/runs/repro-r3d1.json.xz
.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/r3_controls_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d1 --replay /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-controls/results/probe.json.xz --output /Users/liyang/Developer/star-lab/runs/repro-r3d1-replay.json
.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/r3_window_controls_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d1 --output /Users/liyang/Developer/star-lab/runs/repro-r3d1-window --driver cocoa
```

工具依赖同目录 r3_observations_probe.py 的 git/digest；精确版本可用上述Lab SHA的 `git show SHA:tools/rust_migration/...` 提取。
归档 probe.json.xz 是完整原始JSON的无损XZ压缩，直接支持 --replay。
解压后265288799字节，SHA256 `72d729ab5e594711838969d4d84a2b2640612eecaa6998651be9858d886ac34d`；没有删节点或只保存成功样本。
各文件checksum在manifest.yaml。raw/summary/compact/replay、全部窗口帧状态摘要与截图、回归/build日志共同构成证据链。

## 后续

继续 R3d2：完整GameScene/输入生命周期和后端选择，然后HUD/VLM、BOT和结算。
主分支仍 `6a970deaee7d9b8d3939edd102973f2377edd6ac`，默认Python；未merge/push。
活动目录49处无关Agent/font删除保持原状，完整验证在Lab独立checkout中完成。
