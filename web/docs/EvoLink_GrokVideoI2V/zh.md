# EvoLink Grok Imagine Image-to-Video (Official)

EvoLink 官方节点：xAI Grok Imagine 图生视频（首图必接，最多 7 张参考），6~30 秒，normal/fun/spicy 三种风格。xAI Grok Imagine image-to-video.

## 参数
- `duration`：视频时长（秒），6~30 任意整数，按时长计费
- `mode`：生成风格：normal 常规 / fun 趣味 / spicy 大胆
- `aspect_ratio`：画幅比例
- `quality`：分辨率

## 图像输入
- `image1`：首帧/参考图（必接，最多 7 张）（必接）
- `image2`：参考图 2（可选）
- `image3`：参考图 3（可选）

## 输出
`video`（结果，已下载落地）、`task_id`、`status_info`（摘要）、`result_urls`（原始链接每行一个，24h 过期）、`response_json`（任务接口完整 JSON，供下游解析）。

费用与任务详情：https://evolink.ai/zh/dashboard/logs ；接口文档：https://evolink.ai/docs
