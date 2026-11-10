#!/usr/bin/env python3
"""Fills the digital silence in each voice take with the voice's own quiet floor.

A cloned voice carries a faint room floor while it speaks and exact zeros before, after and between
phrases. Cut together, the zeros sound like the track switching off between takes (a reviewer hears it
on headphones at once). This writes voice/takes/filled/<id>.wav for every take: the same read, at its
full timeline length, with a room tone mixed into every stretch that is silent. The words are not
touched. `build_takes.py assemble` uses the filled file when it is newer than the read.

The tone (voice/ref/room-tone.wav) is cut from the quiet moments inside the takes themselves, so it
matches this voice. It is made once; move the file away to make it again.

Usage:  uv run --with numpy --with soundfile python3 fill_tone.py [take id ...] [--project <dir>]
"""
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project import duration, find_project, load_config, load_takes

SR = 48000
P = find_project()
CFG = load_config(P)


def read(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def make_tone(takes, out):
    """About 8 s of the voice's floor: quiet (not silent) stretches of the takes, crossfaded, evened out, loopable."""
    x = np.concatenate([read(P / "voice" / "takes" / f"{t['id']}.mp3") for t in takes])
    w = int(0.02 * SR); k = len(x) // w
    db = 20 * np.log10(np.maximum(np.sqrt((x[:k * w].reshape(k, w) ** 2).mean(1)), 1e-10))
    floor = np.percentile(db[db > -90], 5)                      # the level of the quietest real sound
    quiet = (db > floor - 9) & (db < floor + 2.5)
    runs, i = [], 0
    while i < k:
        if quiet[i]:
            j = i
            while j < k and quiet[j]:
                j += 1
            if j - i >= 12:                                      # at least 0.24 s; drop 40 ms at each side
                runs.append((i + 2, j - 2))
            i = j
        else:
            i += 1
    if sum(b - a for a, b in runs) * 0.02 < 2:
        sys.exit("under 2 s of quiet floor found in the takes: nothing to build a room tone from")
    xf, tone = int(0.012 * SR), np.zeros(0)
    for a, b in runs:
        seg = x[a * w:b * w].copy()
        if len(tone) == 0:
            tone = seg
            continue
        f = np.linspace(0, 1, xf)
        tone[-xf:] = tone[-xf:] * (1 - f) + seg[:xf] * f
        tone = np.concatenate([tone, seg[xf:]])
        if len(tone) > SR * 8:
            break
    win = int(0.25 * SR)                                         # even out slow level changes so the loop does not pump
    env = np.sqrt(np.convolve(tone ** 2, np.ones(win) / win, mode="same"))
    tone = tone * np.clip(np.median(env) / np.maximum(env, 1e-9), 0.5, 2.0)
    f = np.linspace(0, 1, xf * 4)                                # loopable: the end fades into the start
    tone[:xf * 4] = tone[:xf * 4] * f + tone[-xf * 4:] * (1 - f)
    tone = tone[:-xf * 4]
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out, tone.astype(np.float32), SR, subtype="PCM_16")
    print(f"room tone: {len(tone) / SR:.1f} s at {20 * np.log10(np.sqrt((tone ** 2).mean())):.1f} dB (floor {floor:.1f} dB)")


if __name__ == "__main__":
    takes = load_takes(P)
    tone_file = P / "voice" / "ref" / "room-tone.wav"
    if not tone_file.exists():
        make_tone(takes, tone_file)
    tone, tsr = sf.read(tone_file)
    assert tsr == SR, "room-tone.wav must be 48 kHz"
    out_dir = P / "voice" / "takes" / "filled"
    out_dir.mkdir(exist_ok=True)
    for i, t in enumerate(takes):
        if sys.argv[1:] and t["id"] not in sys.argv[1:]:
            continue
        mp3 = P / "voice" / "takes" / f"{t['id']}.mp3"
        x = read(mp3)
        n = round(math.ceil((duration(mp3) + float(t.get("tail", CFG["tail"]))) * 30) / 30 * SR)   # the take's length on the timeline
        y = np.zeros(n); y[:min(n, len(x))] = x[:n]
        w = int(0.005 * SR); m = n // w                              # silent = a 5 ms level under -70 dB
        level = np.sqrt((y[:m * w].reshape(m, w) ** 2).mean(1))
        silent = np.concatenate([np.repeat(level < 10 ** (-70 / 20), w), np.full(n - m * w, True)])
        edges = np.flatnonzero(np.diff(np.concatenate([[0], silent.astype(int), [0]])))
        mask = np.zeros(n)
        for a, b in zip(edges[::2], edges[1::2]):
            if b - a >= 0.015 * SR:                                  # shorter stretches are left alone
                mask[a:b] = 1
        ramp = int(0.008 * SR)                                       # 8 ms in and out, so the floor does not click on
        mask = np.convolve(mask, np.ones(ramp) / ramp, mode="same")
        bed = np.resize(np.roll(tone, -int(((i * 1.37) % 6) * SR)), n)
        sf.write(out_dir / f"{t['id']}.wav", (y + bed * mask).astype(np.float32), SR, subtype="PCM_16")
        print(f"  {t['id']}  {n / SR:6.2f} s  filled {mask.mean() * 100:4.1f} %", flush=True)
