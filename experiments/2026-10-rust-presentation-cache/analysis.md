# E6 当前基线归因与缓存契约

状态：第一阶段完成；以下均为带探针的诊断成本，不是无诊断性能基线或收益。

进度：`身份/契约 █ | 原型/单测 █ | 基线归因 █ | 完整等价 ░ | 配对/条件live ░ | 归档 ░`。

## 成本表

源码5f567d36e89450da203b20fed212fd6b21fde1e1；原ordinary apply AST与4657dd4相同，native扩展838c693…保持。Cocoa2480×1239，固定static展示脚本，完整40994请求/9880tick，响应/完整delta流与最终权威状态匹配规范轨迹。

| 组件 | 复制µs/tick | 转换µs/tick | 构造µs/tick | 次数 |
|---|---:|---:|---:|---:|
| HexPosition | 114.96 | 42.42 | 45.91 | 1239642 |
| Unit | 191.45 | 99.25 | 61.86 | 1239642 |
| UnitCount | 107.03 | 40.24 | 44.82 | 1239642 |
| MovementAnimation | 606.19 | 74.01 | 75.37 | 1239477 |
| MovementPoints | 158.23 | 39.76 | 60.19 | 1239642 |
| ActionPoints | 105.71 | 40.41 | 44.41 | 1239642 |
| UnitStatus | 157.73 | 47.37 | 54.90 | 1239642 |
| SkillPoints | 0.00 | 0.00 | 0.00 | 0 |
| ConstructionPoints | 0.00 | 0.00 | 0.00 | 0 |

组件表是_component内部三个相邻区间；ECS write包含invalidate，显示System在display区间之内，不能相加重算整帧。

当前诊断阶段均值：encode_ns=0.234ms, decode_ns=0.524ms, apply_ns=3.971ms, display_ns=6.038ms, submit_ns=1.963ms, platform_ns=1.366ms, chain_ns=13.862ms, total_ns=17.668ms, request_ns=3.309ms, step_ns=0.262ms。

8761673次缓存失效调用、36452次eviction；必须区分大量调用与实际移除。Unit组件引用版本随替换变化；原地写入应保持版本且让持有者看到当前字段。没有将旧E2约2.7ms与本次带探针约3.97ms的差异解释为回退。

## 依赖与安全边界

| 消费者/机制 | 保存什么 | 正确失效条件 |
|---|---|---|
| ECS query/ordered query | 组件成员与原序ID | 新增/移除/删除；字段写入不改成员 |
| Animation引用列表 | Position/Movement对象引用 | 引用替换及成员变化；活字段直接可见 |
| UI阵营列表 | Unit引用＋逐帧faction序列 | 引用/成员改变重建；faction序列变化重算计数 |
| 空间索引 | 坐标/阵营/存活事实 | 每个完整Unit row后继续upsert；删除先移除 |
| 派生观测/计算结果 | 字段计算值 | World revision或专用revision；不能用引用版本代替 |

普通World.add_component仍为替换语义。本轮私有路径仅复用9类规范Unit对象；缺字段/未知字段/扩展对象/非规范容器走原构造替换。每组件转换完整成功后一次发布，保留原成功前缀和容器所有权。

## 方法限制

规范trace不包含镜头/选择/像素。static脚本来自本轮准备的显示World；exercise额外脚本固定每300tick镜头缩放/移动、阵营和选择。新的脚本与像素校验链单独归档，不冒充原R4e窗口输入。

固定轨迹工作包含请求、step、delta编码、client decode、apply、全部挂载displaySystems、clear/RMS提交；dummy无平台flip，Cocoa诊断单列flip。IO/hash/验证/初始化/等待不进入性能区间。它不是完整生产窗口循环，实际容量仍由新live验收。

首次导入和字体/纹理准备在计时前，不把冷启动摊进稳态收益。正式9880tick包含原轨迹预热且保留所有慢尾。
