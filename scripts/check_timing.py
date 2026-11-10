#!/usr/bin/env python3
"""Has any word moved since the timeline was locked?

Part writers anchor scenes to word ids, which survive anything. But they also cut clips to word TIMES
(a B-roll reveal re-timed to land on a word, a screen recording trimmed to a sentence), and those go
out of step when the cut changes after they were made: a new `assemble`, a `holds:` entry, a word end
moved for scan_cuts.py. Run this after every later `screenplay aroll`.

It compares <work>/words.out.json with <work>/review/words.out.locked.json (parts.py keeps that copy
the first time it runs) and lists every place where time was added or removed: the word, the output
second, and how much. Everything after such a place shifts together, and scenes follow their words, so
only a clip that PLAYS ACROSS one of these places is out of step, from there on, by that amount.

  - Nothing moved: carry on.
  - Places you meant (a fix from scan_cuts.py, a hold at the very end): find the scene that is on screen
    at each one (`screenplay still <work> --at <word id>`). If it plays a clip that a writer cut to word
    times (the part's notes in lanes/<X>/plan.md say so), re-cut that clip or move its beat. Then --relock.
  - Places you did not mean: undo the change that caused them.

Usage:  python3 check_timing.py [--project <dir>] [--relock]
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project import find_project, load_config, work_dir

FRAME = 1 / 30
W = work_dir(load_config(find_project()))
now_file, locked_file = W / "words.out.json", W / "review" / "words.out.locked.json"
if "--relock" in sys.argv or not locked_file.exists():
    locked_file.parent.mkdir(exist_ok=True)
    shutil.copyfile(now_file, locked_file)
    sys.exit(f"locked: {locked_file} is now a copy of words.out.json")
now = {w["id"]: w for w in json.loads(now_file.read_text())}
locked = {w["id"]: w for w in json.loads(locked_file.read_text())}
gone, new = [i for i in locked if i not in now], [i for i in now if i not in locked]
if gone or new:
    print(f"word ids changed: {len(gone)} gone, {len(new)} new (first gone: {gone[:3]}, first new: {new[:3]})\n"
          "  The transcript or the cut list changed. Scenes anchored to those ids are broken: run `screenplay check`.")
moved = [(i, now[i]["start"] - w["start"]) for i, w in locked.items() if i in now and abs(now[i]["start"] - w["start"]) > FRAME]
if not moved and not gone and not new:
    print(f"no word moved more than a frame since the lock ({len(now)} words)")
    sys.exit(0)
if moved:
    clock = lambda t: f"{int(t // 60)}:{t % 60:04.1f}"
    steps, last = [], 0.0
    for i, w in locked.items():
        if i not in now:
            continue
        d = now[i]["start"] - w["start"]
        if abs(d - last) > FRAME:
            steps.append((i, d - last))
            last = d
    print(f"{len(moved)} of {len(locked)} words moved; time changed at {len(steps)} place(s):")
    for i, d in steps:
        print(f"  {i:>6}  {clock(now[i]['start'])}  {d:+.2f} s  before \"{now[i]['text']}\"")
    print(f"The video now ends at {clock(list(now.values())[-1]['end'])}. A clip that plays across one of these places and was cut to\n"
          "word times is out of step from there. Check each (see this script's notes), then --relock.")
sys.exit(1)
