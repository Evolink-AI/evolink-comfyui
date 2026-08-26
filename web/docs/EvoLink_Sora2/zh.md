# EvoLink Sora 2 (Official)

OpenAI Sora 2 / Sora 2 Pro 文生视频、图生视频。输出 VIDEO 可直连原生「保存视频」节点。

- **duration**：4 / 8 / 12 秒，按时长计费；**aspect_ratio**：16:9 横屏 / 9:16 竖屏
- **quality**：仅 Pro 可选 720p/1080p（1080p 约 1.67 倍价）
- **图生视频**：接 image 口；sora-2-preview 要求参考图像素与画幅完全一致，节点会自动缩放；不支持真人照片
- Sora 内容审核较严，任务失败不扣费
- 生成通常需要几分钟，期间可随时点「取消」（服务端任务不会停止，完成仍会扣费，可到 dashboard/logs 查看）
