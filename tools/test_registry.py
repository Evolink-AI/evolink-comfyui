"""离线验证拆分后的注册表 + 工厂：不联网、桩掉重依赖。"""
import sys
import types

for name in ("torch", "numpy", "requests", "PIL", "PIL.Image", "comfy_api",
             "comfy_api.latest", "comfy", "comfy.utils"):
    sys.modules.setdefault(name, types.ModuleType(name))

import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import importlib
factory = importlib.import_module("nodes.factory")

classes, names = factory.build_nodes()
assert len(classes) == 53, f"期望 53 个工厂节点，实际 {len(classes)}"
assert len(names) == 53

registry = factory.load_registry()
specs = {s["node_id"]: s for s in registry["nodes"]}

for node_id, cls in classes.items():
    spec = specs[node_id]
    it = cls.INPUT_TYPES()
    req, opt = it["required"], it["optional"]
    # prompt 恒有；单模型无 model 下拉，多模型有
    assert "prompt" in req
    if len(spec["models"]) > 1:
        assert "model" in req, f"{node_id}: 多模型应有 model 下拉"
        assert req["model"][1]["default"] == spec["default_model"]
    else:
        assert "model" not in req, f"{node_id}: 单模型不应有 model 下拉"
    # 必接图口进 required，可选进 optional
    for slot in spec.get("image_slots", []):
        target = req if slot.get("required") else opt
        assert slot["name"] in target, f"{node_id}: 槽位 {slot['name']} 位置错误"
        assert target[slot["name"]][0] == "IMAGE"
    assert "api_key" in opt and "timeout_seconds" in opt
    # 枚举参数默认值必须在选项里
    for p in spec.get("params", []):
        if p["widget"] == "enum":
            assert p["default"] in p["values"], f"{node_id}: {p['name']} 默认值不在选项中"

# payload 组装抽查
def build(node_id, model=None, prompt="test", kwargs=None, urls=None):
    spec = specs[node_id]
    model = model or spec["default_model"]
    notes = []
    return factory._build_payload(spec, model, prompt, kwargs or {}, urls or {}, notes), notes

p, _ = build("EvoLink_Veo31I2V", "veo-3.1-fast-generate-preview",
             kwargs={"quality": "1080p", "seed": 0, "generate_audio": True},
             urls={"image_urls": ["u1", "u2"]})
assert p["generation_type"] == "FIRST&LAST", p
assert p["model"] == "veo-3.1-fast-generate-preview"
assert p["quality"] == "1080p" and "seed" not in p and p["generate_audio"] is True
assert p["image_urls"] == ["u1", "u2"]

p, _ = build("EvoLink_Veo31Ref", urls={"image_urls": ["r1"]})
assert p["generation_type"] == "REFERENCE"

p, _ = build("EvoLink_KlingV3I2V", kwargs={"duration": 7, "sound": "on"},
             urls={"image_start": "s", "image_end": "e"})
assert p["duration"] == 7 and p["sound"] == "on"
assert p["image_start"] == "s" and p["image_end"] == "e"

p, _ = build("EvoLink_NanoBanana2",
             kwargs={"quality": "4K", "thinking_level": "high", "web_search": False})
assert p["model"] == "gemini-3.1-flash-image-preview", "官方渠道须映射 gemini ID"
assert p["model_params"] == {"thinking_level": "high"}

p, _ = build("EvoLink_NanoBananaLite", kwargs={"size": "1:1"})
assert p["model"] == "gemini-3.1-flash-lite-image"
assert "quality" not in p, "Lite 固定 1K，不应有 quality"

p, _ = build("EvoLink_Seedance25I2V", kwargs={"duration": 8, "generate_audio": True},
             urls={"image_urls": ["f", "l"]})
assert p["duration"] == 8 and "aspect_ratio" not in p

# auto_duration 开关：开=duration 覆写为 -1 且自身不进请求体；关=不影响
p, _ = build("EvoLink_Seedance25T2V", kwargs={"duration": 10, "auto_duration": True})
assert p["duration"] == -1 and "auto_duration" not in p
p, _ = build("EvoLink_Seedance25T2V", kwargs={"duration": 10, "auto_duration": False})
assert p["duration"] == 10 and "auto_duration" not in p
p, _ = build("EvoLink_Wan30I2V", kwargs={"duration": 5, "auto_duration": True},
             urls={"image_start": "s"})
