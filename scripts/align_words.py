#!/usr/bin/env python3
"""Exact word times for real footage: forced alignment of <work>/words.json against the audio.

The transcriber's word times are good enough for a clean cloned voice. On the presenter's own outdoor
footage three passes disagreed by up to 1.3 s, and graphics anchored to those words landed on the wrong
ones. This keeps the words and replaces their times (torchaudio's MMS forced aligner). The old file is
kept as words.whisper.json. Numbers are aligned as they are spoken: fix the SPOKEN table for yours.

Then check a few anchors the cheap way before trusting it: cut 1.5 to 2.5 s around a phrase and
transcribe just that slice (`whisper-cli -f slice.wav -nt -np`). Whisper does not move words between
slices.

Usage:  uv run --with torch --with torchaudio --with soundfile python3 align_words.py <work dir> [audio.wav]
        (audio defaults to the mic in <work>/source.json; first run downloads the aligner, about 1.2 GB)
"""
import json
import re
import sys
from pathlib import Path

import soundfile as sf
import torch
import torchaudio

SPOKEN = {"5.2": "five point two", "5.5": "five point five", "5.1": "five point one"}   # how numbers in the transcript are said

if len(sys.argv) < 2:
    sys.exit(__doc__)
W = Path(sys.argv[1]).expanduser()
if not (W / "words.json").exists():
    sys.exit(f"no {W / 'words.json'}: run `screenplay transcribe` on the opener's work dir first")
audio = sys.argv[2] if len(sys.argv) > 2 else json.loads((W / "source.json").read_text())["mic"]
data, sr = sf.read(audio, dtype="float32", always_2d=True)
wav = torch.from_numpy(data).mean(1)[None, :]
bundle = torchaudio.pipelines.MMS_FA
if sr != bundle.sample_rate:
    wav = torchaudio.functional.resample(wav, sr, bundle.sample_rate)
words = json.loads((W / "words.json").read_text())
norm = []
for w in words:
    t = SPOKEN.get(w["text"].strip(".,!?"), w["text"]).lower()
    t = re.sub(r"[^a-z' ]", "", t).replace("'", "")
    norm.append(t.split() or ["a"])
model, tok, aligner = bundle.get_model(), bundle.get_tokenizer(), bundle.get_aligner()
with torch.inference_mode():
    emission, _ = model(wav)
    spans = aligner(emission[0], tok([p for ws in norm for p in ws]))
ratio = wav.shape[1] / emission.shape[1] / bundle.sample_rate
k, low = 0, []
for w, ws in zip(words, norm):
    sp = spans[k:k + len(ws)]
    k += len(ws)
    w["start"], w["end"] = round(sp[0][0].start * ratio, 3), round(sp[-1][-1].end * ratio, 3)
    score = sum(s.score for x in sp for s in x) / sum(len(x) for x in sp)
    if score < 0.4:
        low.append(f"{w['text']}@{w['start']:.2f}")
for a, b in zip(words, words[1:]):
    a["end"] = max(a["start"] + 0.06, min(a["end"], b["start"]))
backup = W / "words.whisper.json"
if not backup.exists():
    backup.write_text((W / "words.json").read_text())
(W / "words.json").write_text(json.dumps(words, ensure_ascii=False))
print(f"aligned {len(words)} words; last word ends {words[-1]['end']:.2f} s")
print("low-confidence words (check these by slice):", " ".join(low) or "none")
