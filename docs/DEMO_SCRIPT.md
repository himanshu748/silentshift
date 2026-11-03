# Catch meaning before delivery

A two-minute, silent product walkthrough for an integration engineer. The story follows the decision they need to make: keep a contract-breaking event held, while allowing a change that has approved evidence.

This is an **edited walkthrough of recorded native cases**, not a continuous recording or a fresh model run. All events are synthetic and the destination is the IRIS-persisted simulator. That scope stays on screen. No generated narration or music is used; Deepgram is the only authorized provider if narration is added later.

| Time | The operator's story | Actual material |
|---|---|---|
| 0:00–0:09 | A valid message can carry the wrong meaning. SilentShift checks that meaning before delivery. | The real product landing page and recorded workbench. |
| 0:09–0:22 | A payment declares `12550` in minor units where its approved contract declares `125.50` in major units. | Recorded currency investigation B. Preserve the original values and scale labels. |
| 0:22–0:33 | A plausible conversion does not authorize changing a contract. The verified contradiction stays held. | A closer view of B's actual evidence and deterministic policy; zero destination receipts in the native record. |
| 0:33–0:47 | A supplier's `20 CASE` is held against `240 EA` in A. A current approved amendment changes the answer in C. | The frozen A/C comparison, then C's actual approved-reference lineage. Separate case labels make the edit explicit. |
| 0:47–0:58 | C matches the approved amendment effective at event time. It reaches the simulator exactly once. | Recorded C delivery and reference snapshot. Receipt count comes from the native trace evidence. |
| 0:58–1:14 | The agent reads the current message, approved contracts and related records. Deterministic policy retains release authority. | Actual Agent capture, with tool counts established by the corresponding native trace record. No fabricated tool animation. |
| 1:14–1:31 | The explanation stays attached to the transaction, so an operator can inspect how the recommendation was reached. | The actual expanded Timeline event for C's native session 52. Whole invocation/tool spans; no per-provider-round claim. |
| 1:31–1:45 | Five frozen synthetic cases produced five controlled final outcomes in the recorded November 2 fresh-volume repeat. | Actual Evaluations screen. The rule-only baseline also scored 5/5; no AI accuracy uplift or general accuracy claim. |
| 1:45–2:00 | Catch meaning before delivery. Inspect the source and run the same native production locally. | Product page, [public source](https://github.com/himanshu748/silentshift), and the real doctor/bootstrap commands. Build 154 was tested; the authorized kit is separate. |

## Produce the edited walkthrough

The composition preserves the Signal / Substance palette and uses the app's installed Manrope and IBM Plex Mono font files. It crops and scales real screenshots; it never draws an imitation workbench. Each source file, crop, caption and hash is recorded in the local manifest.

The script uses the **browser-video-recording skill's bundled renderer** rather than replacing it. Its default path is `~/.codex/skills/browser-video-recording/scripts/render_browser_demo.py`; use `--renderer /path/to/render_browser_demo.py` if that skill is installed elsewhere. Python dependencies are isolated by the commands below; ffmpeg and ffprobe must be available on PATH. Brotli decodes the installed app's WOFF2 font files. No app dependency changes are needed.

Prepare and inspect the composed stills without starting video encoding:

```bash
uv run --no-project --with pillow --with fonttools --with brotli \
  python scripts/render_product_demo.py --prepare-only
```

The checked-in configuration names the actual captures used for this edit. They remain in ignored evidence storage unless separately selected for public release. To substitute later **actual** captures and the verified source URL:

```bash
uv run --no-project --with pillow --with fonttools --with brotli \
  python scripts/render_product_demo.py --prepare-only \
  --unit-shot evidence/browser/demo/unit-quarantine-full.png \
  --agent-shot evidence/browser/demo/approved-agent-full.png \
  --timeline-shot evidence/browser/demo/approved-timeline-full.png \
  --evaluation-shot evidence/browser/demo/evaluation-full.png \
  --source-url https://github.com/himanshu748/silentshift
```

Substitutions preserve the explicit crop rectangle in `config/demo/product.json`; edit that rectangle if a later capture has a different layout. The script rejects crops outside the source. The Timeline capture must refer to the same approved case as `docs/evidence/traceability.json`; never splice another case into a claimed continuous trace.

After reviewing the stills and when native verification is idle, run the same invocation without `--prepare-only`. The output defaults to `evidence/local/silentshift-product-walkthrough.mp4`, with a matching SRT caption file and verification manifest. Composition frames and renderer configuration go to ignored `work/product-demo/`. Do not run encoding concurrently with the local model or native safety checks on the constrained demo host.

The deliberate override is **1920×1080 at 30fps**, silent H.264 with fast-start metadata. This edited evidence walkthrough uses static framing and brief fades, with no animated cursor, staged clicks, zoom-follow or spatial motion. This keeps small interface text readable and avoids implying real-time interaction. It also keeps the artifact small enough for the demo machine's available storage. The primary skill's 4K/60fps/cursor defaults apply to interaction recordings; this output is labeled as an edited walkthrough.

The renderer writes a locally extracted mid-video thumbnail and `ffprobe` output. Confirm duration 120 seconds, 1920×1080, 30/1fps, no audio stream, correct captions and actual source frames before uploading. The SRT remains useful for accessible player captions in addition to the burned-in text.

## Upload copy

**Title:** SilentShift: catch wrong data before it leaves IRIS

An integration can accept a valid message while changing the meaning of a payment or order. SilentShift gives the integration engineer the evidence to hold a contract-breaking event and allow an approved change.

This walkthrough follows a declared currency-scale mismatch, compares an unapproved unit change with an effective amendment, and shows the native agent, deterministic release policy and transaction-linked trace. The core runs inside InterSystems IRIS.

Edited, silent walkthrough of recorded native cases. All data is synthetic; the destination is an IRIS simulator. The recorded November 2 fresh-volume repeat had five controlled outcomes across five frozen cases. The rule-only baseline also scored 5/5; no AI accuracy uplift is demonstrated.

Source and local setup: https://github.com/himanshu748/silentshift

## Publication gate

A completed local MP4 is an upload-ready artifact, not a YouTube publication or an awarded bonus. Add the actual public YouTube URL to Open Exchange only after upload and public playback are observed. Do not invent a hosted demo, source URL, completed native run, receipt, provider usage or contest award.
