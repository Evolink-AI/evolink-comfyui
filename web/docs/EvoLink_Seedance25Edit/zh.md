# EvoLink Seedance 2.5 Video Edit (Official)

EvoLink 官方节点：字节豆包 Seedance 2.5 视频编辑——换主体/增删物体/重绘风格，输出时长跟随原片。视频 URL 可直接接上游生成节点的 result_urls 输出。ByteDance Seedance 2.5 video editing.

## 参数
- `video_urls`：要编辑的视频 URL（必填，每行一个，最多 10 条，4~30 秒），可接上游节点的 result_urls 输出
- `quality`：分辨率；480p 为低价档
- `generate_audio`：生成同步音频（不额外收费）
- `audio_urls`：参考音频 URL，每行一个（最多 10 条，2~30 秒）

## 图像输入
- `image1`：参考图 1（可选，最多 30 张）
- `image2`：参考图 2（可选）

## 输出
`video`（结果，已下载落地）、`task_id`、`status_info`（摘要）、`result_urls`（原始链接每行一个，24h 过期）、`response_json`（任务接口完整 JSON，供下游解析）。

费用与任务详情：https://evolink.ai/zh/dashboard/logs ；接口文档：https://evolink.ai/docs
