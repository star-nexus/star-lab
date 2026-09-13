# R3b：非图像观测与版本缓存

**状态：已验证的功能检查点，完整 R3 仍在进行。** 生产 `d5abc70e9cda8a6820546112e6172dd9e43c1515` / `rust-kernel-r3b-2026-09-13`。Python 默认，main 未合并。

## 1. 问题与影响

R3a 尚未实现 `observation`、`unit_observation`、`faction_observation`、`limited_observation`、`godview_observation`，即使 MatchRules 允许也返回 native not implemented。这阻碍了完整 ENV 接口迁移。另发现两处 Python 观测列表未按坐标排序，先以 R0c 补齐规范化基线。

## 2. 精确版本与环境

- 问题源码：`7f4ad57bbd6966748c0fb49deb82f6ad43fc7aee`，使用 [R3a 原 wheel](../2026-09-rust-r3-actions/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl)。
- R0c：`3cc4ffea091dcf6afa8691c217ec4b09e25d4b5f` / `rust-python-oracle-r0c-2026-09-13`，1299 回归。
- 测量/实现/验证：`d5abc70e9cda8a6820546112e6172dd9e43c1515`。
- Lab probe/replay：`f10dd87452b771f70e15af19d38a2299f4a9532c`。
- M4 ARM64，macOS 26.5.2，CPython 3.13.12；Rust 1.98.1 / Bevy ECS 0.19.1 / PyO3 0.29.2 / maturin 1.15.0。Chrome 保持开启。[环境](results/environment.json)。
- 三 Unit、三注册合成身份；none/dummy/window 是行为配置，**没有实际绘制窗口**。没有 Hub、真实 LLM 或容量测量。

## 3. 重现问题与修复

假设 STAR 在 `/Users/liyang/Developer/star-main`、Lab 在 `/Users/liyang/Developer/star-lab`。先在独立 worktree 检出问题 SHA（不要覆盖用户未提交内容）：

```bash
git -C /Users/liyang/Developer/star-main worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-r3b-before 7f4ad57bbd6966748c0fb49deb82f6ad43fc7aee
cd /Users/liyang/Developer/star-lab/runs/repro-r3b-before
uv sync
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-actions/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
PYTHONPATH=. .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-observations/artifacts/interface-repro.py
PYTHONPATH=. .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-observations/artifacts/order-repro.py
```

预期：五种查询均报告 `native action ... is not implemented yet`；两种坐标列表 `coordinate_order=false`。[原输出](results/interface-before.log)、[顺序反例](results/order-before.log)。

修复版用独立 checkout，安装本目录 wheel；API/schema=4，不能混用 R3a/R2 的扩展：

```bash
git -C /Users/liyang/Developer/star-main worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-r3b-after d5abc70e9cda8a6820546112e6172dd9e43c1515
cd /Users/liyang/Developer/star-lab/runs/repro-r3b-after
uv sync
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-observations/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
PYTHONPATH=. .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-observations/artifacts/interface-repro.py
PYTHONPATH=. .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-observations/artifacts/order-repro.py
.venv/bin/python -m pytest -q
```

预期：五种查询 `success=true`，两种列表按坐标排序；1443 回归通过。战报非空的历史 godview 错误由专门契约保留，最小示例使用空战报。

## 4. 构建与完整差分

归档 wheel 来自 `runs/star-rust-r3-observations` 的干净精确源码。源构建命令如下；环境和实际构建目录也见 manifest。新生成的 wheel 未必逐字节相同，精确归档重放必须安装本目录 wheel。

```bash
export PATH=/Users/liyang/.cargo/bin:$PATH
cargo fmt --all --check
cargo clippy --workspace --all-targets --locked -- -D warnings
cargo test -p star-core -p star-rotk --locked
uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /tmp/star-r3b-wheels
.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/r3_observations_probe.py --source . --output /tmp/r3b-probe.json.gz
.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/replay_r3_observations_probe.py --source . --input /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-observations/results/probe.json.gz --output /tmp/r3b-replay.json
```

工具需为上述 Lab SHA 中的文件。probe 归档每次完整解码响应、权威状态、有效观测缓存和有序事件；replay 核验精确源码/扩展 SHA，再从初始世界重新执行。合法原始失败响应也必须一致，不把失败动作排除。

## 5. 结果与证据

- 1443 完整回归，其中 522 native 契约，本轮新增 144；3 Rust 单元测试、fmt、Clippy 通过。
- 54 配置 = 3 fixture × 3 display × 2 mode × 3 thread setting。
- 4203 节点 = 3447 请求 + 702 ticks + 54 reset；差分与独立 Rust 重放全部通过。三线程设置轨迹一致，当前仍串行执行。
- [Compact](results/compact.json)、[完整分组摘要](results/probe.summary.json)、[重放报告](results/replay.json)。
- [Raw](results/probe.json.gz)：22833971 bytes，SHA256 `d62735a1aee16c785bac29e1e14f326d7cf06134028747d62c750408cc6781f3`。原始 console 已嵌入 raw，每条轨迹保留完整字段；没有删减慢帧的问题，因为本轮不是时延实验。

```bash
cd /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-observations
shasum -a 256 -c artifacts/SHA256SUMS
```

## 6. 下一步

VLM 截帧、真实窗口展示增量/战斗事件/输入、BOT/结算仍待接入。R4 实际并行、R5 5000/1000/30Hz 容量与平台安装验收未完成。本轮不新增 Performance Frontier，也不把 1/2/4 配置一致写成并行提速。

参见 [manifest](manifest.yaml)、[分析](analysis.md)、[决策](decision.md)、[恢复入口](../../records/10k-online-resume.md)。
