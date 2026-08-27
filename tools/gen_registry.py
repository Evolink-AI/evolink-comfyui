"""生成拆分后的 evolink_registry.json：一个变体一个节点（fal 风格）。

拆分规则：
- API model ID 不同的任务变体（t2v/i2v/reference）各自成节点
- 同节点内多个模型仅当输入 schema 完全一致（Veo standard/fast、Wan standard/prime）
- beta 渠道与老模型收进 EvoLink Image / EvoLink Video 通用节点
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "data", "evolink_registry.json")

# ---------- 公共片段 ----------

NB_SIZES_FULL = ["auto", "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4",
                 "9:16", "16:9", "21:9", "1:4", "4:1", "1:8", "8:1"]
NB_SIZES_PRO = ["auto", "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4",
                "9:16", "16:9", "21:9"]

IMG_EDIT_TIP = "参考图 1：接「加载图像」即图生图/图片编辑"


def ref_slots(count, first_tip=IMG_EDIT_TIP):
    slots = [{"name": "image1", "api_param": "image_urls", "tooltip": first_tip}]
    for i in range(2, count + 1):
        slots.append({"name": f"image{i}", "api_param": "image_urls",
                      "tooltip": f"参考图 {i}（可选）"})
    return slots


def first_last_slots(api="image_urls", single=False, with_last=True,
                     first_tip="首帧图（必接）", last_tip="尾帧图（可选，接上即首尾帧模式）"):
    first = {"name": "first_frame", "api_param": "image_start" if api == "start_end" else api,
             "required": True, "tooltip": first_tip}
    if api == "start_end":
        first["api_param"] = "image_start"
    if single or api == "start_end":
        first["single"] = True
    slots = [first]
    if with_last:
        last = {"name": "last_frame",
                "api_param": "image_end" if api == "start_end" else api,
                "tooltip": last_tip}
        if single or api == "start_end":
            last["single"] = True
        slots.append(last)
    return slots


def p_enum(name, values, default=None, tooltip="", **kw):
    p = {"name": name, "widget": "enum", "values": values,
         "default": default if default is not None else values[0]}
    if tooltip:
        p["tooltip"] = tooltip
    p.update(kw)
    return p


def p_int(name, default, mn, mx, tooltip="", **kw):
    p = {"name": name, "widget": "int", "default": default, "min": mn, "max": mx}
    if tooltip:
        p["tooltip"] = tooltip
    p.update(kw)
    return p


def p_bool(name, default, tooltip="", **kw):
    p = {"name": name, "widget": "bool", "default": default}
    if tooltip:
        p["tooltip"] = tooltip
    p.update(kw)
    return p


def p_str(name, default="", tooltip="", **kw):
    p = {"name": name, "widget": "string", "default": default}
    if tooltip:
        p["tooltip"] = tooltip
    p.update(kw)
    return p


def node(node_id, display, output, desc, models, **kw):
    spec = {
        "node_id": node_id,
        "display_name": display,
        "output": output,
        "endpoint": "/videos/generations" if output == "video" else "/images/generations",
        "description": desc,
        "models": models,
        "default_model": kw.pop("default_model", models[0]),
    }
    spec.update(kw)
    return spec


nodes = []

# ---------- 图像：Nano Banana 系列（beta 渠道见 EvoLink Image 通用节点） ----------

THINKING = p_enum("thinking_level", ["auto", "min", "high"], "auto",
                  "生成前的推理深度；auto 由模型决定",
                  skip_value="auto", nest="model_params")
WEB_SEARCH = p_bool("web_search", False, "用联网搜索结果优化生成（可能产生额外费用）",
                    skip_value=False, nest="model_params")
NB_PROMPT_TIP = "画面描述或修改指令，支持中文，最长约 2000 tokens。含真人照片的参考图最多 4~5 张。"

nodes.append(node(
    "EvoLink_NanoBanana2", "EvoLink Nano Banana 2 (Official)", "image",
    "EvoLink 官方节点：Google Nano Banana 2（gemini-3.1-flash-image）文生图、图生图、图片编辑，"
    "0.5K~4K 分辨率与极端比例（1:8/8:1 等），接「加载图像」即图生图"
    "（本地图经 EvoLink 官方通道上传，72 小时自动删除）。beta 低价渠道见 EvoLink Image 通用节点。"
    "Nano Banana 2 text-to-image & image editing.",
    ["nano-banana-2"],
    prompt_tooltip=NB_PROMPT_TIP,
    model_map={"nano-banana-2": "gemini-3.1-flash-image-preview"},
    params=[
        p_enum("size", NB_SIZES_FULL, "auto", "画面比例；auto 由模型自定"),
        p_enum("quality", ["2K", "0.5K", "1K", "4K"], "2K",
               "输出分辨率档位（注意与 gpt-image-2 的 quality 含义不同）；4K 加价"),
        THINKING, WEB_SEARCH,
    ],
    image_slots=ref_slots(4), url_text_param="image_urls",
    max_images=14, default_timeout=300,
))

nodes.append(node(
    "EvoLink_NanoBananaPro", "EvoLink Nano Banana Pro (Official)", "image",
    "EvoLink 官方节点：Google Nano Banana Pro（gemini-3-pro-image）高质量文生图、图生图、图片编辑，"
    "支持 4K 输出与联网搜索增强。接「加载图像」即图生图。beta 低价渠道见 EvoLink Image 通用节点。"
    "Nano Banana Pro text-to-image & image editing.",
    ["nano-banana-pro"],
    prompt_tooltip=NB_PROMPT_TIP,
    model_map={"nano-banana-pro": "gemini-3-pro-image-preview"},
    params=[
        p_enum("size", NB_SIZES_PRO, "auto", "画面比例；auto 由模型自定"),
        p_enum("quality", ["2K", "1K", "4K"], "2K", "输出分辨率档位；4K 加价"),
        WEB_SEARCH,
    ],
    image_slots=ref_slots(4), url_text_param="image_urls",
    max_images=14, default_timeout=300,
))

nodes.append(node(
    "EvoLink_NanoBananaLite", "EvoLink Nano Banana 2 Lite (Official)", "image",
    "EvoLink 官方节点：Google Nano Banana 2 Lite（gemini-3.1-flash-lite-image）——最便宜的 "
    "Nano Banana 档位，固定 1K 输出，适合批量与调试。接「加载图像」即图生图。"
    "beta 低价渠道见 EvoLink Image 通用节点。Nano Banana 2 Lite budget text-to-image & image editing.",
    ["nano-banana-2-lite"],
    prompt_tooltip=NB_PROMPT_TIP,
    model_map={"nano-banana-2-lite": "gemini-3.1-flash-lite-image"},
    params=[
        p_enum("size", NB_SIZES_FULL, "auto", "画面比例；auto 由模型自定（输出固定 1K）"),
        THINKING,
    ],
    image_slots=ref_slots(4), url_text_param="image_urls",
    max_images=14, default_timeout=300,
))

# ---------- 图像：Seedream 系列 ----------

SEEDREAM_SIZE = p_str("size", "auto", "auto / 比例如 1:1、16:9、9:21 / 像素如 2048x2048")

nodes.append(node(
    "EvoLink_Seedream5Pro", "EvoLink Seedream 5.0 Pro (Official)", "image",
    "EvoLink 官方节点：字节豆包 Seedream 5.0 Pro 文生图、图生图、图片编辑——单图质量最优档，"
    "支持中文提示词与多图参考（上限 10 张）；不支持一次多图输出（要多图请用 Seedream 5.0 Lite）。"
    "Doubao Seedream 5.0 Pro text-to-image & image editing.",
    ["doubao-seedream-5.0-pro"],
    prompt_tooltip="画面描述或修改指令，支持中文，建议 300 字以内。",
    params=[
        SEEDREAM_SIZE,
        p_enum("quality", ["2K", "1K", "1.5K"], "2K", "分辨率档位"),
        p_bool("watermark", False, "是否加水印", skip_value=False),
    ],
    image_slots=ref_slots(4, IMG_EDIT_TIP + "（参考图上限 10 张）"),
    url_text_param="image_urls", max_images=10, default_timeout=300,
))

nodes.append(node(
    "EvoLink_Seedream5Lite", "EvoLink Seedream 5.0 Lite (Official)", "image",
    "EvoLink 官方节点：字节豆包 Seedream 5.0 Lite 文生图、图生图、图片编辑，一次最多 15 张，"
    "2K/3K/4K 分辨率，支持中文提示词与多图参考。Doubao Seedream 5.0 Lite text-to-image & image editing.",
    ["doubao-seedream-5.0-lite"],
    prompt_tooltip="画面描述或修改指令，支持中文。要一次多图时在 prompt 里说明张数。",
    params=[
        SEEDREAM_SIZE,
        p_enum("quality", ["2K", "3K", "4K"], "2K", "分辨率档位"),
        p_int("n", 1, 1, 15, "最多生成几张（上限，需同时在 prompt 中要求多图）", skip_value=1),
    ],
    image_slots=ref_slots(4), url_text_param="image_urls",
    max_images=14, default_timeout=300,
))

for ver, qualities in (("4.5", ["2K", "4K"]), ("4.0", ["2K", "1K", "4K"])):
    nodes.append(node(
        f"EvoLink_Seedream{ver.replace('.', '')}", f"EvoLink Seedream {ver} (Official)", "image",
        f"EvoLink 官方节点：字节豆包 Seedream {ver} 文生图、图生图、图片编辑，一次最多 15 张，"
        f"支持中文提示词与多图参考。Doubao Seedream {ver} text-to-image & image editing.",
        [f"doubao-seedream-{ver}"],
        prompt_tooltip="画面描述或修改指令，支持中文。要一次多图时在 prompt 里说明张数。",
        params=[
            SEEDREAM_SIZE,
            p_enum("quality", qualities, "2K", "分辨率档位"),
            p_int("n", 1, 1, 15, "最多生成几张（上限，需同时在 prompt 中要求多图）", skip_value=1),
        ],
        image_slots=ref_slots(4), url_text_param="image_urls",
        max_images=14, default_timeout=300,
    ))

# ---------- 图像：Grok Imagine（原样保留，本就单模型） ----------

nodes.append(node(
    "EvoLink_GrokImagine", "EvoLink Grok Imagine Image 2.0 (Official)", "image",
    "EvoLink 官方节点：xAI Grok Imagine Image 2.0 文生图、图生图、多图编辑（<IMAGE_0> 引用语法），"
    "支持 13 种画幅与一次最多 10 张。xAI Grok Imagine text-to-image & image editing.",
    ["grok-imagine-image-2.0"],
    prompt_tooltip="画面描述或编辑指令。多图编辑用 <IMAGE_0>、<IMAGE_1> 引用第 1、2 张参考图。",
    params=[
        p_enum("size", ["auto", "1:1", "4:3", "3:4", "3:2", "2:3", "16:9", "9:16",
                        "2:1", "1:2", "19.5:9", "9:19.5", "20:9", "9:20"], "auto",
               "画幅比例；auto 由模型自定（通常偏竖图）"),
        p_enum("resolution", ["1K", "2K"], "1K", "像素档位（不支持 4K）"),
        p_enum("quality", ["medium", "low"], "medium", "low 更快更便宜；medium 质量更好（无 high 档）"),
        p_int("n", 1, 1, 10, "一次生成几张，每张独立计费", skip_value=1),
    ],
    image_slots=[
        {"name": "image1", "api_param": "image_urls",
         "tooltip": "参考图 1（接图即图生图/编辑；编辑时参考图按次加价，不随 n 翻倍）"},
        {"name": "image2", "api_param": "image_urls", "tooltip": "参考图 2（可选，共最多 3 张）"},
        {"name": "image3", "api_param": "image_urls", "tooltip": "参考图 3（可选）"},
    ],
    max_images=3, default_timeout=300,
))

# ---------- 图像：Qwen / Z-Image / Krea（2026-08-27 新增批次） ----------

QWEN_SEED = p_int("seed", 0, 0, 2147483647, "0=随机；固定可复现结果", skip_value=0)

def qwen_params(prompt_extend_default):
    return [
        p_str("size", "auto", "auto / 比例如 1:1、16:9 / 像素如 1328x1328"),
        p_enum("quality", ["1K", "2K"], "1K", "分辨率档位"),
        p_int("n", 1, 1, 6, "一次生成几张（1~6）", skip_value=1),
        p_str("negative_prompt", "", "不希望出现的内容"),
        p_bool("prompt_extend", prompt_extend_default, "提示词智能扩写（短 prompt 建议开启）"),
        p_bool("watermark", False, "是否加水印", skip_value=False),
        QWEN_SEED,
    ]

nodes.append(node(
    "EvoLink_QwenImage3", "EvoLink Qwen Image 3.0 (Official)", "image",
    "EvoLink 官方节点：阿里通义千问 Qwen Image 3.0 文生图、图生图，中文文字渲染强，"
    "一次最多 6 张。Alibaba Qwen Image 3.0 text-to-image & image-to-image.",
    ["qwen-image-3.0"],
    prompt_tooltip="画面描述，支持中文，擅长画面内文字渲染。",
    params=qwen_params(False),
    image_slots=ref_slots(4, "参考图 1：接「加载图像」即图生图"),
    url_text_param="image_urls", default_timeout=300,
))

nodes.append(node(
    "EvoLink_QwenImage3Pro", "EvoLink Qwen Image 3.0 Pro (Official)", "image",
    "EvoLink 官方节点：阿里通义千问 Qwen Image 3.0 Pro 高质量文生图、图生图，中文文字渲染强，"
    "一次最多 6 张。Alibaba Qwen Image 3.0 Pro text-to-image & image-to-image.",
    ["qwen-image-3.0-pro"],
    prompt_tooltip="画面描述，支持中文，擅长画面内文字渲染。",
    params=qwen_params(False),
    image_slots=ref_slots(4, "参考图 1：接「加载图像」即图生图"),
    url_text_param="image_urls", default_timeout=300,
))

nodes.append(node(
    "EvoLink_QwenImageEditPlus", "EvoLink Qwen Image Edit Plus (Official)", "image",
    "EvoLink 官方节点：阿里通义千问 Qwen Image Edit Plus 图片编辑（必接输入图），"
    "改文字/换风格/局部修改，一次最多 6 张。Alibaba Qwen Image Edit Plus image editing.",
    ["qwen-image-edit-plus"],
    prompt_tooltip="编辑指令，支持中文（如「把招牌文字改成…」）。",
    params=[
        p_str("size", "", "留空=跟随输入图；或比例/像素"),
        p_int("n", 1, 1, 6, "一次生成几张（1~6）", skip_value=1),
        p_str("negative_prompt", "", "不希望出现的内容"),
        p_bool("prompt_extend", True, "提示词智能扩写"),
        p_bool("watermark", False, "是否加水印", skip_value=False),
        QWEN_SEED,
    ],
    image_slots=[
        {"name": "image1", "api_param": "image_urls", "required": True,
         "tooltip": "要编辑的图片（必接）"},
        {"name": "image2", "api_param": "image_urls", "tooltip": "参考图 2（可选）"},
        {"name": "image3", "api_param": "image_urls", "tooltip": "参考图 3（可选）"},
    ],
    url_text_param="image_urls", default_timeout=300,
))

nodes.append(node(
    "EvoLink_ZImageTurbo", "EvoLink Z-Image Turbo (Official)", "image",
    "EvoLink 官方节点：阿里通义 Z-Image Turbo 轻量极速文生图——出图快、价格低，"
    "适合批量与实时场景。Alibaba Z-Image Turbo fast budget text-to-image.",
    ["z-image-turbo"],
    prompt_tooltip="画面描述，支持中文。",
    params=[
        p_enum("size", ["auto", "1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9",
                        "1:2", "2:1"], "auto",
               "画幅比例；auto=不指定，用模型默认", skip_value="auto"),
        p_int("seed", 0, 0, 2147483647, "0=随机；固定可复现结果", skip_value=0),
        p_bool("nsfw_check", False, "开启 NSFW 内容检测", skip_value=False),
    ],
    default_timeout=300,
))

nodes.append(node(
    "EvoLink_Krea2Turbo", "EvoLink Krea 2 Turbo (Official)", "image",
    "EvoLink 官方节点：Krea 2 Turbo 文生图——真实感风格出众、速度快。"
    "Krea 2 Turbo photorealistic fast text-to-image.",
    ["krea-2-turbo"],
    prompt_tooltip="画面描述。",
    params=[
        p_enum("size", ["1:1", "4:3", "3:4", "5:4", "4:5", "2:3", "3:2", "9:16",
                        "16:9", "1:2", "2:1"], "1:1", "画幅比例"),
        p_enum("quality", ["1K", "2K"], "1K", "分辨率档位"),
        p_int("seed", 0, 0, 1048576, "0=随机；固定可复现结果", skip_value=0),
        p_bool("nsfw_check", False, "开启 NSFW 内容检测", skip_value=False),
    ],
    default_timeout=300,
))

# ---------- 图像：通用节点（含 beta 渠道与老模型，原样保留） ----------

nodes.append(node(
    "EvoLink_Image", "EvoLink Image (All Models)", "image",
    "EvoLink 通用图像节点：一个节点调用全部图像模型（含各 beta 低价渠道与老模型）。"
    "模型专属参数用 extra_params 以 JSON 传入，接口文档见 evolink.ai/docs。",
    ["gpt-image-2", "grok-imagine-image-2.0", "nano-banana-2", "nano-banana-pro",
     "nano-banana-2-lite", "doubao-seedream-5.0-pro", "doubao-seedream-5.0-lite",
     "doubao-seedream-4.5", "doubao-seedream-4.0", "qwen-image-3.0",
     "qwen-image-3.0-pro", "qwen-image-edit-plus", "qwen-image-edit",
     "z-image-turbo", "krea-2-turbo", "wan2.5-text-to-image", "wan2.5-image-to-image",
     "doubao-seedream-5.0-pro-layerize", "gpt-image-1.5", "nano-banana-2-beta",
     "nano-banana-pro-beta", "nano-banana-2-lite-beta", "nano-banana-beta",
     "gpt-image-2-beta"],
    prompt_tooltip="画面描述或修改指令，支持中文。",
    model_map={
        "nano-banana-2": "gemini-3.1-flash-image-preview",
        "nano-banana-2-lite": "gemini-3.1-flash-lite-image",
        "nano-banana-pro": "gemini-3-pro-image-preview",
    },
    params=[p_str("size", "auto", "auto / 比例如 1:1、16:9 / 像素如 1024x1024（支持范围随模型而异）")],
    extra_json_param=True,
    image_slots=ref_slots(4, "参考图 1：接「加载图像」即图生图"),
    url_text_param="image_urls", max_images=16, default_timeout=300,
))

# ---------- 视频：Sora 2 ----------

SORA_PROMPT_TIP = "镜头/画面描述，支持中文，最长约 5000 tokens。Sora 内容审核较严，参考图不支持真人照片。"
SORA_SLOT = [{"name": "image", "api_param": "image_urls",
              "tooltip": "参考图（图生视频）；不支持真人照片"}]

nodes.append(node(
    "EvoLink_Sora2", "EvoLink Sora 2 (Official)", "video",
    "EvoLink 官方节点：OpenAI Sora 2 文生视频、图生视频。接「加载图像」即图生视频"
    "（参考图会自动缩放到与画幅一致的像素）。输出可直连原生「保存视频」节点。"
    "更高分辨率见 EvoLink Sora 2 Pro 节点。Sora 2 text-to-video & image-to-video.",
    ["sora-2-preview"],
    preprocess="sora_exact_size",
    prompt_tooltip=SORA_PROMPT_TIP,
    params=[
        p_enum("aspect_ratio", ["16:9", "9:16"], "16:9", "横屏 16:9 / 竖屏 9:16"),
        p_enum("duration", [4, 8, 12], 4, "视频时长（秒），按时长计费"),
    ],
    image_slots=SORA_SLOT, max_images=1, default_timeout=1200,
))

nodes.append(node(
    "EvoLink_Sora2Pro", "EvoLink Sora 2 Pro (Official)", "video",
    "EvoLink 官方节点：OpenAI Sora 2 Pro 文生视频、图生视频，支持 1080p。"
    "接「加载图像」即图生视频。输出可直连原生「保存视频」节点。"
    "Sora 2 Pro text-to-video & image-to-video.",
    ["sora-2-pro-preview"],
    prompt_tooltip=SORA_PROMPT_TIP,
    params=[
        p_enum("aspect_ratio", ["16:9", "9:16"], "16:9", "横屏 16:9 / 竖屏 9:16"),
        p_enum("duration", [4, 8, 12], 4, "视频时长（秒），按时长计费"),
        p_enum("quality", ["720p", "1080p"], "720p", "1080p 价格约为 720p 的 1.67 倍"),
    ],
    image_slots=SORA_SLOT, max_images=1, default_timeout=1200,
))

# ---------- 视频：Veo 3.1（standard/fast 输入一致共用下拉；beta 渠道见 EvoLink Video） ----------

VEO_MODELS = ["veo-3.1-generate-preview", "veo-3.1-fast-generate-preview"]
VEO_PROMPT_TIP = "镜头/画面描述，支持中文，最长约 2000 tokens。"


def veo_params(ar_tip):
    return [
        p_enum("aspect_ratio", ["auto", "16:9", "9:16"], "auto", ar_tip),
        p_enum("duration", [8, 4, 6], 8, "视频时长（秒）"),
        p_enum("quality", ["720p", "1080p", "4k"], "720p", "分辨率"),
        p_bool("generate_audio", True, "生成原生音频（额外收费）"),
        p_str("negative_prompt", "", "不希望出现的内容"),
        p_int("seed", 0, 0, 4294967295, "0=随机", skip_value=0),
    ]


nodes.append(node(
    "EvoLink_Veo31T2V", "EvoLink Veo 3.1 Text-to-Video (Official)", "video",
    "EvoLink 官方节点：Google Veo 3.1 / 3.1 Fast 文生视频，原生音频，最高 4K。"
    "首尾帧图生视频、参考图生视频请用对应的 EvoLink Veo 3.1 节点；beta 低价渠道见 "
    "EvoLink Video 通用节点。Veo 3.1 text-to-video with native audio.",
    VEO_MODELS,
    prompt_tooltip=VEO_PROMPT_TIP,
    params=veo_params("auto：按 prompt 自动选择画幅"),
    default_timeout=1200,
))

nodes.append(node(
    "EvoLink_Veo31I2V", "EvoLink Veo 3.1 Image-to-Video (Official)", "video",
    "EvoLink 官方节点：Google Veo 3.1 / 3.1 Fast 首尾帧图生视频（first_frame 必接，"
    "last_frame 可选），原生音频，最高 4K。Veo 3.1 image-to-video (first/last frame) with native audio.",
    VEO_MODELS,
    prompt_tooltip=VEO_PROMPT_TIP,
    payload_const={"generation_type": "FIRST&LAST"},
    params=veo_params("auto：按首帧图比例"),
    image_slots=[
        {"name": "first_frame", "api_param": "image_urls", "required": True,
         "tooltip": "首帧图（必接）"},
        {"name": "last_frame", "api_param": "image_urls", "tooltip": "尾帧图（可选）"},
    ],
    max_images=2, default_timeout=1200,
))

nodes.append(node(
    "EvoLink_Veo31Ref", "EvoLink Veo 3.1 Reference-to-Video (Official)", "video",
    "EvoLink 官方节点：Google Veo 3.1 / 3.1 Fast 参考图生视频（最多 3 张参考图，"
    "保持主体/风格一致），原生音频。Veo 3.1 reference-to-video with native audio.",
    VEO_MODELS,
    prompt_tooltip=VEO_PROMPT_TIP,
    payload_const={"generation_type": "REFERENCE"},
    params=veo_params("auto：按参考图与 prompt 自动"),
    image_slots=[
        {"name": "reference_image1", "api_param": "image_urls", "required": True,
         "tooltip": "参考图 1（必接，最多 3 张）"},
        {"name": "reference_image2", "api_param": "image_urls", "tooltip": "参考图 2（可选）"},
        {"name": "reference_image3", "api_param": "image_urls", "tooltip": "参考图 3（可选）"},
    ],
    max_images=3, default_timeout=1200,
))

# ---------- 视频：Kling（V3 / Turbo / O3 × T2V / I2V） ----------

KLING_PROMPT_TIP = "镜头/画面描述，支持中文，最长 2500 字符。多分镜等高级用法见 evolink.ai/docs。"
KLING_DUR = p_int("duration", 5, 3, 15, "视频时长（秒），3~15 任意整数，按时长计费")
KLING_AR = p_enum("aspect_ratio", ["16:9", "9:16", "1:1"], "16:9", "画幅比例")
KLING_SOUND = p_enum("sound", ["off", "on"], "off", "生成音效", skip_value="off")
KLING_NEG = p_str("negative_prompt", "", "不希望出现的内容")
KLING_Q_FULL = p_enum("quality", ["720p", "1080p", "4k"], "720p", "分辨率")
KLING_Q_TURBO = p_enum("quality", ["720p", "1080p"], "720p", "分辨率（Turbo 不支持 4k）")
KLING_FIRST = {"name": "first_frame", "api_param": "image_start", "single": True,
               "required": True, "tooltip": "首帧图（必接）；宽高≥300px，比例 1:2.5~2.5:1"}
KLING_LAST = {"name": "last_frame", "api_param": "image_end", "single": True,
              "tooltip": "尾帧图（可选）"}

nodes.append(node(
    "EvoLink_KlingV3T2V", "EvoLink Kling V3 Text-to-Video (Official)", "video",
    "EvoLink 官方节点：快手可灵 Kling V3 文生视频，3~15 秒任意时长，最高 4K，支持音效与负向提示词。"
    "Kuaishou Kling V3 text-to-video.",
    ["kling-v3-text-to-video"],
    prompt_tooltip=KLING_PROMPT_TIP,
    params=[KLING_DUR, KLING_AR, KLING_Q_FULL, KLING_SOUND, KLING_NEG],
    default_timeout=1200,
))

nodes.append(node(
    "EvoLink_KlingV3I2V", "EvoLink Kling V3 Image-to-Video (Official)", "video",
    "EvoLink 官方节点：快手可灵 Kling V3 图生视频（首帧必接，尾帧可选），画幅由首帧图决定，"
    "3~15 秒任意时长，最高 4K，支持音效。Kuaishou Kling V3 image-to-video (first/last frame).",
    ["kling-v3-image-to-video"],
    prompt_required=False,
    prompt_tooltip=KLING_PROMPT_TIP,
    params=[KLING_DUR, KLING_Q_FULL, KLING_SOUND, KLING_NEG],
    image_slots=[KLING_FIRST, KLING_LAST],
    default_timeout=1200,
))

nodes.append(node(
    "EvoLink_KlingTurboT2V", "EvoLink Kling V3 Turbo Text-to-Video (Official)", "video",
    "EvoLink 官方节点：快手可灵 Kling V3 Turbo 文生视频——更快更便宜的档位，3~15 秒，"
    "最高 1080p（不支持音效与负向提示词）。Kuaishou Kling V3 Turbo fast text-to-video.",
    ["kling-v3-turbo-text-to-video"],
    prompt_tooltip=KLING_PROMPT_TIP,
    params=[KLING_DUR, KLING_AR, KLING_Q_TURBO],
    default_timeout=1200,
))

nodes.append(node(
    "EvoLink_KlingTurboI2V", "EvoLink Kling V3 Turbo Image-to-Video (Official)", "video",
    "EvoLink 官方节点：快手可灵 Kling V3 Turbo 图生视频——更快更便宜的档位（仅首帧，"
    "不支持尾帧/音效），画幅由首帧图决定，最高 1080p。Kuaishou Kling V3 Turbo fast image-to-video.",
    ["kling-v3-turbo-image-to-video"],
    prompt_required=False,
    prompt_tooltip=KLING_PROMPT_TIP,
    params=[KLING_DUR, KLING_Q_TURBO],
    image_slots=[KLING_FIRST],
    default_timeout=1200,
))

nodes.append(node(
    "EvoLink_KlingO3T2V", "EvoLink Kling O3 Text-to-Video (Official)", "video",
    "EvoLink 官方节点：快手可灵 Kling O3 文生视频，3~15 秒任意时长，最高 4K，支持音效。"
    "Kuaishou Kling O3 text-to-video.",
    ["kling-o3-text-to-video"],
    prompt_tooltip=KLING_PROMPT_TIP,
    params=[KLING_DUR, KLING_AR, KLING_Q_FULL, KLING_SOUND],
    default_timeout=1200,
))

nodes.append(node(
    "EvoLink_KlingO3I2V", "EvoLink Kling O3 Image-to-Video (Official)", "video",
    "EvoLink 官方节点：快手可灵 Kling O3 图生视频（首帧必接，尾帧可选，可指定画幅），"
    "3~15 秒任意时长，最高 4K，支持音效。Kuaishou Kling O3 image-to-video (first/last frame).",
    ["kling-o3-image-to-video"],
    prompt_required=False,
    prompt_tooltip=KLING_PROMPT_TIP,
    params=[KLING_DUR, KLING_AR, KLING_Q_FULL, KLING_SOUND],
    image_slots=[KLING_FIRST, KLING_LAST],
    default_timeout=1200,
))

# ---------- 视频：Seedance 2.5 / 2.0 / 2.0 Fast / 2.0 Mini × T2V / I2V ----------

SD_AR_FULL = p_enum("aspect_ratio",
                    ["adaptive", "16:9", "9:16", "1:1", "4:3", "3:4", "21:9"],
                    "adaptive", "画幅；adaptive 由模型自动选择")
SD_AUDIO = p_bool("generate_audio", True, "生成同步音频（不额外收费）")
SD_SLOTS = [
    {"name": "first_frame", "api_param": "image_urls", "required": True,
     "tooltip": "首帧图（必接）"},
    {"name": "last_frame", "api_param": "image_urls",
     "tooltip": "尾帧图（可选，接上即首尾帧模式；比例不同时自动对齐首帧）"},
]
SD25_DUR = p_int("duration", 5, 4, 30, "视频时长（秒），4~30 任意整数，按时长计费")
SD25_AUTO_DUR = p_bool("auto_duration", False,
                       "智能时长：开启后忽略 duration，由模型在 4~30 秒内自选，按实际输出时长计费",
                       true_sets={"duration": -1})
SD20_DUR = p_int("duration", 5, 4, 15, "视频时长（秒），4~15 任意整数，按时长计费")
SD_T2V_TIP = "镜头/画面描述，支持中文（建议 500 字内）。"
SD_I2V_TIP = "镜头/画面描述，支持中文（建议 500 字内）。接 first_frame 出图生视频，可再接 last_frame 做首尾帧。"

nodes.append(node(
    "EvoLink_Seedance25T2V", "EvoLink Seedance 2.5 Text-to-Video (Official)", "video",
    "EvoLink 官方节点：字节豆包 Seedance 2.5 文生视频，4~30 秒或智能时长，"
    "同步音频不加价。ByteDance Seedance 2.5 text-to-video.",
    ["seedance-2.5-text-to-video"],
    prompt_tooltip=SD_T2V_TIP,
    params=[SD25_DUR, SD25_AUTO_DUR,
            p_enum("quality", ["720p", "480p", "1080p"], "720p", "分辨率；480p 为低价档"),
            SD_AR_FULL, SD_AUDIO],
    default_timeout=1800,
))

nodes.append(node(
    "EvoLink_Seedance25I2V", "EvoLink Seedance 2.5 Image-to-Video (Official)", "video",
    "EvoLink 官方节点：字节豆包 Seedance 2.5 图生视频（首帧必接，尾帧可选即首尾帧模式），"
    "画幅跟随首帧图，4~30 秒或智能时长，同步音频不加价。ByteDance Seedance 2.5 image-to-video.",
    ["seedance-2.5-image-to-video"],
    prompt_tooltip=SD_I2V_TIP,
    params=[SD25_DUR, SD25_AUTO_DUR,
            p_enum("quality", ["720p", "480p", "1080p"], "720p", "分辨率；480p 为低价档"),
            SD_AUDIO],
    image_slots=SD_SLOTS, max_images=2, default_timeout=1800,
))

nodes.append(node(
    "EvoLink_Seedance20T2V", "EvoLink Seedance 2.0 Text-to-Video (Official)", "video",
    "EvoLink 官方节点：字节豆包 Seedance 2.0 文生视频，4~15 秒，最高 4K，同步音频不加价。"
    "ByteDance Seedance 2.0 text-to-video.",
    ["seedance-2.0-text-to-video"],
    prompt_tooltip=SD_T2V_TIP,
    params=[SD20_DUR,
            p_enum("quality", ["720p", "480p", "1080p", "4k"], "720p", "分辨率"),
            SD_AR_FULL, SD_AUDIO],
    default_timeout=1800,
))

nodes.append(node(
    "EvoLink_Seedance20I2V", "EvoLink Seedance 2.0 Image-to-Video (Official)", "video",
    "EvoLink 官方节点：字节豆包 Seedance 2.0 图生视频（首帧必接，尾帧可选即首尾帧模式），"
    "4~15 秒，最高 4K，同步音频不加价。ByteDance Seedance 2.0 image-to-video.",
    ["seedance-2.0-image-to-video"],
    prompt_tooltip=SD_I2V_TIP,
    params=[SD20_DUR,
            p_enum("quality", ["720p", "480p", "1080p", "4k"], "720p", "分辨率"),
            SD_AR_FULL, SD_AUDIO],
    image_slots=SD_SLOTS, max_images=2, default_timeout=1800,
))

nodes.append(node(
    "EvoLink_Seedance20FastT2V", "EvoLink Seedance 2.0 Fast Text-to-Video (Official)", "video",
    "EvoLink 官方节点：字节豆包 Seedance 2.0 Fast 文生视频——更快更便宜的档位，4~15 秒，"
    "最高 720p，同步音频不加价。ByteDance Seedance 2.0 Fast text-to-video.",
    ["seedance-2.0-fast-text-to-video"],
    prompt_tooltip=SD_T2V_TIP,
    params=[SD20_DUR,
            p_enum("quality", ["720p", "480p"], "720p", "分辨率；fast 档最高 720p"),
            SD_AR_FULL, SD_AUDIO],
    default_timeout=1800,
))

nodes.append(node(
    "EvoLink_Seedance20FastI2V", "EvoLink Seedance 2.0 Fast Image-to-Video (Official)", "video",
    "EvoLink 官方节点：字节豆包 Seedance 2.0 Fast 图生视频——更快更便宜的档位（首帧必接，"
    "尾帧可选），画幅跟随首帧图，4~15 秒，最高 720p。ByteDance Seedance 2.0 Fast image-to-video.",
    ["seedance-2.0-fast-image-to-video"],
    prompt_tooltip=SD_I2V_TIP,
    params=[SD20_DUR,
            p_enum("quality", ["720p", "480p"], "720p", "分辨率；fast 档最高 720p"),
            SD_AR_FULL, SD_AUDIO],
    image_slots=SD_SLOTS, max_images=2, default_timeout=1800,
))

nodes.append(node(
    "EvoLink_Seedance20MiniT2V", "EvoLink Seedance 2.0 Mini Text-to-Video (Official)", "video",
    "EvoLink 官方节点：字节豆包 Seedance 2.0 Mini 文生视频——最便宜的视频档位，适合批量与调试，"
    "4~15 秒，最高 720p，同步音频不加价。ByteDance Seedance 2.0 Mini budget text-to-video.",
    ["seedance-2.0-mini-text-to-video"],
    prompt_tooltip=SD_T2V_TIP,
    params=[SD20_DUR,
            p_enum("quality", ["720p", "480p"], "720p", "分辨率；480p 更便宜"),
            SD_AR_FULL, SD_AUDIO],
    default_timeout=1800,
))

nodes.append(node(
    "EvoLink_Seedance20MiniI2V", "EvoLink Seedance 2.0 Mini Image-to-Video (Official)", "video",
    "EvoLink 官方节点：字节豆包 Seedance 2.0 Mini 图生视频——最便宜的视频档位（首帧必接，"
    "尾帧可选），画幅跟随首帧图，4~15 秒，最高 720p。ByteDance Seedance 2.0 Mini budget image-to-video.",
    ["seedance-2.0-mini-image-to-video"],
    prompt_tooltip=SD_I2V_TIP,
    params=[SD20_DUR,
            p_enum("quality", ["720p", "480p"], "720p", "分辨率；480p 更便宜"),
            SD_AR_FULL, SD_AUDIO],
    image_slots=SD_SLOTS, max_images=2, default_timeout=1800,
))

# ---------- 视频：Wan 3.0（standard/prime 输入一致共用下拉）× T2V / I2V / Reference ----------

WAN_DUR = p_int("duration", 5, 2, 30, "视频时长（秒），2~30 任意整数，按时长计费")
WAN_AUTO_DUR = p_bool("auto_duration", False,
                      "智能时长：开启后忽略 duration，模型按 prompt 与素材自选时长"
                      "（按 30s 上限预扣、按实际输出结算退差额）",
                      true_sets={"duration": -1})
WAN_Q = p_enum("quality", ["720p", "480p", "1080p"], "720p",
               "480p=计费基准最便宜；720p 约 2 倍；1080p 约 4 倍")
WAN_AR = p_enum("aspect_ratio", ["adaptive", "16:9", "9:16", "1:1", "4:3", "3:4"],
                "adaptive", "adaptive：按素材与 prompt 自动推荐")
WAN_AUDIO = p_bool("generate_audio", True, "输出是否含音轨（开关同价）")
WAN_SEED = p_int("seed", 0, 0, 2147483647, "0=随机；固定可复现结果", skip_value=0)
WAN_PARAMS = [WAN_DUR, WAN_AUTO_DUR, WAN_Q, WAN_AR, WAN_AUDIO, WAN_SEED]

nodes.append(node(
    "EvoLink_Wan30T2V", "EvoLink Wan 3.0 Text-to-Video (Official)", "video",
    "EvoLink 官方节点：阿里通义万相 Wan 3.0 / 3.0 Prime 文生视频，智能时长可选（按实际输出结算），"
    "480p 起步低价档。Alibaba Wan 3.0 text-to-video.",
    ["wan3.0-text-to-video", "wan3.0-prime-text-to-video"],
    prompt_tooltip="镜头/画面描述，支持中文，最长 20000 字符。",
    params=WAN_PARAMS, extra_json_param=True, default_timeout=1800,
))

nodes.append(node(
    "EvoLink_Wan30I2V", "EvoLink Wan 3.0 Image-to-Video (Official)", "video",
    "EvoLink 官方节点：阿里通义万相 Wan 3.0 / 3.0 Prime 首尾帧图生视频（首帧必接，尾帧可选），"
    "智能时长可选，480p 起步低价档。Alibaba Wan 3.0 image-to-video (first/last frame).",
    ["wan3.0-image-to-video", "wan3.0-prime-image-to-video"],
    prompt_required=False,
    prompt_tooltip="镜头/画面描述，支持中文，最长 20000 字符。",
    params=WAN_PARAMS, extra_json_param=True,
    image_slots=[
        {"name": "first_frame", "api_param": "image_start", "single": True, "required": True,
         "tooltip": "首帧图（必接）；240~8000px，比例 1:8~8:1"},
        {"name": "last_frame", "api_param": "image_end", "single": True,
         "tooltip": "尾帧图（可选，须与首帧同用）"},
    ],
    default_timeout=1800,
))

nodes.append(node(
    "EvoLink_Wan30Ref", "EvoLink Wan 3.0 Reference-to-Video (Official)", "video",
    "EvoLink 官方节点：阿里通义万相 Wan 3.0 / 3.0 Prime 多模态参考生视频"
    "（图+视频+音频混合参考，视频/音频素材经 extra_params 的 video_urls/audio_urls 传入），"
    "prompt 里用「图1」「视频1」引用素材。Alibaba Wan 3.0 reference-to-video.",
    ["wan3.0-reference-video", "wan3.0-prime-reference-video"],
    prompt_tooltip="镜头/画面描述，支持中文，最长 20000 字符。用「图1」「视频1」引用素材。",
    params=WAN_PARAMS, extra_json_param=True,
    image_slots=[
        {"name": "reference_image1", "api_param": "image_urls",
         "tooltip": "参考图 1（prompt 里写「图1」引用；单主体单图）"},
        {"name": "reference_image2", "api_param": "image_urls",
         "tooltip": "参考图 2（可选，最多 10 张，其余可经 extra_params 的 image_urls 传）"},
    ],
    max_images=10, default_timeout=1800,
))

# ---------- 视频：Grok Imagine（2026-08-27 新增批次） ----------

GROK_V_TIP = "镜头/画面描述。"
GROK_MODE = p_enum("mode", ["normal", "fun", "spicy"], "normal",
                   "生成风格：normal 常规 / fun 趣味 / spicy 大胆")

nodes.append(node(
    "EvoLink_GrokVideo15", "EvoLink Grok Imagine Video 1.5 (Official)", "video",
    "EvoLink 官方节点：xAI Grok Imagine Video 1.5——一个模型三种玩法：不接图=文生视频，"
    "接 1 张=首帧图生视频，接 2~7 张=参考图生视频。1~15 秒，最高 1080p。"
    "xAI Grok Imagine Video 1.5 text/image/reference-to-video.",
    ["grok-imagine-video-1.5-preview"],
    prompt_tooltip=GROK_V_TIP,
    params=[
        p_int("duration", 6, 1, 15, "视频时长（秒），1~15 任意整数，按时长计费"),
        p_enum("quality", ["480p", "720p", "1080p"], "480p", "分辨率；480p 最便宜"),
        p_enum("aspect_ratio", ["auto", "16:9", "9:16", "1:1", "3:2", "2:3"], "auto",
               "画幅；接图时由图决定"),
    ],
    image_slots=[
        {"name": "image1", "api_param": "image_urls",
         "tooltip": "不接=文生视频；1 张=首帧；2 张以上=参考图（最多 7 张）"},
        {"name": "image2", "api_param": "image_urls", "tooltip": "参考图 2（可选）"},
        {"name": "image3", "api_param": "image_urls", "tooltip": "参考图 3（可选）"},
    ],
    url_text_param="image_urls", max_images=7, default_timeout=1200,
))

nodes.append(node(
    "EvoLink_GrokVideoT2V", "EvoLink Grok Imagine Text-to-Video (Official)", "video",
    "EvoLink 官方节点：xAI Grok Imagine 文生视频，6~30 秒，normal/fun/spicy 三种风格。"
    "xAI Grok Imagine text-to-video.",
    ["grok-imagine-text-to-video-beta"],
    prompt_tooltip=GROK_V_TIP,
    params=[
        p_int("duration", 6, 6, 30, "视频时长（秒），6~30 任意整数，按时长计费"),
        GROK_MODE,
        p_enum("aspect_ratio", ["16:9", "9:16", "1:1", "3:2", "2:3"], "16:9", "画幅比例"),
        p_enum("quality", ["480p", "720p"], "480p", "分辨率"),
    ],
    default_timeout=1200,
))

nodes.append(node(
    "EvoLink_GrokVideoI2V", "EvoLink Grok Imagine Image-to-Video (Official)", "video",
    "EvoLink 官方节点：xAI Grok Imagine 图生视频（首图必接，最多 7 张参考），6~30 秒，"
    "normal/fun/spicy 三种风格。xAI Grok Imagine image-to-video.",
    ["grok-imagine-image-to-video-beta"],
    prompt_tooltip=GROK_V_TIP,
    params=[
        p_int("duration", 6, 6, 30, "视频时长（秒），6~30 任意整数，按时长计费"),
        GROK_MODE,
        p_enum("aspect_ratio", ["16:9", "9:16", "1:1", "3:2", "2:3"], "16:9", "画幅比例"),
        p_enum("quality", ["480p", "720p"], "480p", "分辨率"),
    ],
    image_slots=[
        {"name": "image1", "api_param": "image_urls", "required": True,
         "tooltip": "首帧/参考图（必接，最多 7 张）"},
        {"name": "image2", "api_param": "image_urls", "tooltip": "参考图 2（可选）"},
        {"name": "image3", "api_param": "image_urls", "tooltip": "参考图 3（可选）"},
    ],
    url_text_param="image_urls", max_images=7, default_timeout=1200,
))

# ---------- 视频：MiniMax Hailuo 2.3 ----------

HAILUO_PARAMS = [
    p_enum("quality", ["768p", "1080p"], "768p", "分辨率"),
    p_enum("duration", [6, 10], 6, "视频时长（秒）"),
    p_bool("prompt_optimizer", True, "自动优化 prompt；要精确控制时关闭", nest="model_params"),
    p_bool("fast_pretreatment", False, "快速预处理，缩短优化耗时", skip_value=False,
           nest="model_params"),
]

nodes.append(node(
    "EvoLink_Hailuo23", "EvoLink MiniMax Hailuo 2.3 (Official)", "video",
    "EvoLink 官方节点：MiniMax 海螺 Hailuo 2.3 文生视频、图生视频（接 first_frame 即图生），"
    "动作表现力强，6/10 秒，最高 1080p。MiniMax Hailuo 2.3 text/image-to-video.",
    ["MiniMax-Hailuo-2.3"],
    prompt_tooltip="镜头/画面描述（含运镜指令），支持中文。",
    params=HAILUO_PARAMS,
    image_slots=[{"name": "first_frame", "api_param": "image_urls",
                  "tooltip": "首帧图（可选，接上即图生视频）"}],
    max_images=1, default_timeout=1200,
))

nodes.append(node(
    "EvoLink_Hailuo23Fast", "EvoLink MiniMax Hailuo 2.3 Fast (Official)", "video",
    "EvoLink 官方节点：MiniMax 海螺 Hailuo 2.3 Fast 图生视频——更快更便宜的档位"
    "（首帧必接），6/10 秒，最高 1080p。MiniMax Hailuo 2.3 Fast fast image-to-video.",
    ["MiniMax-Hailuo-2.3-Fast"],
    prompt_required=False,
    prompt_tooltip="镜头/画面描述（可选），支持中文。",
    params=HAILUO_PARAMS,
    image_slots=[{"name": "first_frame", "api_param": "image_urls", "required": True,
                  "tooltip": "首帧图（必接）"}],
    max_images=1, default_timeout=1200,
))

# ---------- 视频：Google Gemini Omni Flash ----------

GEMINI_OMNI_PARAMS = [
    p_int("duration", 10, 3, 10, "视频时长（秒），3~10 任意整数"),
    p_enum("aspect_ratio", ["16:9", "9:16", "auto"], "16:9", "画幅比例"),
]
GEMINI_OMNI_TIP = "镜头/画面描述，支持中文。"

nodes.append(node(
    "EvoLink_GeminiOmniT2V", "EvoLink Gemini Omni Flash Text-to-Video (Official)", "video",
    "EvoLink 官方节点：Google Gemini Omni Flash 文生视频，3~10 秒。"
    "Google Gemini Omni Flash text-to-video.",
    ["gemini-omni-flash-text-to-video"],
    prompt_tooltip=GEMINI_OMNI_TIP,
    params=GEMINI_OMNI_PARAMS, default_timeout=1200,
))

nodes.append(node(
    "EvoLink_GeminiOmniI2V", "EvoLink Gemini Omni Flash Image-to-Video (Official)", "video",
    "EvoLink 官方节点：Google Gemini Omni Flash 图生视频（首帧必接），3~10 秒。"
    "Google Gemini Omni Flash image-to-video.",
    ["gemini-omni-flash-image-to-video"],
    prompt_tooltip=GEMINI_OMNI_TIP,
    params=GEMINI_OMNI_PARAMS,
    image_slots=[{"name": "first_frame", "api_param": "image_urls", "required": True,
                  "tooltip": "首帧图（必接）"}],
    max_images=1, default_timeout=1200,
))

nodes.append(node(
    "EvoLink_GeminiOmniRef", "EvoLink Gemini Omni Flash Reference-to-Video (Official)", "video",
    "EvoLink 官方节点：Google Gemini Omni Flash 参考图生视频（最多 6 张，保持主体一致），"
    "3~10 秒。Google Gemini Omni Flash reference-to-video.",
    ["gemini-omni-flash-reference-to-video"],
    prompt_tooltip=GEMINI_OMNI_TIP,
    params=GEMINI_OMNI_PARAMS,
    image_slots=[
        {"name": "reference_image1", "api_param": "image_urls", "required": True,
         "tooltip": "参考图 1（必接，最多 6 张）"},
        {"name": "reference_image2", "api_param": "image_urls", "tooltip": "参考图 2（可选）"},
        {"name": "reference_image3", "api_param": "image_urls", "tooltip": "参考图 3（可选）"},
    ],
    url_text_param="image_urls", max_images=6, default_timeout=1200,
))

nodes.append(node(
    "EvoLink_GeminiOmniEdit", "EvoLink Gemini Omni Flash Video Edit (Official)", "video",
    "EvoLink 官方节点：Google Gemini Omni Flash 视频编辑——对输入视频改主体/风格/局部。"
    "视频 URL 可直接接上游生成节点的 result_urls 输出。Google Gemini Omni Flash video editing.",
    ["gemini-omni-flash-video-edit"],
    prompt_tooltip="编辑指令，支持中文（如「把背景换成雪山」）。",
    params=[
        p_str("video_url", "", "要编辑的视频 URL（必填），可接上游节点的 result_urls 输出",
              api_name="video_urls", url_list=True, max_items=1, required=True,
              multiline=True),
    ],
    default_timeout=1800,
))

# ---------- 视频：Seedance 2.5 参考 / 编辑 / 延长 ----------

SD25_VIDEO_URLS = p_str(
    "video_urls", "",
    "参考视频 URL，每行一个（最多 10 条，2~30 秒），可接上游节点的 result_urls 输出",
    url_list=True, max_items=10, multiline=True)
SD25_AUDIO_URLS = p_str(
    "audio_urls", "",
    "参考音频 URL，每行一个（最多 10 条，2~30 秒）",
    url_list=True, max_items=10, multiline=True)
SD25_Q = p_enum("quality", ["720p", "480p", "1080p"], "720p", "分辨率；480p 为低价档")

nodes.append(node(
    "EvoLink_Seedance25Ref", "EvoLink Seedance 2.5 Reference-to-Video (Official)", "video",
    "EvoLink 官方节点：字节豆包 Seedance 2.5 多模态参考生视频——图（≤30）+视频（≤10）+"
    "音频（≤10）混合参考，至少给一种素材，4~30 秒。ByteDance Seedance 2.5 reference-to-video.",
    ["seedance-2.5-reference-to-video"],
    prompt_tooltip="镜头/画面描述，可引用参考素材（支持中文）。至少接一张图或填一条视频/音频 URL。",
    params=[
        p_int("duration", 5, 4, 30, "视频时长（秒），4~30 任意整数，按时长计费"),
        SD25_Q, SD_AR_FULL, SD_AUDIO, SD25_VIDEO_URLS, SD25_AUDIO_URLS,
    ],
    image_slots=ref_slots(4, "参考图 1（可选，最多 30 张）"),
    url_text_param="image_urls", max_images=30, default_timeout=1800,
))

nodes.append(node(
    "EvoLink_Seedance25Edit", "EvoLink Seedance 2.5 Video Edit (Official)", "video",
    "EvoLink 官方节点：字节豆包 Seedance 2.5 视频编辑——换主体/增删物体/重绘风格，"
    "输出时长跟随原片。视频 URL 可直接接上游生成节点的 result_urls 输出。"
    "ByteDance Seedance 2.5 video editing.",
    ["seedance-2.5-video-edit"],
    prompt_tooltip="编辑指令（必填），如「Edit the video: 去掉背景音乐，主体换成柴犬」。",
    params=[
        p_str("video_urls", "",
              "要编辑的视频 URL（必填，每行一个，最多 10 条，4~30 秒），"
              "可接上游节点的 result_urls 输出",
              url_list=True, max_items=10, required=True, multiline=True),
        SD25_Q, SD_AUDIO, SD25_AUDIO_URLS,
    ],
    image_slots=ref_slots(2, "参考图 1（可选，最多 30 张）"),
    url_text_param="image_urls", max_images=30, default_timeout=1800,
))

nodes.append(node(
    "EvoLink_Seedance25Extend", "EvoLink Seedance 2.5 Video Extend (Official)", "video",
    "EvoLink 官方节点：字节豆包 Seedance 2.5 视频延长——把输入视频向前/向后续写 4~30 秒。"
    "视频 URL 可直接接上游生成节点的 result_urls 输出。ByteDance Seedance 2.5 video extend.",
    ["seedance-2.5-video-extend"],
    prompt_tooltip="延长指令（必填），如「Extend @video1 backward, 人物走出画面」。",
    params=[
        p_str("video_urls", "",
              "要延长的视频 URL（必填，每行一个，最多 10 条，2~30 秒），"
              "可接上游节点的 result_urls 输出",
              url_list=True, max_items=10, required=True, multiline=True),
        p_int("duration", 5, 4, 30, "延长时长（秒），4~30 任意整数，按时长计费"),
        SD25_Q, SD_AUDIO, SD25_AUDIO_URLS,
    ],
    image_slots=ref_slots(2, "参考图 1（可选，最多 30 张）"),
    url_text_param="image_urls", max_images=30, default_timeout=1800,
))

# ---------- 视频：Kling 参考 / 编辑 / 运动控制 ----------

KLING_KEEP_SOUND = p_bool("keep_original_sound", True, "保留原视频声音")
KLING_Q_O3 = p_enum("quality", ["720p", "1080p"], "720p", "分辨率")

nodes.append(node(
    "EvoLink_KlingO3Ref", "EvoLink Kling O3 Reference-to-Video (Official)", "video",
    "EvoLink 官方节点：快手可灵 Kling O3 参考视频生视频——提取参考视频的风格与运动特征"
    "生成新视频，可搭配参考图。视频 URL 可接上游节点的 result_urls 输出。"
    "Kuaishou Kling O3 reference-to-video.",
    ["kling-o3-reference-to-video"],
    prompt_tooltip="镜头/画面描述（必填），支持中文，最长 2500 字符。",
    params=[
        p_str("video_url", "", "参考视频 URL（必填），可接上游节点的 result_urls 输出",
              required=True, multiline=True),
        p_int("duration", 5, 3, 10, "视频时长（秒），3~10 任意整数"),
        p_enum("aspect_ratio", ["16:9", "9:16", "1:1"], "16:9", "画幅比例"),
        KLING_Q_O3, KLING_KEEP_SOUND,
    ],
    image_slots=[
        {"name": "reference_image1", "api_param": "image_urls", "tooltip": "参考图 1（可选）"},
        {"name": "reference_image2", "api_param": "image_urls", "tooltip": "参考图 2（可选）"},
    ],
    default_timeout=1200,
))

nodes.append(node(
    "EvoLink_KlingO3Edit", "EvoLink Kling O3 Video Edit (Official)", "video",
    "EvoLink 官方节点：快手可灵 Kling O3 视频编辑——用文字指令/参考图修改原视频，"
    "输出时长与画幅跟随原片。视频 URL 可接上游节点的 result_urls 输出。"
    "Kuaishou Kling O3 video editing.",
    ["kling-o3-video-edit"],
    prompt_required=False,
    prompt_tooltip="编辑指令（支持中文），如「把外套换成红色」。",
    params=[
        p_str("video_url", "", "要编辑的视频 URL（必填），可接上游节点的 result_urls 输出",
              required=True, multiline=True),
        KLING_Q_O3, KLING_KEEP_SOUND,
    ],
    image_slots=[
        {"name": "reference_image1", "api_param": "image_urls", "tooltip": "参考图 1（可选）"},
        {"name": "reference_image2", "api_param": "image_urls", "tooltip": "参考图 2（可选）"},
    ],
    default_timeout=1200,
))

nodes.append(node(
    "EvoLink_KlingMotion", "EvoLink Kling V3 Motion Control (Official)", "video",
    "EvoLink 官方节点：快手可灵 Kling V3 运动控制——从参考视频提取动作轨迹，"
    "套用到参考图中的人物/物体上生成新视频。视频 URL 可接上游节点的 result_urls 输出。"
    "Kuaishou Kling V3 motion control (reference image + motion video).",
    ["kling-v3-motion-control"],
    prompt_required=False,
    prompt_tooltip="画面描述（可选），支持中文。",
    params=[
        p_str("video_urls", "", "参考动作视频 URL（必填），可接上游节点的 result_urls 输出",
              url_list=True, max_items=1, required=True, multiline=True),
        p_enum("character_orientation", ["image", "video"], "image",
               "人物朝向跟随：image=跟参考图（≤10 秒）/ video=跟参考视频（≤30 秒）",
               nest="model_params"),
        KLING_Q_O3,
    ],
    image_slots=[
        {"name": "reference_image1", "api_param": "image_urls", "required": True,
         "tooltip": "参考图（必接）：要被驱动的人物/物体"},
    ],
    max_images=1, default_timeout=1200,
))

# ---------- 视频：Topaz 超分 ----------

nodes.append(node(
    "EvoLink_TopazUpscale", "EvoLink Topaz Video Upscale (Official)", "video",
    "EvoLink 官方节点：Topaz 视频超分/画质增强——1x 仅增强、2x/4x 放大分辨率，"
    "接上游生成节点的 result_urls 输出即可做后处理链。Topaz AI video upscaling & enhancement.",
    ["topaz-video-upscale"],
    prompt_required=False,
    prompt_tooltip="无需填写（Topaz 为画质处理，不看 prompt）。",
    params=[
        p_str("video_urls", "", "要超分的视频 URL（必填），可接上游节点的 result_urls 输出",
              url_list=True, max_items=1, required=True, multiline=True),
        p_enum("upscale_factor", ["2", "1", "4"], "2",
               "放大倍数：1=仅增强不放大 / 2=2 倍 / 4=4 倍（影响计费）",
               nest="model_params"),
    ],
    default_timeout=1800,
))

# ---------- 视频：通用节点（含 beta 渠道与全部变体，原样保留） ----------

nodes.append(node(
    "EvoLink_Video", "EvoLink Video (All Models)", "video",
    "EvoLink 通用视频节点：一个节点调用全部视频模型（含各 beta 低价渠道与 video-edit/extend 等变体）。"
    "模型专属参数（video_urls、sound、seed 等）用 extra_params 以 JSON 传入，"
    "接口文档见 evolink.ai/docs。Kling/Wan 图生视频请用专属节点（首帧参数不同）。",
    ["sora-2-preview", "sora-2-pro-preview", "veo-3.1-generate-preview",
     "veo-3.1-fast-generate-preview", "veo3.1-pro-beta", "veo3.1-fast-beta",
     "kling-v3-text-to-video", "kling-v3-turbo-text-to-video", "kling-o3-text-to-video",
     "seedance-2.5-text-to-video", "seedance-2.5-image-to-video",
     "seedance-2.5-reference-to-video", "seedance-2.5-video-edit",
     "seedance-2.5-video-extend", "seedance-2.0-text-to-video",
     "seedance-2.0-image-to-video", "seedance-2.0-fast-text-to-video",
     "seedance-2.0-fast-image-to-video", "seedance-2.0-mini-text-to-video",
     "seedance-2.0-mini-image-to-video", "seedance-2.0-reference-to-video",
     "seedance-2.0-fast-reference-to-video", "seedance-2.0-mini-reference-to-video",
     "wan3.0-text-to-video", "wan3.0-image-to-video",
     "wan3.0-reference-video", "wan3.0-prime-text-to-video", "wan3.0-prime-image-to-video",
     "wan3.0-prime-reference-video", "grok-imagine-video-1.5-preview",
     "grok-imagine-text-to-video-beta", "grok-imagine-image-to-video-beta",
     "MiniMax-Hailuo-2.3", "MiniMax-Hailuo-2.3-Fast",
     "gemini-omni-flash-text-to-video", "gemini-omni-flash-image-to-video",
     "gemini-omni-flash-reference-to-video", "gemini-omni-flash-video-edit",
     "kling-o3-reference-to-video", "kling-o3-video-edit", "kling-v3-motion-control",
     "topaz-video-upscale"],
    default_model="seedance-2.5-text-to-video",
    prompt_tooltip="镜头/画面描述，支持中文。",
    params=[
        p_int("duration", 0, -1, 30,
              "视频时长（秒）；0=用模型默认；-1=Seedance 2.5/Wan 自动时长。各模型允许范围见 evolink.ai/docs",
              skip_value=0),
        p_enum("quality", ["auto", "480p", "720p", "1080p", "4k"], "auto",
               "分辨率；auto=用模型默认。各模型支持面不同，选不支持的档会报错", skip_value="auto"),
        p_str("aspect_ratio", "", "留空=用模型默认；可填 16:9 / 9:16 / 1:1 / adaptive 等（支持面随模型而异）"),
    ],
    extra_json_param=True,
    image_slots=[
        {"name": "image1", "api_param": "image_urls", "tooltip": "参考图/首帧（是否支持随模型而异）"},
        {"name": "image2", "api_param": "image_urls", "tooltip": "参考图 2/尾帧（可选）"},
    ],
    url_text_param="image_urls", max_images=9, default_timeout=1800,
))

registry = {
    "updated": "2026-08-27",
    "source": "evolink.ai/docs api-manual（image-series / video-series 逐页核实）；"
              "2026-08-27 按变体拆分：一个 API model 变体一个节点，beta 渠道收进通用节点",
    "nodes": nodes,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)
    f.write("\n")

ids = [n["node_id"] for n in nodes]
assert len(ids) == len(set(ids)), "node_id 重复"
print(f"OK: {len(nodes)} 个节点写入 {OUT}")
for n in nodes:
    req = [s["name"] for s in n.get("image_slots", []) if s.get("required")]
    print(f"  {n['node_id']:32s} models={len(n['models'])} required_slots={req}")
