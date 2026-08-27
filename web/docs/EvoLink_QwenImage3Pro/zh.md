# EvoLink Qwen Image 3.0 Pro (Official)

EvoLink 官方节点：阿里通义千问 Qwen Image 3.0 Pro 高质量文生图、图生图，中文文字渲染强，一次最多 6 张。Alibaba Qwen Image 3.0 Pro text-to-image & image-to-image.

## 参数
- `size`：auto / 比例如 1:1、16:9 / 像素如 1328x1328
- `quality`：分辨率档位
- `n`：一次生成几张（1~6）
- `negative_prompt`：不希望出现的内容
- `prompt_extend`：提示词智能扩写（短 prompt 建议开启）
- `watermark`：是否加水印
- `seed`：0=随机；固定可复现结果

## 图像输入
- `image1`：参考图 1：接「加载图像」即图生图
- `image2`：参考图 2（可选）
- `image3`：参考图 3（可选）
- `image4`：参考图 4（可选）

## 输出
`image`（结果，已下载落地）、`task_id`、`status_info`（摘要）、`result_urls`（原始链接每行一个，24h 过期）、`response_json`（任务接口完整 JSON，供下游解析）。

费用与任务详情：https://evolink.ai/zh/dashboard/logs ；接口文档：https://evolink.ai/docs
