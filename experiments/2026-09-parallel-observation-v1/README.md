# 并行观测v1：结果等价，逐请求完整快照成本抵消收益

日期：2026-09-11。第一版本地进程池原型已完成，保留开发分支；不合并main，不启用默认路径，不登记实时容量Frontier。

5000存活Units、1000已注册合成Agents、selected面板、Fog开启的冻结场景上，串行与1/2/4 worker各测两轮、每轮120次，**960次业务结果全部一致**。完整guard全部通过，936项回归测试通过。查询在三个阵营间轮转，覆盖120个Agent；不代表1000Agent同时请求。

| 模式 | 查询/秒 | owner导出均值ms | worker还原均值ms | 构建均值ms | 请求P99 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| 串行 | 141.12–141.65 | — | — | 5.52–5.55 | 7.41–7.64 |
| 1 worker | 32.25–32.50 | 8.14–8.22 | 10.41–10.45 | 17.87–18.03 | 161.06–165.18 |
| 2 worker | 51.25–52.18 | 8.52–8.54 | 11.44–11.69 | 20.90–21.40 | 121.84–126.93 |
| 4 worker | 62.31–62.65 | 9.31–9.61 | 11.12–11.25 | 26.12–26.25 | 139.29–140.49 |

这些是无窗口、世界停止推进、持续补充至最多4个在途任务的吞吐探针，不是30秒思考的动态闭环。P99包含主进程轮询等待及客户端解码；并行队列与串行单请求的并发度不同，不能外推运行时P99。吞吐计时包括等价断言开销，各组相同。restore只包含解包/索引还原，按需组件还原仍计在build中。

## 精确版本

- STAR生产main基线：6a970deaee7d9b8d3939edd102973f2377edd6ac。
- 同一次测量中的串行与并行路径均来自：`3c4fba1a40fccee7bfc06575ade338c30a4b784e`。
- 开发分支：`codex/parallel-observation-v1`。
- annotated tag：`p3-parallel-observation-v1-prototype-2026-09-11`，tag对象7427d5bc4337f44af06eff701ff2a92ccdc74cd0。此tag标记功能原型和负性能证据，不代表容量达标。
- 主测量Lab工具：`57343ce1b18f457b745391b5352081f547e40b45`；前一轮工具734f5c21dc29757501cf39859fa06a54077d0141的960次对照也保留在raw的pre-guard组。
- 实现和使用说明位于STAR的`docs/parallel-observation.md`；阶段记录见[实施记录](../../records/10k-parallel-env-v1.md)。

## 复现

使用独立STAR checkout固定到上述tag/commit，按uv.lock准备Python3.13环境；Lab checkout固定到上述主测量工具SHA。Chrome保持开启，实验串行执行，禁止同时跑测试/压缩或另一性能实验。地图通过Lab fixture工具生成，规范fixture复用[已有归档](../2026-09-p3-clock24/artifacts/fixture-1eeff5d72863206587e852c85fb5b594dc5489488bf40556e848fe13a9fc1a52.zip)。

```sh
# 在star-lab目录执行。替换source与Python为固定版本checkout的实际路径。
/Users/liyang/Developer/star-main/.venv/bin/python tools/p3_parallel_probe.py \
  --source /Users/liyang/Developer/star-main \
  --units 5000 --agents 1000 --queries 120 --workers 2 --max-pending 4 \
  --output runs/parallel-v1-guarded/r1-w2.json
```

依次将workers设为0、1、2、4，完成后再重复一轮。所有参数都记录在raw。没有额外专用环境变量；display=none、hub_url=None、seed=42由工具设置。先执行一次world.update(1/24)及空间索引构建；注册认领后用全部120次串行查询生成等价参考，再预热全部worker和4/8次观测。计时内不再world.update、不发送move/attack、不模拟思考，GC保持默认开启。预热和建世界时间不计入吞吐。

预期功能签名：all_equal=true，guards全部true，注册1000、Unit与存活各5000，前后census完全一致。
预期成本签名：逐请求导出+还原明显超过被移出的普通观测成本；增加worker改善这个原型的吞吐，但仍落后于串行。具体毫秒值依赖机器，不将此区间设为可移植断言。

## 不重跑性能的证据核验

在包含本归档工具的Lab版本上：

```sh
/Users/liyang/Developer/star-main/.venv/bin/python tools/p3_parallel_archive.py \
  --case experiments/2026-09-parallel-observation-v1 --verify
cd experiments/2026-09-parallel-observation-v1
shasum -a 256 -c artifacts/SHA256SUMS
```

核验从raw重算每组统计，检查样本完整性、版本/fixture/参考结果hash一致、guard与compact一致。完整记录见[manifest](manifest.yaml)、[分析](analysis.md)、[决策](decision.md)。
