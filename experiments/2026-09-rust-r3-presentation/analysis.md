# Analysis — R3c presentation

## Observation

R3b可信attack在display=dummy返回2012，明确缺失展示handoff。该入口在R3c成功，
并产生攻击、伤害和效果的3条展示行。1504回归和144配置5184节点的差分/精确重放通过。
两组真实Cocoa检查各480帧，均保持Rust状态不受渲染影响。

## Hypotheses and instrumentation

H1：只需把伤害结果交给Python重建动画。检查旧AnimationSystem发现，弹道/伤害/CRIT/效果
分配和释放外部实体ID；它们会影响后续捕获任务等ID。只迁结果会破坏精确重放。
H2：把权威生命周期和ID留Rust，视觉数学留Python。逐动作/逐tick记录完整响应、权威状态、
事件与展示增量，覆盖近/远程、死/活、暴击/普通、3种display、2种mode、3个线程设置以及中途reset。

## Evidence and causal chain

全部权威数据与规范化Python一致；独立重放还校验完整presentation payload。
Projectile_created标记和新弹道当帧接收整个dt均须保留，否则小dt跨射击阶段时实体流不同。
资源恢复、rest、回合重置、领地占领/捕获、Fog重叠和死亡的变更队列由专门契约检查：
每1或7次更新读取展示数据都能重建相同状态，空闲帧无全量Unit/territory输出。

Python消费者将外部ID导入展示World，更新索引和缓存；没有native句柄。
实际绘制前后对Rust export_state断言相等，保留24张PNG和逐帧视觉实体计数。
代表性截图确认坐标和飘字可用，选中覆盖层的遮挡属于既有呈现顺序，另有无覆盖层视图用于检查。

## Decision and limits

采用H2。没有改变碰撞、MP弱化、CD或阵营共享规则。没有用上一帧/TTL观测。
这里的O(changed/active)指变化队列维护和消费者访问范围；没有测量总窗口P99或调度收益。
渲染器仍可在选中Unit上计算Python展示用范围，R4前不宣称消除了所有Python热路径。
完整HUD、VLM、输入/场景、BOT和结算未接；窗口相机输入由脚本注入，非真人按键验收。
1/2/4线程仍串行，3 Units不能推导5000/1000容量。跨平台安装和默认切换也未验收。

原始证据见manifest、compact、probe.json.xz、replay与window*/render.json。
XZ只是原JSON的无损重新压缩，内容SHA和原gzip恢复SHA均通过，不改变任何测量或gate。
