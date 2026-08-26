# EvoLink Video (All Models)

通用视频节点：一个节点调用 EvoLink 全部视频模型（Sora 2、Veo 3.1、Kling、Seedance 含 reference/edit/extend）。

- duration=0 用模型默认；quality=auto 用模型默认；aspect_ratio 留空用模型默认
- 模型专属参数（video_urls、sound、seed、generation_type 等）用 **extra_params** 以 JSON 传入，如 `{"video_urls": ["https://..."], "generate_audio": false}`
- Kling 图生视频首帧参数不同（image_start），请用专属 Kling 节点
- 各模型参数见 evolink.ai/docs
