# R4c — Native window closed loop and direct presentation encoding

进度：`R0 █ | R1 █ | R2/R3 ▒ | R4 ▒ | R5 ░`（阶段覆盖，不是工时百分比）。

已在限定canonical配置下通过5000Units＋1000Agents/30Hz的三次300秒门槛。

本阶段把既有合成Agent调度器接入生产Rust窗口运行链，保存实际输入以便重放；随后根据分段测量优化Rust展示增量编码。保留Python用户接口、配置、策略、网络、窗口和绘制。

## Reproduce

从同级star-main/star-lab克隆检出manifest中的源码和工具SHA。不要把新wheel安装进before目录。全部命令/环境/退出码见results/commands.json；生产构建使用锁定Rust1.98.1与release。示例从Lab根目录执行：

```sh
git -C ../star-main worktree add --detach "$PWD/runs/repro-r4c" e85e3067b1d2aed5cf08be9dbe35b1deed91dba1
cd runs/repro-r4c
uv sync --locked --python 3.13
uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /tmp/r4c-wheel
uv pip install --python .venv/bin/python /tmp/r4c-wheel/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python -m pytest -q
cargo test -p star-core -p star-rotk --locked
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked -- -D warnings
cd ../..
HEADLESS=0 SDL_VIDEODRIVER=cocoa PYTHONUNBUFFERED=1 PYTHONPATH="$PWD/runs/repro-r4c:$PWD/tools:$PWD/tools/rust_migration" runs/repro-r4c/.venv/bin/python tools/p3_runtime.py --source "$PWD/runs/repro-r4c" --backend rust --native-threads 1 --record-native-inputs --fps 30 --clock-mode fixed --cycle-mode post-action --jitter-seconds 5 --units 5000 --agents 1000 --delay 30 --scope selected --layout canonical --policy stochastic --seconds 60 --warmup 30 --budget-ms 8 --gc-policy realtime_defer --output /tmp/r4c-60.json
```

保持Chrome开启、串行测试、勿操作游戏窗口。通过60秒诊断后将seconds改为300，执行三个独立进程；任何一次失败就停止余下重复并保留有效负结果。输入捕获开销包含在测量中。frame工作包含Agent入口、世界、展示应用、绘制及呈现，排除主动限帧等待；不剔除慢帧。每帧budget只限制下一事件是否开始，单个事件可能越过预算。

重放 / 编码分解：

```sh
runs/repro-r4c/.venv/bin/python tools/rust_migration/replay_rendered_loop.py --source "$PWD/runs/repro-r4c" --trace /tmp/r4c-60.trace.json.gz --threads 4 --output /tmp/r4c-replay.json
runs/repro-r4c/.venv/bin/python tools/rust_migration/delta_trace_probe.py --source "$PWD/runs/repro-r4c" --trace experiments/2026-09-rust-rendered-loop/results/t1-budget8-300-r1.trace.json.gz --output /tmp/r4c-delta
```

普通重放严格核验源码/wheel身份，因此新编译产物即使源码相同也应重放自己生成的轨迹；复核已归档轨迹请安装归档wheel。跨版本编码probe有意不要求同wheel，核验初始场景、所有请求与事件，并由analyzer对完整增量hash/长度/最终状态进行对照。前缀2000tick，排除tick<900；剩余1101样本。不能与窗口300秒性能等同。

## Scope

首关5000 Units /1000 Agents；这些是在线Unit，不是每帧5000同时移动。世界dt=1/30，Agent墙钟思考截断正态均值30秒/标准差5秒/15–45秒，首次uniform0–30秒错开；不在思考期轮询。逐Unit move/attack/wait=50/25/25，非法选择等待、不重抽；canonical120×120地形，Fog开启，selected子集每Agent约5Units，初始1000注册/认领亦走Rust入口。窗口大小和实际并发移动量见各compact。沿用canonical禁用minimap单位层与有限实验GC延迟维护配置；不是所有窗口配置的承诺。

Protocol/Hub、真实LLM、5000Agents、10000Units、高接触密度、24Hz、跨平台安装、网络/BOT应用集成、默认切换不由本轮验收。默认Python/1线程；G008/G009、R001/R002继续开放。GUI渲染仍在Python，无玩法近似、字段删除或TTL。

Compact入口results/comparison.json与blocks.json。raw帧/请求/census、实际输入、初始状态、截图、验证日志及releasewheel均由artifacts/SHA256SUMS覆盖。历史失败结果保留；原始帧/请求、输入轨迹、截图、日志及wheel仅在raw.zip中归档；本地解压副本由本目录.gitignore排除。artifact-index逐项记录文件hash，compact.zip只包含审阅材料及raw包身份，不复制原始载荷。环境、工具SHA、canonical场景引用见manifest。

## Checkpoints and verification

构建/测量 `e85e3067b1d2aed5cf08be9dbe35b1deed91dba1`；最终文档节点 `b05c1465e551072bced220ae12c2474ec7e81e85` / annotated `rust-kernel-r4c-2026-09-25`。测量目录 `runs/star-rust-presentation-encoding` 保持构建SHA，便于严格身份重放；生产venv已安装同wheel。main仍6a970dea、49原删除保留，未merge/push。API17/schema5，extension SHA `8c74d05d89f1037c0157ad25e32ed4c6852bad7d316694cb056faa8c72f2d2e2`。

首次复核归档先从本目录解包（raw.zip保持唯一归档原件，解包文件是工作副本）：

```sh
shasum -a 256 -c artifacts/SHA256SUMS
unzip -o artifacts/r4c-rendered-loop-raw.zip
cd ../..
runs/star-rust-presentation-encoding/.venv/bin/python tools/rust_migration/analyze_rendered_loop.py --root experiments/2026-09-rust-rendered-loop
runs/star-rust-presentation-encoding/.venv/bin/python tools/rust_migration/analyze_rendered_blocks.py --root experiments/2026-09-rust-rendered-loop
```

源码/工具SHA按manifest检出，解释器与wheel相匹配。结果中的analyzer_sha随检出版本变化；正式原值来自manifest指定分析器。raw.zip逐项checksum见results/artifact-index.json，两包的SHA/size见results/packages.json。

## Validated scoped capacity

| Run | Frame P99 ms | Observation response P99 ms | Action queue P99 ms | Hz | Max moving |
|---|---:|---:|---:|---:|---:|
| t1-after-budget8-300-r1 | 32.478751 | 85.989951 | 94.090125 | 30.0 | 171 |
| t1-after-budget8-300-r2 | 32.613375 | 82.840035 | 93.040334 | 30.0 | 173 |
| t1-after-budget8-300-r3 | 32.405167 | 87.093479 | 94.272292 | 30.0 | 178 |

三轮每轮30秒预热＋300秒测量，全部guard通过，5000Units始终存活。世界单线程、Lab预算8ms；包括真实Cocoa窗口。个别30秒分段仍超33.33ms，余量不足1ms，不保证任意窗口或所有帧均满足。详见results/blocks.json；所有慢帧保留。

第三轮原始输入在4线程内核重放：40741请求、9878tick及presentation，响应/事件/最终状态一致。输入不同的实时时序不要求最终世界彼此相同；不能把不同随机轨迹的实时测量当锁步比较。
