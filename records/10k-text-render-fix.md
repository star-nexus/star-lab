# 坐标/伤害/CRIT 缓存修复

2026-09-10，用户授权解决文字卡顿并尽量降低复杂度。

## 起点与边界

生产main906386312d70d77af25e4b4da883f6dd5b0fe5ef；Lab067b35e65281f598be342636e0a5c4d2a80c046c。
新分支`codex/cached-combat-coordinate-text`，worktree `runs/star-text-cache-dev`。
只调整文字呈现，维持博弈规则、时钟、控制、透明度/坐标语义；不做并行、Protocol/Hub或移动弱化调整。
合并前annotated tag钉死开发节点，生产仅squash merge。

## 实现与复杂度

- 坐标：culler发布不可变可见集；固定视图O(1)比较和一次overlay提交，不逐格遍历/字符串渲染。改变视图O(Vvisible)，同字体字号重用重叠标签，仅新标签生成2个颜色图并合成4方向描边。仅保留一个视图、一种字号及该视图标签；像素提交成本仍与视口面积有关。
- 飘字：O(Aactive)生命周期与呈现遍历；首次可见时渲染一次文字，各实体独有surface、按帧更新alpha和位置；屏幕外不入绘制队列。缓存只保留仍存活组件，文字/颜色/字体/组件替换失效。没有新ECS系统/新模块/定时缓存维护。
- 像素oracle发现直接RGBA多级叠加会改变抗锯齿边缘，改用预乘alpha；本机pygame2.6.1对SDL_ttf带padding的surface直接premul会错位，因此先copy成紧凑行。生产像素契约覆盖此路径，不绕过测试。官方API语义：[pygame.Surface](https://www.pygame.org/docs/ref/surface.html#pygame.Surface.premul_alpha)。

## 阶段 A 验证

912项完整pytest通过，94项结构性能契约通过；13个新用例覆盖坐标稳态无逐格工作、平移/缩放/resize/方向/世界切换、缓存有界、关闭/低缩放、描边像素、各CRIT独立alpha、变更/替换/删除、部分可见边缘以及伤害像素等价。
此前诊断的replay预热不足，本轮增加每condition120帧坐标OFF的地图稳定期，记录overscan完成guard。之后10帧文字预热+100测量帧，2轮seed42随机条件顺序；另保留首次开启的cold_activation帧，不混入warm P99也不删除。
正式选择8项：zoom1/0.5坐标OFF/ON、zoom0.5连续每帧平移1px、1000可见飘字、1000屏幕外飘字、保留1000组件但关闭绘制。5000U/1000已注册Agent，delta0且不pump，保持独立渲染归因。
固定base与candidate工具SHA后串行测量；修复版再运行canonical5000U/1000A自然闭环30s预热+60s（24Hz、30±5秒思考、18ms预算）。Chrome保留，无删慢帧、不并发性能任务。

## 当前状态

实现与回归完成，性能工具smoke进行中；下一步固定源码/工具提交进行上述对照，然后归档与tag+squash集成。
