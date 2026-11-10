#!/usr/bin/env python3
"""Render avatar takes again when their room differs from the rest, and keep the closest result.

Give it the take ids that room_check.py called ODD. For each: the clip in place is parked in
takes/alt/<id>.roomN.mp4, a new one is rendered from the same photo and the same read (the voice is not
touched), and it is checked against avatar/room_ref.json. Up to three tries; the closest render stays.
A take made of two clips is given as its part (x07.a or x07.b) and is joined again afterwards.

Usage:  uv run --with numpy --with opencv-python-headless python3 rerender_room.py <take id>... [--project <dir>]
Costs one avatar clip per try (about 26 Higgsfield credits for a 15 s Wan 3.0 clip at 720p).
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_takes as bt
from room_check import features, score, verdict

ALT = bt.AVATAR_DIR / "alt"
REGIONS = bt.CFG["room_regions"]
TRIES = 3


def park(stem, tag="room"):
    """Moves takes/<stem>.mp4 and its job file to alt/<stem>.<tag>N.*; returns the parked clip."""
    n = 1
    while (ALT / f"{stem}.{tag}{n}.mp4").exists():
        n += 1
    for ext in ("mp4", "job.json"):
        src = bt.AVATAR_DIR / f"{stem}.{ext}"
        if src.exists():
            src.rename(ALT / f"{stem}.{tag}{n}.{ext}")
    return ALT / f"{stem}.{tag}{n}.mp4"


def render_part(t, part):
    """One clip of a two-clip take, from the part audio that is already on disk."""
    tid = t["id"]
    audio, mp4, js = (bt.AVATAR_DIR / f"{tid}.{part}.{e}" for e in ("mp3", "mp4", "job.json"))
    secs = max(2, min(bt.MAX_CLIP, bt.math.ceil(bt.duration(audio) + 0.25)))
    job = bt.create(bt.AVATAR_MODEL, ["--prompt", bt.AVATAR_PROMPT, "--image-references", bt.IMAGE_ID,
                                      "--audio-references", str(audio), "--resolution", bt.CFG["resolution"],
                                      "--duration", str(secs), "--generate_audio", "false", "--aspect_ratio", "16:9"], js)
    bt.urllib.request.urlretrieve(job["result_url"], mp4)


def one(name, reference):
    tid, _, part = name.partition(".")
    t = bt.load_takes([tid])[0]
    live = bt.AVATAR_DIR / f"{name}.mp4"
    candidates = []
    for attempt in range(1, TRIES + 1):
        parked = park(name)
        ft = features(parked, REGIONS)
        candidates.append((bool(verdict(ft, reference, REGIONS)), score(ft, reference), parked))
        if attempt > 1 and not candidates[-1][0]:
            break   # the render from the round before is clean
        if part:
            render_part(t, part)
        else:
            bt.avatar_one(t)
        ft = features(live, REGIONS)
        why = verdict(ft, reference, REGIONS)
        print(f"  {name} try {attempt}: {'clean' if not why else '; '.join(why)}", flush=True)
        if not why:
            break
    ft = features(live, REGIONS)
    best = min(candidates + [(bool(verdict(ft, reference, REGIONS)), score(ft, reference), live)], key=lambda c: (c[0], c[1]))
    if best[2] != live:   # an earlier render was closer: put it back
        park(name)
        shutil.copyfile(best[2], live)
        js = Path(str(best[2])[:-4] + ".job.json")
        if js.exists():
            shutil.copyfile(js, bt.AVATAR_DIR / f"{name}.job.json")
    if part:   # join the take again from its two clips
        park(tid, "joined")
        bt.avatar_long(t)
    return name, ("clean" if not best[0] else f"closest kept ({best[1]:.2f} x limit): look at it")


if __name__ == "__main__":
    names = sys.argv[1:]
    refp = bt.P / "avatar" / "room_ref.json"
    if not names or not refp.exists():
        sys.exit(__doc__ if not names else "no avatar/room_ref.json: run room_check.py with no arguments first")
    bt.need("image_id")
    ALT.mkdir(parents=True, exist_ok=True)
    reference = json.loads(refp.read_text())
    with bt.cf.ThreadPoolExecutor(max_workers=3) as pool:
        for name, state in pool.map(lambda n: one(n, reference), names):
            print(f"{name}: {state}", flush=True)
