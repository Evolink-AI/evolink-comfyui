# EvoLink GPT Image 2

用 EvoLink 云端 gpt-image-2 模型生成图片，本地无需显卡。

## 文生图

填 `prompt`（支持中文）→ 把 `image` 输出连到「预览图像」或「保存图像」→ 运行。

## 图生图（3 步）

1. 添加「加载图像」节点，选择本地图片；
2. 把它的图像输出连到本节点的 `image1`；
3. `prompt` 里写修改要求 → 运行。

本地图会经 **EvoLink 官方通道**自动上传（72 小时后自动删除，不经任何第三方图床）。
最多支持 16 张参考图：`image1~image4` 口 + `image_urls` 文本框（每行一个公网 URL）可混用。

## API Key

`api_key` 首次填写后自动保存到本机配置文件，之后可留空。
**分享工作流前请清空该框**，避免泄露 Key。也可用环境变量 `EVOLINK_API_KEY`。
获取 Key：https://evolink.ai/dashboard/keys

## 费用提示

- `quality` 越高越贵，调试建议 `low`；
- 参数不变重复运行走 ComfyUI 缓存，**不重复扣费**；
- 失败/超时任务不扣费；每笔消耗可在 https://evolink.ai/zh/dashboard/logs 按 `task_id` 查询。
