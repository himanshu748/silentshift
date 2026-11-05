# Catch meaning before delivery

A 2:30 captioned product walkthrough for an integration engineer. The story holds
an unsupported quantity change, allows an approved amendment and follows the
operator's evidence through review and delivery.

This is an **edited walkthrough of recorded native cases**, not continuous
interaction or a fresh model run. All messages are synthetic and the destination
is an IRIS simulator. That scope stays on screen. No cursor clicks are staged.
The AAC track is silent; no generated narration or music is used.

| Time | Story | Actual material |
| --- | --- | --- |
| 0:00–0:08 | Valid transport can conceal wrong business meaning. | Recorded product landing page |
| 0:08–0:24 | `20 CASE` cannot replace `240 EA` without approved authority. | Actual quantity-mismatch evidence, with a closer crop of the values |
| 0:24–0:36 | Keep the critical order held before delivery. | Same recorded critical hold and deterministic policy |
| 0:36–0:53 | An effective amendment makes that incoming value legitimate. | Separate approved-amendment investigation; one simulator delivery |
| 0:53–1:10 | Similar history supplies context without release authority. | Actual Similar precedents view: source IDs, scores and native vectors |
| 1:10–1:26 | Follow each model exchange in the business case. | Native Visual Trace session 374; four actual provider request/response pairs |
| 1:26–1:41 | Give an eligible hold a human next step. | Recorded native Review worklist and selected task |
| 1:41–1:55 | Approve with a reason; preserve one receipt. | Actual approved review result, case 299A6FC4 |
| 1:55–2:09 | A ready file enters the same production and policy. | Actual PartnerFiles intake, native session 1610 |
| 2:09–2:18 | File recovery does not create another delivery. | Same native session at Destination; separate critical-file containment established in the adapter receipt |
| 2:18–2:30 | Inspect the source and reproduce the native workflow. | Source URL, documented setup and recorded product page |

The different case labels are deliberate. Provider session 374 is an earlier
recorded run; the later live four-tool run made two exchanges per case, while the
keyless recorded replay makes five. The video
does not splice the shots into a claim that one case visited every state.

## Artifact and upload copy

- [MP4](../evidence/video/silentshift-demo.mp4)
- [English SRT](../evidence/video/silentshift-demo.srt)
- [Source/crop/hash manifest](../evidence/video/silentshift-demo.json)
- [YouTube title, description, tags and clicks](YOUTUBE_UPLOAD.md)

The video is below 50 MB and is included in Git. It was published on November 4:
[watch the captioned demo](https://youtu.be/a4dOcqu89EA). Organizer bonus
acceptance remains unconfirmed.

## Reproduce the edit

All scene captures are tracked in the repository. The composition preserves the
Signal / Substance palette and uses the installed Manrope and IBM Plex Mono
fonts. Crops retain actual screenshot pixels; no replacement UI is drawn.

The Homebrew ffmpeg 8.1.2 binary expected missing `libx265.216.dylib`, while the
installed x265 library was ABI 217. Reinstalling the official Homebrew ffmpeg
package repaired ffmpeg/ffprobe (recorded version 9.0.2). No incompatible library
symlink was created. The encoder uses **libx264**, then copies that H.264 stream
into the final MP4 with AAC silence and an English `mov_text` caption track.

```sh
# Only if the installed ffmpeg/ffprobe cannot start:
HOMEBREW_NO_AUTO_UPDATE=1 HOMEBREW_NO_INSTALL_CLEANUP=1 brew reinstall ffmpeg
ffmpeg -version
ffprobe -version

npm --prefix web ci
uv run --no-project --with pillow --with fonttools --with brotli \
  python scripts/render_product_demo.py --prepare-only
uv run --no-project --with pillow --with fonttools --with brotli \
  python scripts/render_product_demo.py
```

The renderer uses the installed browser-video-recording skill's bundled
`render_browser_demo.py`; its default path is
`~/.codex/skills/browser-video-recording/scripts/render_browser_demo.py`. If the
skill lives elsewhere, pass `--renderer /absolute/path/render_browser_demo.py`.
The tracked [scene configuration](../config/demo/product.json) specifies all
source paths, crops, captions and timings. Intermediate frames and the picture
stream go to ignored `work/product-demo/`.

The output is **1920×1080, 30 fps, 150 seconds**, with static framing and short
fades. This overrides the skill's 4K/60 fps interaction-recording defaults for a
readable, compact evidence edit. No model calls or application changes occur.

## Verify before upload

```sh
ffprobe -v error -show_entries \
  stream=codec_name,codec_type,width,height,r_frame_rate,pix_fmt:format=duration,size \
  -of json evidence/video/silentshift-demo.mp4
ffmpeg -v error -i evidence/video/silentshift-demo.mp4 \
  -map 0:v:0 -map 0:a:0 -f null -
```

Expect H.264 / `yuv420p`, 1920×1080, 30/1 fps, AAC, English captions and 150 seconds.
The manifest records actual `ffprobe` results and SHA-256 hashes. Decoded samples
cover the hold, amendment, precedents, provider trace, review and file adapter.
The published video remains an explicitly historical edit of these recorded
cases. Later landing-page interactions, expanded provider metadata and keyless
replay are documented in the README; the film does not claim to demonstrate
those additions. Its hold, amendment, precedent, review and file-intake story
remains accurate. No replacement recording or upload was made in the November 5
consistency check.
