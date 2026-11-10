#!/usr/bin/env python3
"""After `screenplay aroll`: did any cut take sound out of a word?

The engine trims pauses using each word's end time, and the transcriber's end time for the last word of
a sentence is often early. The cut then lands inside the word: "starts at 50 cents" loses "cents", and
no transcript of the source shows it, because the source is intact. This looks at the sound inside
every piece the cut removed and lists the cuts where real sound was thrown away.

For each hit it prints the fix:
  - sound right after the last kept word  -> move that word's "end" later in <work>/words.json
  - a breath or an "s" running into the pause -> add  holds: [{after: s<i>, keep: 0.4}]  to <work>/cuts.yaml
Then run `screenplay aroll <work>` again and this script again until it prints "clean".

Usage:  uv run --with numpy --with soundfile python3 scan_cuts.py [--project <dir>] [--work <dir>]
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project import find_project, load_config, work_dir

if "--work" in sys.argv:
    W = Path(sys.argv[sys.argv.index("--work") + 1]).expanduser()
else:
    W = work_dir(load_config(find_project()))
source = json.loads((W / "source.json").read_text())
mic = source.get("mic") or source.get("camera")
if isinstance(mic, dict):
    mic = mic.get("path")
x, sr = sf.read(mic) if str(mic).endswith(".wav") else (None, None)
if x is None:
    import subprocess
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(mic), "-vn", "-ac", "1", "-ar", "48000", "-f", "f32le", "-"])
    x, sr = np.frombuffer(raw, dtype=np.float32).astype(np.float64), 48000
if x.ndim > 1:
    x = x.mean(1)
segs = json.loads((W / "aroll.json").read_text())["segments"]
words = json.loads((W / "words.json").read_text())
words = words if isinstance(words, list) else words["words"]
db = lambda v: 20 * np.log10(max(float(v), 1e-9))
speech = np.sqrt((x ** 2).mean())
limit = db(speech) - 17                      # sound this close to speech level is a word, not room
win = int(0.02 * sr)
hits = []
for a, b in ((s["srcEnd"], n["srcStart"]) for s, n in zip(segs, segs[1:])):
    if b - a <= 0.02:
        continue
    cut = x[int(a * sr):int(b * sr)]
    k = len(cut) // win
    if k == 0:
        continue
    r = np.sqrt((cut[:k * win].reshape(k, win) ** 2).mean(1))
    loud = np.flatnonzero(r > 10 ** (limit / 20))
    secs = len(loud) * 0.02
    if secs < 0.04 or (secs < 0.06 and db(r.max()) < limit + 14):   # a 40 ms blip of breath is not a word
        continue
    before = [w for w in words if w["end"] <= a + 0.05][-1]
    after = [w for w in words if w["start"] >= b - 0.05][0]
    hits.append((a, b, len(loud) * 0.02, db(r.max()), before, after, a + loud[0] * 0.02, a + (loud[-1] + 1) * 0.02))
print(f"speech level {db(speech):.1f} dB; a cut is a hit when it removes 60 ms or more of sound above {limit:.1f} dB (or a loud 40 ms)")
for a, b, secs, peak, before, after, s0, s1 in hits:
    print(f"\ncut {a:.2f}-{b:.2f} s removes {secs:.2f} s of sound (peak {peak:.1f} dB) at {s0:.2f}-{s1:.2f} s")
    print(f"  after  s{before['i']} \"{before['text']}\" (ends {before['end']:.2f})   before  s{after['i']} \"{after['text']}\" (starts {after['start']:.2f})")
    if s0 - before["end"] < 0.25:
        print(f"  fix: set \"end\" of word {before['i']} to {s1 + 0.02:.2f} in words.json (the word runs on past its time stamp)")
    else:
        print(f"  fix: add  {{after: s{before['i']}, keep: {min(1.2, s1 - a + 0.15):.2f}}}  under holds: in cuts.yaml, or look at what the sound is")
print(f"\n{len(hits)} cut(s) removed sound" if hits else "\nclean: no cut removed sound")
sys.exit(1 if hits else 0)
