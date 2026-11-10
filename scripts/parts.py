#!/usr/bin/env python3
"""Split the locked timeline into parts for the part writers: <work>/parts.md.

Run after `screenplay aroll` and `screenplay brief`. Each take's words are found by time (the take's
place in avatar/takes-timeline.json against <work>/words.json), sections are grouped into parts of
about 60 to 115 seconds, and the file lists every part's first and last word id, its output times and
its takes with their word ranges. It also prints the chapter anchors (the first word of each section
after the first) for <work>/edit.header.yaml.

It also checks the transcript against the script, take by take, and lists every take whose words
differ: the gate "words.json matches the script". With --words that check is all it does, so it can run
right after `screenplay transcribe`, before the cut. And the first time it writes parts.md it keeps a
copy of words.out.json as <work>/review/words.out.locked.json, which check_timing.py compares against.

Usage:  python3 parts.py [--project <dir>] [--words] [--group "Intro+Why This Matters|What's New|..."]
  --words   only compare <work>/words.json with the script (needs avatar/takes-timeline.json)
  --group   sections joined with + make one part, | separates parts (default: grouped by length)
"""
import difflib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project import find_project, load_config, spoken, work_dir

P = find_project()
W = work_dir(load_config(P))
group = None
if "--group" in sys.argv:
    i = sys.argv.index("--group")
    if i + 1 >= len(sys.argv):
        sys.exit('--group needs the split: --group "Intro+Why This Matters|What\'s New|..."')
    group = [[s.strip() for s in part.split("+")] for part in sys.argv[i + 1].split("|")]
tl = json.loads((P / "avatar" / "takes-timeline.json").read_text())
src = json.loads((W / "words.json").read_text())


def compare_words(words):
    """Each take's transcript words against its script line. Number formats are folded together; what is
    left is a word the transcriber got wrong (fix its text in words.json) or dropped (transcribe again)."""
    bad = 0
    for t in tl:
        heard = " ".join(w["text"] for w in words if t["start"] <= (w["start"] + w["end"]) / 2 < t["end"])
        a, b = spoken(t["say"]), spoken(heard)
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        diffs = [f"[{' '.join(a[i1:i2])}]->[{' '.join(b[j1:j2])}]" for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]
        if diffs:
            bad += 1
            print(f"  {t['id']}  {sm.ratio():.2f}  {' '.join(diffs)}")
    print(f"transcript against script: {len(tl) - bad} of {len(tl)} takes word for word" + ("" if not bad else
          f"; {bad} differ (script]->[transcript). Fix spellings and names in words.json by hand. A take missing whole"
          f" words needs a new `screenplay transcribe` (try it with and without --whole) BEFORE any part is written."))
    return bad


if "--words" in sys.argv:
    sys.exit(1 if compare_words(src) else 0)
out = {w["src"]: w for w in json.loads((W / "words.out.json").read_text())}
kept = [w for w in src if w["i"] in out]


def clock(t):
    return f"{int(t // 60):02d}:{t % 60:04.1f}"

# every word belongs to the take whose span holds its middle (a transcriber's start time can sit just before the take)
takes = []
for t in tl:
    ws = [w for w in kept if t["start"] <= (w["start"] + w["end"]) / 2 < t["end"]]
    if not ws:
        sys.exit(f"take {t['id']} has no words in words.json: transcribe again, or check takes-timeline.json")
    first, last = out[ws[0]["i"]], out[ws[-1]["i"]]
    takes.append({**t, "w0": first["id"], "w1": last["id"], "o0": first["start"], "o1": last["end"]})
sections = []
for t in takes:
    if not sections or sections[-1]["name"] != t["section"]:
        sections.append({"name": t["section"], "takes": []})
    sections[-1]["takes"].append(t)
for s in sections:
    s["len"] = s["takes"][-1]["o1"] - s["takes"][0]["o0"]
if group:
    names = [n for g in group for n in g]
    if names != [s["name"] for s in sections]:
        sys.exit(f"--group must name every section once, in order: {' | '.join(s['name'] for s in sections)}")
    by = {s["name"]: s for s in sections}
    parts = [[by[n] for n in g] for g in group]
else:
    parts = []
    for s in sections:   # join a section to the part before it while the part stays under 115 s and either is short
        if parts and sum(x["len"] for x in parts[-1]) + s["len"] <= 115 and (sum(x["len"] for x in parts[-1]) < 60 or s["len"] < 45):
            parts[-1].append(s)
        else:
            parts.append([s])
letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lines = ["# Parts: word ranges and takes", "",
         "Times are output time (after the cut). A take is one voice line; its `w` range is where its words sit in `brief.txt`.",
         "Each part starts on its first word id and runs until the next part's first word id.", "",
         "| Part | Sections | First word | Last word | Output time | Length |", "|---|---|---|---|---|---|"]
for i, part in enumerate(parts):
    a, b = part[0]["takes"][0], part[-1]["takes"][-1]
    lines.append(f"| {letters[i]} | {', '.join(s['name'] for s in part)} | {a['w0']} | {b['w1']} | {clock(a['o0'])} to {clock(b['o1'])} | {b['o1'] - a['o0']:.0f} s |")
chapters = []
for i, part in enumerate(parts):
    lines += ["", f"## Part {letters[i]}"]
    for s in part:
        first = s is sections[0]
        lines += ["", f"**{s['name']}**" + ("" if first else f"  (chapter card at {s['takes'][0]['w0']})"), ""]
        if not first:
            chapters.append((s["takes"][0]["w0"], s["name"]))
        for t in s["takes"]:
            lines.append(f"- `{t['id']}`  {t['w0']} to {t['w1']}  [{clock(t['o0'])} to {clock(t['o1'])}]  {t['say']}")
(W / "parts.md").write_text("\n".join(lines) + "\n")
print(f"wrote {W / 'parts.md'}: {len(parts)} parts, {len(takes)} takes")
locked = W / "review" / "words.out.locked.json"
if not locked.exists():
    locked.parent.mkdir(exist_ok=True)
    shutil.copyfile(W / "words.out.json", locked)
    print(f"timeline locked: kept a copy of words.out.json as {locked.name} (check_timing.py compares against it)")
compare_words(kept)
for i, part in enumerate(parts):
    print(f"  {letters[i]}  {sum(s['len'] for s in part):4.0f} s  {', '.join(s['name'] for s in part)}")
print("\nchapters for edit.header.yaml (the first section has no card):")
for w, name in chapters:
    print(f'    - {{ at: {w}, title: "{name}" }}')
