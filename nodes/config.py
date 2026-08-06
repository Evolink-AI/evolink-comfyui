"""EvoLink API Key 三级解析与本地持久化。

优先级：节点输入框 > 本地配置文件 evolink_config.json > 环境变量 EVOLINK_API_KEY。
节点框首次填写后自动保存到配置文件，之后可留空 —— key 因此不必留在会被
导出/分享的 workflow JSON 里。
"""

import json
import os

# 插件根目录（本文件位于 <plugin>/nodes/ 下）
PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PLUGIN_DIR, "evolink_config.json")
ENV_KEY = "EVOLINK_API_KEY"

NO_KEY_MESSAGE = (
    "未找到 EvoLink API Key。请任选一种方式配置：\n"
    "  1) 在节点的 api_key 输入框填入（首次填写后自动保存到本机，之后可留空）；\n"
    "  2) 设置环境变量 EVOLINK_API_KEY。\n"
    "获取 Key：https://evolink.ai/dashboard/keys\n"
    "(No EvoLink API key found. Fill the node's api_key field once, "
    "or set the EVOLINK_API_KEY environment variable.)"
)


def _read_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_api_key(api_key):
    """把 key 写入本地配置文件（幂等）。失败不阻断生成，仅打印提示。"""
    cfg = _read_config()
    if cfg.get("api_key") == api_key:
        return
    cfg["api_key"] = api_key
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        try:
            os.chmod(CONFIG_PATH, 0o600)
        except OSError:
            pass
        print("[EvoLink] API Key 已保存到本机 evolink_config.json，下次节点框可留空。")
    except OSError as e:
        print(f"[EvoLink] 警告：API Key 保存失败（{e}），本次仍可正常使用。")


def resolve_api_key(node_value=""):
    """按三级优先级解析 key；节点框有值时顺手持久化。找不到则抛中文错误。"""
    key = (node_value or "").strip()
    if key:
        save_api_key(key)
        return key
    key = str(_read_config().get("api_key", "") or "").strip()
    if key:
        return key
    key = os.environ.get(ENV_KEY, "").strip()
    if key:
        return key
    raise ValueError(NO_KEY_MESSAGE)
