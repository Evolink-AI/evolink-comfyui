# ComfyUI-EvoLink (Official EvoLink Nodes)

[中文](README.md) | Docs: https://evolink.ai/docs/en/integration-guide/comfyui

Generate images inside ComfyUI with [EvoLink](https://evolink.ai) cloud models
(gpt-image-2, text-to-image & image-to-image). **No local GPU required.**

- ✅ **Zero-friction img2img**: connect "Load Image" to `image1` — local images are
  uploaded through EvoLink's official file channel (auto-deleted after 72h),
  **no third-party image hosting to sign up for**
- ✅ **Your key stays local**: saved to a local config file on first use, leave the
  field empty afterwards — it never travels inside shared workflow JSON
- ✅ **Friendly errors** and full CJK prompt support
- ✅ **Cost-aware**: unchanged parameters re-run from ComfyUI's cache (no re-charge);
  failed / timed-out tasks are never charged

## Install

**ComfyUI-Manager** (recommended once listed): search `EvoLink` → install → fully restart.

**git**

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/deeplearning-goethe/comfyui-evolink.git
```

**ZIP**: download, unzip into `ComfyUI/custom_nodes/`, make sure `__init__.py`
sits directly inside `custom_nodes/comfyui-evolink/` (no nested folder), then fully restart.

The only dependency is `requests`.

## Quick start

1. Get an API key (`sk-...`): https://evolink.ai/dashboard/keys
2. Double-click the canvas → search `EvoLink` → add **EvoLink GPT Image 2 (Official)**
3. Fill `api_key` (first time only) and `prompt`
4. Connect the `image` output to a Preview/Save Image node (**required to see results**)
5. Queue — ~35 s at `quality=low`

**Image-to-image**: Load Image → `image1` → describe the edit in `prompt` → run.
Up to 16 reference images via `image1~4` sockets and/or `image_urls` (one URL per line).

Drag-and-drop examples: [example_workflows/](example_workflows/)

## Nodes

| Node | Purpose |
|---|---|
| `EvoLink GPT Image 2 (Official)` | text2img / img2img generation, returns `image`, `task_id`, `status_info` |
| `EvoLink Upload Image (Official)` | advanced: local images → official channel → URL text |

## Key safety

Leave the `api_key` field empty after first use (it is read from the local
`evolink_config.json` or the `EVOLINK_API_KEY` env var) so it never ends up in a
shared workflow. Rotate the key at https://evolink.ai/dashboard/keys if leaked.

## Migrating

- **Old official nodes** (delisted repo): same usage — Load Image → `image1`.
- **Community `torans/ComfyUI_EvoLink`**: same parameter names; the imgbb-based
  `Evolink Image Input` node is no longer needed; `poll_interval`/`max_polls`
  became `timeout_seconds`. Both plugins can coexist.

## License

[MIT](LICENSE) © 2026 EvoLink | support@evolink.ai
