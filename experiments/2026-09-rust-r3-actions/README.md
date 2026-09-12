# Rust R3a：回合交接、休息、领地与技能接口

**Status:** VALIDATED 中间检查点；完整R3/容量/窗口迁移仍未完成。

**Production:** `/Users/liyang/Developer/star-main`，分支 `codex/rust-env-migration`。

**Problem commit:** `2c83c001780ddf103b94905df81e8a1bc469af6e`（R2e）。

**Fix / validated commit:** `7f4ad57bbd6966748c0fb49deb82f6ad43fc7aee`。

**Annotated tag:** `rust-kernel-r3a-2026-09-13`。

**Lab probe/replay tools:** `cb336f40a973050c2fb5eba7ec886f779042577d`。

## 1. 问题与影响

R2e已能通过可信本地接口注册/认领、move/attack/get_faction_state，但配置启用rest、occupy、fortify、skill时仍会遇到未迁移的动作；回合交接也未接完整实现。现阶段需要先保证玩法与Python oracle一致，才能继续窗口和性能迁移。本实验没有增加技能效果、修改MP弱化或重平衡资源规则。

## 2. 源码与环境

Mac mini M4，10核、16GiB，macOS26.5.2/25F84 ARM64；CPython3.13.12、Rust1.98.1、Bevy ECS0.19.1、PyO3.29.2、maturin1.15.0。Chrome保持开启，验证串行运行。见[环境](results/environment.json)。

从Lab根目录执行（worktree已经存在时复用同一SHA，不重复创建）：

```sh
git -C /Users/liyang/Developer/star-main worktree add --detach \
  /Users/liyang/Developer/star-lab/runs/star-rust-r3-actions \
  7f4ad57bbd6966748c0fb49deb82f6ad43fc7aee
cd /Users/liyang/Developer/star-lab/runs/star-rust-r3-actions
uv sync
uv pip install --python .venv/bin/python \
  /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-actions/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
```

此wheel限本机平台/CPython3.13，不代替R5跨平台验收。API/scene版本现为3；旧R2必须使用原tag/原wheel，不能混用新扩展重放schema1。e3da7a中间turn版本为API/schema2，也须保持配套。

## 3. 复现旧入口和新入口

固定的两个checkout分别安装自己的归档wheel。在Lab根目录：

```sh
runs/star-rust-r2-lifecycle/.venv/bin/python \
  experiments/2026-09-rust-r3-actions/artifacts/rest-interface-repro.py \
  runs/star-rust-r2-lifecycle
runs/star-rust-r3-actions/.venv/bin/python \
  experiments/2026-09-rust-r3-actions/artifacts/rest-interface-repro.py \
  runs/star-rust-r3-actions
```

旧版输出 `RuntimeError: native action rest is not implemented yet`；新版返回success/result=true、remaining_action_points=2。两份实际输出保存在[旧入口](results/previous-interface.log)和[新入口](results/current-interface.log)。这只是入口缺失的最小复现，完整语义由后面的差分轨迹验证。

## 4. 验证与重放命令

以下命令均在Lab根目录运行，不启动Hub/真实LLM/真实绘制：

```sh
runs/star-rust-r3-actions/.venv/bin/python tools/rust_migration/r3_actions_probe.py \
  --source runs/star-rust-r3-actions \
  --output runs/r3-actions-repro/probe.json.gz
runs/star-rust-r3-actions/.venv/bin/python tools/rust_migration/replay_r3_actions_probe.py \
  --source runs/star-rust-r3-actions \
  --input experiments/2026-09-rust-r3-actions/results/probe.json.gz \
  --output runs/r3-actions-repro/replay.json
```

复现工具时checkout Lab工具SHA或核对工具内容。原测量输出路径为 `experiments/2026-09-rust-r3-actions/results/probe.json.gz`；重跑写 `runs/`，不要覆盖正式证据。

源码构建/完整回归（在生产checkout中，PATH先加入`/Users/liyang/.cargo/bin`）：

```sh
cargo test -p star-core -p star-rotk --locked
cargo clippy --workspace --all-targets --locked -- -D warnings
uvx --from maturin==1.15.0 maturin build --release --locked \
  --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python \
  --out /Users/liyang/Developer/star-lab/runs/r3-actions-rebuilt-wheel
# 将此目录实际生成的cp313 wheel安装到同一.venv，再运行：
.venv/bin/python -m pytest -q
```

原正式构建使用 `CARGO_TARGET_DIR=/Users/liyang/Developer/star-main/target`，产物在本实验artifacts；构建、Rust测试、Clippy与pytest完整日志在results。新构建的二进制SHA可能随构建路径变化；严格归档重放校验使用本实验原wheel。

## 5. 结果和判定

| 验证 | 结果 |
|---|---:|
| 完整Python回归，包含Native契约 | 1298通过 |
| 其中Native契约 | 378项（较R2e新增14回合＋132动作/领地） |
| Rust单元测试 / Clippy | 3通过 / 通过 |
| 差分配置 | 27 |
| 不同操作节点 | 1524 |
| 其中世界更新 | 762 |
| 1/2/4配置完整轨迹 | 一致 |
| Rust重放归档轨迹 | 1524节点全部一致 |

动作族18配置：display none/dummy/window × realtime/turn × threads1/2/4；840节点（366可信请求、18计时占领启动、438ticks、18reset）。回合族9配置：三种display×三种threads，684节点（243请求、108人工end-turn、324ticks、9reset）。原始数据逐节点保存完整响应、导入权威状态、有序事件，两套内核各一份；重放不是新增独立节点，不能重复计数。

总事件：BattleEvent6、UnitDeathEvent6、GameOverEvent3、TurnStartEvent324。动作族Fog关闭以保留丰富投影；回合族沿用原小场景Fog。小场景均3个Unit、注册3个合成身份；无网络。校验时间显式注入，capture测试墙钟每步跨1000秒而模拟只推进0.5秒。计时任务/round状态跨reset继续一致。

**没有容量结论**：dummy/window是行为配置，不调用真实绘制；attack只在none执行。线程数仍为配置兼容测试，内核没有并行worker。原R2e的5000/1000负结果保持原结论，本轮不测性能、不更新Frontier。完整R3尚缺其他观测变体、BOT/结算、实际窗口接入等。

## 6. 正式证据

- [raw完整轨迹](results/probe.json.gz)、[compact摘要](results/probe.summary.json)、[精确重放](results/replay.json)。
- [manifest](manifest.yaml)、[分析与保留的历史行为](analysis.md)、[决策](decision.md)。
- [SHA256SUMS](artifacts/SHA256SUMS)覆盖raw、compact、日志、环境、复现脚本和wheel。在本实验目录运行 `shasum -a 256 -c artifacts/SHA256SUMS`。
- 生产main仍 `6a970deaee7d9b8d3939edd102973f2377edd6ac`，未合并/推送/切换默认。活动目录原有49处Agent/font删除未纳入本轮；完整回归在Lab干净checkout执行。
