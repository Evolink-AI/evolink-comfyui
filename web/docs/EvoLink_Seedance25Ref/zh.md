# EvoLink Seedance 2.5 Reference-to-Video (Official)

EvoLink 官方节点：字节豆包 Seedance 2.5 多模态参考生视频——图（≤30）+视频（≤10）+音频（≤10）混合参考，至少给一种素材，4~30 秒。ByteDance Seedance 2.5 reference-to-video.

## 参数
- `duration`：视频时长（秒），4~30 任意整数，按时长计费
- `quality`：分辨率；480p 为低价档
- `aspect_ratio`：画幅；adaptive 由模型自动选择
- `generate_audio`：生成同步音频（不额外收费）
- `video_urls`：参考视频 URL，每行一个（最多 10 条，2~30 秒），可接上游节点的 result_urls 输出
- `audio_urls`：参考音频 URL，每行一个（最多 10 条，2~30 秒）

## 图像输入
- `image1`：参考图 1（可选，最多 30 张）
- `image2`：参考图 2（可选）
- `image3`：参考图 3（可选）
- `image4`：参考图 4（可选）

## 输出
`video`（结果，已下载落地）、`task_id`、`status_info`（摘要）、`result_urls`（原始链接每行一个，24h 过期）、`response_json`（任务接口完整 JSON，供下游解析）。

费用与任务详情：https://evolink.ai/zh/dashboard/logs ；接口文档：https://evolink.ai/docs
