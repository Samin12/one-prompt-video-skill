#!/usr/bin/env python3
"""Room check: does each avatar clip sit in the same room as the rest?

The avatar model takes the photo as a reference, not as its first frame, so about one clip in six comes
back with the room reframed, an object added or moved, or the wall a different colour. Cut together,
the room jumps between takes. No per-clip check of the face or the lip sync sees this.

For each clip this takes seven frames, keeps the per-pixel median (so a passing hand drops out) and
measures the patches of room that show around a centred presenter (`room_regions` in project.json): the
patch's median colour and which strong hues are in it. The reference room is the median over all takes,
and each patch's limit is set from how much the takes themselves vary there, so the check needs no
setup: a patch the presenter keeps moving through gets a loose limit by itself, a patch of bare wall a
tight one. A clip is ODD when a patch's colour or its hue mix sits beyond its limit.

Usage (inside the project, or with --project <dir>):
    uv run --with numpy --with opencv-python-headless python3 room_check.py            # every take; writes avatar/room_ref.json and avatar/qa/room-odd.jpg
    uv run --with numpy --with opencv-python-headless python3 room_check.py a.mp4 ...  # these clips against the saved reference
Exit code 1 when any clip is odd. Open the sheet before you trust either answer: the thresholds were
set on one presenter's studio, and a presenter who moves across a patch can trip them.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project import find_project, load_config

COLOUR_FLOOR = 10.0   # a patch's median colour may sit this far (0..255 units) from the usual room, at least
HUE_FLOOR = 0.03      # share of a patch that may hold other strong hues, at least
SPREAD = 4.0          # limits also give way to 4 x the takes' own spread in that patch
BINS = 12
K = 3 + BINS


def features(path, regions):
    cap = cv2.VideoCapture(str(path))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []
    for at in (0.05, 0.2, 0.35, 0.5, 0.65, 0.8, 0.95):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(n * at))
        ok, f = cap.read()
        if ok:
            frames.append(f)
    if not frames:
        raise RuntimeError(f"no frames in {path}")
    med = np.median(np.array(frames), axis=0).astype(np.uint8)
    hsv = cv2.cvtColor(med, cv2.COLOR_BGR2HSV)
    h, w = med.shape[:2]
    row = []
    for x0, y0, x1, y1 in regions.values():
        sl = (slice(int(y0 * h), int(y1 * h)), slice(int(x0 * w), int(x1 * w)))
        patch, hs = med[sl].reshape(-1, 3).astype(np.float64), hsv[sl].reshape(-1, 3)
        strong = (hs[:, 1] > 120) & (hs[:, 2] > 60)                 # only clearly coloured pixels count as a hue
        hist = np.bincount(hs[strong, 0].astype(int) * BINS // 180, minlength=BINS)[:BINS] / max(1, len(hs))
        row.append(np.concatenate([np.median(patch, axis=0), hist]))
    return np.concatenate(row)


def patch_distances(ft, ref):
    """Per patch: (colour distance, hue-mix distance) from the reference room."""
    out = []
    for i in range(len(ft) // K):
        a, b = ft[i * K:(i + 1) * K], ref[i * K:(i + 1) * K]
        out.append((float(np.linalg.norm(a[:3] - b[:3])), float(np.abs(a[3:] - b[3:]).sum())))
    return out


def make_reference(all_features):
    """The usual room (median over the takes) and each patch's limits, from the takes' own spread."""
    fts = np.array(all_features)
    ref = np.median(fts, axis=0)
    d = np.array([patch_distances(f, ref) for f in fts])            # takes x patches x (colour, hue)
    med = np.median(d, axis=0)
    mad = np.median(np.abs(d - med), axis=0)
    limits = np.maximum(med + SPREAD * 1.4826 * mad, [COLOUR_FLOOR, HUE_FLOOR])
    return {"ref": ref.tolist(), "limits": limits.tolist()}


def verdict(ft, reference, regions):
    why = []
    for name, (colour, hue), (c_lim, h_lim) in zip(regions, patch_distances(ft, np.array(reference["ref"])), reference["limits"]):
        if colour > c_lim:
            why.append(f"{name}: colour off by {colour:.0f} (limit {c_lim:.0f})")
        if hue > h_lim:
            why.append(f"{name}: other colours in it, {hue:.3f} (limit {h_lim:.3f})")
    return why


def score(ft, reference, regions=None):
    """Lower is closer to the usual room: picks between several renders of one take."""
    return max(max(c / cl, h / hl) for (c, h), (cl, hl) in zip(patch_distances(ft, np.array(reference["ref"])), reference["limits"]))


def sheet(clips, out):
    rows = []
    for c in clips:
        cap = cv2.VideoCapture(str(c))
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cells = []
        for at in (0.05, 0.5, 0.93):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(n * at))
            ok, f = cap.read()
            cells.append(cv2.resize(f, (426, 240)) if ok else np.zeros((240, 426, 3), np.uint8))
        row = np.hstack(cells)
        for colour, thick in (((0, 0, 0), 4), ((255, 255, 255), 2)):
            cv2.putText(row, Path(c).stem, (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.9, colour, thick)
        rows.append(row)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])


if __name__ == "__main__":
    P = find_project()
    regions = load_config(P)["room_regions"]
    refp = P / "avatar" / "room_ref.json"
    named = [Path(a) for a in sys.argv[1:]]
    clips = named or sorted(P.glob("avatar/takes/*.mp4"))
    if not clips:
        sys.exit("no clips in avatar/takes/")
    fts = {c: features(c, regions) for c in clips}
    if not named:   # every take: the median take is the reference room
        refp.write_text(json.dumps(make_reference(list(fts.values()))))
    if not refp.exists():
        sys.exit("no avatar/room_ref.json yet: run room_check.py with no arguments first")
    reference = json.loads(refp.read_text())
    odd = []
    for c, ft in sorted(fts.items(), key=lambda kv: -score(kv[1], reference)):
        why = verdict(ft, reference, regions)
        print(f"{c.name:18s} {score(ft, reference):5.2f} x limit  {'ODD: ' + '; '.join(why) if why else 'ok'}")
        if why:
            odd.append(c)
    if odd and not named:
        usual = min(fts, key=lambda c: score(fts[c], reference))
        sheet([usual, *odd], P / "avatar" / "qa" / "room-odd.jpg")
        print(f"\n{len(odd)} odd of {len(clips)}. Sheet (first row is the usual room): {P / 'avatar' / 'qa' / 'room-odd.jpg'}")
    sys.exit(1 if odd else 0)
