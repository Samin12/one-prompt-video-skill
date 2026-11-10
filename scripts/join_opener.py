#!/usr/bin/env python3
"""Put the presenter's own opener in front of the finished avatar video, without re-encoding the picture.

The opener is its own screenplay render (its own work dir), so the main video's word ids and checked
picture are never touched. This copies both pictures through MPEG-TS (frame-exact), rebuilds the sound
once (both halves at the same loudness, the opener's sound effects mixed in), and writes the joined
captions and the chapter list.

Usage:
  python3 join_opener.py --intro <intro.mp4> --main <main.mp4> --out <final.mp4>
      [--intro-work <dir> --whoosh s1,s4,s5 --pop w38,w94 --pop-at 46.23]   sound effects, by scene id / word id / second
      [--main-work <dir>]            chapters from the main timeline (<dir>/.screenplay/timeline.json)
      [--main-srt <full.srt>]        captions of the whole main timeline (the intro's are read beside --intro)
      [--skip-frames N]              frames of the main TIMELINE that are not in --main (it was rendered --from a later anchor)
      [--handoff "The Clone Takes Over"]   chapter name where the main video starts
      [--lufs -14]
Sound effects are Borumi's built-ins. Their gains put a whoosh's peak near -9.5 dBFS and a pop's near -13:
measured against the voice, not guessed (the first guess was 16 dB under the voice, which is not there).
After it runs: compare a few frames with the two renders and check the sound offset is 0 (references/opener.md).
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project import frame_count

SOUNDS = Path("/Applications/Borumi.app/Contents/Resources")
LIMITER_DELAY = 239   # samples at 48 kHz: alimiter looks 5 ms ahead and hands the sound back that much late (measured)
WHOOSH_LEAD = 0.05    # the whoosh peaks 0.055 s in: start it just before the cut
GAIN = {"whoosh": -5.0, "pop": -8.5}

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
for name in ("--intro", "--main", "--out"):
    ap.add_argument(name, required=True)
ap.add_argument("--intro-work"); ap.add_argument("--whoosh", default=""); ap.add_argument("--pop", default=""); ap.add_argument("--pop-at", default="")
ap.add_argument("--main-work"); ap.add_argument("--main-srt"); ap.add_argument("--skip-frames", type=int, default=0)
ap.add_argument("--handoff", default=""); ap.add_argument("--lufs", type=float, default=-14.0)
a = ap.parse_args()
INTRO, MAIN, OUT = (Path(p).expanduser() for p in (a.intro, a.main, a.out))


def run(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"FAILED: {' '.join(map(str, cmd[:6]))} ...\n{r.stderr[-800:]}")
    return r


def lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    return float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", r.stderr)[-1])


frames_intro, frames_main = frame_count(INTRO), frame_count(MAIN)
secs_intro, skip = frames_intro / 30, a.skip_frames / 30

# ---- the opener's sound effects: (sound, second, gain in dB) ----
sfx = []
if a.intro_work:
    iw = Path(a.intro_work).expanduser()
    tl = json.loads((iw / ".screenplay/timeline.json").read_text())["timeline"]
    start = {s["id"]: s["from"] / tl["fps"] for s in tl["scenes"]}
    words = {w["id"]: w for w in json.loads((iw / "words.out.json").read_text())}
    sfx += [("whoosh", start[s] - WHOOSH_LEAD, GAIN["whoosh"]) for s in a.whoosh.split(",") if s]
    sfx += [("pop", words[w]["start"], GAIN["pop"]) for w in a.pop.split(",") if w]
sfx += [("pop", float(t), GAIN["pop"] + 1.5) for t in a.pop_at.split(",") if t]

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    # ---- sound: each half at the target, effects on the opener, a safety limiter, exact lengths ----
    g_intro, g_main = a.lufs - lufs(INTRO), a.lufs - lufs(MAIN)
    inputs, graph, mix = ["-i", INTRO], [f"[0:a]aresample=48000,aformat=channel_layouts=stereo,volume={g_intro:.2f}dB[v]"], "[v]"
    for i, (name, t, gain) in enumerate(sfx, 1):
        inputs += ["-i", SOUNDS / f"built-in-sound-{name}.wav"]
        graph.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain}dB,adelay={int(round(t * 1000))}:all=1[s{i}]")
        mix += f"[s{i}]"
    graph.append(f"{mix}amix=inputs={len(sfx) + 1}:normalize=0:duration=first,alimiter=limit=0.89:level=false,"
                 f"atrim=start_sample={LIMITER_DELAY},asetpts=PTS-STARTPTS,apad,atrim=end_sample={round(secs_intro * 48000)}[a]")
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(graph), "-map", "[a]", "-c:a", "pcm_s24le", tmp / "intro.wav"])
    run(["ffmpeg", "-v", "error", "-y", "-i", MAIN, "-vn", "-af",
         f"aresample=48000,aformat=channel_layouts=stereo,volume={g_main:.2f}dB,apad,atrim=end_sample={round(frames_main / 30 * 48000)}", "-c:a", "pcm_s24le", tmp / "main.wav"])
    (tmp / "audio.txt").write_text(f"file '{tmp / 'intro.wav'}'\nfile '{tmp / 'main.wav'}'\n")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", tmp / "audio.txt", "-c:a", "pcm_s24le", tmp / "all.wav"])
    # ---- picture: both renders copied through MPEG-TS so each keeps its own stream headers ----
    for name, src in (("intro", INTRO), ("main", MAIN)):
        run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an", "-c:v", "copy", "-bsf:v", "h264_mp4toannexb", "-f", "mpegts", tmp / f"{name}.ts"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-fflags", "+genpts", "-r", "30", "-i", f"concat:{tmp / 'intro.ts'}|{tmp / 'main.ts'}", "-i", tmp / "all.wav",
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", OUT])


# ---- captions and chapters, moved by the opener's length ----
def secs(ts):
    h, m, s = ts.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def stamp(t):
    return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{t % 60:06.3f}".replace(".", ",")


intro_srt = INTRO.with_suffix(".srt")
if a.main_srt and intro_srt.exists():
    blocks = intro_srt.read_text().strip().split("\n\n")
    for b in Path(a.main_srt).expanduser().read_text().strip().split("\n\n"):
        lines = b.split("\n")
        t0, t1 = (secs(x) for x in lines[1].split(" --> "))
        if t1 <= skip:
            continue   # a line that is not in this cut
        blocks.append("\n".join([lines[0], f"{stamp(max(t0, skip) - skip + secs_intro)} --> {stamp(t1 - skip + secs_intro)}", *lines[2:]]))
    OUT.with_suffix(".srt").write_text("\n\n".join("\n".join([str(i), *b.split("\n")[1:]]) for i, b in enumerate(blocks, 1)) + "\n")
chapters = ["00:00 Intro"]
if a.handoff:
    chapters.append(f"{int(round(secs_intro)) // 60:02d}:{int(round(secs_intro)) % 60:02d} {a.handoff}")
if a.main_work:
    tl = json.loads((Path(a.main_work).expanduser() / ".screenplay/timeline.json").read_text())["timeline"]
    for ch in tl["chapters"]:   # exact chapter-card frames from the main timeline
        t = int(ch["frame"] / tl["fps"] - skip + secs_intro)
        chapters.append(f"{t // 60:02d}:{t % 60:02d} {ch['title']}")
    OUT.with_name(OUT.stem + ".chapters.txt").write_text("\n".join(chapters) + "\n")
print(f"intro {frames_intro} frames ({secs_intro:.3f} s, gain {g_intro:+.2f} dB), main {frames_main} frames (gain {g_main:+.2f} dB), {len(sfx)} sound effects")
print("wrote", OUT)
print("\n".join(chapters))
