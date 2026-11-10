#!/usr/bin/env python3
"""script/takes.src.txt -> script/takes.json (what build_takes.py reads).

takes.src.txt is the source of truth for every spoken word. A take starts at its header line and runs
to the next header:

    o06 | The Orchestrator
    And here's why it matters for your wallet. Fable 5.2 costs 40 dollars per million tokens coming out.

    c03 | Where This Is Going | tail=1.6 freeze_at=8.63
    ... Have fun.

Header: id | section | optional settings. The id is one word (i01, n04). Then what the voice says, in
spoken forms ("40 dollars", "a dollar eighty-two", "A P I"): the voice reads symbols badly and the
fact-check needs the exact words. Blank lines inside a take are fine (one sentence per paragraph).
Lines starting with # are notes. Settings: `tail` = seconds of picture kept after the line (the last
take holds a beat), `freeze_at` = second of the take at which its picture holds still, `speech_rate`.
Order is file order, unless script/takes.order.txt lists ids in another order.

One avatar clip holds about 45 words. A longer take (up to about 85 words) still works, as two clips
joined at a pause: one more seam for the final reviewer to look at.

Usage:  python3 make_takes.py [--project <dir>]
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project import find_project

ONE_CLIP, TWO_CLIPS = 45, 85
SETTINGS = ("tail", "freeze_at", "speech_rate")
HEADER = re.compile(r"^\s*([A-Za-z][\w.-]*)\s*\|\s*(.*)$")

if "--help" in sys.argv or "-h" in sys.argv:
    sys.exit(__doc__)
here = find_project() / "script"
src = here / "takes.src.txt"
if not src.exists():
    sys.exit(f"no {src}: write the script there first (format: python3 make_takes.py --help)")
takes, cur = [], None
for n, line in enumerate(src.read_text().splitlines(), 1):
    if line.startswith("#") or not line.strip():
        continue
    m = HEADER.match(line)
    if m:
        head = [x.strip() for x in m.group(2).split("|")]
        if not head[0]:
            sys.exit(f"{src.name} line {n}: take {m.group(1)} has no section name (id | section | settings)")
        cur = {"id": m.group(1), "section": head[0], "say": [], "_line": n}
        for setting in (head[1].split() if len(head) > 1 else []):
            k, eq, v = setting.partition("=")
            try:
                if k not in SETTINGS or not eq:
                    raise ValueError
                cur[k] = float(v)
            except ValueError:
                sys.exit(f"{src.name} line {n}: cannot read the setting \"{setting}\" (use {', '.join(s + '=<number>' for s in SETTINGS)})")
        takes.append(cur)
    elif cur is None:
        sys.exit(f"{src.name} line {n}: text before the first take header. Every take starts with a line like  i01 | Intro")
    else:
        cur["say"].append(line.strip())
if not takes:
    sys.exit(f"{src.name} has no takes yet. Every take starts with a line like  i01 | Intro")
for t in takes:
    line = t.pop("_line")
    t["say"] = " ".join(t["say"])
    if not t["say"]:
        sys.exit(f"{src.name} line {line}: take {t['id']} has no words")
order = here / "takes.order.txt"
if order.exists():
    rank = {t: i for i, t in enumerate(order.read_text().split())}
    takes.sort(key=lambda t: rank.get(t["id"], 10**6))
ids = [t["id"] for t in takes]
dup = sorted({i for i in ids if ids.count(i) > 1})
if dup:
    sys.exit(f"duplicate take ids: {' '.join(dup)}")
(here / "takes.json").write_text(json.dumps(takes, indent=1))
words = {t["id"]: len(t["say"].split()) for t in takes}
two = [i for i, n in words.items() if ONE_CLIP < n <= TWO_CLIPS]
over = [i for i, n in words.items() if n > TWO_CLIPS]
print(f"{len(takes)} takes, {sum(words.values())} words, longest {max(words.values())} words")
if two:
    print(f"over {ONE_CLIP} words, will be two avatar clips joined at a pause: {' '.join(two)}")
if over:
    sys.exit(f"over {TWO_CLIPS} words, too long even for two clips, split them: {' '.join(over)}")
