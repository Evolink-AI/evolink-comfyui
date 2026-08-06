# EvoLink GPT Image 2

Generate images with EvoLink's cloud-hosted gpt-image-2 model. No local GPU required.

## Text to image

Fill in `prompt` → connect the `image` output to a Preview Image / Save Image node → run.

## Image to image (3 steps)

1. Add a "Load Image" node and pick a local picture;
2. Connect its image output to this node's `image1`;
3. Describe the edit in `prompt` → run.

Local images are uploaded through **EvoLink's official file channel** (auto-deleted
after 72 hours, no third-party image hosting involved). Up to 16 reference images:
`image1~image4` sockets and the `image_urls` text box (one public URL per line) can be mixed.

## API Key

`api_key` is saved to a local config file the first time you fill it in; leave it
empty afterwards. **Clear the field before sharing a workflow.** The environment
variable `EVOLINK_API_KEY` is also supported. Get a key: https://evolink.ai/dashboard/keys

## Cost notes

- Higher `quality` costs more; use `low` while testing;
- Re-running with unchanged parameters hits ComfyUI's cache — you are **not** charged again;
- Failed / timed-out tasks are not charged. Check per-task usage at https://evolink.ai/dashboard/logs