assert p["duration"] == -1

# 文档范围核对：duration 控件范围与档位不越界
def param(node_id, name):
    return next(pp for pp in specs[node_id]["params"] if pp["name"] == name)

for nid in ("EvoLink_Seedance25T2V", "EvoLink_Seedance25I2V"):
    d = param(nid, "duration")
    assert (d["min"], d["max"]) == (4, 30), nid
for nid in ("EvoLink_Wan30T2V", "EvoLink_Wan30I2V", "EvoLink_Wan30Ref"):
    d = param(nid, "duration")
    assert (d["min"], d["max"]) == (2, 30), nid
for nid in ("EvoLink_KlingV3T2V", "EvoLink_KlingTurboI2V", "EvoLink_KlingO3I2V"):
    d = param(nid, "duration")
    assert (d["min"], d["max"]) == (3, 15), nid
for nid in ("EvoLink_Seedance20FastI2V", "EvoLink_Seedance20MiniI2V"):
    assert param(nid, "aspect_ratio")["values"][0] == "adaptive", nid
assert set(param("EvoLink_Seedance20FastT2V", "quality")["values"]) == {"720p", "480p"}
assert set(param("EvoLink_KlingTurboT2V", "quality")["values"]) == {"720p", "1080p"}
assert set(param("EvoLink_Sora2Pro", "quality")["values"]) == {"720p", "1080p"}
assert param("EvoLink_Veo31T2V", "duration")["values"] == [8, 4, 6]

# --- 2026-08-27 新增批次 ---
# url_list：多行 URL 文本 -> 数组；截断超限
p, notes = build("EvoLink_Seedance25Ref",
                 kwargs={"duration": 5, "quality": "720p", "aspect_ratio": "adaptive",
                         "generate_audio": True,
                         "video_urls": "http://a/v1.mp4\nhttp://a/v2.mp4\nhttp://a/v1.mp4\n",
                         "audio_urls": ""})
assert p["video_urls"] == ["http://a/v1.mp4", "http://a/v2.mp4"], p
assert "audio_urls" not in p

# required 参数：缺失时报错，给了就通过；api_name 映射（gemini video_url -> video_urls）
try:
    build("EvoLink_Seedance25Edit", kwargs={"quality": "720p", "generate_audio": True})
    raise AssertionError("video_urls 缺失应报错")
except factory.EvoLinkError:
    pass
p, _ = build("EvoLink_GeminiOmniEdit", kwargs={"video_url": "http://a/v.mp4"})
assert p["video_urls"] == ["http://a/v.mp4"] and "video_url" not in p

# Kling O3 参考视频是单字符串参数；运动控制 model_params 嵌套 + 必填视频
p, _ = build("EvoLink_KlingO3Ref",
             kwargs={"video_url": "http://a/ref.mp4", "duration": 5,
                     "aspect_ratio": "16:9", "quality": "720p",
                     "keep_original_sound": True})
assert p["video_url"] == "http://a/ref.mp4"
p, _ = build("EvoLink_KlingMotion",
             kwargs={"video_urls": "http://a/m.mp4", "character_orientation": "video",
                     "quality": "720p"},
             urls={"image_urls": ["img"]})
assert p["video_urls"] == ["http://a/m.mp4"]
assert p["model_params"] == {"character_orientation": "video"}

# Topaz：倍数走 model_params，无 prompt 时请求体不带 prompt
p, _ = build("EvoLink_TopazUpscale", prompt="",
             kwargs={"video_urls": "http://a/v.mp4", "upscale_factor": "4"})
assert p["model_params"] == {"upscale_factor": "4"} and "prompt" not in p

# Hailuo：model_params 嵌套 + duration 枚举；Fast 必接图
p, _ = build("EvoLink_Hailuo23",
             kwargs={"quality": "768p", "duration": 6, "prompt_optimizer": False,
                     "fast_pretreatment": False})
