# EvoLink Gemini Omni Flash Image-to-Video (Official)

EvoLink 官方节点：Google Gemini Omni Flash 图生视频（首帧必接），3~10 秒。Google Gemini Omni Flash image-to-video.

## 参数
- `duration`：视频时长（秒），3~10 任意整数
- `aspect_ratio`：画幅比例

## 图像输入
- `first_frame`：首帧图（必接）（必接）

## 输出
`video`（结果，已下载落地）、`task_id`、`status_info`（摘要）、`result_urls`（原始链接每行一个，24h 过期）、`response_json`（任务接口完整 JSON，供下游解析）。

费用与任务详情：https://evolink.ai/zh/dashboard/logs ；接口文档：https://evolink.ai/docs
