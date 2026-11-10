#!/usr/bin/env python3
"""Does the finished video say the script? Transcribes it take by take and lists every difference.

Transcribing a whole 10-minute file in one pass loops and skips minutes; take by take it is exact.
Each take's place in the file comes from avatar/takes-timeline.json and the cut in <work>/aroll.json.

Usage:  python3 check_takes.py <video or audio file> [--offset S] [--skip-takes N] [--project <dir>]
  --offset S       seconds of other material in front (the presenter's own opener, a cold open)
  --skip-takes N   the first N takes are not in this file (it was rendered from a later anchor)
Reads as differences only: number formats ("50 cents" heard as "$0.50") and names are normal; a dropped,
added or changed word is not. Writes <project>/logs/check-takes.json. Exit code 1 under 0.90 for any take.
"""
import difflib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project import WHISPER_MODEL, find_project, load_config, out_time, work_dir

P = find_project()
args = sys.argv[1:]
def opt(name, default):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default
offset, skip = float(opt("--offset", 0)), int(opt("--skip-takes", 0))
if not args:
    sys.exit(__doc__)
video = Path(args[0]).expanduser()
W = work_dir(load_config(P))
tl = json.loads((P / "avatar" / "takes-timeline.json").read_text())
aroll = json.loads((W / "aroll.json").read_text())
starts = [out_time(aroll["segments"], t["start"], aroll["duration"]) for t in tl] + [aroll["duration"]]
base = starts[skip] if skip else 0.0


def norm(s):
    s = s.lower().replace("$", "").replace("%", " percent")
    s = re.sub(r"[^a-z0-9. ]", " ", s)
    return re.sub(r"(?<!\d)\.|\.(?!\d)", " ", s).split()


with tempfile.TemporaryDirectory() as tmp:
    whole = Path(tmp) / "all.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(whole)], check=True)
    rows = []
    for i, t in enumerate(tl):
        if i < skip:
            continue
        a, b = max(0.0, starts[i] - base + offset - 0.15), starts[i + 1] - base + offset + 0.1
        wav = Path(tmp) / f"{t['id']}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", str(whole), str(wav)], check=True)
        heard = subprocess.run(["whisper-cli", "-m", str(WHISPER_MODEL), "-l", "en", "-f", str(wav), "-nt", "-np"], capture_output=True, text=True).stdout.strip().replace("\n", " ")
        A, B = norm(t["say"]), norm(heard)
        sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
        diffs = [f"[{' '.join(A[i1:i2])}]->[{' '.join(B[j1:j2])}]" for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]
        rows.append({"id": t["id"], "at": round(a, 1), "match": round(sm.ratio(), 3), "diffs": diffs, "heard": heard})
(P / "logs").mkdir(exist_ok=True)
(P / "logs" / "check-takes.json").write_text(json.dumps(rows, indent=1))
for r in rows:
    if r["diffs"]:
        print(f"{r['id']}  {int(r['at'] // 60)}:{r['at'] % 60:04.1f}  {r['match']:.3f}  {' '.join(r['diffs'])}")
low = [r["id"] for r in rows if r["match"] < 0.90]
print(f"\n{len(rows)} takes checked, lowest match {min(r['match'] for r in rows):.3f}" + (f"; READ THESE: {' '.join(low)}" if low else ""))
sys.exit(1 if low else 0)
