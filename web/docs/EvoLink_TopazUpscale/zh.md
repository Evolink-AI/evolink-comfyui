# EvoLink Topaz Video Upscale (Official)

EvoLink 官方节点：Topaz 视频超分/画质增强——1x 仅增强、2x/4x 放大分辨率，接上游生成节点的 result_urls 输出即可做后处理链。Topaz AI video upscaling & enhancement.

## 参数
- `video_urls`：要超分的视频 URL（必填），可接上游节点的 result_urls 输出
- `upscale_factor`：放大倍数：1=仅增强不放大 / 2=2 倍 / 4=4 倍（影响计费）

## 输出
`video`（结果，已下载落地）、`task_id`、`status_info`（摘要）、`result_urls`（原始链接每行一个，24h 过期）、`response_json`（任务接口完整 JSON，供下游解析）。

费用与任务详情：https://evolink.ai/zh/dashboard/logs ；接口文档：https://evolink.ai/docs