assert p["model_params"] == {"prompt_optimizer": False}
assert param("EvoLink_Hailuo23", "duration")["values"] == [6, 10]

# 新增文档核对：范围/档位
assert (param("EvoLink_GrokVideo15", "duration")["min"],
        param("EvoLink_GrokVideo15", "duration")["max"]) == (1, 15)
assert (param("EvoLink_GrokVideoT2V", "duration")["min"],
        param("EvoLink_GrokVideoT2V", "duration")["max"]) == (6, 30)
assert (param("EvoLink_GeminiOmniT2V", "duration")["min"],
        param("EvoLink_GeminiOmniT2V", "duration")["max"]) == (3, 10)
assert (param("EvoLink_KlingO3Ref", "duration")["min"],
        param("EvoLink_KlingO3Ref", "duration")["max"]) == (3, 10)
assert set(param("EvoLink_QwenImage3", "quality")["values"]) == {"1K", "2K"}
assert param("EvoLink_QwenImage3", "n")["max"] == 6
assert set(param("EvoLink_Hailuo23", "quality")["values"]) == {"768p", "1080p"}
# 视频编辑不暴露 duration（API 仅支持 -1 跟随原片）
assert all(pp["name"] != "duration" for pp in specs["EvoLink_Seedance25Edit"]["params"])
assert all(pp["name"] != "duration" for pp in specs["EvoLink_KlingO3Edit"]["params"])

p, _ = build("EvoLink_Wan30T2V", "wan3.0-prime-text-to-video",
             kwargs={"duration": 5, "quality": "480p", "aspect_ratio": "adaptive",
                     "generate_audio": True, "seed": 0,
                     "extra_params": '{"style": "anime"}'})
assert p["model"] == "wan3.0-prime-text-to-video" and p["style"] == "anime"
assert "seed" not in p

p, _ = build("EvoLink_Seedream5Pro", kwargs={"quality": "1.5K", "watermark": False, "n": 5})
assert p["quality"] == "1.5K" and "watermark" not in p
assert "n" not in p, "5.0 Pro 无 n 参数（kwargs 里多余键不应写入）"

# 变体覆盖完整性：拆分节点 + 通用节点合起来须覆盖原 15 节点的全部 model ID
old_models = {
    "nano-banana-2", "nano-banana-pro", "nano-banana-2-lite", "nano-banana-2-beta",
    "nano-banana-pro-beta", "nano-banana-2-lite-beta", "nano-banana-beta",
    "doubao-seedream-5.0-pro", "doubao-seedream-5.0-lite", "doubao-seedream-4.5",
    "doubao-seedream-4.0", "gpt-image-2", "gpt-image-2-beta", "grok-imagine-image-2.0",
    "sora-2-preview", "sora-2-pro-preview",
    "veo-3.1-generate-preview", "veo-3.1-fast-generate-preview", "veo3.1-pro-beta",
    "veo3.1-fast-beta",
    "kling-v3-text-to-video", "kling-v3-image-to-video", "kling-v3-turbo-text-to-video",
    "kling-v3-turbo-image-to-video", "kling-o3-text-to-video", "kling-o3-image-to-video",
    "seedance-2.5-text-to-video", "seedance-2.5-image-to-video",
    "seedance-2.0-text-to-video", "seedance-2.0-image-to-video",
    "seedance-2.0-fast-text-to-video", "seedance-2.0-fast-image-to-video",
    "seedance-2.0-mini-text-to-video", "seedance-2.0-mini-image-to-video",
    "wan3.0-text-to-video", "wan3.0-image-to-video", "wan3.0-reference-video",
    "wan3.0-prime-text-to-video", "wan3.0-prime-image-to-video",
    "wan3.0-prime-reference-video",
}
new_models = set()
for s in registry["nodes"]:
    new_models.update(s["models"])
missing = old_models - new_models
# kling turbo/o3/v3 i2v 原本只在专属 Kling 节点里；确认没丢
assert not missing, f"拆分后丢失的模型: {missing}"

print(f"OK: {len(classes)} 节点全部通过；模型覆盖 {len(new_models)} 个 ID，无丢失")
