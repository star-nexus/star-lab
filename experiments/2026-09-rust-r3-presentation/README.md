# R3c：Rust 战斗生命周期与 Python 战场展示

**Status: VALIDATED CHECKPOINT，完整 R3/R4/R5 仍 OPEN。** 2026-09-14。

生产源码 `5bda51db6cd68455aa5724a6ef0eca1e66f89dda`，annotated tag
`rust-kernel-r3c-2026-09-14`。前置问题版本 `d5abc70e9cda8a6820546112e6172dd9e43c1515`。
差分/重放与选中窗口工具 `1743d0effd96365fdfb5bf55c4486ef8e5cc82c2`；
普通视图工具 `079c99a73f18a7a4cae1e0a37cb1a2ae51be5610`。

## 1. 问题与结果

旧 Rust 在 dummy/window 的可信攻击入口拒绝执行：`error_code=2012`，
`native combat display handoff is not implemented yet`，没有 visual/Fog/territory 增量。
新版同一攻击成功，返回 3 条视觉行（攻击者、伤害数字、效果）。见 before/after.json。

Rust 现在拥有战斗动画、弹道、伤害/CRIT 与效果的生命周期和外部实体 ID；
Python 继续使用原插值、旋转、相机、字体、Surface、坐标和飘字缓存。
单位资源、地块控制与 Fog 使用累积变化队列。WorldPresentation 只更新派生展示 World，
渲染不能修改 Rust 状态；旧 epoch 或更旧 revision 会在写展示缓存前拒绝。

这是战场展示组件接入，不是完整可玩的 `--backend rust` GameScene。
输入、完整 HUD、VLM、BOT/结算及场景启动仍待后续 R3；R4 尚无并行任务。

## 2. 环境与验证

Mac mini M4 / 10 logical CPU / 16GiB，macOS 26.5.2 ARM64，CPython 3.13.12；
Chrome 开启。Rust 1.98.1、maturin 1.15.0、release wheel；原 uv.lock/Cargo.lock。
精确信息见 environment.json、probe.summary.json 和两份 render.json。

- 1504 完整 Python 回归通过（其中 582 native 契约），3 Rust 测试与 Clippy/fmt 通过。
- 144 配置：3 display × 2 mode × 2近远程 × 2死亡 × 2暴击 × 3线程设置。
  5184 节点 = 864 请求 + 4032 ticks + 288 reset；完整响应、权威状态和事件逐节点相等。
- 独立 Rust 重放还逐项验证所有展示增量；1/2/4 设置一致，仍为串行 Mutex 执行。
- 真实 Cocoa 1200×800：选中/普通视图各 4 配置×120帧，总960帧；3 Units、1本地合成身份，
  实时/回合制、近战/远程、移动、暴击、效果清理、Fog、坐标、缩放与平移。
  每帧断言渲染前后 Rust 状态不变；远程必须出现弹道，最后所有临时特效清空。
- 共24张PNG；代表性近战/远程、缩小/放大截图已人工检查。原有选中攻击范围覆盖层会遮挡地块标签，
  因此另做相同状态的普通视图检查；两组都保留，并未以删除覆盖层改变游戏规则。

**不报告容量或加速倍数。** 这里没有5000/1000负载、Hub、真实LLM、长期P99或平台wheel矩阵。
世界仍由显式 dt 推进；测试每步1/30，窗口限速等待不参与任何性能结论。

## 3. 固定源码与安装

以下命令在这两个本地仓库运行；新路径必须不存在。复现工具与证据均在 Lab。

```sh
cd /Users/liyang/Developer/star-main
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-r3c 5bda51db6cd68455aa5724a6ef0eca1e66f89dda
cd /Users/liyang/Developer/star-lab/runs/repro-r3c
uv sync --locked
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-presentation/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python -m pytest -q
```

重建 wheel（不要覆盖归档产物）：

