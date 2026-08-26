"""本地图 -> EvoLink 官方文件通道 -> 公网 URL。

替代社区版的 imgbb 第三方图床方案：图片经 EvoLink 官方接口上传
（POST files-api.evolink.ai/api/v1/files/upload/base64，单次一张，
返回 data.file_url，72 小时后自动删除，默认配额 2000 个文件）。
"""

import base64
import io
import uuid

import numpy as np
from PIL import Image

from .client import FILES_API_BASE, EvoLinkError, request_json


def tensor_to_pil_list(image_tensor):
    """ComfyUI IMAGE tensor [B,H,W,C] float 0-1 -> PIL RGB 列表（逐帧）。"""
    arr = image_tensor.cpu().numpy() if hasattr(image_tensor, "cpu") else np.asarray(image_tensor)
    if arr.ndim == 3:
        arr = arr[None, ...]
    images = []
    for frame in arr:
        frame = np.clip(frame * 255.0, 0, 255).astype(np.uint8)
        if frame.shape[-1] == 4:
            frame = frame[..., :3]
        images.append(Image.fromarray(frame, mode="RGB"))
    return images


def pil_to_data_uri(pil_image):
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def upload_pil(api_key, pil_image):
    """上传一张 PIL 图，返回公网 file_url。"""
    payload = {
        "base64_data": pil_to_data_uri(pil_image),
        "file_name": f"comfyui_{uuid.uuid4().hex[:12]}.png",
    }
    try:
        body = request_json(
            "POST", f"{FILES_API_BASE}/files/upload/base64", api_key, payload, timeout=120
        )
    except EvoLinkError as e:
        raise EvoLinkError(
            f"参考图上传失败：{e}\n"
            "若提示配额（quota）已满：上传文件默认配额 2000 个（72 小时自动清理），"
            "可联系 support@evolink.ai 提额。"
        )
    data = body.get("data") or {}
    file_url = data.get("file_url")
    if not file_url:
        raise EvoLinkError(
            f"上传接口未返回 file_url，原始响应：{str(body)[:200]}"
        )
    return file_url


def upload_image_tensor(api_key, image_tensor, limit=None, resize_to=None):
    """上传一个 IMAGE 输入（可能是多帧 batch），返回 URL 列表。

    limit 为剩余可用张数（防止超过 API 的 16 张上限时白白上传）。
    resize_to=(w, h)：上传前缩放到精确像素（sora-2-preview 要求
    参考图与 aspect_ratio 像素完全一致）。
    """
    urls = []
    for pil_image in tensor_to_pil_list(image_tensor):
        if limit is not None and len(urls) >= limit:
            break
        if resize_to and pil_image.size != tuple(resize_to):
            pil_image = pil_image.resize(tuple(resize_to), Image.LANCZOS)
        urls.append(upload_pil(api_key, pil_image))
    return urls
