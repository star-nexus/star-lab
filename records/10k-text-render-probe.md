# 飘字 / 坐标 P99 诊断执行记录

2026-09-10。用户要求分析伤害数字、CRIT 和按0打开坐标是否显著影响P99；未要求修改生产实现。

生产906386312d70d77af25e4b4da883f6dd5b0fe5ef，Lab起点3e136989e00c0c8a7a63f385a528bd71dce1aedb。
Lab工具 `tools/p3_text_probe.py`；正式运行前提交，结果自动记录工具SHA。
Macmini M4/16GB/macOS26.5.2，Chrome保留；实验串行，不删慢帧。

## 预先定义的测量

1. 同一5000Unit世界、1000注册认领Agent，Agent不pump、测量delta=0冻结世界。真实生产window update、绘制队列与display.flip仍运行。这是渲染归因，不是实时博弈容量认证。
2. 60初始预热帧，每condition10预热+100测量帧，seed42随机condition次序、2轮重复。
3. 默认zoom0.15，0/10/100/500/1000飘字、1000飘字禁止绘制但保留动画更新、1000屏幕外飘字；25%CRIT/75%数字，固定elapsed0.5秒。坐标ON/OFF在zoom0.15/0.5/1对照。另100飘字+坐标ON（0.15，预计被阈值跳过）。
4. 原始frame_ms测量GameEngine._update（包含所有ENV systems、render flush、display.flip；不含等待和Lab外部census）。分别记录飘字准备/更新、坐标准备、flush、present。每帧记录可见格数和飘字数，单独确认固定world fingerprint和时钟。
5. 再跑1次30秒预热+60秒自然闭环5000U/1000A、24Hz、canonical、stochastic50/25/25、post-action截断正态30±5秒思考、18ms预算，给出实际飘字数与耗时。复用p3_runtime的整帧口径（包含Agent pump）；probe.frame_ms只含ENV部分，不能混用。
6. 本次只判断归因和量级，不实现修复、不更新Frontier、不声称历史44.54ms能由新运行逐帧还原。

## 代码假设

坐标逐格每帧Font(None)并font.render5次；当前默认zoom0.15低于0.3提前返回阈值。
飘字Font有缓存/预热，但文字surface每帧重建、所有活动飘字均走渲染路径、没有屏幕外提前裁剪。
各系统计时不含后续批量blit，须同时看flush及完整frame。不能把攻击业务开销全部算在飘字里。

## Smoke

短测仅用于验证工具，不作正式性能证据。首个replay因引擎退出清理world后读guard失败；修正为退出前捕获。后续replay/live smoke正常。全部位于ignored runs/，不晋升正式证据。

## 状态

工具完成；下一步固定提交，串行运行replay和live，按PROTOCOL打包原始/compact证据、复算和更新恢复入口。
