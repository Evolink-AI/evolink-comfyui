"""注册表驱动的节点工厂。

data/evolink_registry.json 描述每个节点：模型清单、参数 schema、输入槽位。
本模块据此批量生成节点类 —— 专属节点（EvoLink Sora 2 等）与通用动态节点
（EvoLink Image/Video）共用同一套提交/轮询/落地逻辑，不产生重复代码。

registry 条目字段：
  node_id       ComfyUI 注册名（如 "EvoLink_Sora2"）
  display_name  画布显示名（含模型关键词，供双击搜索命中）
  output        "image" | "video"
  endpoint      提交路径（如 "/videos/generations"）
  description   节点帮助文本
  models        model 下拉框选项；只有 1 个时不显示下拉，直接用 default_model
  payload_const 可选：原样并入请求体的固定字段（如 Veo 的 generation_type）
  default_model 默认选中
  params        参数定义列表，见 _build_widget()
  image_slots   IMAGE 输入口定义：[{name, api_param, tooltip, required?}]
                同名 api_param 的多个槽位按顺序合并成 URL 列表
  url_text_param 可选：提供"每行一个 URL"的进阶文本框，值并入该 api_param
  max_images    该 api_param 的张数上限
"""

import asyncio
import json
import os
import time

from .client import EvoLinkError, poll_task_async, submit_task
from .config import resolve_api_key
from .task_utils import make_progress_bar, url_to_video, urls_to_tensor_batch
from .upload import upload_image_tensor

REGISTRY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "evolink_registry.json",
)

_API_KEY_TOOLTIP = (
    "EvoLink API Key（sk- 开头）。首次填写后自动保存到本机配置，之后可留空。"
    "分享工作流前请清空此框。获取：evolink.ai/dashboard/keys"
)


def load_registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_widget(param):
    """参数定义 -> ComfyUI 输入widget 元组。

    param 字段：
      name      API 参数名（即 widget 名，除非另给 api_name）
      widget    enum | string | int | float | bool
      values    enum 的选项
      default / min / max / step / multiline / tooltip
      skip_value  等于此值时不写入请求（如 seed=-1 表示随机）
      models    仅对这些模型生效（其余模型提交时自动剔除）；None=全部
    """
    tooltip = param.get("tooltip", "")
    if param.get("models"):
        tooltip = f"[仅 {', '.join(param['models'])}] {tooltip}"
    opts = {"tooltip": tooltip} if tooltip else {}
    widget = param["widget"]
    if widget == "enum":
        if "default" in param:
            opts["default"] = param["default"]
        return (list(param["values"]), opts)
    if widget == "string":
        opts["default"] = param.get("default", "")
        opts["multiline"] = bool(param.get("multiline"))
        return ("STRING", opts)
    if widget == "int":
        opts["default"] = int(param.get("default", 0))
        if "min" in param:
            opts["min"] = int(param["min"])
        if "max" in param:
            opts["max"] = int(param["max"])
        opts["step"] = int(param.get("step", 1))
        return ("INT", opts)
    if widget == "float":
        opts["default"] = float(param.get("default", 0.0))
        if "min" in param:
            opts["min"] = float(param["min"])
        if "max" in param:
            opts["max"] = float(param["max"])
        return ("FLOAT", opts)
    if widget == "bool":
        opts["default"] = bool(param.get("default", False))
        return ("BOOLEAN", opts)
    raise ValueError(f"registry 中未知 widget 类型: {widget}")


def _build_input_types(spec):
    required = {
        "prompt": ("STRING", {
            "multiline": True, "default": "",
            "tooltip": spec.get("prompt_tooltip", "画面/镜头描述，支持中文。"),
        }),
    }
    if len(spec["models"]) > 1:
        required["model"] = (list(spec["models"]), {"default": spec["default_model"]})
    optional = {}
    for param in spec.get("params", []):
        optional[param["name"]] = _build_widget(param)
    for slot in spec.get("image_slots", []):
        target = required if slot.get("required") else optional
        target[slot["name"]] = ("IMAGE", {"tooltip": slot.get("tooltip", "")})
    if spec.get("url_text_param"):
        optional["image_urls_text"] = ("STRING", {
            "multiline": True, "default": "",
            "tooltip": "进阶：已有公网图片 URL 时每行贴一个，与 IMAGE 口混用",
        })
    if spec.get("extra_json_param"):
        optional["extra_params"] = ("STRING", {
            "multiline": True, "default": "",
            "tooltip": "进阶：JSON 对象，原样并入请求体（如 {\"quality\":\"2K\"}），"
                       "用于本节点未暴露的模型专属参数，见 evolink.ai/docs 接口文档",
        })
    optional["api_key"] = ("STRING", {"default": "", "tooltip": _API_KEY_TOOLTIP})
    optional["timeout_seconds"] = ("INT", {
        "default": spec.get("default_timeout", 300), "min": 60, "max": 3600, "step": 30,
        "tooltip": "最长等待时间；生成失败或审核拦截的任务不扣费",
    })
    return {"required": required, "optional": optional}


