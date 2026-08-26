"""EvoLink 官方 ComfyUI 节点包。

图像：GPT Image 2、Nano Banana 2/Pro、Seedream 5.0 文生图/图生图；
视频：Sora 2、Veo 3.1、Kling 3.0、Seedance 2.5 文生视频/图生视频；
以及通用动态节点（全模型）、余额查询。本地参考图自动走 EvoLink 官方
上传通道，不依赖任何第三方图床。
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
