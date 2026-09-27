# Evidence

**Observation**：旧实现只把Unicode数字/分隔符规范化后交给BigInt，没有CPython的十进制字符串位数限制。默认4300限制下，4301位有效语法仍被Rust累计。首次report保存文本、第二次report才发生转换；因此观察一次响应不能证明统计正确。

**Hypothesis and test**：通过真实注册＋两次report_llm_stats比较完整响应及世界，而不是直接调用辅助parser。三种长度4299/4300/4301×ASCII/Unicode/分隔符/负号，共12边界案例；另8个空值/错误语法/普通数值/容器/全零/长小数负对照。实测4组状态不同，响应全部相同；原始反例保留。

**Root cause and fix**：Python累计函数捕获int()的ValueError并用0，而BigInt直接接受超长字符串。可信适配器在统计请求接纳时传解释器设置，Rust按规范化后的十进制数字计数；保留既有fallback，不修改Python规则。仅report带新元数据，正常move/attack/观测热路径不采样此设置。API18阻止混用旧扩展；低层原始信封省略字段仍为默认4300。

**Evidence**：after20组完整响应/状态全部等于同运行Python；24新契约覆盖全部11个累计字段、非默认限制、批次/reset、运行期间变化和浮点路径。2195完整回归、177针对性、4Rust/fmt/Clippy、15Lab与旧6场景510节点均通过。录制器保存每个请求的转换环境，CLI重放在执行请求前恢复；新增640位限制轨迹从默认子进程启动、4线程重放通过。

**Confounders/limits**：跨运行初始GameTime三个创建墙钟不同，comparison辅助核对仅对这三处归零，raw不删值；同运行Python/Rust的权威状态比较没有任何排除。没有证明历史LLM日志曾触发该输入，也没有证明排名或战斗数值变化。此修复改变的是Rust错误累计行为以匹配oracle，不能标为原规则重平衡。R001其他边界、R002写入消费者、G008/G009继续开放；未测新性能，不继承成API18容量验收。
