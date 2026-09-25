# Analysis — R4b 公共事实直接编码

## 1. Observation

R4a 的 Unit 面板并行收益有限。仅增加计时的源码244b17f显示：5000 Units、单线程查询5个Unit，普通调用中位19.189ms；诊断调用的公共阵营构建14.109ms、面板计算0.240ms、对象释放4.894ms。最终完整响应编码为0.056ms。这个场景的主要成本并非可达格计算或最终输出。

6211个可见地块的场景也类似：公共构建8.154ms、释放3.014ms。只有7格可见的局部Fog场景成本低得多。

## 2. Competing hypotheses

- H1：公共JSON对象树的构建、深复制、首次编码及缓存释放占据主要时间。
- H2：Unit面板/寻路，或完整响应输出占据主要时间。

单次5-Unit查询的分段数据支持H1；不推论大子集和大批次永远也是如此。

## 3. Instrumentation

API17新增内部、按需启用的handler诊断，普通report与计时JSON分开返回。正常调用不读取计时器。census/public_encode嵌套于faction，faction/panels嵌套于batch，不能把全部字段相加。panels包含调度、等待和缓存提交，不能当作worker累计CPU时间。drop显式包含report、batch和请求的释放。

native总计不包含锁等待、计时报告自身编码、Python字符串转换；主要性能指标使用普通调用的墙钟耗时，包含返回Python字符串但不含Python解码。诊断与普通调用每轮交替先后顺序。初始化及准备期的参考查询不计入样本；每种调用1轮预热、5轮测量。

保留原API16源码作为计时改动的对照。其与仅计时版本的少量差异不当作优化收益。未采集分阶段分配次数/RSS；不声称已量化内存峰值。

## 4. Evidence

typed serde直接将每个敌军/地块事实编码为拥有独立生命周期的RawValue，同只读段跨阵营复用Arc。避免第一次投影的递归复制和缓存对象树；数组与最终响应仍复制完整字节。

5000 Units、single5、1线程：公共构建14.109→1.999ms，释放4.894→0.234ms，面板0.240→0.207ms；普通调用19.189→2.547ms。存活数量、工作计数、世界状态、响应内容和字节长度一致。这把收益定位到公共数据表示，而不是减少工作负载或信息。

### Handler普通调用中位数，ms

| 场景 | 查询子集 | 线程 | R4a/API16 | 仅计时/API17 | 直接编码/API17 |
| --- | --- | ---: | ---: | ---: | ---: |
| terrain-local | single5 | 1 | 0.105 | 0.099 | 0.086 |
| terrain-local | single5 | 2 | 0.115 | 0.077 | 0.069 |
| terrain-local | single5 | 4 | 0.097 | 0.092 | 0.084 |
| terrain-disabled | single5 | 1 | 12.973 | 11.854 | 1.477 |
| terrain-disabled | single5 | 2 | 13.572 | 13.208 | 1.417 |
| terrain-disabled | single5 | 4 | 12.088 | 12.121 | 1.403 |
| units-5000 | single5 | 1 | 20.412 | 19.189 | 2.547 |
| units-5000 | single100 | 1 | 24.499 | 23.339 | 6.218 |
| units-5000 | repeat100 | 1 | 26.448 | 25.865 | 8.988 |
| units-5000 | disjoint5 | 1 | 25.035 | 24.710 | 6.442 |
| units-5000 | single5 | 2 | 20.639 | 20.085 | 3.040 |
| units-5000 | single100 | 2 | 23.075 | 24.955 | 4.588 |
| units-5000 | repeat100 | 2 | 35.081 | 24.783 | 6.944 |
| units-5000 | disjoint5 | 2 | 23.461 | 21.711 | 5.421 |
| units-5000 | single5 | 4 | 20.683 | 19.262 | 2.621 |
| units-5000 | single100 | 4 | 22.624 | 22.307 | 3.852 |
| units-5000 | repeat100 | 4 | 24.300 | 23.974 | 6.120 |
| units-5000 | disjoint5 | 4 | 23.076 | 26.174 | 5.627 |

### 可信动作入口及handler对照，ms

相同注册数据，MP6、1线程；5000Units场景查询100Units。正常调用不启用计时，初始化/reset不计入样本。

| 场景 | 入口/请求数 | 修改前 | 修改后 |
| --- | --- | ---: | ---: |
| terrain-local | handler/1 | 0.167 | 0.149 |
| terrain-local | public/1 | 0.181 | 0.158 |
| terrain-local | single/1 | 0.165 | 0.153 |
| terrain-local | handler/8 | 0.183 | 0.191 |
| terrain-local | public/8 | 0.193 | 0.183 |
| terrain-disabled | handler/1 | 12.604 | 1.472 |
| terrain-disabled | public/1 | 12.460 | 1.488 |
| terrain-disabled | single/1 | 13.516 | 1.509 |
| terrain-disabled | handler/8 | 14.004 | 2.298 |
| terrain-disabled | public/8 | 14.189 | 2.394 |
| units-5000 | handler/1 | 23.929 | 6.591 |
| units-5000 | public/1 | 23.899 | 6.439 |
| units-5000 | single/1 | 24.713 | 6.362 |
| units-5000 | handler/8 | 26.797 | 9.513 |
| units-5000 | public/8 | 26.511 | 8.742 |

## 5. Root cause

公共事实的中间表示带来了可避免的分配、复制、析构工作。代码结构与相同响应下的分段下降共同支持这一结论。必需的规则计算和输出字节没有减少。

大批次中最终输出开始占更大比例，100Unit查询的面板计算仍有明显成本，此时并行更有效。小子集在2/4线程下仍可能因调度及背景波动变慢，不能用本微测决定全局默认线程。

## 6. Regression

2171项完整Python回归、89项针对性、4项Rust测试、fmt/Clippy通过；旧6场景510节点重放通过。84组完整响应/状态/字节长度及原工作计数相同，worker利用数允许随调度变化。新增三阵营共享以及reset至变更地形/兵力的契约测试。

新增测试曾误计外部ID=0地块；完整响应当时已与Python一致，修正测试预期后全部通过，运行代码不变。没有确认新增玩法GAP；G008/G009、R001/R002仍开放。

## 7. Limitations / next

没有世界move/attack、展示和队列计时；不是P99或30Hz验收，也不包含Hub或真实LLM。5000Units场景不等于5000Agents。源码版本按顺序串行测量，没有随机化，因此保留全部样本和负对照，不作统计显著性声明。

下一步用当前Rust内核重新接入完整合成闭环诊断，保持约30秒思考、期间不轮询，包含世界/展示/排队及存活负载guard。Python宿主、SDK、UI继续保留；按组合负载结果处理剩余内核热点。
