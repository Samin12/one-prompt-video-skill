#!/usr/bin/env python3
"""A dot-matrix globe that turns from one place to another while a message flies the great circle.

Made for "how the prompt got home": the presenter's phone in one country, the machine that did the work
in another. It is a diagram, so everything on it has to be true: the two places, the route between them
(a real great circle), and any line of text you add. Do not name a city or show a distance you have not
been given, and do not put clock times on it unless the footage it sits beside was shot at that time.

Usage:
  uv run --with numpy --with pillow --with shapely python3 globe.py \
      --from "Korea|His phone|37.55,126.99" --to "Home|Mac Studio · Claude Fable 5.2|38.5,-78.0" \
      --title "One prompt, sent *home*" --chip "Home is 14 hours behind Korea" \
      --bg <work>/src/canvas-bg.png --out <work>/media/globe.mp4
  add --still 2.6 to write one frame (a .png) instead: look at three or four before you render.
A place is "Title|second line|lat,lon". *word* in the title is drawn in the accent colour. --chip is optional.
Timing: the route starts at 0.45 s and lands at 2.9 s; the second label appears as it lands. 5.4 s, 30 fps.
"""
import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import shapely
from shapely.geometry import shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project import cached, font_file

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--from", dest="src", required=True)
ap.add_argument("--to", dest="dst", required=True)
ap.add_argument("--title", default="")
ap.add_argument("--chip", default="")
ap.add_argument("--bg", required=True, help="a still of the engine's empty canvas")
ap.add_argument("--out", required=True)
ap.add_argument("--still", type=float)
A_ = ap.parse_args()


def place(s):
    title, sub, ll = s.split("|")
    lat, lon = (float(v) for v in ll.split(","))
    return title, sub, (lat, lon)

W, H, SS, FPS, DUR = 1920, 1080, 2, 30, 5.4
CX, CY, R = 1010, 566, 392           # globe centre and radius, 1x px (bottom-left stays free for the picture-in-picture)
FROM_TITLE, FROM_SUB, START = place(A_.src)
TO_TITLE, TO_SUB, END = place(A_.dst)
LAT0 = max(-45.0, min(45.0, (START[0] + END[0]) / 2 - 4))   # camera tilt
TURN = ((END[1] - START[1] + 180) % 360) - 180               # degrees of longitude to turn, the short way round
LON_A, LON_B = START[1] + math.copysign(12, TURN), START[1] + TURN - math.copysign(14, TURN)
ACCENT, TEXT, MUTED = (226, 119, 78), (244, 241, 236), (172, 166, 158)
CARD, EDGE = (30, 29, 27), (58, 55, 51)


def font(weight, size):
    return ImageFont.truetype(str(font_file(weight)), int(size * SS))


def ease(x):
    x = min(1.0, max(0.0, x))
    return 4 * x * x * x if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2

def out_back(x):
    x = min(1.0, max(0.0, x)); c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def unit(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)

def project(v, lon0):
    """Earth-fixed unit vectors -> screen x, y (1x px) and depth z (1 = centre of the disc)."""
    l0, p0 = math.radians(lon0), math.radians(LAT0)
    c = np.array([math.cos(p0) * math.cos(l0), math.cos(p0) * math.sin(l0), math.sin(p0)])      # toward the camera
    e = np.array([-math.sin(l0), math.cos(l0), 0.0])                                             # screen right
    n = np.cross(c, e)                                                                            # screen up
    return CX + R * (v @ e), CY - R * (v @ n), v @ c

# ---- land: a lat/lon dot grid and the coast lines (Natural Earth, public domain, fetched once) ----
LAND = cached("ne_110m_land.geojson", "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson")
land = unary_union([shape(f["geometry"]) for f in json.loads(LAND.read_text())["features"]])
STEP = 1.5
pts = []
for lat in np.arange(-88.5, 89, STEP):
    n = max(1, round(360 * math.cos(math.radians(lat)) / STEP))
    for k in range(n):
        pts.append((lat, -180 + 360 * (k + 0.5) / n))
pts = np.array(pts)
DOTS = unit(pts[:, 0], pts[:, 1])[shapely.contains_xy(land, pts[:, 1], pts[:, 0])]
COAST = []
for poly in getattr(land, "geoms", [land]):
    xy = np.array(poly.exterior.coords)
    if len(xy) > 8:
        COAST.append(unit(xy[:, 1], xy[:, 0]))
