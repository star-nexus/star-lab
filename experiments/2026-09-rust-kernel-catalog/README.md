# R3k2 — Rust公共观测：Unit成员索引与可见地形投影

**VALIDATED内核检查点；完整迁移/容量仍未完成。** 最终 `67e35deaacef22ed1754f39245d771c3af887888` / annotated tag `rust-kernel-r3k2-2026-09-24`；构建/测量 `0e912d85c18027e77125fd770500bdd123c30d75`，最终仅两份文档变化。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 内核补齐中 | R4 ░ | R5 ░`（非工时百分比；真正并行尚未开始）。

## 范围和改动

继续只迁移Rust负责高效执行世界的部分。Python保留SDK、策略、网络/ACK、UI和报告。前置R3k1已补攻击候选空间筛选，本次减少公共观测无关实体和隐藏地图扫描。Unit成员索引存稳定ID→ECS句柄，导入/reset建立，死亡与视觉过期销毁时更新；不复制组件。当前运行期间只动态创建视觉实体，未来新增Unit创建必须维护成员表。

阵营统计/敌军投影由O(全部ECS实体)降为O(Unit成员)；仍保留死亡未销毁/缺组件的原过滤规则。地形选可见格或地图格较小的一方，精确求交集并保留坐标排序；空视野不扫地图，关闭Fog仍输出全图。没有TTL、跨帧缓存、信息删减、玩法近似或新线程实现。

## 场景、方法与结果

M4/16GiB/macOS26.5.2、CPython3.13.12、release构建；Chrome保持开启、实验串行。工具 `b395de44a4c08cbf08841195a5fd5f49dea0f5d7`。100静止Units、魏蜀各半，查询5个己方Unit，MP0用于隔离本项扫描成本；地块6211/60919，Fog局部7格/空/关闭，seed42，墙钟字段固定1720000000。非canonical网游闭环。每组预热1次、5样本，计时原生查询与JSON编码，不含导入、Python解码、tick、窗口、网络或排队。未删除慢样本。

| 地块 | Fog | 旧中位ms | 新中位ms | 旧/新 |
| --- | --- | --- | --- | --- |
| 6211 | local | 0.218 | 0.124 | 1.76× |
| 6211 | empty | 0.172 | 0.086 | 1.99× |
| 6211 | disabled | 26.659 | 25.250 | 1.06× |
| 60919 | local | 1.224 | 0.125 | 9.76× |
| 60919 | empty | 0.842 | 0.084 | 9.99× |
| 60919 | disabled | 294.697 | 296.953 | 0.99× |

60919地块局部Fog：旧两次实体遍历各61019→新各100，地形60919→7。旧访问量是按源码和实际输入推导，新量来自诊断计数，不能混称两边都实测计数。空Fog地形访问0。关闭Fog仍访问60919格，294.697→296.953ms的有效负对照保留；5样本不做统计显著性判断。整个观测并非O(active)。

诊断包的`response_bytes`包括新增metrics，前后因此略有不同；Agent完整响应hash逐项相同。全地图约4.28MB输出成本仍然存在，不能把局部7格场景的提速当作普遍倍数或30Hz容量通过。

## 等价验证和GAP

2144完整回归（新增32）、165针对性、3Rust/fmt/Clippy全部通过；旧6场景510节点重放一致。6组初始状态与完整响应hash相同，查询前后状态不变；6211地块3组另对照Python完整响应。契约覆盖Fog开关/缺失/空/局部/超出地图，特殊缺组件Unit、tile缺Terrain、死亡、reset、Unit+特效混合实体到期销毁、1/2/4线程参数（仍串行）。未发现新增游戏规则差异，[GAP台账](../../../star-main/docs/native-benchmark-gaps.md)已更新；G008/G009及R001/R002不自动关闭。

## 复现

两个仓库平级放置；精确工具用Lab `b395de44a4c08cbf08841195a5fd5f49dea0f5d7` 建worktree。下列命令里的Lab路径改为该工具worktree可固定工具版本。

```sh
cd /Users/liyang/Developer/star-main
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-kernel-catalog 0e912d85c18027e77125fd770500bdd123c30d75
cd /Users/liyang/Developer/star-lab/runs/repro-kernel-catalog
uv sync --locked
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-kernel-catalog/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python -m pytest -q
.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/kernel_observation_catalog_probe.py --source . --output /Users/liyang/Developer/star-lab/runs/repro-kernel-catalog-results
```

before使用 `d5a1d5cfc0096a632019a6cc7d94929b77238db7` 与R3k1唯一归档wheel，执行相同工具。release构建、目标测试、安装、cargo与重放完整argv/cwd见`results/commands.json`；环境、扩展SHA、源SHA和轨迹引用见manifest。旧场景轨迹引用R3-host-authority唯一归档，不重复复制。raw.xz包含初始化状态、完整响应、原始样本，compact/comparison可逐项核对。

```sh
cd /Users/liyang/Developer/star-lab/experiments/2026-09-rust-kernel-catalog
shasum -a 256 -c artifacts/SHA256SUMS
```

## 接续

API14 release已安装到生产venv和完整目录`runs/star-rust-kernel-catalog`；旧API13目录保持原样。生产49处原删除保留，main仍6a970dea，未merge/push，Python默认。

下一步继续核验Rust观测公共数据装配、序列化和跨语言批次成本，以及权威状态写入覆盖，确定并行只读任务边界后再进入R4。Python网络/ACK/BOT策略集成仍单列，不作为Rust重写任务。首个5000Units+1000Agents/30Hz/约30秒闭环与5000Agents扩展尚未验收。
