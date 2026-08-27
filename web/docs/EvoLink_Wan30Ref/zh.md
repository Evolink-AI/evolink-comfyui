# EvoLink Wan 3.0 (Official)

阿里通义万相 Wan 3.0 / Prime 文生视频、首尾帧图生视频、多模态参考生视频。

- **模型选择决定模式**：text-to-video / image-to-video（first_frame + 可选 last_frame）/ reference-video（参考图槽位 + prompt 里用「图1」「视频1」引用素材）
- **duration**：秒数或 **-1 智能时长**（按 30 秒上限预扣、按实际输出结算退差额）
- **quality**：480p=计费基准最便宜，720p 约 2 倍，1080p 约 4 倍；Standard 与 Prime 参数相同，仅计费倍率不同
- **seed**：固定可复现结果；音轨开关同价
- reference 模式的视频/音频/文件参考（video_urls、audio_urls、file_url）用 **extra_params** 以 JSON 传入
