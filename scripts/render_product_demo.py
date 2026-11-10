#!/usr/bin/env python3
"""Compose actual product captures, then invoke the installed browser demo renderer.

This is an edited, captioned walkthrough. No interactions or model calls are staged.
Frames, hashes, captions and the exact render configuration remain inspectable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
CANVAS, SURFACE, TEXT, MUTED, MINT, BORDER = (
    "#0B1116", "#121C23", "#EBF3F5", "#A2B4BC", "#44D6B4", "#2B3D47"
)
SIZE = (1920, 1080)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value.resolve() if value.is_absolute() else (ROOT / value).resolve()


def source_name(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return path.name


def font_files(directory: Path) -> dict[str, Path]:
    sources = {
        "regular": (ROOT / "web/node_modules/@fontsource-variable/manrope/files/manrope-latin-wght-normal.woff2", 400),
        "heading": (ROOT / "web/node_modules/@fontsource-variable/manrope/files/manrope-latin-wght-normal.woff2", 600),
        "mono": (ROOT / "web/node_modules/@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff", None),
    }
    result: dict[str, Path] = {}
    for name, (source, weight) in sources.items():
        if not source.is_file():
            raise ValueError(f"Install web dependencies before composing: {source_name(source)}")
        target = directory / f"{name}-{digest(source)[:12]}.ttf"
        if target.is_file():
            result[name] = target
            continue
        font = TTFont(source)
        if weight is not None:
            font = instantiateVariableFont(font, {"wght": weight}, inplace=False)
        font.flavor = None
        font.save(target)
        result[name] = target
    return result


def draw_text(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], *, font: ImageFont.FreeTypeFont,
              width: int, fill: str = TEXT, spacing: int = 10, max_lines: int = 5) -> int:
    """Wrap at actual font measurements and reject clipped composition copy."""
    lines: list[str] = []
    for paragraph in text.splitlines():
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}".strip()
            if draw.textlength(candidate, font=font) > width:
                if not line:
                    raise ValueError(f"Word exceeds caption width: {word}")
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    if len(lines) > max_lines:
        raise ValueError(f"Composition copy needs {len(lines)} lines: {text}")
    line_height = font.size + spacing
    for index, line in enumerate(lines):
        draw.text((xy[0], xy[1] + index * line_height), line, font=font, fill=fill)
    return xy[1] + len(lines) * line_height


def screenshot(canvas: Image.Image, path: Path, crop: list[int], box: tuple[int, int, int, int]) -> None:
    with Image.open(path) as raw:
        if raw.format not in {"PNG", "JPEG", "WEBP"}:
            raise ValueError(f"Expected an actual raster browser capture: {source_name(path)}")
        left, top, right, bottom = crop
        if not (0 <= left < right <= raw.width and 0 <= top < bottom <= raw.height):
            raise ValueError(f"Crop outside capture: {source_name(path)} {crop}")
        image = raw.convert("RGB").crop(tuple(crop))
    width, height = box[2] - box[0], box[3] - box[1]
    # Contain rather than cover: every pixel inside the declared crop is visible.
    image = ImageOps.contain(image, (width, height), Image.Resampling.LANCZOS)
    x, y = box[0] + (width - image.width) // 2, box[1] + (height - image.height) // 2
    canvas.paste(image, (x, y))
    ImageDraw.Draw(canvas).rectangle((x - 1, y - 1, x + image.width, y + image.height), outline=BORDER, width=1)


def override_shot(scene: dict, value: str | None, label: str) -> None:
    if not value:
        return
    path = resolve(value)
    with Image.open(path) as capture:
        width, height = capture.size
    left, top, right, bottom = scene["crop"]
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError(f"New capture needs an explicit crop in --config: {source_name(path)}")
    scene.update(source=str(path), source_label=label)


def trace_facts(scenes: list[dict]) -> dict:
    path = ROOT / "docs/evidence/provider-calls.json"
    evidence = json.loads(path.read_text())
    case = next((case for case in evidence["success_cases"]["cases"] if case.get("scenario_id") == "approved-amendment"
                 and case.get("routing") == "DELIVERED" and case.get("delivery_count") == 1), None)
    if not case:
        raise ValueError("No recorded approved delivery in the reviewed trace evidence")
    requests = [m["call_id"] for m in case["provider_messages"] if m["event_kind"] == "provider_request"]
    responses = [m["call_id"] for m in case["provider_messages"] if m["event_kind"] == "provider_response"]
    count = len(requests)
    if count < 1 or len(set(requests)) != count or sorted(requests) != sorted(responses) or len(case["provider_messages"]) != count * 2 or not all(case["checks"].values()):
        raise ValueError("Recorded native provider request/response pairs are incomplete")
    scene = next(scene for scene in scenes if scene["id"] == "trace")
    scene["caption"] = f"Recorded native session {case['trace_id']}: {count} actual provider exchanges, each with its own request and response. Policy retains release authority."
    return {"source": source_name(path), "sha256": digest(path), "case_id": case["case_id"], "trace_id": case["trace_id"], "provider_exchanges": count}


def compose(scene: dict, fonts: dict[str, Path], scope: str, source_url: str | None) -> Image.Image:
    image = Image.new("RGB", SIZE, CANVAS)
    draw = ImageDraw.Draw(image)
    font = lambda role, size: ImageFont.truetype(str(fonts[role]), size)
    draw.text((72, 32), "SilentShift.", font=font("heading", 32), fill=TEXT)
    draw.text((72, 77), "Edited product walkthrough", font=font("regular", 19), fill=MUTED)
    chapter = scene["chapter"]
    chapter_width = draw.textlength(chapter, font=font("regular", 22))
    draw.text((1848 - chapter_width, 47), chapter, font=font("regular", 22), fill=MINT)
    draw.line((72, 116, 1848, 116), fill=BORDER)
    if scene["layout"] == "split":
        bottom = draw_text(draw, scene["headline"], (72, 178), font=font("heading", 55), width=535, max_lines=5, spacing=13)
        for fact in scene.get("facts", []):
            bottom = draw_text(draw, fact, (72, bottom + 28), font=font("mono", 29), width=535, fill=MINT, max_lines=2, spacing=5)
        screenshot(image, resolve(scene["source"]), scene["crop"], (662, 148, 1848, 848))
    elif scene["layout"] == "closing":
        draw_text(draw, scene["headline"], (72, 174), font=font("heading", 67), width=830, spacing=15, max_lines=3)
        draw_text(draw, "Native InterSystems IRIS\nAI Hub investigation\nDeterministic release policy", (72, 470), font=font("regular", 30), width=780, spacing=22, max_lines=3)
        if source_url:
            visible_url = source_url.removeprefix("https://")
            draw_text(draw, visible_url, (72, 675), font=font("mono", 26), width=850, fill=MINT, max_lines=2)
        else:
            draw.text((72, 675), "Source and setup: README.md", font=font("regular", 28), fill=MINT)
        draw_text(draw, "uv run --env-file .env python scripts/doctor.py\nuv run --env-file .env python scripts/bootstrap.py", (72, 755), font=font("mono", 20), width=850, fill=MUTED, spacing=14, max_lines=2)
        screenshot(image, resolve(scene["source"]), scene["crop"], (980, 175, 1848, 820))
    else:
        draw_text(draw, scene["headline"], (72, 143), font=font("heading", 46), width=1776, max_lines=2, spacing=10)
        screenshot(image, resolve(scene["source"]), scene["crop"], (72, 254, 1848, 846))
    draw.line((72, 876, 1848, 876), fill=BORDER)
    draw_text(draw, scene["caption"], (72, 895), font=font("heading", 29), width=1776, spacing=8, max_lines=2)
    draw_text(draw, scene["source_label"], (72, 980), font=font("regular", 20), width=1776, fill=MUTED, max_lines=1)
    draw.text((72, 1030), scope, font=font("regular", 19), fill=MUTED)
    return image


def srt_time(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/demo/product.json")
    parser.add_argument("--output", default="evidence/video/silentshift-demo.mp4")
    parser.add_argument("--work-dir", default="work/product-demo")
    parser.add_argument("--renderer", default="~/.codex/skills/browser-video-recording/scripts/render_browser_demo.py")
    parser.add_argument("--source-url")
    parser.add_argument("--unit-shot")
    parser.add_argument("--agent-shot")
    parser.add_argument("--timeline-shot")
    parser.add_argument("--evaluation-shot")
    parser.add_argument("--prepare-only", action="store_true", help="Write stills, captions and renderer config; do not encode")
    args = parser.parse_args()
    config_path, work, output = resolve(args.config), resolve(args.work_dir), resolve(args.output)
    config = json.loads(config_path.read_text())
    args.source_url = args.source_url or config.get("source_url")
    if args.source_url:
        parsed = urlparse(args.source_url)
        if parsed.scheme != "https" or parsed.hostname not in {"github.com", "gitlab.com"} or parsed.username or parsed.password or parsed.query or parsed.fragment:
            parser.error("Use the verified public HTTPS GitHub/GitLab repository URL without credentials or query parameters")
    if tuple(config["output_size"]) != SIZE or config["fps"] != 30 or not 120 <= config["duration"] <= 180:
        parser.error("Use 1920x1080 / 30fps and a duration from 120 through 180 seconds")
    scenes = config["scenes"]
    for index, scene in enumerate(scenes):
        expected = 0 if index == 0 else scenes[index - 1]["end"]
        if scene["start"] != expected or scene["end"] <= scene["start"]:
            parser.error("Scene intervals must be continuous and increasing")
    if scenes[-1]["end"] != config["duration"]:
        parser.error("Scene intervals must cover the complete duration")
    proof = trace_facts(scenes)
    by_id = {scene["id"]: scene for scene in scenes}
    override_shot(by_id["amendment"], args.unit_shot, "Actual case A; C's approved amendment shown in the next recorded case")
    if args.agent_shot:
        parser.error("The current edit uses the fourth-tool precedent view; update --config explicitly for other captures")
    override_shot(by_id["trace"], args.timeline_shot, f"Actual recorded Timeline view; native session {proof['trace_id']}")
    if args.evaluation_shot:
        parser.error("Update --config explicitly to add a recorded evaluation capture")
    work.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    fonts = font_files(work)
    inputs, shots = [], {}
    for scene in scenes:
        source = resolve(scene["source"])
        target = work / f"{scene['id']}.png"
        compose(scene, fonts, config["scope"], args.source_url).save(target)
        shots[scene["id"]] = str(target)
        inputs.append({"scene": scene["id"], "source": source_name(source), "source_sha256": digest(source),
                       "crop": scene["crop"], "frame_sha256": digest(target), "source_label": scene["source_label"]})
    # Transparent cursor + off-canvas key deliberately prevent fabricated interaction.
    cursor = work / "no-cursor.png"
    Image.new("RGBA", (1, 1), (0, 0, 0, 0)).save(cursor)
    render_config = {
        "duration": config["duration"], "fps": config["fps"], "output_size": list(SIZE), "source_size": list(SIZE),
        "cursor_asset": str(cursor), "cursor_hotspot": [0, 0], "cursor_scale": 1,
        "click_strength": 0, "rotation_strength_degrees": 0, "click_times": [],
        "shots": shots, "scene_starts": [[scene["start"], scene["id"], "fade"] for scene in scenes],
        "cursor_keys": [[0, -1000, -1000]], "camera_keys": [[0, 960, 540, 1.0]], "preset": "veryfast", "crf": 20,
    }
    render_path = work / "renderer-config.json"
    render_path.write_text(json.dumps(render_config, indent=2) + "\n")
    captions = "\n\n".join(f"{index + 1}\n{srt_time(scene['start'])} --> {srt_time(scene['end'])}\n{scene['headline']}\n{scene['caption']}" for index, scene in enumerate(scenes))
    output.with_suffix(".srt").write_text(captions + "\n")
    manifest = {"kind": "edited-screenshot-product-walkthrough", "scope": config["scope"], "duration": config["duration"],
                "fps": 30, "output_size": list(SIZE), "audio": "AAC silence; no generated narration or music", "source_url": args.source_url,
                "config_sha256": digest(config_path), "script_sha256": digest(Path(__file__)), "trace_proof": proof,
                "inputs": inputs, "rendered": False, "captions": [{key: scene[key] for key in ("id", "start", "end", "headline", "caption")} for scene in scenes]}
    manifest_path = output.with_suffix(".json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Prepared {len(scenes)} real-capture scenes: {source_name(work)}")
    if args.prepare_only:
        return 0
    renderer = Path(args.renderer).expanduser().resolve()
    if not renderer.is_file():
        parser.error("Install the browser-video-recording skill or provide --renderer; no substitute renderer is silently used")
    for executable in ("ffmpeg", "ffprobe"):
        if not shutil.which(executable):
            parser.error(f"Missing local tool: {executable}")
    if shutil.disk_usage(output.parent).free < 700 * 1024 * 1024:
        parser.error("Less than700MiB free; preserve working space before video encoding")
    picture = work / "picture.mp4"
    subprocess.run([sys.executable, str(renderer), "--config", str(render_path), "--output", str(picture)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(picture), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-i", str(output.with_suffix(".srt")), "-map", "0:v:0", "-map", "1:a:0", "-map", "2:s:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "96k", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng",
                    "-t", str(config["duration"]), "-movflags", "+faststart", str(output)], check=True)
    probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,codec_type,width,height,r_frame_rate,pix_fmt", "-show_entries", "format=duration,size", "-of", "json", str(output)]))
    streams = probe.get("streams", [])
    video = next((stream for stream in streams if stream["codec_type"] == "video"), {})
    audio = next((stream for stream in streams if stream["codec_type"] == "audio"), {})
    subtitle = next((stream for stream in streams if stream["codec_type"] == "subtitle"), {})
    if (len(streams) != 3 or video.get("codec_name") != "h264" or video.get("pix_fmt") != "yuv420p" or video.get("width") != 1920 or video.get("height") != 1080 or video.get("r_frame_rate") != "30/1" or audio.get("codec_name") != "aac" or subtitle.get("codec_name") != "mov_text" or abs(float(probe["format"]["duration"]) - config["duration"]) > .1):
        raise ValueError("Encoded artifact failed H.264/AAC/caption, duration, resolution or frame-rate verification")
    thumbnail = output.with_suffix(".png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "65", "-i", str(output), "-frames:v", "1", "-update", "1", str(thumbnail)], check=True)
    manifest.update(rendered=True, renderer_sha256=digest(renderer), video_sha256=digest(output), ffprobe=probe,
                    thumbnail=source_name(thumbnail), thumbnail_sha256=digest(thumbnail))
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Verified local video: {source_name(output)} ({output.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError) as error:
        print(f"Demo preparation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
