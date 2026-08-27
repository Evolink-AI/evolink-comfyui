# EvoLink Wan 3.0 (Official)

Alibaba Wan 3.0 / Prime text-to-video, first/last-frame image-to-video and multimodal reference-to-video.

- **Model choice sets the mode**: text-to-video / image-to-video (first_frame + optional last_frame) / reference-video (reference image slots; cite materials in the prompt as "Image 1", "Video 1")
- **duration**: seconds, or **-1 smart duration** (pre-authorized at the 30 s cap, settled against actual output)
- **quality**: 480p is the billing baseline, 720p ≈ 2x, 1080p ≈ 4x; Standard and Prime share parameters, only billing multipliers differ
- **seed** for reproducibility; audio on/off costs the same
- Pass reference video/audio/file params (video_urls, audio_urls, file_url) via **extra_params** as JSON
