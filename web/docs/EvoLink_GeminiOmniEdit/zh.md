# EvoLink Gemini Omni Flash Video Edit (Official)

EvoLink 官方节点：Google Gemini Omni Flash 视频编辑——对输入视频改主体/风格/局部。视频 URL 可直接接上游生成节点的 result_urls 输出。Google Gemini Omni Flash video editing.

## 参数
- `video_url`：要编辑的视频 URL（必填），可接上游节点的 result_urls 输出

## 输出
`video`（结果，已下载落地）、`task_id`、`status_info`（摘要）、`result_urls`（原始链接每行一个，24h 过期）、`response_json`（任务接口完整 JSON，供下游解析）。

费用与任务详情：https://evolink.ai/zh/dashboard/logs ；接口文档：https://evolink.ai/docs
