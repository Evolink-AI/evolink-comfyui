# EvoLink Kling O3 Video Edit (Official)

EvoLink 官方节点：快手可灵 Kling O3 视频编辑——用文字指令/参考图修改原视频，输出时长与画幅跟随原片。视频 URL 可接上游节点的 result_urls 输出。Kuaishou Kling O3 video editing.

## 参数
- `video_url`：要编辑的视频 URL（必填），可接上游节点的 result_urls 输出
- `quality`：分辨率
- `keep_original_sound`：保留原视频声音

## 图像输入
- `reference_image1`：参考图 1（可选）
- `reference_image2`：参考图 2（可选）

## 输出
`video`（结果，已下载落地）、`task_id`、`status_info`（摘要）、`result_urls`（原始链接每行一个，24h 过期）、`response_json`（任务接口完整 JSON，供下游解析）。

费用与任务详情：https://evolink.ai/zh/dashboard/logs ；接口文档：https://evolink.ai/docs
