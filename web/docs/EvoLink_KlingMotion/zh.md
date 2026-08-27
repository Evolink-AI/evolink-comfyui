# EvoLink Kling V3 Motion Control (Official)

EvoLink 官方节点：快手可灵 Kling V3 运动控制——从参考视频提取动作轨迹，套用到参考图中的人物/物体上生成新视频。视频 URL 可接上游节点的 result_urls 输出。Kuaishou Kling V3 motion control (reference image + motion video).

## 参数
- `video_urls`：参考动作视频 URL（必填），可接上游节点的 result_urls 输出
- `character_orientation`：人物朝向跟随：image=跟参考图（≤10 秒）/ video=跟参考视频（≤30 秒）
- `quality`：分辨率

## 图像输入
- `reference_image1`：参考图（必接）：要被驱动的人物/物体（必接）

## 输出
`video`（结果，已下载落地）、`task_id`、`status_info`（摘要）、`result_urls`（原始链接每行一个，24h 过期）、`response_json`（任务接口完整 JSON，供下游解析）。

费用与任务详情：https://evolink.ai/zh/dashboard/logs ；接口文档：https://evolink.ai/docs
