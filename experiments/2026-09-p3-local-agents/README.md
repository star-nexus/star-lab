# P3 — 本地合成 Agent：第一轮优化与容量负结果

**状态：第一轮优化已验证并集成；千 Agent 容量目标未达成，P3 继续。**
P0 保持完成，P1/P2 跳过，Protocol/Hub 与 P4 暂缓。本轮不新增 Performance Frontier。

生产起点 `02d0fc1b598c54a172e1122ac9ea4c1e2f46ec15`；正式测量候选
`e8b48c0568fb8830055bf053a724acc2b4e5c04c`；合并前开发 tag
`p3-observation-pre-squash-2026-09-09` → `c9737451de97f1b1903123377a1514227c3ffdf5`；
squash 后 main `08c857e5df39f671c5a13bf04b9af9aac0800e78`。tag 是可追溯检查点，不是容量达标里程碑。

## 本轮结论

真实注册、多 Unit 认领、所控 Unit 观测、独立慢决策、合法 move/attack 执行已在本地贯通。
生产增加可选 `unit_ids` 投影，并消除逐 Unit 重复全局占用扫描、攻击候选全量枚举和重复阵营统计。
完整共享 Fog、地形、可见敌人仍保留；省略参数兼容原行为。

1Hz 观测下，3,000 Units / 1,000 Agents 只完成 12.06% 目标请求；
5,000 / 1,000 完成 8.99%。关闭 JSON 编码后 3,000 / 1,000 也只达到 14.99%。
世界 30Hz 与 Agent 服务能力必须分别判断。

较早的 5,000 / 1,000、每 30 秒一次观测/决策的闭环，60 秒短测通过，但 300 秒整帧
P99 为 34.591ms，超过 33.333ms。完整失败窗口保留，不拿短测替代长测。
**没有任何点满足一条 >=300s 加三条独立 >=60s 的完整发布条件。**

## 阅读顺序

1. [analysis.md](analysis.md)：矩阵、归因、负结果与测量纠正。
2. [decision.md](decision.md)：保留的优化、集成回执、尚未完成事项。
3. [manifest.yaml](manifest.yaml)：版本、环境、边界和制品入口。
4. [results/discovery-matrix.json](results/discovery-matrix.json)：机器可读矩阵。
5. [artifacts/index.json](artifacts/index.json)：24 组 compact/raw 包及 SHA256/大小。

## 复现

分别检出结果内 `source.sha` 和 `tooling.sha`；不要仅按分支名复现。
在 Lab checkout 中用 STAR 的精确依赖锁安装环境，例如在 STAR worktree 执行 `uv sync --frozen`。
依赖锁哈希、Python、窗口尺寸与安全环境键在每个运行结果中。
本机 Apple M4 / Mac16,10 / 16GiB，macOS 26.5.2，Python 3.13.12，窗口 2480×1261。
Chrome 保持开启；没有因系统负载删帧。每次性能实验使用独立进程，严格串行。

```bash
# 从 Lab 执行；/path/to/star-worktree 固定在目标 source.sha。
/path/to/star/.venv/bin/python tools/p3_runtime.py \
  --source /path/to/star-worktree --units 3000 --agents 1000 \
  --observation-hz 1 --delay 1 --scope selected --budget-ms 12 \
  --seconds 15 --warmup 5 --policy move --gc-policy realtime_defer \
  --output runs/reproduce-poll3000.json > runs/reproduce-poll3000.log 2>&1

# 期望失败签名：offered_load_met、observation_p99、action_queue_p99、queue_bounded 失败。
# 15s discovery 本身也不满足 duration_formal，不能作为容量发布点。
```

矩阵覆盖 100/100、1000/1000、3000/1000、5000/1000、10000/1000、
10000/5000、10000/10000（Units/Agents）的 1Hz；5000/1000 再测 5/10/30Hz。
所有精确启动参数位于各点 `workload`，随机种子固定 42。
复现旧闭环时不传 `--observation-hz`，并按点设置 `--delay`、warmup 和 seconds。
静态归因使用 `tools/p3_local_agents.py`，不等同于 runtime 容量。

```bash
cd experiments/2026-09-p3-local-agents
shasum -a 256 -c artifacts/SHA256SUMS
unzip artifacts/gate5000-d30-300-raw.zip -d /tmp/star-p3-audit
cd ../..
/path/to/star/.venv/bin/python tools/p3_analyze.py /tmp/star-p3-audit/gate5000-d30-300.json
/path/to/star/.venv/bin/python tools/p3_report.py
```

每组 raw 包保留原始点、全部帧/事件/每秒 census 和日志；compact 指向 raw 文件及包哈希。
相同 fixture 只存一份 canonical ZIP；每点 `fixture_package` 指向它。
生成 fixture 仍来自 E8 canonical scenario 和精确版本的 Lab parser 工具。
解包复核只使用标准库，不必启动窗口。

## 测量边界

真实窗口 ENV/Animation/Vision/Fog/render 保持开启。调用
`LLMSystem._process_action_request(send_response=False)`：保留 ENV 业务校验和执行，
绕过 socket/Hub、传输会话和消息入口冷却包装；不是网络在线容量测试。
观测 JSON 编码计入，动作响应 JSON 编码未计入，真实动作业务/寻路计入。
合成 Agent 是状态机，不是 10,000 个线程、进程或真实 LLM。

世界、观测、决策三个时钟独立。周期观测保留原始 deadline，不丢请求、不合并积压；
慢决策仍使用开始思考时的快照，后续观测不会替换在途决策。
闭环和周期模式分开报告；计划早期错误地将观测与决策频率绑定，已纠正并保留历史负证据。

`realtime_defer` 仅表示有限实验 epoch 前收集 GC、epoch 内禁用；不能推断长期运营无维护成本。
MiniMap 动态单位关闭、gameplay input 屏蔽，世界仍有真实渲染。
resident 数不等于同时 moving 数；本轮没有宣称 100% 单位同时移动，也未运行移动 overlay 容量验证。
