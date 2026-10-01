# E6：展示数据与 ECS 缓存优化研究

状态：执行中；研究模式默认关闭，无新性能/容量结论。

起点4657dd4；目标5000 Units＋1000 Agents，5000 Agents暂缓。
普通apply函数体保持；三个私有模式baseline/reuse_constructed/reuse_typed。

进度：`身份/契约 █ | 原型/单测 █ | 归因/完整等价 ░ | 配对收益 ░ | 条件live/归档 ░`。

固定输入沿用R4e ZIP，9880 tick和40994请求；当前ordinary Rust重生成delta。
新增static/exercise展示脚本是本轮输入，不改写原trace。诊断与正式计时分开。

原49项删除、冻结目录和E2/E3/E4/E5标签保留。不push/merge。
