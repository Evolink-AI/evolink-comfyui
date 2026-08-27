# EvoLink MiniMax Hailuo 2.3 (Official)

EvoLink 官方节点：MiniMax 海螺 Hailuo 2.3 文生视频、图生视频（接 first_frame 即图生），动作表现力强，6/10 秒，最高 1080p。MiniMax Hailuo 2.3 text/image-to-video.

## 参数
- `quality`：分辨率
- `duration`：视频时长（秒）
- `prompt_optimizer`：自动优化 prompt；要精确控制时关闭
- `fast_pretreatment`：快速预处理，缩短优化耗时

## 图像输入
- `first_frame`：首帧图（可选，接上即图生视频）

## 输出
`video`（结果，已下载落地）、`task_id`、`status_info`（摘要）、`result_urls`（原始链接每行一个，24h 过期）、`response_json`（任务接口完整 JSON，供下游解析）。

费用与任务详情：https://evolink.ai/zh/dashboard/logs ；接口文档：https://evolink.ai/docs