GRAT = [unit(np.full(181, la), np.linspace(-180, 180, 181)) for la in (-60, -30, 0, 30, 60)] + \
       [unit(np.linspace(-85, 85, 86), np.full(86, lo)) for lo in range(-180, 180, 30)]

# ---- the route: great circle, lifted off the surface so it reads as a flight ----
A, B = unit(*START), unit(*END)
OMEGA = math.acos(float(np.clip(A @ B, -1, 1)))
ARC = np.array([(math.sin((1 - s) * OMEGA) * A + math.sin(s * OMEGA) * B) / math.sin(OMEGA) * (1 + 0.17 * math.sin(math.pi * s)) for s in np.linspace(0, 1, 140)])


def segments(xs, ys, vis):
    run = []
    for x, y, ok in zip(xs, ys, vis):
        if ok:
            run.append((x * SS, y * SS))
        else:
            if len(run) > 1: yield run
            run = []
    if len(run) > 1: yield run

def label(d, x, y, title, sub, alpha, side, dot=None):
    """A two-line card beside a pin at (x, y). side: -1 = card to the left, 1 = to the right."""
    ft, fs = font(700, 36), font(500, 25)
    tw = max(d.textlength(title, font=ft), d.textlength(sub, font=fs)) / SS
    w, h, gap = tw + 44, 104, 74
    x0 = x + gap if side > 0 else x - gap - w
    y0 = y - h / 2 - 46
    a = int(255 * alpha)
    d.line([(x * SS, y * SS), ((x0 if side > 0 else x0 + w) * SS, (y0 + h / 2) * SS)], fill=(*TEXT, int(110 * alpha)), width=2 * SS)
    d.rounded_rectangle([x0 * SS, y0 * SS, (x0 + w) * SS, (y0 + h) * SS], radius=18 * SS, fill=(*CARD, int(242 * alpha)), outline=(*EDGE, a), width=SS)
    d.text(((x0 + 22) * SS, (y0 + 14) * SS), title, font=ft, fill=(*TEXT, a))
    d.text(((x0 + 22) * SS, (y0 + 60) * SS), sub, font=fs, fill=(*(dot or MUTED), a))

BG = Image.open(A_.bg).convert("RGB").resize((W * SS, H * SS), Image.BICUBIC)


