"""EvoLink 官方 ComfyUI 节点包。

文生图 / 图生图（gpt-image-2），本地参考图自动走 EvoLink 官方上传通道，
不依赖任何第三方图床。文档：https://evolink.ai/docs/cn/integration-guide/comfyui
"""

from .nodes.image_gen import EvoLinkGPTImage2, EvoLinkUploadImage

NODE_CLASS_MAPPINGS = {
    "EvoLink_GPTImage2": EvoLinkGPTImage2,
    "EvoLink_UploadImage": EvoLinkUploadImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EvoLink_GPTImage2": "EvoLink GPT Image 2 (Official)",
    "EvoLink_UploadImage": "EvoLink Upload Image (Official)",
}

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