def _parse_url_lines(text):
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


def _sora_resize_target(model, kwargs):
    """sora-2-preview 要求参考图像素与 aspect_ratio 完全一致，算出目标尺寸。"""
    if model != "sora-2-preview":
        return None
    ratio = str(kwargs.get("aspect_ratio") or "16:9")
    return {
        "16:9": (1280, 720), "1280x720": (1280, 720),
        "9:16": (720, 1280), "720x1280": (720, 1280),
    }.get(ratio, (1280, 720))


async def _collect_image_urls(spec, model, key, kwargs, notes):
    """上传各 IMAGE 槽位并合并 URL 文本框 -> {api_param: [url, ...] 或 单个 url}。

    槽位可选字段：
      models  仅这些模型使用该槽位；其余模型接了图会被忽略并提示
      single  api_param 是单个 URL 字符串（如 Kling 的 image_start），非数组
    """
    resize_to = None
    if spec.get("preprocess") == "sora_exact_size":
        resize_to = _sora_resize_target(model, kwargs)
    by_param, singles = {}, set()
    for slot in spec.get("image_slots", []):
        tensor = kwargs.get(slot["name"])
        if tensor is None:
            continue
        allowed = slot.get("models")
        if allowed and model not in allowed:
            notes.append(f"{model} 不使用 {slot['name']} 输入，已忽略")
            continue
        urls = await asyncio.to_thread(
            upload_image_tensor, key, tensor, None, resize_to
        )
        if slot.get("single"):
            singles.add(slot["api_param"])
        by_param.setdefault(slot["api_param"], []).extend(urls)
    text_param = spec.get("url_text_param")
    if text_param:
        by_param.setdefault(text_param, []).extend(
            _parse_url_lines(kwargs.get("image_urls_text"))
        )
    max_images = spec.get("max_images")
    result = {}
    for api_param, urls in by_param.items():
        deduped = list(dict.fromkeys(urls))
        if not deduped:
            continue
        if api_param in singles:
            result[api_param] = deduped[0]
        else:
            if max_images and len(deduped) > max_images:
                deduped = deduped[:max_images]
                notes.append(f"参考图超过 {max_images} 张上限，已截断")
            result[api_param] = deduped
    return result


def _build_payload(spec, model, prompt, kwargs, image_urls_by_param, notes):
    """按参数定义组装请求体。

    额外字段：
      nest          "model_params" 之类的嵌套对象名，参数写入 payload[nest][name]
      model_values  {model_id: [该模型允许的值]}；模型不在表里则参数整个剔除，
                    用户选了不支持的值时回退到该模型允许的第一个值并提示
    """
    payload = {"model": model}
    if prompt:
        payload["prompt"] = prompt
    for param in spec.get("params", []):
        allowed = param.get("models")
        if allowed and model not in allowed:
            continue
        value = kwargs.get(param["name"])
        if value is None:
            continue
        if "skip_value" in param and value == param["skip_value"]:
            continue
        # true_sets：布尔开关参数，开启时把指定字段写入请求体（如 auto_duration
        # -> duration=-1），自身不进请求体。放在被覆盖参数之后定义。
        if param.get("true_sets") is not None:
            if value:
                payload.update(param["true_sets"])
            continue
        if param.get("widget") == "string" and not str(value).strip():
            continue
        # url_list：多行文本框，每行一个 URL -> 数组参数（video_urls/audio_urls 等，
        # 可直接接上游节点的 result_urls 输出）
        if param.get("url_list"):
            urls = list(dict.fromkeys(
                line.strip() for line in str(value).splitlines() if line.strip()
            ))
            cap = param.get("max_items")
            if cap and len(urls) > cap:
                urls = urls[:cap]
                notes.append(f"{param['name']} 超过 {cap} 条上限，已截断")
            value = urls
        model_values = param.get("model_values")
        if model_values is not None:
            valid = model_values.get(model)
            if not valid:
                continue
            if value not in valid:
                fallback = valid[0]
                notes.append(
                    f"{model} 不支持 {param['name']}={value}，已改用 {fallback}"
                )
                value = fallback
        name = param.get("api_name", param["name"])
        nest = param.get("nest")
        if nest:
            payload.setdefault(nest, {})[name] = value
        else:
            payload[name] = value
    payload.update(spec.get("payload_const") or {})
    payload.update(image_urls_by_param)
    extra = (kwargs.get("extra_params") or "").strip()
    if extra:
        try:
            parsed = json.loads(extra)
            if not isinstance(parsed, dict):
                raise ValueError("必须是 JSON 对象")
        except ValueError as e:
            raise EvoLinkError(f"extra_params 不是合法的 JSON 对象：{e}")
        payload.update(parsed)
    # required 参数校验（如视频编辑必须给 video_urls），extra_params 也算数
    for param in spec.get("params", []):
        if param.get("required"):
            name = param.get("api_name", param["name"])
            if not payload.get(name):
                raise EvoLinkError(
                    f"{param['name']} 不能为空。{param.get('tooltip', '')}"
                )
    # 注册表用友好名做下拉选项，提交前换成 API 真实 model ID
    # （如 nano-banana-2 官方渠道实为 gemini-3.1-flash-image-preview）
    payload["model"] = spec.get("model_map", {}).get(model, model)
    return payload


