# Decision — R3c

**accepted checkpoint，2026-09-14。** 生产5bda51db6cd68455aa5724a6ef0eca1e66f89dda，
annotated tag rust-kernel-r3c-2026-09-14。

采用Rust权威战斗生命周期/稳定ID与变化队列，Python派生World和既有渲染器。
依据是完整兼容性和渲染隔离验证，并非帧率。短生命周期对象按活动数推进，单位/地块/Fog按变化发送；
首次导入和reset构建完整基线。GameTime等小状态每次返回当前值。

拒绝让Python再次执行AnimationSystem的模拟部分：会重复推进位置、计时和实体分配。
拒绝每帧export_state全量镜像和视觉数据进入Agent协议：前者扩大同步成本，后者绕过权限与Fog投影。
不借迁移调整MP、重叠、技能等既有机制。保留字体/Surface、坐标和伤害文字缓存。

下一步R3d：通过明确命令接入GameScene/输入/后端选择、完整HUD与VLM，再补BOT/结算/场景生命周期。
其后R4才引入并行任务和做成本拆分；R5做5000/1000/30Hz长测、平台wheel和默认切换。
本次没有确定线程默认值或新增Frontier。main未合并，Python仍默认。

新增视觉种类、场景重置/地图变化、UI输入或运行时生成单位时，应补相应派生数据/失效契约；
并行/多消费者或缓冲观测改变时，应复查epoch、读写顺序与临时ID分配。

复现与全部证据入口见README.md、manifest.yaml和results/compact.json。
