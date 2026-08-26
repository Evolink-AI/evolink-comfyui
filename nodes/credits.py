"""EvoLink 余额查询节点（GET /v1/credits，不扣费）。"""

import asyncio

from .client import get_credits
from .config import resolve_api_key

_API_KEY_TOOLTIP = (
    "EvoLink API Key（sk- 开头）。首次填写后自动保存到本机配置，之后可留空。"
    "获取：evolink.ai/dashboard/keys"
)


class EvoLinkCredits:
    """查询账户剩余 credits，接在工作流前可确认余额再跑昂贵任务。"""

    DESCRIPTION = (
        "EvoLink 官方节点：查询账户余额（免费接口，不消耗 credits）。"
        "remaining_credits 输出账户剩余额度；若当前 Key 设置了独立限额，"
        "info 里会一并显示 Key 的剩余额度。"
    )
    CATEGORY = "EvoLink"
    FUNCTION = "check"
    RETURN_TYPES = ("FLOAT", "STRING")
    RETURN_NAMES = ("remaining_credits", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "api_key": ("STRING", {"default": "", "tooltip": _API_KEY_TOOLTIP}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # 余额随消费变化，永远重新查询而不是走 ComfyUI 缓存
        return float("nan")

    async def check(self, api_key=""):
        key = resolve_api_key(api_key)
        user_remaining, token_remaining, token_unlimited = await asyncio.to_thread(
            get_credits, key
        )
        parts = [f"账户余额 {user_remaining:.2f} credits"]
        if not token_unlimited:
            parts.append(f"当前 Key 限额剩余 {token_remaining:.2f}")
        parts.append("充值/明细: evolink.ai/dashboard")
        info = " | ".join(parts)
        print(f"[EvoLink] {info}")
        return (user_remaining, info)
