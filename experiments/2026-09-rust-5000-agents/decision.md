# 决策

交付正式的get_faction_state_json，保留原字典API；Python保留host/SDK/策略/UI，Rust继续持有权威世界及观测计算。不是新增规则，也不扩大线程数。

默认后端Python/内核1线程不变，Lab旧边界保持默认，--native-wire显式开启直传。8/12/14ms是诊断变量，不发布为已验证的5000-Agent推荐预算；旧18ms负结果保留。未测得满足5000-Agent全部门槛的最小预算，因此不杜撰默认值或安全余量。

完成接口与重复转换优化，不关闭整个5000-Agent实时性问题。下一步优先验证同只读段的公共事实复用及有界批次；不优先重写Python用户层，也不将共享可变ECS系统贸然并行。功能、平台安装和默认切换仍按原迁移计划分开验收。

本轮不修改performance-frontier中的已通过容量，不merge、不push；保留生产原49处删除。测量完整checkout保持实现SHA，旧checkout/wheel/负结果保持可复现。最终阶段tag仅代表本接口及验证范围。
