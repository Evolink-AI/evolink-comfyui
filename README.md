# ComfyUI-EvoLink（EvoLink 官方节点）

[English](README_EN.md) ｜ 官方教程：https://evolink.ai/docs/cn/integration-guide/comfyui

在 ComfyUI 里直接调用 [EvoLink](https://evolink.ai) 云端模型出图（gpt-image-2 文生图 / 图生图），**本地无需显卡**。

- ✅ **图生图零门槛**：「加载图像」连到 `image1` 就行 —— 本地图自动经 EvoLink 官方通道上传（72 小时自动删除），**不需要注册任何第三方图床**
- ✅ **Key 只留在本机**：首次在节点框填写后自动保存，之后留空即可，不会跟着工作流 JSON 被分享出去
- ✅ **中文全程可用**：prompt 支持中文，报错提示是中文
- ✅ **省钱**：参数不变重复运行走 ComfyUI 缓存不重复扣费；失败/超时任务不扣费

> **旧版用户请注意**：本插件替代已下架的旧版 Evolink-AI 官方节点，恢复了"加载图像直连图生图"的用法。
> 如果你在用社区版 `torans/ComfyUI_EvoLink`（图生图需要 imgbb 图床），两者可共存，迁移对照见[下文](#从旧版社区版迁移)。

---

## 安装

**方式一：ComfyUI-Manager（推荐，上架后可用）**
Manager → Custom Nodes Manager → 搜索 `EvoLink` → 安装 → **完全重启 ComfyUI**。

**方式二：git**

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/deeplearning-goethe/comfyui-evolink.git
```

**方式三：下载 ZIP**
[Code → Download ZIP](https://github.com/deeplearning-goethe/comfyui-evolink) → 解压后把文件夹放进 `ComfyUI/custom_nodes/`。
⚠️ 检查一层：打开 `custom_nodes/comfyui-evolink/` 应**直接看到** `__init__.py`；如果里面还套了一层同名文件夹，把内层移出来。

依赖只有 `requests`（ComfyUI 环境一般已自带），装完后**完全重启 ComfyUI**（关掉控制台窗口重开，不是只刷新浏览器）。

## 快速开始

1. 获取 API Key：https://evolink.ai/dashboard/keys （`sk-` 开头）
2. 画布空白处双击 → 搜 `EvoLink` → 添加 **EvoLink GPT Image 2 (Official)**
3. 填 `api_key`（只需第一次）和 `prompt`（支持中文）
4. 从 `image` 输出口拖线 → 选「预览图像」或「保存图像」（**必连，否则看不到图**）
5. 点运行，约 35 秒出图（quality=low）

**图生图（3 步）**：添加「加载图像」→ 连到 `image1` → `prompt` 写修改要求 → 运行。
最多 16 张参考图：`image1~4` 口与 `image_urls` 文本框（每行一个公网 URL）可混用。

现成工作流见 [example_workflows/](example_workflows/)，拖进画布即用。

## 参数说明

| 参数 | 说明 |
|---|---|
| `prompt` | 画面描述 / 修改要求，支持中文，最长 32000 字符 |
| `model` | `gpt-image-2` / `gpt-image-2-beta` |
| `size` | `auto`（默认）/ 比例 `1:1`、`16:9` 等 / 像素 `1024x1024` |
| `resolution` | `1K` / `2K` / `4K`（size 为比例或 auto 时生效） |
| `quality` | `low` / `medium` / `high`，越高越贵，**调试建议 low** |
| `n` | 一次生成几张（1–10） |
| `api_key` | 首次填写自动存本机，之后留空；也支持环境变量 `EVOLINK_API_KEY` |
| `image1~4` | 参考图口，接「加载图像」即图生图 |
| `image_urls` | 进阶：已有公网 URL 每行贴一个 |
| `timeout_seconds` | 最长等待（默认 300s），超时失败不扣费 |

输出：`image`（结果图，已自动下载落地）、`task_id`（对账/报障凭证）、`status_info`（本次任务摘要）。

## Key 安全

- Key 等同账户余额，**不要**发到聊天窗口、截图或公开仓库；
- 分享工作流前清空节点上的 `api_key` 框（留空时 key 从本机 `evolink_config.json` 或环境变量读取，不会进入工作流 JSON）；
- 怀疑泄露立即到 [dashboard/keys](https://evolink.ai/dashboard/keys) 删除重建。

## 计费

按量计费无订阅。每笔任务可在 [任务日志](https://evolink.ai/zh/dashboard/logs) 按 `task_id` 查询状态与扣费；失败/超时任务自动退回积分；参数不变重复运行是 ComfyUI 缓存复用，不发起新请求、不扣费。

## 从旧版/社区版迁移

| 你在用 | 迁移方法 |
|---|---|
| 旧版官方节点（已下架，带图像输入口） | 用法一致：加载图像连 `image1` 即可，直接换装本插件 |
| 社区版 `torans/ComfyUI_EvoLink` | 参数同名（prompt/model/size/resolution/quality/n/image_urls）；`Evolink Image Input` + imgbb key → 不再需要，图直接连 `image1`；`poll_interval`/`max_polls` → 合并为 `timeout_seconds`。两插件可共存，无需先卸载 |

## 常见问题

- **搜不到节点**：确认插件目录位置正确、没有嵌套两层文件夹、已完全重启；启动日志里搜 `EvoLink` 看有无红色报错。
- **任务完成但看不到图**：`image` 输出没连「预览图像/保存图像」，补连后再运行（走缓存不重复扣费）。
- **401**：Key 无效或已删除；**402**：余额不足；**429**：请求过频稍后再试。
- **内容审核失败**：调整提示词或参考图后重试，失败不扣费。
- 更多见官方教程：https://evolink.ai/docs/cn/integration-guide/comfyui

## Roadmap

- [ ] Nano Banana（gemini 系列）/ Seedream 节点
- [ ] 余额查询节点（EvoLink Credits）
- [ ] mask 局部重绘（API 已支持 `mask_url`，实测后上线）
- [ ] 视频模型节点（Veo / Sora / Kling）

## License

[MIT](LICENSE) © 2026 EvoLink ｜ 技术支持：support@evolink.ai
