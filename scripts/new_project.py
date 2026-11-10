#!/usr/bin/env python3
"""Start a video: the project folder, the screenplay work dir, the shared briefs and the run log.

Usage:  python3 new_project.py "<working title>" --project <project dir> --work <work dir>
  e.g.  python3 new_project.py "Claude Fable 5.2 Made This Video" \\
            --project "~/SaminOS/10 YouTube/Projects/2026-Q4 Fable 5.2 Release Video" \\
            --work "~/Borumi Projects/Fable 5.2 screenplay"
Nothing existing is overwritten. The presenter's photo is copied in from `photo_source` in
~/.config/one-prompt-video/defaults.json when that is set.
"""
import json
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
args = sys.argv[1:]
def opt(name):
    if name not in args or args.index(name) + 1 >= len(args):
        sys.exit(__doc__)
    i = args.index(name); v = args[i + 1]; del args[i:i + 2]
    return Path(v).expanduser().resolve()
P, W = opt("--project"), opt("--work")
if len(args) != 1:
    sys.exit(__doc__)
title, today = args[0], time.strftime("%b %-d, %Y")
for d in ("script/drafts", "research/sources", "research/transcripts", "proof/official", "proof/posts/media", "proof/community", "proof/live-test",
          "voice/ref", "voice/takes/alt", "avatar/ref", "avatar/takes/alt", "avatar/qa", "thumbnail", "refs/thumbnails", "logs", "Exports", "Resources", "edit"):
    (P / d).mkdir(parents=True, exist_ok=True)
for d in ("parts", "lanes", "media/own", "media/broll", "src", "tools", "review/v1", "out"):
    (W / d).mkdir(parents=True, exist_ok=True)
# Scenes name files relative to the work dir. Everything the research workers capture lives in the
# project's proof/ folder, so the work dir gets a link to it: `proof/official/x.png` works in the edit.
if not (W / "proof").exists() and not (W / "proof").is_symlink():
    (W / "proof").symlink_to(P / "proof", target_is_directory=True)
    print(f"linked {W / 'proof'} -> {P / 'proof'}")


def write_new(path, text):
    if not path.exists():
        path.write_text(text)
        print("wrote", path)


defaults = Path.home() / ".config/one-prompt-video/defaults.json"
cfg = json.loads(defaults.read_text()) if defaults.exists() else {}
write_new(P / "project.json", json.dumps({"title": title, "work": str(W)}, indent=1) + "\n")
src = Path(cfg.get("photo_source", "")).expanduser()
if cfg.get("photo_source") and src.exists() and not (P / cfg.get("photo", "avatar/ref/presenter.jpg")).exists():
    shutil.copyfile(src, P / cfg.get("photo", "avatar/ref/presenter.jpg"))
    print("copied the presenter's photo")
photo = P / cfg.get("photo", "avatar/ref/presenter.jpg")
if photo.exists() and not (W / "media" / "own" / photo.name).exists():
    shutil.copyfile(photo, W / "media" / "own" / photo.name)   # the edit shows the one real photo the avatar was made from
fill = lambda text: text.replace("{{TITLE}}", title).replace("{{P}}", str(P)).replace("{{W}}", str(W)).replace("{{TODAY}}", today).replace("{{PRESENTER}}", cfg.get("presenter", "the presenter"))
write_new(P / "BRIEF.md", fill((HERE.parent / "briefs" / "BRIEF.md").read_text()))
for name in ("WRITER.md", "REVIEWER.md", "FIXER.md", "FINAL-REVIEW.md"):
    write_new(W / name, fill((HERE.parent / "briefs" / name).read_text()))
write_new(W / "run-facts.md", fill((HERE.parent / "briefs" / "run-facts.md").read_text()))
write_new(W / "receipts.json", (HERE.parent / "briefs" / "receipts.json").read_text())
write_new(W / "edit.header.yaml", fill((HERE.parent / "briefs" / "edit.header.yaml").read_text()))
write_new(P / "logs" / "run-log.md", f"# Run log: {title}, {today}\n\nKept by the orchestrator. Times are local, from the machine's clock. Error lines are copied from the tools' own output.\n\n| Time | Event |\n|---|---|\n")
write_new(P / "script" / "takes.src.txt", "# One take per block: \"id | section\" on the header line, then what the voice says (spoken forms).\n# A take runs to the next header. 45 words or fewer fits one avatar clip; up to 85 becomes two.\n# Format and settings: python3 <skill>/scripts/make_takes.py --help\n\n")
for tool in ("lane.sh", "merge.sh"):
    if not (W / "tools" / tool).exists():
        shutil.copyfile(HERE / tool, W / "tools" / tool)
        (W / "tools" / tool).chmod(0o755)
print(f"\nproject: {P}\nwork:    {W}\nNext: save the prompt word for word as {W / 'media' / 'the-prompt.txt'}, fill in BRIEF.md "
      "(what the video is, who it is for, known starting points), then brief the research workers.")
