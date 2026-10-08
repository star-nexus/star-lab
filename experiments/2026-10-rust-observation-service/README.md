# E8：观测服务专项——ECS 定位与人口统计分配

**Status:** REPRODUCED；服务候选有收益，组合收益门槛未通过，默认关闭。
**STAR repository:** `star-nexus/star`
**Problem commit:** `11d9927f7a1bffa32dd85c9009944424826508e5`
**Entity lookup candidate:** `455ab9937de5134fcd1ac70610544c1b0a43b9f3`
**Census candidate:** `8c2afd7153ebc8ec6c80dd9f3a1406be440405e0`
**Validated production commit/tag:** N/A

## 1. Problem

前一轮 E8 缓存复用改善观测服务，完整 Lab 宿主却未通过净收益门槛。此次只追踪单条、段首和段内请求的实际构建，选择两个独立小因子；不重跑长 P2，不扩大矩阵。

## 2. Why it matters

5000 Units＋1000 Agents 的冷观测仍需人口统计和阵营事实。降低这部分成本可能改善服务和尾部，但服务改善不能直接换算整帧收益。

## 3. Source checkout

未 push/merge。先从上一实验 `e8-accounting-v2-20261007-raw.zip` 中的 `raw/admitted-observation-source.bundle` 恢复父节点 `11d9927`；遵循上一实验 README 的源恢复链。再解压本实验原始包，依次恢复增量源：

```bash
git fetch /path/to/extracted/runs/scan-source.bundle HEAD
git fetch /path/to/extracted/runs/census/source.bundle HEAD
git checkout 8c2afd7153ebc8ec6c80dd9f3a1406be440405e0
uv sync --frozen
```

第一个 bundle 要求父节点 `11d9927`，第二个要求 `455ab99`；`git bundle verify` 必须通过。正式数字分别属于各自二进制内的配对，不能把两次 baseline 差异视为候选间因果差异。

## 4. Environment

Mac16,10／Apple M4，10 physical/logical CPU，16 GiB；macOS 26.5.2；CPython 3.13.12，NumPy 2.3.2；Rust 1.98.1／maturin 1.15.0／uv 0.12.5。锁文件 SHA 见 manifest。

```bash
RUSTUP_TOOLCHAIN=1.98.1 uv tool run --from maturin==1.15.0 maturin build \
  --release --locked --manifest-path native/python/Cargo.toml \
  --interpreter .venv/bin/python --out /path/to/wheels
```

解压 wheel 到独立 extension 目录，避免覆盖已安装的 `3e0ebb` 扩展。验收测试使用 `SDL_VIDEODRIVER=dummy` 和 `PYTHONPATH=<extension>:<source>`。测量无渲染，不打开窗口；压力仅记录，不自动暂停、kill 或超时。

## 5. Reproduce the problem / controlled screen

规范输入复用上一实验 `e8-p0-20261007-raw.zip`：`runs/window.trace.json.gz`、其 initial 文件及 `runs/window.admission.json`。不重新采集实时轨迹。每侧都是同一 12148 请求／2617 tick／3010 观测，保留全部预热和慢样本。

下面使用 census wheel（SHA 见 manifest/identity）；首因子用 `455ab99` wheel 和 `screen_observation_scan.py`，完整原始命令也保存在各 monitor 的 `command` 中。

```bash
python tools/rust_migration/monitor_observation_admission.py \
  --report /path/to/new/screen.monitor.json -- \
  /path/to/source/.venv/bin/python tools/rust_migration/screen_observation_census.py \
  --source /path/to/source --extension-dir /path/to/census/extension \
  --extension-sha256 c6a60a42fdafeee481620e89248a1a8604b7e3b3835b7b2a0f43053999977d88 \
  --trace /path/to/input/window.trace.json.gz \
  --admission /path/to/input/window.admission.json --output /path/to/new/screen.json
```

四个持续存在的 World，逐 enclosing tick 交替 ABBA/BAAB。两侧均使用相同 encoded 段；只保留执行长度 2–4 的 750 个原录制段，早结束的一条段走普通路径。这是固定输入服务筛选，排除真实 heap 接纳、持续 Session、显示 apply/render/submit 和生产网络。新 Session、固定 clock 的消费核保持一致，不能称真实宿主消费。

## 6. Expected problem / candidate signatures

首因子未通过：服务改善 2.773%，区间跨零；所测总工作变慢 3.138%。第二因子服务均值 2.3733→2.1560ms，改善 9.1569%，服务 P99 3.4066→3.0226ms；所测总工作 3.6577→3.5957ms，改善 1.6956%，但改善区间 −0.0598–0.1878ms 跨零。两个组合筛选均不通过，不采用默认。

## 7. Validate the candidate / integrity

```bash
SDL_VIDEODRIVER=dummy PYTHONPATH=/path/to/extension:/path/to/source \
  /path/to/source/.venv/bin/python -m pytest -q \
  rotk_env/tests/test_native_observation_scan.py \
  rotk_env/tests/test_native_admitted_observation.py \
  rotk_env/tests/test_native_observation.py rotk_env/tests/test_native_encoded_observation.py \
  rotk_env/tests/test_native_observation_profile.py rotk_env/tests/test_native_parallel_observation.py
python tools/rust_migration/verify_observation_service.py \
  --runs /path/to/extracted/runs --output /path/to/new/integrity.json
cd experiments/2026-10-rust-observation-service
shasum -a 256 -c artifacts/SHA256SUMS
```

最终 131 项通过；每次短完整重放校验所有 wire、四侧展示增量、事件、消费命令和最终权威状态。不是新源完整 9880-tick、多轮稳定性、native4 宿主或像素验收。原始 ZIP 内另有 SHA256SUMS，38 个成员已逐项核验。wheel、两个源码 bundle、冻结执行/分析/监督工具和两次全部样本均在原始包；原输入不重复归档。

当前运行全部结束。旧 `.progress.json` 可能保留最后 running checkpoint，以最终报告和 monitor 为准，勿从该 checkpoint 重启。
