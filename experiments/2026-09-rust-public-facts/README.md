# R4b — Rust公共事实直接编码

进度：`R0 █ | R1 █ | R2/R3 ▒ 内核补齐中 | R4 ▒ 并行与数据装配优化 | R5 ░`（非工时百分比）。

本轮按分段计时移除公共敌军/地形中间JSON树及深复制，同一只读段跨阵营共享编码事实；完整输出、Fog、权限与玩法不变。5000Units/MP6单线程查询5Units **19.189→2.547ms**，查询100Units **23.339→6.218ms**。可信单请求100Units **23.899→6.439ms**，8请求 **26.511→8.742ms**。均为1预热+5样本中位，**不是30Hz整帧/P99/排队/5000Agents验收**。

2171完整回归（新增6项）、89针对性、4Rust/fmt/Clippy、旧6场景510节点通过；54handler+30入口对照，共84组完整响应/状态/字节长度/原工作计数相同。[全部样本与分析](analysis.md)、[决策](decision.md)、[GAP台账](../../../star-main/docs/native-benchmark-gaps.md)。默认Python/1线程；Chrome保持开启、实验串行。

## Exact checkpoints

- Original R4a `45bd11cca09a88fb4c757feecc234a4efe932dae`，API16、旧wheel保留。
- Instrumentation-only `244b17fabdde585c4dac367acd52a3247929f886`，API17；完整目录`runs/star-rust-profile-before`。
- Optimized build `290de0a7c7dde1255b3d7556552fc6acddac6fbe`；measurement/test `94f7b0c41f88d9012600556b123552ced9d48b69`（只改测试zeroID预期）。
- Final `90481f985bc66f30d8ed7627afe0ee37aec1aa75` / annotated`rust-kernel-r4b-2026-09-25`（只改文档）；完整目录`runs/star-rust-public-facts`。
- Comparison tool `d34a3ac02c81c39620a73259ceae180a204b44b2`；每组runner精确SHA在compact/manifest。
- API17/schema5，extensionSHA `90fe642f549c2d3a1bebc05e14e0db013f7a105959a2340afc2f7accc922c1f3`。生产与完整目录均已安装afterwheel；两种API17构建须按SHA区分。
- main仍`6a970deaee7d9b8d3939edd102973f2377edd6ac`，未merge/push，49处用户原删除未动。

## Reproduce

使用同级star-main/star-lab克隆及上述精确commit。manifest记录canonical初始世界和旧重放的路径/hash，避免重复保存。构建示例：

```sh
git -C star-main worktree add --detach ../star-lab/runs/repro-r4b 94f7b0c41f88d9012600556b123552ced9d48b69
cd star-lab/runs/repro-r4b
uv sync --locked --python 3.13
uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /tmp/r4b-wheel
uv pip install --python .venv/bin/python /tmp/r4b-wheel/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python -m pytest -q
cargo test -p star-core -p star-rotk --locked
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked -- -D warnings
.venv/bin/python ../../tools/rust_migration/observation_phase_probe.py --source "$PWD" --output /tmp/r4b-after
.venv/bin/python ../../tools/rust_migration/kernel_observation_assembly_probe.py --source "$PWD" --output /tmp/r4b-after-public --threads 1 --mp 6
.venv/bin/python ../../tools/rust_migration/r3_scene_host_probe.py --source "$PWD" --output /tmp/r4b-replay --replay ../../experiments/2026-09-rust-r3-host-authority/results/window/trace.json.xz
```

修改前与原R4a分别使用独立完整checkout和venv。旧API16只测普通调用；不得向旧环境安装新wheel。全部精确命令、环境和退出码见`results/commands.json`。依次将输出放入`oracle`、`before`、`after`、`before-public`、`after-public`后运行：

```sh
python3 tools/rust_migration/compare_observation_phases.py --results experiments/2026-09-rust-public-facts/results
cd experiments/2026-09-rust-public-facts
shasum -a 256 -c artifacts/SHA256SUMS
```

预期：84组通过全部比较，输出字节长度、状态不变，计时嵌套关系正确。精确毫秒数随硬件与背景负载变化。当前验证CPython3.13/macOS ARM64；其余平台安装矩阵留待R5。

## Evidence layout

Compact包含comparison、各组compact、environment、commands与artifact-index。Raw的各组raw.json.xz保存实际响应/请求及全部分段样本；初始世界使用已有canonical原件。工具确定性地设置MP6，将5000Units分散到现有5677格，保持全部存活单位且存在可达空格。artifact-index记录原始数据大小/hash/路径及源码/工具/扩展身份。两个release wheel、验证日志和被排除的测试预期失败日志均保留；本包全部文件受SHA256SUMS覆盖。

## Next

重新验证约30秒Agent合成闭环，包含世界更新、展示、排队和存活负载guard。完整门槛通过前不切换默认；Python用户接口不需要重写为Rust。
