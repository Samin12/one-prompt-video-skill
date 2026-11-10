#!/usr/bin/env python3
"""Preview cards for the opener: real stretches of the finished video, framed and tagged.

Each card is a clip of the finished video on the canvas with a "LATER IN THIS VIDEO" tag, so a viewer
never mistakes it for the video having started. The card sits right of centre and leaves the bottom-left
free for the presenter's picture-in-picture. Only tease what is really in the final cut: if the main
video changes after this, check every card's moment is still there.

Usage:
  python3 make_teases.py <finished video.mp4> <opener work dir> name:start:seconds [name:start:seconds ...]
  e.g. python3 make_teases.py main.mp4 "~/Borumi Projects/X intro screenplay" boss:17.5:4.2 price:297.8:4.8
Writes <work>/media/later-<name>.mp4 (1920x1080, 30 fps, silent, a keyframe every 15 frames).
Needs <work>/src/canvas-bg.png: a still of the engine's empty canvas (see references/opener.md).
In edit.yaml:  - {kind: app, at: w42, transition: cut, screen: media/later-boss.mp4, start: 1.6, size: [1920, 1080], webcam: pip}
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project import font_file

W, H, SS = 1920, 1080, 2
CW, CH = 1520, 855            # the preview card (16:9)
CX0, CY0 = 344, 158           # its top-left: right of the picture-in-picture (x 17..285), under the tag
ACCENT, TEXT, CARD, EDGE = (226, 119, 78), (244, 241, 236), (30, 29, 27), (58, 55, 51)
TAG = "LATER IN THIS VIDEO"

if len(sys.argv) < 4:
    sys.exit(__doc__)
video, work = Path(sys.argv[1]).expanduser(), Path(sys.argv[2]).expanduser()
src, media = work / "src", work / "media"
media.mkdir(parents=True, exist_ok=True)
canvas = src / "canvas-bg.png"
if not canvas.exists():
    sys.exit(f"missing {canvas}: render a still of the empty canvas first (references/opener.md)")

# the plate: canvas + tag + the card's frame (the clip goes into the hole)
bg = Image.open(canvas).convert("RGBA").resize((W * SS, H * SS), Image.BICUBIC)
d = ImageDraw.Draw(bg)
f = ImageFont.truetype(str(font_file(700)), 30 * SS)
tw = d.textlength(TAG, font=f) / SS
x0, y0, h = CX0, 74, 56
d.rounded_rectangle([x0 * SS, y0 * SS, (x0 + tw + 66) * SS, (y0 + h) * SS], radius=28 * SS, fill=CARD, outline=EDGE, width=SS)
d.ellipse([(x0 + 22) * SS, (y0 + h / 2 - 7) * SS, (x0 + 36) * SS, (y0 + h / 2 + 7) * SS], fill=ACCENT)
d.text(((x0 + 48) * SS, (y0 + 10) * SS), TAG, font=f, fill=TEXT)
d.rounded_rectangle([(CX0 - 3) * SS, (CY0 - 3) * SS, (CX0 + CW + 3) * SS, (CY0 + CH + 3) * SS], radius=25 * SS, fill=(12, 12, 11), outline=EDGE, width=3 * SS)
plate, mask_file = src / "later-plate.png", src / "later-mask.png"
bg.resize((W, H), Image.LANCZOS).convert("RGB").save(plate)
mask = Image.new("L", (CW * SS, CH * SS), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, CW * SS - 1, CH * SS - 1], radius=22 * SS, fill=255)
mask.resize((CW, CH), Image.LANCZOS).save(mask_file)

for spec in sys.argv[3:]:
    name, start, secs = spec.split(":")
    out = media / f"later-{name}.mp4"
    # the plate and the mask loop for ever: -t stops the render at the clip's length
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-i", str(plate), "-ss", start, "-t", secs, "-i", str(video),
                        "-loop", "1", "-framerate", "30", "-i", str(mask_file), "-filter_complex",
                        f"[1:v]fps=30,scale={CW}:{CH}:flags=lanczos,format=rgba[c];[2:v]format=gray[m];[c][m]alphamerge[ca];"
                        f"[0:v][ca]overlay={CX0}:{CY0},format=yuv420p[v]",
                        "-map", "[v]", "-t", secs, "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-g", "15", str(out)], capture_output=True, text=True)
    print(out.name, "ok" if r.returncode == 0 else r.stderr[-300:])