```sh
PATH=/Users/liyang/.cargo/bin:$PATH uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /Users/liyang/Developer/star-lab/runs/repro-r3c-wheel
PATH=/Users/liyang/.cargo/bin:$PATH cargo test -p star-core -p star-rotk --locked
PATH=/Users/liyang/.cargo/bin:$PATH cargo clippy --workspace --all-targets --locked -- -D warnings
PATH=/Users/liyang/.cargo/bin:$PATH cargo fmt --all -- --check
```

归档扩展 SHA256 `a60b227d02e47998762c735a047e10a90a225fb8b78727b41afcc0d68c1d3f89`。
重建 wheel 的编译路径可能改变二进制 hash；精确重放默认要求原归档 wheel。
API/schema=5，oracle=`python-r0c-3cc4ffe`；旧检查点必须使用旧版 wheel。

## 4. 前后对照

```sh
cd /Users/liyang/Developer/star-main
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-r3c-before d5abc70e9cda8a6820546112e6172dd9e43c1515
cd /Users/liyang/Developer/star-lab/runs/repro-r3c-before
uv sync --locked
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-observations/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
PYTHONPATH=. .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-presentation/artifacts/interface-repro.py
cd /Users/liyang/Developer/star-lab/runs/repro-r3c
PYTHONPATH=. .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-presentation/artifacts/interface-repro.py
```

预期旧版 success=false / error2012 / visual_rows=0，新版 success=true / visual_rows=3。

## 5. 差分、归档重放和窗口复现

可用 `git -C /Users/liyang/Developer/star-lab show 1743d0effd96365fdfb5bf55c4486ef8e5cc82c2:tools/rust_migration/r3_presentation_probe.py`
检查精确工具；其依赖 r3_observations_probe.py 同样在该提交。当前同名工具内容未改。

```sh
cd /Users/liyang/Developer/star-lab/runs/repro-r3c
.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/r3_presentation_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3c --output /Users/liyang/Developer/star-lab/runs/repro-r3c.json.gz
.venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-presentation/artifacts/unpack-replay.py --output /Users/liyang/Developer/star-lab/runs/repro-r3c-original.json.gz
.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/r3_presentation_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3c --replay /Users/liyang/Developer/star-lab/runs/repro-r3c-original.json.gz --output /Users/liyang/Developer/star-lab/runs/repro-r3c-replay.json
.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/r3_window_presentation_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3c --output /Users/liyang/Developer/star-lab/runs/repro-r3c-window --driver cocoa
.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/r3_window_presentation_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3c --output /Users/liyang/Developer/star-lab/runs/repro-r3c-selected --driver cocoa --selection
```

窗口工具当前采用079c99a版本；首个选中运行1743版本固定选中a，当前`--selection`相同行为。
`--driver dummy`仅用于离屏检查，不能替代本次cocoa结论。保持Chrome开启，逐个执行工具。
脚本直接注入已记录的相机和选择值，没有走鼠标/键盘输入；不宣称输入迁移通过。

## 6. 原始证据与完整性

默认读取 results/compact.json；完整逐节点数据保存在 results/probe.json.xz。
原始JSON为194433027字节，以XZ无损存储189416字节，逐字节解压比较通过；
并可在本机恢复原40602923字节gzip，SHA与原采集完全相同。没有抽样或删除节点。
packing.json记录两种压缩和解压内容SHA；probe.summary.json保留原采集gzip的身份，
compact.json指向实际归档XZ。原gzip冗余包装留在Lab runs/r3c-original-probe.json.gz，不写大文件进Git。

```sh
cd /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-presentation
shasum -a 256 -c artifacts/SHA256SUMS
```

manifest.yaml列出源码、工具、环境和全部正式证据；analysis.md与decision.md说明边界。
正式验证checkout为Lab runs/star-rust-r3-presentation，源码完整。活动star-main保留无关49处Agent/font删除，
这些删除未进入提交。生产main及Python默认入口保持原样；本阶段没有merge或容量发布。
