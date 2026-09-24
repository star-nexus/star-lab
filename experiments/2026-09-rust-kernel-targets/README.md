# R3k1 — Rust观测内核：精确局部攻击候选

**VALIDATED检查点；完整迁移/容量仍未完成。** 最终 `d5a1d5cfc0096a632019a6cc7d94929b77238db7` / annotated tag `rust-kernel-r3k1-2026-09-24`。生产实现/构建 `7460cd9`，测试/测量 `8dd16f4`；其间只有测试变化，最终仅文档变化。manifest保存精确SHA和代码相同证明。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 内核补齐中 | R4 ░ | R5 ░`（非工时百分比；真正并行尚未开始）。

## 范围与原因

用户明确只迁移Rust负责高效执行世界的部分。本轮暂停上一恢复入口建议的网络host集成，连接、ACK、BOT策略、窗口与报告继续属于Python；这些未接通项单独保留，不当成需要重写Rust的模块。

原Python在有空间索引时已经局部筛选attackable；API12 Rust遗漏这项优化，每个己方Unit扫描全部阵营可见敌军。射程外判断还构造了详细错误JSON。理论候选对随己方选择数P×可见敌军数V增长；本轮在原Rust占用索引上补齐原优化，无新缓存、依赖或跨语言回调。

新内核先检查攻击者基础条件，再选择遍历精确hex射程盘或敌军列表中工作量较小的一边。局部盘与可见敌军集合相交后，仍使用原Combat谓词；返回按实体ID排序。大射程走敌军坐标筛选，不枚举天量空格。移动使用已提交格子，死亡即时移除占用，reset重建已有索引。Fog/权限/行动点/叠格/移动弱化与批次边界不变。

局部路径是O(R²+盘内占用)，另含可见集合查找与结果排序；大射程路径仍O(V)。不声称任何密度下O(1)。地形、可见敌军公共事实、面板装配和编码仍有成本。API13仅新增诊断工作计数字段，Agent响应不变，schema5/oracle不变。

## 实验与结果

M4/16GiB/macOS26.5.2、CPython3.13.12、release构建，Chrome保持开启；实验串行。工具 `264bc5ec77dc787a161fedfa184e7614e45c4738`。before为API12/tag `rust-kernel-r3d4a-2026-09-24`，after为API13。

Probe构建500/5000个静止Units的普通地形盘，各半魏蜀；Fog关闭，查询分界附近100个己方Units，MP设0以隔离合法攻击查询。不是canonical网游闭环场景，不代表Agent实际单次载荷或30Hz世界帧。每配置预热1次、测5次；计时包括原生查询和JSON编码，不含Python解码、世界tick、绘制、Hub或Agent排队。原始每次样本与初始化完整状态、完整响应均已存档。

| Units | 可见敌军 | 射程/AP | 旧中位ms | 新中位ms | 旧/新 |
| --- | --- | --- | --- | --- | --- |
| 500 | 250 | 1/2 | 48.75 | 5.52 | 8.82× |
| 500 | 250 | 3/2 | 47.12 | 5.60 | 8.41× |
| 500 | 250 | 80/2 | 14.72 | 15.13 | 0.97× |
| 500 | 250 | 3/0 | 6.27 | 5.34 | 1.18× |
| 5000 | 2500 | 1/2 | 468.45 | 42.50 | 11.02× |
| 5000 | 2500 | 3/2 | 465.20 | 44.01 | 10.57× |
| 5000 | 2500 | 80/2 | 143.43 | 144.66 | 0.99× |
| 5000 | 2500 | 3/0 | 52.65 | 44.35 | 1.19× |

**有效负对照保留**：射程80几乎所有敌军都合法，不能用空间局部性降低目标数量，新增距离过滤略增工作；500/5000两档分别约2.8%/0.9%变慢。本次5样本只作局部诊断，不推断统计显著性或普遍吞吐比例。

因果计数：5000档原路径每100面板检查250000目标对（由源码与实际面板/敌军数推导，非旧版新增计数器）；新射程1为700格查表、166目标合法性检查；射程3为3700格查表、1393检查。AP0直接退出、三项新计数均为0。射程80仍检查250000敌军位置、248654目标合法性判断，符合负对照预期。公开payload约0.75MB/2.06MB，不能把剩余42ms忽略后宣传为整帧30Hz已通过。

## 等价验证与GAP

8组新旧初始状态和完整响应hash逐项相同，查询前后完整状态不变；500档4组另外对照Python完整响应。2112项完整回归通过（新增133），163项针对性通过；3Rust测试、fmt/Clippy通过；原六场景510节点重放通过。新契约覆盖坐标奇偶/负坐标、Fog、三阵营/叠格/死亡/缺组件、负/零/普通/巨大射程、移动过程与落格、攻击死亡、reset及只读批次复用。未新增多线程实现。

首次新窗口死亡fixture混用了基础Combat与窗口索引，留下Python尸体占用，reachable差一格；原生产使用WindowCombatSystem，先清索引再销毁。fixture纠正为生产组合后通过。日志存于setup-error，不当作生产Bug或优化收益。其他中间提交仅在运行前修正测试索引和巨大射程对照，未改玩法。无已确认新增规则/机制GAP；[生产台账](../../../star-main/docs/native-benchmark-gaps.md)记录本轮边界，原G008/G009/R001/R002不自动关闭。

## 复现

```sh
cd /Users/liyang/Developer/star-main
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-kernel-targets 8dd16f4
cd /Users/liyang/Developer/star-lab/runs/repro-kernel-targets
uv sync --locked
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-kernel-targets/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python -m pytest -q
.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/kernel_attack_candidates_probe.py --source . --output /Users/liyang/Developer/star-lab/runs/repro-kernel-targets-results
```

精确工具用Lab `264bc5ec77dc787a161fedfa184e7614e45c4738`新建worktree。before用生产 `5ce4b3f02a5fb676e11c8bc240e86513d3e00b25`和R3d4a归档唯一wheel，运行同一probe。构建、安装、检查及旧场景重放参数见 `results/commands.json`，源码/环境/扩展SHA见manifest/environment；raw、compact、comparison与所有文件checksum在本目录。旧场景轨迹继续引用R3d4a唯一归档，不重复复制。成本数字没有通过改采样窗口或删慢样本得到。

## 决策与接续

保留精确局部筛选。下一步继续Rust观测内核公共事实构建、索引与批量装配成本审计，按证据优化，再进入只读并行；Python网络/ACK/BOT策略集成单列，不能再次成为Rust改写任务。继续保留完整差分、GAP与重放门槛。5000Units+1000Agents/30Hz/30秒闭环正式验收和5000Agents扩展目标均未完成。

当前完整试玩目录 `runs/star-rust-kernel-targets` 为最终tag；生产venv也装API13。旧API12 checkout保持原状。生产原49处Agent/font删除保留，main未变，未merge/push，Python默认。
