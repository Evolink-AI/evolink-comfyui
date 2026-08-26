"""结果落地与进度上报工具。

EvoLink 的结果链接 24 小时过期，所以节点必须把图片下载为 tensor 返回，
用户用「保存图像」节点即可永久落盘。
"""

import io

import numpy as np
import requests
import torch
from PIL import Image

from .client import USER_AGENT, EvoLinkError


def _download(url, timeout=120):
    last_exc = None
    for _ in range(2):
        try:
            resp = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
            if resp.status_code == 200:
                return resp.content
            last_exc = EvoLinkError(f"下载结果图失败 HTTP {resp.status_code}: {url}")
        except requests.RequestException as e:
            last_exc = EvoLinkError(f"下载结果图失败：{e}")
    raise EvoLinkError(
        f"{last_exc}\n提示：结果链接 24 小时过期；如已过期请重新运行生成，"
        "或到 https://evolink.ai/zh/dashboard/logs 查看任务详情。"
    )


def url_to_pil(url):
    return Image.open(io.BytesIO(_download(url))).convert("RGB")


def urls_to_tensor_batch(urls):
    """下载全部结果 -> ComfyUI IMAGE tensor [B,H,W,C]。尺寸不一致时对齐到首图。"""
    if not urls:
        raise EvoLinkError("任务完成但未返回任何图片链接（results 为空）。")
    pils = [url_to_pil(u) for u in urls]
    base_size = pils[0].size
    tensors = []
    for img in pils:
        if img.size != base_size:
            img = img.resize(base_size, Image.LANCZOS)
        arr = np.asarray(img).astype(np.float32) / 255.0
        tensors.append(torch.from_numpy(arr)[None, ...])
    return torch.cat(tensors, dim=0)


def url_to_video(url):
    """下载结果视频 -> ComfyUI VIDEO 对象，可直连原生「保存视频」节点。"""
    try:
        from comfy_api.input_impl import VideoFromFile
    except Exception:
        raise EvoLinkError(
            "当前 ComfyUI 版本不支持 VIDEO 输出（缺少 comfy_api），"
            "请把 ComfyUI 升级到较新版本后再使用视频节点。"
        )
    data = _download(url, timeout=600)
    return VideoFromFile(io.BytesIO(data))


def make_progress_bar(total=100):
    """ComfyUI 进度条；在 ComfyUI 外（单测环境）静默降级。"""
    try:
        from comfy.utils import ProgressBar

        bar = ProgressBar(total)
        return lambda value: bar.update_absolute(min(max(value, 0), total), total)
    except Exception:
        return lambda value: None
