# EvoLink Upload Image

Uploads local images through **EvoLink's official file channel** and outputs public
URLs as text (one per line).

- Regular image-to-image does **not** need this node — connect your image straight
  to `image1` of "EvoLink GPT Image 2" instead;
- Use this node when composing advanced workflows;
- Uploaded files are auto-deleted after 72 hours; default quota is 2000 files;
- No third-party image hosting (no imgbb registration) involved.

`api_key` behaves the same as on the generation node: saved locally on first use,
leave empty afterwards.
