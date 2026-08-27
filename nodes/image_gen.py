"""EvoLink 官方 ComfyUI 节点。

EvoLink_GPTImage2  文生图 / 图生图（IMAGE 口直连，本地图自动走官方上传通道）
EvoLink_UploadImage 独立上传节点：本地图 -> 官方通道 -> URL 文本（进阶用）
"""

import asyncio
import json
import time

from .client import EvoLinkError, poll_task_async, submit_image_task
from .config import resolve_api_key
from .task_utils import make_progress_bar, urls_to_tensor_batch
from .upload import upload_image_tensor

MAX_REFERENCE_IMAGES = 16  # API 上限：单次请求 1~16 张参考图

_API_KEY_TOOLTIP = (
    "EvoLink API Key（sk- 开头）。首次填写后自动保存到本机配置，之后可留空。"
    "分享工作流前请清空此框，避免泄露 Key。获取：evolink.ai/dashboard/keys"
)


def _parse_url_lines(text):
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


def _dedupe(urls):
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


class EvoLinkGPTImage2:
    """gpt-image-2 云端生成。加载图像连 image1 即图生图，无参考图即文生图。"""

    DESCRIPTION = (
        "EvoLink 官方节点：gpt-image-2 文生图/图生图。"
        "把「加载图像」连到 image1 即可图生图（本地图经 EvoLink 官方通道上传，"
        "72 小时自动删除，不经任何第三方图床）。参数不变时重复运行走 ComfyUI 缓存、不重复扣费。"
    )
    CATEGORY = "EvoLink"
    FUNCTION = "generate"
    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("image", "task_id", "status_info", "result_urls", "response_json")
    OUTPUT_TOOLTIPS = (
        "生成结果（已下载落地，可直连保存节点）",
        "EvoLink 任务 ID，可到 evolink.ai/zh/dashboard/logs 查询",
        "人读状态摘要（模型/用时/消耗 credits）",
        "结果原始链接，每行一个（24 小时过期）",
        "平台 GET /v1/tasks/{id} 的完整 JSON 响应（status/usage/results 等），供下游节点解析",
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True, "default": "",
                    "tooltip": "画面描述，支持中文；图生图时写修改要求。最长 32000 字符。",
                }),
                "model": (["gpt-image-2", "gpt-image-2-beta"], {
                    "default": "gpt-image-2",
                }),
                "size": ("STRING", {
                    "default": "auto",
                    "tooltip": "auto（模型自定构图）/ 比例如 1:1、16:9 / 像素如 1024x1024",
                }),
                "resolution": (["1K", "2K", "4K"], {
                    "default": "1K",
                    "tooltip": "size 为比例或 auto 时生效",
                }),
                "quality": (["low", "medium", "high"], {
                    "default": "low",
                    "tooltip": "质量越高越贵；调试建议 low",
                }),
                "n": ("INT", {
                    "default": 1, "min": 1, "max": 10,
                    "tooltip": "一次生成几张",
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "tooltip": _API_KEY_TOOLTIP}),
                "image1": ("IMAGE", {"tooltip": "参考图 1：接「加载图像」即图生图"}),
                "image2": ("IMAGE", {"tooltip": "参考图 2（可选）"}),
                "image3": ("IMAGE", {"tooltip": "参考图 3（可选）"}),
                "image4": ("IMAGE", {"tooltip": "参考图 4（可选）"}),
                "image_urls": ("STRING", {
                    "multiline": True, "default": "",
                    "tooltip": "进阶：已有公网图片 URL 时每行贴一个，可与 image 口混用，共最多 16 张",
                }),
                "timeout_seconds": ("INT", {
                    "default": 300, "min": 60, "max": 600, "step": 30,
                    "tooltip": "最长等待时间；生成失败或审核拦截的任务不扣费",
                }),
            },
        }

    async def generate(self, prompt, model, size, resolution, quality, n,
                       api_key="", image1=None, image2=None, image3=None, image4=None,
                       image_urls="", timeout_seconds=300):
        key = resolve_api_key(api_key)
        prompt = (prompt or "").strip()
        if not prompt:
            raise EvoLinkError("prompt 不能为空，请填写画面描述（支持中文）。")

        notes = []
        refs = _parse_url_lines(image_urls)
        uploaded = 0
        for tensor in (image1, image2, image3, image4):
            if tensor is None:
                continue
            remaining = MAX_REFERENCE_IMAGES - len(refs)
            if remaining <= 0:
                notes.append(f"参考图超过 {MAX_REFERENCE_IMAGES} 张上限，多余部分已忽略")
                break
            new_urls = await asyncio.to_thread(upload_image_tensor, key, tensor, remaining)
            uploaded += len(new_urls)
            refs.extend(new_urls)
        refs = _dedupe(refs)
        if len(refs) > MAX_REFERENCE_IMAGES:
            refs = refs[:MAX_REFERENCE_IMAGES]
            notes.append(f"参考图超过 {MAX_REFERENCE_IMAGES} 张上限，已截断")

        payload = {
            "model": model,
            "prompt": prompt,
            "size": (size or "auto").strip() or "auto",
            "resolution": resolution,
            "quality": quality,
            "n": n,
        }
        if refs:
            payload["image_urls"] = refs

        started = time.monotonic()
        task = await asyncio.to_thread(submit_image_task, key, payload)
        task_id = task["id"]
        reserved = (task.get("usage") or {}).get("credits_reserved")
        print(f"[EvoLink] 任务已提交 {task_id}，预扣 credits: {reserved}")

        progress = make_progress_bar(100)
        progress(max(int(task.get("progress") or 0), 1))
        info = await poll_task_async(key, task_id, timeout_seconds=timeout_seconds,
                                     progress_callback=progress)
        progress(100)

        results = info.get("results") or []
        images = await asyncio.to_thread(urls_to_tensor_batch, results)
        elapsed = time.monotonic() - started
        used = (info.get("usage") or {}).get("credits_used")

        status_parts = [
            f"任务 {task_id} 完成",
            f"模型 {model}",
            f"用时 {elapsed:.1f}s",
            f"出图 {len(results)} 张",
        ]
        if used is not None:
            status_parts.append(f"消耗 credits {used}")
        if refs:
            mode = f"图生图（参考图 {len(refs)} 张，其中本地上传 {uploaded} 张）"
        else:
            mode = "文生图"
        status_parts.append(mode)
        status_parts.extend(notes)
        status_parts.append("结果已下载为图像输出（原始链接 24 小时过期）")
        status_info = " | ".join(status_parts)
        print(f"[EvoLink] {status_info}")
        return (images, task_id, status_info,
                "\n".join(results), json.dumps(info, ensure_ascii=False))


