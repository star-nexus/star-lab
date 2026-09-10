# Decision — 完成24Hz随机闭环实测，保持生产时钟实现

**Status:** experiment complete; inspect measured limits before choosing a deployment configuration.

## Decision

采用用户指定的固定模拟步长与外部Agent墙钟分离。保留生产已有capped时钟，只扩展Lab工具，不做并行架构。
观测→即时动作→墙钟思考后下一轮；不在思考期间轮询。

## Alternatives / tradeoffs

interleaved高接触密度负结果保留。canonical的12ms与18ms服务预算对照说明世界帧余量与请求尾延迟存在取舍。
没有调整概率、减少Units/Agents、去掉JSON或删除慢帧来伪造成功。

## Revisit

如需要更密集混战、提高动作频率、减少思考时间或接入Protocol/Hub，必须重测。GPU/多进程仍暂停。
若希望生产默认FPS改为24，应单独明确默认配置变更；本轮启动参数只对实验进程生效。

## Provenance

README、manifest、analysis与results；source9063863未更改，Lab当前提交保存工具及证据。历史门槛和历史实验不改标。
