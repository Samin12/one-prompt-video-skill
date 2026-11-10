"""Shared by every script here: which project we are in, its settings, and small media helpers.

A project is a folder with a `project.json`. Scripts find it from `--project <dir>` (anywhere on the
command line), then `$OPV_PROJECT`, then the nearest parent of the current folder that has one.

Settings are read in three layers, later wins:
  1. the defaults below
  2. ~/.config/one-prompt-video/defaults.json   (the presenter's own ids: voice, photo, avatar prompt)
  3. <project>/project.json                      (this video: title, work dir, anything it overrides)

Layout inside a project (made by new_project.py):
  script/takes.src.txt, takes.json, must-hear.json      what the voice says
  voice/takes/<id>.mp3 (+ .job.json, .ok / .diff)        one read per take
  voice/ref/room-tone.wav                                 the voice's own quiet floor (fill_tone.py)
  avatar/ref/<photo>, avatar/takes/<id>.mp4               the photo and one clip per take
  avatar/camera.mov, mic.wav, takes-timeline.json         the assembled "recording"
"""
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

DEFAULTS = {
    "title": "",
    "work": "",                      # the screenplay work dir for this video
    "voice_model": "seed_audio",
    "voice_id": "",                  # Higgsfield voice id (a saved clone)
    "voice_type": "element",
    "speech_rate": -6,
    "target_wpm": 198,               # words a minute the presenter really speaks at
    "wpm_range": [170, 232],
    "avatar_model": "wan3_0",
    "image_id": "",                  # Higgsfield upload id of the photo (higgsfield upload create <photo>)
    "photo": "avatar/ref/presenter.jpg",
    "avatar_prompt": (
        "The person from @image1 talks straight to camera, saying the line in @audio1 with accurate lip "
        "sync, natural blinks, small head movements and relaxed, sparing hand gestures. Keep the face, the "
        "clothes, every object in the room and the lighting exactly as in the image. Static camera, medium shot."
    ),
    "resolution": "720p",
    "max_clip": 15,                  # longest avatar clip that renders with a voice reference (17 s jobs failed)
    "max_audio": 28.0,               # longest voice take: above max_clip it becomes two clips
    "gain_db": 2.0,                  # working-file level of the assembled track
    "tail": 0.18,                    # seconds of picture kept after a line
    # where the room shows around a centred presenter, as fractions of the frame: [x0, y0, x1, y1]
    # (the middle third of a 16:9 frame is what the camera tile shows). Pick patches the presenter never crosses.
    "room_regions": {"left": [0.326, 0.06, 0.40, 0.34], "right": [0.56, 0.20, 0.654, 0.55], "top": [0.34, 0.02, 0.64, 0.125]},
}
WHISPER_MODEL = Path.home() / ".cache/whisper/ggml-large-v3-turbo.bin"
CACHE = Path.home() / ".cache/one-prompt-video"


def _plain_errors(kind, err, tb):
    """A missing input or a failed step is said in one line: the step before this one has not run, or its
    output is somewhere else. Anything unexpected still shows its traceback."""
    if isinstance(err, FileNotFoundError):
        print(f"missing: {err.filename}\n  The step that writes it has not run yet (or run this inside the project, or pass --project <dir>).", file=sys.stderr)
    elif isinstance(err, RuntimeError):
        print(f"failed: {err}", file=sys.stderr)
    else:
        sys.__excepthook__(kind, err, tb)


sys.excepthook = _plain_errors


def find_project():
    argv = sys.argv
    if "--project" in argv:
        i = argv.index("--project")
        if i + 1 >= len(argv):
            sys.exit("--project needs a folder: --project <project dir>")
        p = Path(argv[i + 1]).expanduser()
        del argv[i:i + 2]
        return p.resolve()
    if os.environ.get("OPV_PROJECT"):
        return Path(os.environ["OPV_PROJECT"]).expanduser().resolve()
    for d in (Path.cwd(), *Path.cwd().parents):
        if (d / "project.json").exists():
            return d
    sys.exit("no project: pass --project <dir>, set OPV_PROJECT, or run inside a folder that has project.json")


def load_config(project):
    cfg = dict(DEFAULTS)
    for f in (Path.home() / ".config/one-prompt-video/defaults.json", project / "project.json"):
        if f.exists():
            cfg.update({k: v for k, v in json.loads(f.read_text()).items() if v not in ("", None)})
    return cfg


def work_dir(cfg):
    if not cfg.get("work"):
        sys.exit('project.json has no "work": set it to the screenplay work dir of this video')
    return Path(cfg["work"]).expanduser()


def run(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)


def duration(path):
    if not Path(path).exists():
        raise FileNotFoundError(2, "No such file", str(path))
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout.strip()
    if not out:
        raise RuntimeError(f"{path} is not a media file ffprobe can read")
    return float(out)


def frame_count(path):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", path])
    return int(r.stdout.strip())


def load_takes(project, ids=()):
    f = project / "script" / "takes.json"
    if not f.exists():
        sys.exit(f"no {f}: write script/takes.src.txt, then run make_takes.py")
    takes = json.loads(f.read_text())
    unknown = [i for i in ids if i not in {t["id"] for t in takes}]
    if unknown:
        sys.exit(f"no such take: {' '.join(unknown)}  (ids are in script/takes.json)")
    return [t for t in takes if not ids or t["id"] in ids]


def spoken(text):
    """Words as a transcriber would write them, for comparing a script line with what was heard:
    lower case, "$0.50" as "50 cents", "$8" as "8 dollars", "40%" as "40 percent", "100,000" as "100000"."""
    import re
    s = text.lower()
    s = re.sub(r"(?<=\d),(?=\d{3})", "", s)
    s = re.sub(r"\$0?\.(\d\d)\b", r"\1 cents", s)
    s = re.sub(r"\$(\d+(?:\.\d+)?)", r"\1 dollars", s)
    s = s.replace("%", " percent").replace("$", " dollars ")
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


def cached(name, url):
    """A file this skill needs but does not ship (a font, the world's coastlines): fetched once."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / name
    if not f.exists():
        urllib.request.urlretrieve(url, f)
    return f


def font_file(weight=700):
    return cached(f"Inter-{weight}.ttf", f"https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-{weight}-normal.ttf")


def out_time(segments, t, total):
    """Source second -> output second, through the cut in aroll.json (a second inside a cut lands on the next piece)."""
    for s in segments:
        if s["srcStart"] <= t <= s["srcEnd"]:
            return s["outStart"] + t - s["srcStart"]
    for s in segments:
        if s["srcStart"] > t:
            return s["outStart"]
    return total
