# R3d5 — Python整数转换限制与Rust统计兼容

进度：`R0 █ | R1 █ | R2/R3 ▒ 兼容性补审 | R4 ▒ 首关已过 | R5 ░`（非工时百分比）。这是R4c之后的兼容性阶段，不重跑或改写R4c容量结论。

已确认并修复G014：默认4300位限制下，先上报`prompt_tokens="0"*4300+"1"`，再上报2；旧Rust累计3，Python累计2，两次动作响应却一致。负号版本旧Rust为1。20组公开动作案例中4组完整状态不同；修复后20组完整响应/权威状态一致。Python原规则未改。

新适配器仅在report_llm_stats接纳时采样sys.get_int_max_str_digits，Rust转换时遵循它，0表示不限制；Agent参数不能覆盖可信信封。首次原样存储、累计才转换的时机保留。新增24契约覆盖11累计字段、Unicode/符号/下划线、界限前等后、640/5000/0设置、改变设置、批次/reset和浮点负对照。2195完整回归、177针对性、4Rust/fmt/Clippy、15Lab和旧6场景510节点通过；非默认设置真实轨迹可在4线程子进程重放。

## Checkpoints

- 直接实测before `e85e3067b1d2aed5cf08be9dbe35b1deed91dba1` / API17；代码与前置文档tag R4c运行部分相同，独立目录runs/star-rust-presentation-encoding保留原wheel。
- fix/build/measurement `07bdb2e89c69959c2b8cb8e61329536c032f187e` / API18/schema5，oracle不变；目录runs/star-rust-integer-limit保持该SHA方便严格重放。
- final docs `257ebf11372fe82ed368bdbba2c3760a6450d110` / annotated `rust-kernel-r3d5-2026-09-27`。生产venv已装API18 wheel，extensionSHA `324454a00ab8bd3559c9229e6c6c9644242d65c488585eba7d29a63b39d29405`。
- before tool `41cc5ccc83fecbb21bc3ea5d0bbec2678175011e`；after/replay tool `cb748373dc23d3a29be98355abf767203f08f78e`；comparison `b1aebc8f3472dd25f9e1ae7160a36d04f457ea2c`。源码与工具没有混成一个身份。
- main仍6a970dea，默认Python/1线程、49原删除保留、未merge/push。G008/G009/R001/R002仍开放。

## Reproduce

同级克隆star-main/star-lab；检出上述工具SHA（最新comparison包含此前probe和录制器）。先从本目录解包唯一raw原件，工作副本被.gitignore排除：

```sh
shasum -a 256 -c artifacts/SHA256SUMS
unzip -o artifacts/r3d5-integer-limit-raw.zip
```

从Lab根目录准备两个独立源码/venv。以下是after示例；before替换源码SHA和输出路径，并安装旧API17 wheel或从原commit构建。全部实际命令/环境/退出码见results/commands.json。

```sh
git -C ../star-main worktree add --detach "$PWD/runs/repro-r3d5" 07bdb2e89c69959c2b8cb8e61329536c032f187e
cd runs/repro-r3d5
uv sync --locked --python 3.13
uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /tmp/r3d5-wheel
uv pip install --python .venv/bin/python /tmp/r3d5-wheel/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
HEADLESS=1 SDL_VIDEODRIVER=dummy .venv/bin/python -m pytest -q
cargo test -p star-core -p star-rotk --locked
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked -- -D warnings
cd ../..
HEADLESS=1 runs/repro-r3d5/.venv/bin/python tools/rust_migration/integer_limit_probe.py --source runs/repro-r3d5 --output /tmp/r3d5-after --expect-equal
runs/repro-r3d5/.venv/bin/python tools/rust_migration/compare_integer_limit.py --results experiments/2026-09-rust-integer-limit/results
```

before运行省略--expect-equal，预期4组state不等但response仍相同；after预期20组全等。固定默认4300用于前后probe，自定义设置由契约及录制/重放测试验证。不得关闭解释器限制来掩盖旧差异。首次与累计的完整参数、响应和世界状态保存在raw.json.xz。

每一次Python/Rust配对比较**完整状态，不排除字段**。跨before/after进程另核对相同参数及Pythonoracle，只归零GameTime的三个创建墙钟字段（last_update_time/game_start_time/turn_start_time）；原始值始终保留。它们来自已有组件工厂创建时间，非CD、模拟dt或统计字段。此跨运行辅助归一化不参与判定G014是否修复。

Compact入口results/comparison.json、before/after/compact.json；raw.zip保存原始状态、日志、wheel和旧场景重放结果，compact.zip只含审阅材料和raw身份。逐成员hash见artifact-index，两个包的SHA/size见packages.json，Git保存的所有证据受SHA256SUMS覆盖。

[分析](analysis.md) · [决策](decision.md) · [GAP台账](../../../star-main/docs/native-benchmark-gaps.md)。未重新测量30Hz/5000Agents，CPython3.14及Linux安装矩阵仍留待R5。
