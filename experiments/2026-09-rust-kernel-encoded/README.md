# R3k4 — Rust只读批次：不可变编码事实共享

**Status: VALIDATED 内核检查点；完整迁移/容量仍未完成。** 生产 `star-nexus/star`，problem `a3ff47b796537e2a543d42da6094aa13d64f6e63`，fix/measurement `f37ae76785f05dd9dc9ac3009731267117bbda90`，validated `3892f95af6638e213f1b842fd9c0fe4b7b3dab80`，annotated tag `rust-kernel-r3k4-2026-09-24`。最终仅两份文档变化。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 内核补齐中 | R4 ░ | R5 ░`（非工时百分比）。Python保留SDK、策略、网络/ACK、UI和报告；本阶段只改Rust响应计算/编码。

## 1. 问题、设计与边界

上阶段取消装配时的多余JSON重建后，同阵营每个请求仍完整复制公共事实和Unit面板、重复编码相同嵌套字段。现在在只读段内，各阵营公共字段和每个不同Unit面板各编码一次，以不可变Arc持有。请求分别捕获owner与commandable；它们从不写进共享面板。serde RawValue仅由内核JSON Value编码生成，外部输入不能作为未经转义的原始片段拼接。

单条动作、可信批次与handler probe采用相同响应类型；普通动作继续持有原Value。遇到非faction查询请求就结束共享段，随后新建上下文。已有响应拥有查询时的不可变事实，不保留对运行世界/当前权限的实时引用；晚些序列化时，即便后续认领转移或敌军死亡也不能修改旧响应。保留原计数/校验/错误及revision处理；未加入线程、TTL、跨帧缓存或读请求等待凑批。

字段名与请求权限仍需逐响应编码，完整载荷仍需逐Agent输出、Python仍需解码。减少重复树复制和字段值编码不等于零复制传输或压缩协议。不同阵营仍分别投影Fog；基础地块/敌军事实保留原批次共享。

## 2. 环境与实验

M4/16GiB/macOS26.5.2、CPython3.13.12、Rust1.98.1 release；Chrome保持开启，实验串行，SDL dummy，无世界tick或绘制。复用R3k1/R3k2唯一raw：100静止Units/6211地块/局部7格视野与关闭Fog、5000静止Units/射程3/关闭Fog，MP0、seed42。前两种每请求选择5Units，后一种100Units。

每场景1/8请求；handler、public批次、单条动作single（只在1请求配置）共15项。每请求独立注册身份，墙钟元数据固定；每次导入/reset到同一已注册状态。1次预热+5次测量，保留全部样本。计时native处理与JSON编码，不含注册/import/reset/Python解码/模拟/渲染/Hub/排队，不是真实Agent节奏。

## 3. 前后结果

| 场景 | 入口 | 请求数 | 旧中位ms | 新中位ms | 旧/新 |
| --- | --- | --- | --- | --- | --- |
| terrain-local | handler | 1 | 0.126 | 0.106 | 1.18× |
| terrain-local | public | 1 | 0.139 | 0.106 | 1.32× |
| terrain-local | single | 1 | 0.124 | 0.106 | 1.18× |
| terrain-local | handler | 8 | 0.357 | 0.120 | 2.97× |
| terrain-local | public | 8 | 0.331 | 0.131 | 2.53× |
| terrain-disabled | handler | 1 | 16.128 | 12.283 | 1.31× |
| terrain-disabled | public | 1 | 17.199 | 12.414 | 1.39× |
| terrain-disabled | single | 1 | 17.048 | 12.454 | 1.37× |
| terrain-disabled | handler | 8 | 50.775 | 13.870 | 3.66× |
| terrain-disabled | public | 8 | 51.357 | 14.373 | 3.57× |
| units-5000 | handler | 1 | 28.417 | 22.939 | 1.24× |
| units-5000 | public | 1 | 28.717 | 21.109 | 1.36× |
| units-5000 | single | 1 | 27.639 | 21.531 | 1.28× |
| units-5000 | handler | 8 | 87.741 | 24.184 | 3.63× |
| units-5000 | public | 8 | 88.366 | 23.552 | 3.75× |

5000Unit public八请求88.366→23.552ms；single27.639→21.531ms。八请求只public_encodes=1、panel_encodes=100，响应引用8/800；这两个引用计数包括第一次，不是cache hit。原有扫描/合法攻击/事实构造计数与before相同。

仍输出约6.04MB完整观测。23.552ms不包含世界推进、展示和排队，不能据此宣布5000Units+1000Agents/30Hz达标。五样本只支持局部诊断，不推断显著性或跨机器通用倍数；未单独测量内存峰值/分配次数。前一阶段旧数字不代替本轮同条件before。

## 4. 等价、生命周期与GAP

2156完整回归（新增12）、74针对性、3Rust/fmt/Clippy、旧6场景510节点重放通过。15组前后Agent完整响应、初始/最终状态hash和旧有计数相同；解压后的结果逐项比较，不只依赖hash。public批次还与同内核逐条执行完整结果/最终状态比较。原始观测与canonical归档响应相同；完整回归持续执行Python差分。

新增测试覆盖none/dummy/window×1/2/4参数（仍串行），引号/反斜杠/换行/空字符/Unicode身份与技能文字，同阵营不同权限、跨阵营查询、重复unit_ids及空选择，混合认领→查询→攻击死亡→查询，后续写入不修改旧响应，返回对象独立及reset/close。

API15新增四个诊断字段，诊断包整体hash/长度因此允许不同；Agent响应字段不变，single输出长度相同。schema5与oracle仍旧版，未发现新增玩法差异。[GAP台账](../../../star-main/docs/native-benchmark-gaps.md)已追加本轮证据和限制；G008/G009与R001/R002保持开放。

## 5. 复现

工具固定为Lab `c34682448d033d62c92a65e5b468cac3f5b1790a`，两个仓库平级。命令中工具路径指向该Lab节点的checkout；canonical输入归档路径及SHA见manifest。

```sh
cd /Users/liyang/Developer/star-main
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-kernel-encoded f37ae76785f05dd9dc9ac3009731267117bbda90
cd /Users/liyang/Developer/star-lab/runs/repro-kernel-encoded
uv sync --locked --python 3.13
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-kernel-encoded/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python -m pytest -q
.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/kernel_observation_assembly_probe.py --source . --output /Users/liyang/Developer/star-lab/runs/repro-kernel-encoded-results
```

before用生产 `a3ff47b796537e2a543d42da6094aa13d64f6e63` 与R3k3归档wheel执行相同工具。原始构建/安装/验证/A-B命令、cwd、环境覆盖及返回码在results/commands.json；精确安装扩展/硬件环境在environment.json。raw保存实际请求、完整结果和逐样本耗时；initial/final状态hash对照，由canonical世界与工具固定注册流程可完整重建，不重复存同一世界/旧replay轨迹。

```sh
cd /Users/liyang/Developer/star-lab/experiments/2026-09-rust-kernel-encoded
shasum -a 256 -c artifacts/SHA256SUMS
```

## 6. 当前版本和接续

API15 release已安装生产venv及完整目录`runs/star-rust-kernel-encoded`，扩展SHA `62451b1ee2844373f162e1489d40684894febbc0e8efc27167046f1c18363206`；旧R3k3/API14目录/wheel保留。49处原删除保留，main仍6a970dea，未merge/push，Python默认。

本阶段确定了只读结果不可变持有与权限隔离的边界。下一步继续权威状态写入/派生数据覆盖审计，明确只读任务的输入和生命周期，再推进R4真实并行；不把Python应用集成转成Rust重写。原5000Units+1000Agents/30Hz/约30秒闭环关卡和5000Agents扩展均未验收。
