#!/usr/bin/env python3
"""Two small files the final-cut reviewer needs: where each take starts, and where two-clip takes join.

Writes <work>/review/take-starts.json  [[take id, output second], ...]
   and <work>/review/long-take-joins.json  [[take id, seconds into the take, output second of the join], ...]
Run after the final `screenplay aroll`. Add --offset S when other material sits in front of the main video.

Usage:  python3 review_aids.py [--project <dir>] [--offset S]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project import find_project, load_config, out_time, work_dir

P = find_project()
offset = float(sys.argv[sys.argv.index("--offset") + 1]) if "--offset" in sys.argv else 0.0
W = work_dir(load_config(P))
tl = json.loads((P / "avatar" / "takes-timeline.json").read_text())
aroll = json.loads((W / "aroll.json").read_text())
at = lambda t: round(out_time(aroll["segments"], t, aroll["duration"]) + offset, 1)
(W / "review").mkdir(exist_ok=True)
(W / "review" / "take-starts.json").write_text(json.dumps([[t["id"], at(t["start"])] for t in tl]))
joins = []
for t in tl:
    job = P / "avatar" / "takes" / f"{t['id']}.job.json"
    if job.exists():
        split = json.loads(job.read_text())
        split = split.get("split_at") if isinstance(split, dict) else None
        if split:
            joins.append([t["id"], split, at(t["start"] + split)])
(W / "review" / "long-take-joins.json").write_text(json.dumps(joins))
print(f"{len(tl)} take starts, {len(joins)} mid-take joins -> {W / 'review'}")
