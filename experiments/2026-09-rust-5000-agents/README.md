# R4d：5000-Agent容量诊断与Rust观测JSON直传

进度：`Rust世界内核 █ 已迁移 | 观测数据传递 █ 本轮完成 | 5000-Agent容量 ▒ 未通过 | 发布切换 ░ 未完成`。这是阶段状态，不是工时百分比。

新增Python `RustRuntime.get_faction_state_json`，保留原字典接口，让host直接取得Rust已编码的完整响应。查询仍走原鉴权入口，使用同一接纳锁；不删字段、不跨帧缓存、不改变Agent闭环，也不把SDK/策略/UI重写Rust。此接口尚未自动接入网络host。

## 源码与结果

- 旧版/测量：`07bdb2e89c69959c2b8cb8e61329536c032f187e`，API18；生产恢复点`257ebf11372fe82ed368bdbba2c3760a6450d110`仅有额外文档。
- 新接口/测试/测量：`5147e4d8e0c33c997bd86960d87fa4b5b3ca90c5`。最终生产`72ea765bf3fc962fdea185d0311db2970ed422bd`，tag `rust-kernel-r4d-2026-09-27`；最终只补用户文档和GAP台账。
- Rust二进制未改、无需重新编译；API18扩展SHA `324454a00ab8bd3559c9229e6c6c9644242d65c488585eba7d29a63b39d29405`。native目录/Cargo依赖与旧节点无diff。
- 旧窗口工具 `19c99a32bdbcb4c3727becfcad742b329818441f`；固定输入归因 `c9e15ac`（完整SHA见manifest）；新窗口工具`4fcc2fa`（同上）。实验后的工具提交仅修复内部请求计数及增加分析/归档记录，逐run身份以原始结果为准。

所有窗口run均为本机Apple M4、5000存活Units、30Hz固定世界时钟、30秒预热+60秒测量、Cocoa 2480×1239窗口、Fog开启、canonical地图、minimap单位层关闭、有限实验GC延迟、Chrome开启。Agent观测→动作→15–45秒截断正态思考（均值30/标准差5），初次均匀错开0–30秒，无思考期间轮询。随机move/attack/wait为50/25/25，非法选择等待。5000 Agents每人1Unit，1000 Agents约每人5Units。保留所有准入窗口慢帧；不是5000同时移动。

| Run | Agent数 | wire | 预算ms | 帧P99ms | Hz | 观测P99ms | 动作排队P99ms | 完成比例 | 通过 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| a1000-t1 | 1000 | False | 8 | 28.900 | 30.000 | 121.462 | 128.913 | 1.004 | False |
| a1000-wire-b8 | 1000 | True | 8 | 27.385 | 30.000 | 40.641 | 32.818 | 1.002 | True |
| a5000-t1-b18 | 5000 | False | 18 | 39.710 | 28.517 | 3461.279 | 3462.356 | 0.883 | False |
| a5000-t1 | 5000 | False | 8 | 26.354 | 30.000 | 26593.926 | 26560.403 | 0.550 | False |
| a5000-wire-b12 | 5000 | True | 12 | 33.124 | 30.000 | 1075.260 | 1089.718 | 1.007 | False |
| a5000-wire-b14 | 5000 | True | 14 | 35.300 | 30.000 | 409.486 | 405.624 | 1.008 | False |
| a5000-wire-b8 | 5000 | True | 8 | 26.325 | 30.000 | 7746.797 | 7762.090 | 0.744 | False |


完成比例沿用Lab guard，为测量窗内观测数/名义观测数，窗口边界移动可使其略大于1；不是每个Agent都按时完成。所有run均5000存活，实际同时移动峰值68–172。

**本阶段没有任何300秒×3容量验收结论。** 5000-Agent诊断未满足全部门槛；不能只凭30Hz或完成比例判断达标。1000-Agent新旧短测不构成完整API18容量验收，也不据一次负结果宣称API18发生回归。R4c/API17三轮通过记录仍绑定原tag；旧窗口2480×1243，本轮全部2480×1239，因此也不能直接作为该历史结果的严格版本A/B。

## 固定输入归因与验证

旧5000-Agent轨迹：19929请求、2679tick、2679展示提取。传统路径平均3.223ms（Rust和绑定1.020、服务端解码0.735、服务端重编码0.722、客户端解码0.742）；直接路径1线程1.774ms、4线程1.750ms。移除服务端一次decode/encode约省45%，没有省去客户端decode。全部响应、事件、最终状态一致，该轨迹原始字节也相同。只是单次固定流归因，不宣称线程收益的统计显著性或窗口容量。

新接口实际窗口轨迹另以4线程重放，完整回复、展示事件、最终权威状态一致（计数见`results/after-replay-t4.json`）。新增22契约、完整2217Python回归、Lab18契约通过。没有Rust源码变化，未重复Cargo测试/构建。无新增已确认玩法GAP；G008/G009/R001/R002继续开放，详见生产`docs/native-benchmark-gaps.md`。

## 复现

1. 分别checkout上述before/after SHA；`uv sync --locked`。使用CPython3.13.12及R3d5 API18 wheel。wheel的规范位置为`../2026-09-rust-integer-limit/artifacts/r3d5-integer-limit-raw.zip`中的`artifacts/after/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl`；解包后`uv pip install --python <source>/.venv/bin/python <wheel>`。也可按生产文档用锁定工具链release构建，重新记录扩展hash，严格重放必须使用原wheel。
2. Lab checkout对应工具SHA；canonical场景来自`../2026-09-10k-e8-volume/artifacts/scenario.zip`，runner生成fixture，hash在每份结果里。保留Chrome，串行运行。
3. 完整启动argv、cwd、安全环境变量在`results/commands.json`；将其中source/python/output绝对路径替换为本机路径。窗口命令是`tools/p3_runtime.py --backend rust --record-native-inputs --native-threads 1 --fps 30 --clock-mode fixed --cycle-mode post-action --jitter-seconds 5 --units 5000 --agents <1000|5000> --delay 30 --scope selected --layout canonical --policy stochastic --warmup 30 --seconds 60 --budget-ms <8|12|14|18> --gc-policy realtime_defer --source <source> --output <output>`；新版另加`--native-wire`。设置`HEADLESS=0 SDL_VIDEODRIVER=cocoa PYTHONPATH=<source>:<lab>/tools:<lab>/tools/rust_migration`。
4. 从本阶段raw ZIP解包恢复原始结果/轨迹后，运行`python tools/rust_migration/analyze_agent_capacity.py --root experiments/2026-09-rust-5000-agents`，必须重算通过。固定流对照：`profile_native_boundary.py --source <before> --trace <a5000-t1.trace.json.gz> --mode legacy|direct --threads 1|4 --output <output>`；它是诊断探针，不是用户接口。新轨迹：`replay_rendered_loop.py --source <after> --trace <a5000-wire-b12.trace.json.gz> --threads 4 --output <output>`。
5. `shasum -a 256 -c artifacts/SHA256SUMS`。raw/compact位置、大小、SHA及逐成员hash见`results/packages.json`和`results/artifact-index.json`。本地解包文件忽略入库，ZIP是规范raw位置。

预期旧5000-Agent8ms预算出现秒级排队；新直传减少服务端转换但测试预算仍未同时满足帧P99≤33.33ms、观测/动作排队≤100ms。跨机器绝对耗时会变化；不要根据某次单点差值推断语言或版本回归。
