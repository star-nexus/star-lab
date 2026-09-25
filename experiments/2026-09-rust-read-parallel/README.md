# R4a — Rust观测只读并行首版

进度：`R0 █ | R1 █ | R2/R3 ▒ 内核补齐中 | R4 ▒ 只读并行首版 | R5 ░`（非工时百分比）。

已实现：threads2/4固定线程池计算缺失Unit面板；默认1、世界写入仍串行。2165完整Python回归、83针对性、4Rust测试、fmt/Clippy、旧6场景510节点通过。30查询案例×4配置完整Agent响应/权威状态/原工作计数相同。无已确认新增玩法差异；[GAP台账](../../../star-main/docs/native-benchmark-gaps.md)与[状态边界审计](../../../star-main/docs/native-state-boundaries.md)已更新。

MP6/5000Units/100选中Units、单请求中位25.0→20.9/21.3ms（1/2/4线程）；小查询可能回退。**这是查询微测，不是30Hz/排队/5000Agents容量验收。** 详见[全部30组数值与负结果](analysis.md)、[决策](decision.md)。

## Exact checkpoints

- Before `3892f95af6638e213f1b842fd9c0fe4b7b3dab80` / `rust-kernel-r3k4-2026-09-24`，API15。
- Build/measure `ddb084e42e07fdb359c511b8727f888ff3a5a38b`；final `45bd11cca09a88fb4c757feecc234a4efe932dae` / `rust-kernel-r4a-2026-09-25`，只追加文档。
- Tool各组精确SHA在manifest和compact中；comparison工具 `6c991b76192f4e7941c7dc29844dca8486fd3f2c`。MP0与MP6工具差异仅MP6位置留空格转换。
- API16/schema5，extension SHA `353320733d25979d2213d70d9fc08ed933a2b1b5c5c079199e85e42633fa2141`。
- 完整本机目录 `runs/star-rust-read-parallel`，生产venv也已安装同wheel。旧目录 `runs/star-rust-kernel-encoded` 保持旧API15。
- main未变、未合并/推送；49处既有用户删除完整保留。Chrome保持开启，实验进程串行，GPU未参与。

## Reproduce

Use sibling clones `star-main` and `star-lab`, exact commits above and the archived canonical input files from manifest. Example new-source release installation:

```sh
git -C star-main worktree add --detach ../star-lab/runs/repro-r4a ddb084e42e07fdb359c511b8727f888ff3a5a38b
cd star-lab/runs/repro-r4a
uv sync --locked --python 3.13
uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /tmp/r4a-wheel
uv pip install --python .venv/bin/python /tmp/r4a-wheel/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python -m pytest -q
cargo test -p star-core -p star-rotk --locked
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked -- -D warnings
.venv/bin/python ../../tools/rust_migration/kernel_observation_assembly_probe.py --source "$PWD" --output /tmp/r4a-t2-mp6 --threads 2 --mp 6
.venv/bin/python ../../tools/rust_migration/r3_scene_host_probe.py --source "$PWD" --output /tmp/r4a-replay --replay ../../experiments/2026-09-rust-r3-host-authority/results/window/trace.json.xz
```

Repeat probe withthreads1/2/4 andmp0/6; before source uses ownAPI15 releasewheel, threads1. Do not install newwheel into thebeforeenvironment. For exact8-run naming/arguments/buildenv/returncodes see`results/commands.json`. Comparison:

```sh
python3 tools/rust_migration/compare_read_parallel.py --results experiments/2026-09-rust-read-parallel/results
cd experiments/2026-09-rust-read-parallel
shasum -a 256 -c artifacts/SHA256SUMS
```

Expected signature: allguards pass, fullresponses/states equal, MP6units5000 reachable_cells966; worker counts bounded byconfiguredthreads, no correctness dependence onutilization. Differentmachines neednotreproduceexactms. CPython3.13macOSARM64 only validated here; broaderwheels/platformmatrix remainsR5.

## Evidence layout and classification

Compact: `results/comparison.json`, eachrun`compact.json`, environment/commands/artifact-index. Raw: eachrun`raw.json.xz`, canonical initialworlds/replay referenced byhash rather than duplicated. Artifact-index records rawsize/hash/locator andsource/tool/extensionSHAs. RawdecodedAgentresults compared directly, not justhashes. Releasewheel andvalidationlogs retained. `results/intermediate/` contains rejectedMP6densefixtureguard, excluded fromformalresults. Init/import reported separately; reset andPythondecode excluded; all5querysamples retained.

Next: profile remaining public projection and final encoding vs panel/join costs, then revisit realistic closed-loopframe/queue testing. No automatic move ofPythonUX/network/BOTpolicy toRust.
