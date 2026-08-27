# EvoLink Z-Image Turbo (Official)

EvoLink 官方节点：阿里通义 Z-Image Turbo 轻量极速文生图——出图快、价格低，适合批量与实时场景。Alibaba Z-Image Turbo fast budget text-to-image.

## 参数
- `size`：画幅比例；auto=不指定，用模型默认
- `seed`：0=随机；固定可复现结果
- `nsfw_check`：开启 NSFW 内容检测

## 输出
`image`（结果，已下载落地）、`task_id`、`status_info`（摘要）、`result_urls`（原始链接每行一个，24h 过期）、`response_json`（任务接口完整 JSON，供下游解析）。

费用与任务详情：https://evolink.ai/zh/dashboard/logs ；接口文档：https://evolink.ai/docs