def _make_generate(spec):
    async def generate(self, prompt, model=None, api_key="", timeout_seconds=None, **kwargs):
        key = resolve_api_key(api_key)
        model = model or spec["default_model"]
        prompt = (prompt or "").strip()
        if not prompt and spec.get("prompt_required", True):
            raise EvoLinkError("prompt 不能为空，请填写描述（支持中文）。")
        notes = []
        image_urls_by_param = await _collect_image_urls(spec, model, key, kwargs, notes)
        payload = _build_payload(spec, model, prompt, kwargs, image_urls_by_param, notes)

        started = time.monotonic()
        task = await asyncio.to_thread(submit_task, key, spec["endpoint"], payload)
        task_id = task["id"]
        reserved = (task.get("usage") or {}).get("credits_reserved")
        print(f"[EvoLink] 任务已提交 {task_id}（{model}），预扣 credits: {reserved}")

        progress = make_progress_bar(100)
        progress(max(int(task.get("progress") or 0), 1))
        timeout = timeout_seconds or spec.get("default_timeout", 300)
        info = await poll_task_async(key, task_id, timeout_seconds=timeout,
                                     progress_callback=progress)
        progress(100)

        results = info.get("results") or []
        if not results:
            raise EvoLinkError(f"任务完成但未返回结果链接。任务 ID: {task_id}")
        elapsed = time.monotonic() - started
        used = (info.get("usage") or {}).get("credits_used")
        status_parts = [f"任务 {task_id} 完成", f"模型 {model}", f"用时 {elapsed:.1f}s"]
        if used is not None:
            status_parts.append(f"消耗 credits {used}")
        status_parts.extend(notes)
        result_urls = "\n".join(results)
        response_json = json.dumps(info, ensure_ascii=False)

        if spec["output"] == "video":
            status_parts.append("视频已下载（原始链接 24 小时过期），接「保存视频」节点落盘")
            video = await asyncio.to_thread(url_to_video, results[0])
            status_info = " | ".join(status_parts)
            print(f"[EvoLink] {status_info}")
            return (video, task_id, status_info, result_urls, response_json)
        status_parts.append(f"出图 {len(results)} 张（原始链接 24 小时过期）")
        images = await asyncio.to_thread(urls_to_tensor_batch, results)
        status_info = " | ".join(status_parts)
        print(f"[EvoLink] {status_info}")
        return (images, task_id, status_info, result_urls, response_json)

    return generate


def make_node_class(spec):
    output_type = "VIDEO" if spec["output"] == "video" else "IMAGE"
    attrs = {
        "DESCRIPTION": spec.get("description", ""),
        "CATEGORY": "EvoLink",
        "FUNCTION": "generate",
        "RETURN_TYPES": (output_type, "STRING", "STRING", "STRING", "STRING"),
        "RETURN_NAMES": (spec["output"], "task_id", "status_info",
                         "result_urls", "response_json"),
        "OUTPUT_TOOLTIPS": (
            "生成结果（已下载落地，可直连保存节点）",
            "EvoLink 任务 ID，可到 evolink.ai/zh/dashboard/logs 查询",
            "人读状态摘要（模型/用时/消耗 credits）",
            "结果原始链接，每行一个（24 小时过期）",
            "平台 GET /v1/tasks/{id} 的完整 JSON 响应（status/usage/results 等），供下游节点解析",
        ),
        "INPUT_TYPES": classmethod(lambda cls, _spec=spec: _build_input_types(_spec)),
        "generate": _make_generate(spec),
    }
    return type(spec["node_id"].replace("-", "_"), (), attrs)


def build_nodes():
    """读取注册表，返回 (NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS)。"""
    registry = load_registry()
    class_mappings, display_mappings = {}, {}
    for spec in registry["nodes"]:
        class_mappings[spec["node_id"]] = make_node_class(spec)
        display_mappings[spec["node_id"]] = spec["display_name"]
    return class_mappings, display_mappings
