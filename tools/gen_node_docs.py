"""为节点生成 web/docs/<node_id>/{zh,en}.md 帮助文档（从注册表 description/params 生成）。

用法：
  python3 tools/gen_node_docs.py                 # 只补缺失目录的节点
  python3 tools/gen_node_docs.py EvoLink_Xxx ... # 指定节点（覆盖重写）
"""
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def render(spec):
    zh_desc = spec["description"]
    en_desc = re.split(r"。(?=[A-Z])", zh_desc)[-1] if "。" in zh_desc else zh_desc
    params = "\n".join(f"- `{p['name']}`：{p.get('tooltip', '')}"
                       for p in spec.get("params", []))
    slots = "\n".join(f"- `{s['name']}`：{s.get('tooltip', '')}"
                      + ("（必接）" if s.get("required") else "")
                      for s in spec.get("image_slots", []))
    zh = f"# {spec['display_name']}\n\n{zh_desc}\n\n## 参数\n{params or '（无额外参数）'}\n"
    if slots:
        zh += f"\n## 图像输入\n{slots}\n"
    zh += (f"\n## 输出\n`{spec['output']}`（结果，已下载落地）、`task_id`、`status_info`（摘要）、"
           "`result_urls`（原始链接每行一个，24h 过期）、`response_json`"
           "（任务接口完整 JSON，供下游解析）。\n\n"
           "费用与任务详情：https://evolink.ai/zh/dashboard/logs ；"
           "接口文档：https://evolink.ai/docs\n")
    en = (f"# {spec['display_name']}\n\n{en_desc}\n\n"
          f"Outputs: `{spec['output']}` (downloaded result), `task_id`, `status_info`, "
          "`result_urls` (raw links, one per line, 24h expiry), `response_json` "
          "(full task API response for downstream parsing).\n\n"
          "Billing & task details: https://evolink.ai/dashboard/logs — "
          "API docs: https://evolink.ai/docs\n")
    return zh, en


def main():
    registry = json.load(open(os.path.join(ROOT, "data", "evolink_registry.json"),
                              encoding="utf-8"))
    specs = {s["node_id"]: s for s in registry["nodes"]}
    targets = sys.argv[1:] or [
        nid for nid in specs
        if not os.path.isdir(os.path.join(ROOT, "web", "docs", nid))
    ]
    for nid in targets:
        spec = specs[nid]
        d = os.path.join(ROOT, "web", "docs", nid)
        os.makedirs(d, exist_ok=True)
        zh, en = render(spec)
        open(os.path.join(d, "zh.md"), "w", encoding="utf-8").write(zh)
        open(os.path.join(d, "en.md"), "w", encoding="utf-8").write(en)
        print(f"docs: {nid}")
    print(f"共处理 {len(targets)} 个节点")


if __name__ == "__main__":
    main()
