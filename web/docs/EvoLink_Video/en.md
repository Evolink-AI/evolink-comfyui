# EvoLink Video (All Models)

Dynamic video node: call every EvoLink video model (Sora 2, Veo 3.1, Kling, Seedance incl. reference/edit/extend) from one node.

- duration=0 / quality=auto / empty aspect_ratio use the model defaults
- Pass model-specific params (video_urls, sound, seed, generation_type, …) via **extra_params** as JSON
- For Kling image-to-video use the dedicated Kling node (it takes image_start instead of image_urls)
