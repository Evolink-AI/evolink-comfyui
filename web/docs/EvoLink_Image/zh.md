# EvoLink Image (All Models)

通用图像节点：一个节点调用 EvoLink 全部图像模型（GPT Image 2、Nano Banana 2/Pro、Seedream 5.0 等）。

- 常用参数只保留 size；模型专属参数（quality、n、mask_url 等）用 **extra_params** 以 JSON 传入，如 `{"quality": "2K", "n": 2}`
- 各模型参数见 evolink.ai/docs 接口文档
- 新模型上线后无需更新插件即可尝试（extra_params 直通请求体）
