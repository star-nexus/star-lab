# R3d3c — Rust VLM观测与Python窗口图像接入

**Status: VALIDATED checkpoint; 完整R3/迁移仍OPEN。**
问题节点 `24215823c74a79774d38cc0b354b6e3d091a3b86`；修复/构建/测量 `173410ad603121bfe97c028e6d121c7bd9a8e232`；最终 `30c4b76c152857c98ff45fc7952af9ceb758059e` / annotated tag `rust-kernel-r3d3c-2026-09-23`。最终只更新两份文档，运行代码与测试相同。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 功能迁移中 | R4 ░ | R5 ░`（█完成、▒进行中、░待实施/验收；非工时百分比）。

## 1. 问题与意义

显式允许get_faction_state_vlm后，旧Rust仍报未实现，Python提供阵营状态与现有窗口帧。G007阻断本地VLM接口迁移。新版本由Rust执行原鉴权/选择/观测，Python读取既有RenderEngine画面；默认Skirmish动作集不变，不自动开启VLM。批次完整预校验并冻结输入，在VLM处截图后才继续后续动作；普通查询保留共享。捕获失败仍返回成功的结构化观测和frame_error。

## 2. 环境与身份

M4/16GiB/macOS26.5.2、CPython3.13.12、pygame2.6.1、Rust1.98.1。API11/schema5，oracle=python-r0c-3cc4ffe；release扩展SHA `29e256d91e80337731050164c1fc20b9fb02fbc5ae14d1d49065a90e84c5515b`。工具：54组before/after为 `6e67f8a12be2f3c648fe3aafbc1b3b99367b42ae`；最终窗口/codec/其余重放为 `5eaa8cb223dec051ed4d31fec084a66f96ffd81a`；中间像素诊断 `c3fec33645aa82871009e6c1889167bb05b376d1`。工具文件变化/完整命令详见manifest与commands.json。Chrome保持开启，正式工作串行。

## 3. 精确复现

创建独立完整checkout，保留生产目录原49处Agent/font删除。旧wheel从上一阶段唯一归档安装，新wheel从本目录安装。旧source不得搭配API11。

```sh
cd /Users/liyang/Developer/star-main
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-r3d3c-before 24215823c74a79774d38cc0b354b6e3d091a3b86
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-r3d3c-after 173410ad603121bfe97c028e6d121c7bd9a8e232
cd /Users/liyang/Developer/star-lab
git worktree add --detach runs/repro-r3d3c-tools 5eaa8cb223dec051ed4d31fec084a66f96ffd81a
cd /Users/liyang/Developer/star-lab/runs/repro-r3d3c-before
uv sync --locked
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-text-order/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d3c-tools/tools/rust_migration/r3_vlm_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d3c-before --output /Users/liyang/Developer/star-lab/runs/repro-r3d3c-before-results
cd /Users/liyang/Developer/star-lab/runs/repro-r3d3c-after
uv sync --locked
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-vlm/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d3c-tools/tools/rust_migration/r3_vlm_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d3c-after --output /Users/liyang/Developer/star-lab/runs/repro-r3d3c-after-results --expect-supported
.venv/bin/python -m pytest -q
export PATH="$HOME/.cargo/bin:$PATH"
cargo test -p star-core -p star-rotk --locked
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked -- -D warnings
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d3c-tools/tools/rust_migration/r3_vlm_window_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d3c-after --output /Users/liyang/Developer/star-lab/runs/repro-r3d3c-window
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d3c-tools/tools/rust_migration/r3_vlm_codec_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d3c-after --output /Users/liyang/Developer/star-lab/runs/repro-r3d3c-codec
```

源码构建：after目录中执行 `CARGO_TARGET_DIR=/Users/liyang/Developer/star-main/target uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /Users/liyang/Developer/star-lab/runs/repro-r3d3c-wheel`，安装后使用新进程。所有测试、Player和旧/新场景重放命令在results/commands.json，替换输出目录可重跑；旧trace只引用原归档。

## 4. 预期签名与结果

54组：两模式×三display配置×1/2/4设置×无screen/1×1/13×7。before全54个已鉴权VLM调用抛未实现；after全54组完整响应与状态相同。这些是Surface fixture，不冒充真实窗口。

| 检查 | 结果 |
| --- | --- |
| 完整回归 / Native / 新增VLM契约 | 1935 / 1013 / 38 |
| 54组已启用VLM响应与状态 | 0/54→54/54 |
| Cocoa真实窗口2模式×2显示视角 | 4/4与Python图像字节相同；均请求Wei |
| Rust单测 / fmt / Clippy | 3 / 通过 / 通过 |
| Player权威与投影 | 36/36，各自相等 |
| 旧场景 / 新场景及独立重放 | 各510节点，6场景 |

38项新契约覆盖默认拒绝、注册/越权、身份冒充、unit_ids、四种截图错误、动作M→VLM Q→动作N、正常查询共享、异常批次不执行前缀、输入冻结，以及截图期间step/reset/close排队。1/2/4仍串行，无并行收益结论。

## 5. 原始像素guard负结果与历史行为

旧PNG标签实际是TGA，显示视角取当前窗口而非请求阵营；截图不强制重绘到最新tick。真实窗口原始RGB与解码RGB首次比较失败，但Python/Rust编码字节相同。中间有效诊断保留在results/intermediate/pixel-guard，不能当成通过的无损截图测试。

独立三像素控制在旧、新两节点不使用Rust内核也产生同样结果：RGBA(200,80,30,128)→(100,40,15,128)，alpha0像素RGB归0，opaque对照不变。TGA RLE包原始BGRA值已含变换，排除只是解码器显示不同。结果见codec-before/after；媒体完全相同，只存codec-before一份。真实窗口四组解码RGB分别有2249/2252/2249/2252个通道不同，这只描述本次画面，不是一般图像质量指标。

最终窗口验收比较原Python实际编码字节，另保留原始RGB差异、PNG和TGA。没有通过修改玩法、截图视角、编码或标签消除差异。查看过real_time-shu.png，确认当前蜀视角Fog画面；旧HUD布局保持。VLM能力可用不等于真实LLM收到多模态图像，更不等于视觉权限隔离已建立。

## 6. 归档与当前使用

before/after全量raw、Cocoa四组全量raw和PNG/TGA、codec控制、Player raw、六场景trace及JSON/CSV结算均归档。源/工具SHA、环境、checksum、文档提交等价证明见manifest与results。

```sh
cd /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-vlm
shasum -a 256 -c artifacts/SHA256SUMS
cd /Users/liyang/Developer/star-lab/runs/star-rust-r3-vlm
.venv/bin/python -m rotk_env.main --backend rust --no-hub --skip-start --mode real_time --scenario chibi-small --seed 42
```

完整试玩目录已固定最终节点并安装API11；活动生产venv也更新。普通Skirmish默认不暴露VLM，需由场景MatchRules显式允许；本轮未加新CLI开关。无BOT时AI槽不会自主行动。Python仍默认、main未合并，旧API10/tag保留。

## 7. 后续

G007关闭限本地公开Python运行接口；G009网络host/回合ACK/结束投递、G008 BOT及冷组件覆盖仍待迁移，R001/R002继续开放。之后才R4真并行/R5容量和平台安装。没有新5000/1000/30Hz容量结论，无Linux/3.14验收，无原真实LLM分数影响结论。

[manifest](manifest.yaml) · [analysis](analysis.md) · [decision](decision.md) · [GAP台账](../../../star-main/docs/native-benchmark-gaps.md)
