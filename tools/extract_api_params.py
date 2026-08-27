"""从 evolink.ai 文档页（OpenAPI YAML 嵌在 markdown 里）提取参数约束。

用法：
  python3 tools/extract_api_params.py <页面URL或本地md文件> [...]
  python3 tools/extract_api_params.py --list [关键词]     # 列出 llms.txt 里的接口页
  python3 tools/extract_api_params.py --audit             # 核对注册表全部模型 vs 线上文档

输出每页的：endpoint、model 枚举、required 列表、各参数的 enum/default/min/max/
maxItems/范围描述/-1 特殊值——用于和 data/evolink_registry.json 逐项比对。
上架新节点前必须先跑本脚本，禁止凭记忆写参数。
"""
import json
import re
import sys
import urllib.request

LLMS_TXT = "https://evolink.ai/docs/llms.txt"

RESPONSE_FIELDS = {
    "model", "prompt", "callback_url", "object", "type", "estimated_time",
    "billing_rule", "credits_reserved", "credits_used", "id", "status", "progress",
    "created_at", "results", "usage", "error", "code", "message", "video_duration",
    "completed_at", "updated_at", "task_id", "created", "task_info", "can_cancel",
    "user_group", "content", "200", "400", "401", "402", "403", "429", "500",
}


def fetch(url_or_path):
    if url_or_path.startswith("http"):
        with urllib.request.urlopen(url_or_path, timeout=30) as r:
            return r.read().decode("utf-8")
    with open(url_or_path, encoding="utf-8") as f:
        return f.read()


def extract(text):
    out = {"endpoint": None, "models": None, "required": None, "params": {}}
    ep = re.findall(r"(/v1/(?:videos|images|audio|chat)/[a-z-]+)\b", text)
    if ep:
        out["endpoint"] = ep[0]
    m = re.search(r"^        model:\n(?:^          .*\n)*?^          enum:\n"
                  r"((?:^            - .*\n)+)", text, re.M)
    if m:
        out["models"] = [l.strip("- ").strip() for l in m.group(1).strip().splitlines()]
    else:
        m = re.search(r"^        model:\n(?:^          .*\n)*?^          default: (.+)$",
                      text, re.M)
        if m:
            out["models"] = [m.group(1).strip()]
    r = re.search(r"^      required:\n((?:^        - .*\n)+)", text, re.M)
    if r:
        out["required"] = [l.strip("- ").strip() for l in r.group(1).strip().splitlines()]
    for pm in re.finditer(r"^        '?(\w+)'?:\n((?:^          .*\n|^\n)+)", text, re.M):
        name, body = pm.group(1), pm.group(2)
        if name in RESPONSE_FIELDS:
            continue
        info = {}
        em = re.search(r"^          enum:\n((?:^            - .*\n)+)", body, re.M)
        if em:
            info["enum"] = [l.strip("- ").strip().strip("'\"")
                            for l in em.group(1).strip().splitlines()]
        for pat, key in ((r"^          default: (.+)$", "default"),
                         (r"minimum: (.+)", "min"), (r"maximum: (.+)", "max"),
                         (r"maxItems: (.+)", "maxItems"), (r"^          type: (\w+)", "type")):
            m2 = re.search(pat, body, re.M)
            if m2:
                info[key] = m2.group(1).strip().strip("'\"")
        rng = re.findall(r"`(-?\d+)`\s*[–~-]\s*`?(-?\d+)`?", body)
        if rng:
            info["ranges"] = rng[:2]
        if re.search(r"`-1`", body):
            info["has_minus1"] = True
        # 嵌套 model_params 的子字段
        if name == "model_params":
            subs = re.findall(r"^            (\w+):\n", body, re.M)
            if subs:
                info["nested"] = subs
        info.pop("type", None) if not info else None
        out["params"][name] = info
    return out


def list_pages(keyword=""):
    text = fetch(LLMS_TXT)
    urls = sorted(set(re.findall(
        r"https://evolink\.ai/docs/en/api-manual/[a-z0-9./-]+\.md", text)))
    for u in urls:
        if keyword.lower() in u.lower():
            print(u)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    if args[0] == "--list":
        list_pages(args[1] if len(args) > 1 else "")
        return
    if args[0] == "--audit":
        print("audit 模式：请先用 --list 找到注册表各模型对应页面，逐页 extract 后与 "
              "data/evolink_registry.json 比对（模型 ID、enum、min/max、required、-1 特殊值）。")
        return
    for target in args:
        info = extract(fetch(target))
        print(f"### {target}")
        print(f"  endpoint: {info['endpoint']}  models: {info['models']}")
        print(f"  required: {info['required']}")
        for k, v in info["params"].items():
            if v:
                print(f"    {k}: {json.dumps(v, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
