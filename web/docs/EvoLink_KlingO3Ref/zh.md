# EvoLink Kling O3 Reference-to-Video (Official)

EvoLink 官方节点：快手可灵 Kling O3 参考视频生视频——提取参考视频的风格与运动特征生成新视频，可搭配参考图。视频 URL 可接上游节点的 result_urls 输出。Kuaishou Kling O3 reference-to-video.

## 参数
- `video_url`：参考视频 URL（必填），可接上游节点的 result_urls 输出
- `duration`：视频时长（秒），3~10 任意整数
- `aspect_ratio`：画幅比例
- `quality`：分辨率
- `keep_original_sound`：保留原视频声音

## 图像输入
- `reference_image1`：参考图 1（可选）
- `reference_image2`：参考图 2（可选）

## 输出
`video`（结果，已下载落地）、`task_id`、`status_info`（摘要）、`result_urls`（原始链接每行一个，24h 过期）、`response_json`（任务接口完整 JSON，供下游解析）。

费用与任务详情：https://evolink.ai/zh/dashboard/logs ；接口文档：https://evolink.ai/docs