def frame(t):
    lon0 = LON_A + (LON_B - LON_A) * ease((t - 0.35) / 2.75)
    p = ease((t - 0.45) / 2.45)                       # how far the prompt has flown
    landed = t - 2.9                                   # seconds since it arrived
    im = BG.copy()
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    appear = 1.0   # the scene's own blur-in brings it on: a second fade here left the screen dark for half a second
    # the ball
    box = [(CX - R) * SS, (CY - R) * SS, (CX + R) * SS, (CY + R) * SS]
    g.ellipse([box[0] - 10 * SS, box[1] - 10 * SS, box[2] + 10 * SS, box[3] + 10 * SS], fill=(*ACCENT, int(54 * appear)))
    d.ellipse(box, fill=(27, 26, 24, int(255 * appear)), outline=(*ACCENT, int(120 * appear)), width=SS)
    for line in GRAT:
        x, y, z = project(line, lon0)
        for run in segments(x, y, z > 0.02):
            d.line(run, fill=(255, 255, 255, int(13 * appear)), width=SS)
    for ring in COAST:
        x, y, z = project(ring, lon0)
        for run in segments(x, y, z > 0.03):
            d.line(run, fill=(*TEXT, int(74 * appear)), width=SS)
    x, y, z = project(DOTS, lon0)
    for xi, yi, zi in zip(x[z > 0.04], y[z > 0.04], z[z > 0.04]):
        a = int((46 + 190 * zi ** 0.9) * appear); r = (1.5 + 0.9 * zi) * SS
        d.ellipse([xi * SS - r, yi * SS - r, xi * SS + r, yi * SS + r], fill=(*TEXT, a))
    # the route
    ax, ay, az = project(ARC, lon0)
    n = int(round(p * (len(ARC) - 1)))
    if n >= 1:
        run = [(ax[i] * SS, ay[i] * SS) for i in range(n + 1)]
        g.line(run, fill=(*ACCENT, 150), width=12 * SS, joint="curve")
        d.line(run, fill=(*ACCENT, 255), width=5 * SS, joint="curve")
        d.line(run, fill=(255, 226, 205, 235), width=2 * SS, joint="curve")
        if p < 1:
            hx, hy = run[-1]
            g.ellipse([hx - 30 * SS, hy - 30 * SS, hx + 30 * SS, hy + 30 * SS], fill=(*ACCENT, 190))
            d.ellipse([hx - 9 * SS, hy - 9 * SS, hx + 9 * SS, hy + 9 * SS], fill=(255, 240, 228, 255))
    # the two ends
    for name, v, t_in, side in (("from", A, 0.0, -1 if TURN > 0 else 1), ("to", B, 1.9, 1 if TURN > 0 else -1)):
        px, py, pz = (float(q) for q in project(v, lon0))
        if pz <= 0.05:
            continue
        a = min(1.0, (pz - 0.05) / 0.2) * min(1.0, max(0.0, (t - t_in) / 0.25))
        if a <= 0:
            continue
        pulse = (t * 1.1) % 1.0 if name == "from" and p < 0.2 else (landed * 1.25) % 1.0 if name == "to" and 0 <= landed < 1.6 else None
        if pulse is not None:
            rr = (12 + 44 * pulse) * SS
            d.ellipse([px * SS - rr, py * SS - rr, px * SS + rr, py * SS + rr], outline=(*ACCENT, int(230 * (1 - pulse) * a)), width=3 * SS)
        k = out_back((t - t_in) / 0.35)
        if name == "to" and landed >= 0:
            k *= 1 + 0.35 * math.sin(min(1.0, landed / 0.4) * math.pi)
        g.ellipse([px * SS - 26 * SS * k, py * SS - 26 * SS * k, px * SS + 26 * SS * k, py * SS + 26 * SS * k], fill=(*ACCENT, int(170 * a)))
        d.ellipse([px * SS - 11 * SS * k, py * SS - 11 * SS * k, px * SS + 11 * SS * k, py * SS + 11 * SS * k], fill=(*ACCENT, int(255 * a)), outline=(*TEXT, int(255 * a)), width=2 * SS)
        if name == "from":
            label(d, px, py, FROM_TITLE, FROM_SUB, a * min(1.0, max(0.0, (t - 0.1) / 0.25)), side)
        elif landed >= -0.1:
            label(d, px, py, TO_TITLE, TO_SUB, a * min(1.0, max(0.0, (landed + 0.1) / 0.3)), side, dot=ACCENT)
    # the title (accent on *word*) and the optional chip under the globe
    ft = font(700, 58)
    bits = [(s, i % 2 == 1) for i, s in enumerate(A_.title.split("*")) if s]
    tx = CX - sum(d.textlength(s, font=ft) for s, _ in bits) / SS / 2
    for s, accent in bits:
        d.text((tx * SS, 52 * SS), s, font=ft, fill=(*(ACCENT if accent else TEXT), 255))
        tx += d.textlength(s, font=ft) / SS
    ca = out_back((t - 1.45) / 0.35) if (A_.chip and t > 1.45) else 0
    if ca > 0:
        fc = font(600, 30)
        cw = d.textlength(A_.chip, font=fc) / SS + 64; ch = 58 * min(1.0, ca); x0 = CX - cw / 2; y0 = 996 - ch / 2
        d.rounded_rectangle([x0 * SS, y0 * SS, (x0 + cw) * SS, (y0 + ch) * SS], radius=29 * SS, fill=(*CARD, 245), outline=(*EDGE, 255), width=SS)
        if ca > 0.8:
            d.ellipse([(x0 + 22) * SS, (996 - 6) * SS, (x0 + 34) * SS, (996 + 6) * SS], fill=(*ACCENT, 255))
            d.text(((x0 + 46) * SS, (996 - 19) * SS), A_.chip, font=fc, fill=(*TEXT, 255))
    im.paste(glow.filter(ImageFilter.GaussianBlur(14 * SS)), (0, 0), glow.filter(ImageFilter.GaussianBlur(14 * SS)))
    im.paste(lay, (0, 0), lay)
    return im.resize((W, H), Image.LANCZOS)

if __name__ == "__main__":
    if A_.still is not None:
        frame(A_.still).save(A_.out)
        sys.exit()
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "13", "-g", "15", "-pix_fmt", "yuv420p", A_.out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        enc.stdin.write(frame(i / FPS).tobytes())
    enc.stdin.close()
    enc.wait()
    print("wrote", A_.out)
