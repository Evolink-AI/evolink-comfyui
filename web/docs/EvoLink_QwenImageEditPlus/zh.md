# EvoLink Qwen Image Edit Plus (Official)

EvoLink 官方节点：阿里通义千问 Qwen Image Edit Plus 图片编辑（必接输入图），改文字/换风格/局部修改，一次最多 6 张。Alibaba Qwen Image Edit Plus image editing.

## 参数
- `size`：留空=跟随输入图；或比例/像素
- `n`：一次生成几张（1~6）
- `negative_prompt`：不希望出现的内容
- `prompt_extend`：提示词智能扩写
- `watermark`：是否加水印
- `seed`：0=随机；固定可复现结果

## 图像输入
- `image1`：要编辑的图片（必接）（必接）
- `image2`：参考图 2（可选）
- `image3`：参考图 3（可选）

## 输出
`image`（结果，已下载落地）、`task_id`、`status_info`（摘要）、`result_urls`（原始链接每行一个，24h 过期）、`response_json`（任务接口完整 JSON，供下游解析）。

费用与任务详情：https://evolink.ai/zh/dashboard/logs ；接口文档：https://evolink.ai/docs
