# EvoLink Grok Imagine Video 1.5 (Official)

EvoLink 官方节点：xAI Grok Imagine Video 1.5——一个模型三种玩法：不接图=文生视频，接 1 张=首帧图生视频，接 2~7 张=参考图生视频。1~15 秒，最高 1080p。xAI Grok Imagine Video 1.5 text/image/reference-to-video.

## 参数
- `duration`：视频时长（秒），1~15 任意整数，按时长计费
- `quality`：分辨率；480p 最便宜
- `aspect_ratio`：画幅；接图时由图决定

## 图像输入
- `image1`：不接=文生视频；1 张=首帧；2 张以上=参考图（最多 7 张）
- `image2`：参考图 2（可选）
- `image3`：参考图 3（可选）

## 输出
`video`（结果，已下载落地）、`task_id`、`status_info`（摘要）、`result_urls`（原始链接每行一个，24h 过期）、`response_json`（任务接口完整 JSON，供下游解析）。

费用与任务详情：https://evolink.ai/zh/dashboard/logs ；接口文档：https://evolink.ai/docs