class EvoLinkUploadImage:
    """本地图批量上传到 EvoLink 官方通道，输出 URL 文本（每行一个）。"""

    DESCRIPTION = (
        "EvoLink 官方上传节点：把本地图片经官方文件通道换成公网 URL"
        "（72 小时过期，不经第三方图床），供组装复杂工作流使用。"
        "普通图生图不需要它 —— 直接把图连到生成节点的 image1 即可。"
    )
    CATEGORY = "EvoLink"
    FUNCTION = "upload"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("image_urls", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"image1": ("IMAGE", {"tooltip": "要上传的图片（可接 batch）"})},
            "optional": {
                "api_key": ("STRING", {"default": "", "tooltip": _API_KEY_TOOLTIP}),
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "image4": ("IMAGE",),
                "image5": ("IMAGE",),
                "image6": ("IMAGE",),
                "image7": ("IMAGE",),
                "image8": ("IMAGE",),
            },
        }

    def upload(self, image1, api_key="", **kwargs):
        key = resolve_api_key(api_key)
        tensors = [image1] + [kwargs.get(f"image{i}") for i in range(2, 9)]
        urls = []
        for tensor in tensors:
            if tensor is not None:
                urls.extend(upload_image_tensor(key, tensor))
        urls = _dedupe(urls)
        print(f"[EvoLink] 已上传 {len(urls)} 张图片（72 小时后自动删除）")
        return ("\n".join(urls), len(urls))
