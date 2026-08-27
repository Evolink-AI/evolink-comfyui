"""EvoLink 官方 ComfyUI 节点包。

一个模型变体一个节点（fal 风格，文生/图生分开）：
图像：GPT Image 2、Nano Banana 2/Pro/Lite、Seedream 5.0 Pro/Lite/4.5/4.0、Grok Imagine；
视频：Sora 2/Pro、Veo 3.1（T2V/首尾帧/参考图）、Kling V3/Turbo/O3（T2V/I2V）、
Seedance 2.5/2.0/Fast/Mini（T2V/I2V）、Wan 3.0（T2V/首尾帧/参考）；
以及通用动态节点（全模型，含 beta 渠道）、余额查询。本地参考图自动走
EvoLink 官方上传通道，不依赖任何第三方图床。
文档：https://evolink.ai/docs/cn/integration-guide/comfyui
"""

from .nodes.credits import EvoLinkCredits
from .nodes.image_gen import EvoLinkGPTImage2, EvoLinkUploadImage

NODE_CLASS_MAPPINGS = {
    "EvoLink_GPTImage2": EvoLinkGPTImage2,
    "EvoLink_UploadImage": EvoLinkUploadImage,
    "EvoLink_Credits": EvoLinkCredits,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EvoLink_GPTImage2": "EvoLink GPT Image 2 (Official)",
    "EvoLink_UploadImage": "EvoLink Upload Image (Official)",
    "EvoLink_Credits": "EvoLink Credits (余额查询)",
}

# 注册表驱动的模型节点（Nano Banana / Seedream / Sora 2 / Veo 3.1 / Kling /
# Seedance / 通用 Image & Video）。注册表异常时不拖垮上面的基础节点。
try:
    from .nodes.factory import build_nodes

    _factory_classes, _factory_names = build_nodes()
    NODE_CLASS_MAPPINGS.update(_factory_classes)
    NODE_DISPLAY_NAME_MAPPINGS.update(_factory_names)
except Exception as e:  # noqa: BLE001
    print(f"[EvoLink] 警告：模型注册表加载失败，仅基础节点可用。原因：{e}")

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
