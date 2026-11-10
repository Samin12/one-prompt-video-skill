#!/usr/bin/env python3
"""Build the presenter's "recording" from script takes: a cloned-voice read and an avatar clip per line.

    python3 build_takes.py voice   [ids...]   # one read per take (the saved voice clone); re-reads a take whose words changed
    python3 build_takes.py check   [ids...]   # transcribe each read: script words and script/must-hear.json phrases
    python3 build_takes.py revoice ids...     # read again (up to 5 times) until the must-hear phrases are heard
    python3 build_takes.py avatar  [ids...]   # one talking clip per take (photo + the read), 3 at a time
    python3 build_takes.py avatar-long ids... # a take longer than one clip: two clips joined at a pause
    python3 build_takes.py avatar-loop        # clips for takes as their reads pass the check, 2 at a time
    python3 build_takes.py assemble           # avatar/camera.mov + mic.wav + takes-timeline.json
    python3 build_takes.py status             # per take: read (ok / DIFF / STALE), clip (ok / FAILED / STALE)

Add `--project <dir>` or run inside the project (see project.py). Takes come from script/takes.json
(make_takes.py writes it). Every job's JSON is kept next to its output, so a re-run skips what is done.
Nothing is ever deleted: a replaced read or clip moves to takes/alt/.

A read passes when the transcript matches the script (0.97) AND every phrase listed for the take in
script/must-hear.json is heard. Otherwise it gets a .diff: read it, then `revoice <id>`, or approve it by
writing <id>.ok next to it. Changing a take's words makes its read STALE: `voice <id>` reads it again.
A clip whose read is newer than it is STALE: move its .mp4 and .job.json to avatar/takes/alt/ and run
`avatar <id>`. A clip job that failed leaves avatar/takes/<id>.failed with the error: `avatar <id>` tries again.

The Higgsfield account runs 3 jobs at a time across everything that uses it: a full queue is waited
out, never treated as a failure.
"""
import concurrent.futures as cf
import difflib
import json
import math
import re
import shutil
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project import WHISPER_MODEL, duration, find_project, load_config, run, spoken
from project import load_takes as _load_takes

P = find_project()
CFG = load_config(P)
VOICE_DIR = P / "voice" / "takes"
AVATAR_DIR = P / "avatar" / "takes"
VOICE_MODEL, VOICE_ID, VOICE_TYPE = CFG["voice_model"], CFG["voice_id"], CFG["voice_type"]
IMAGE_ID, AVATAR_MODEL, AVATAR_PROMPT = CFG["image_id"], CFG["avatar_model"], CFG["avatar_prompt"]
MAX_AUDIO, MAX_CLIP = float(CFG["max_audio"]), int(CFG["max_clip"])
AUTO_OK = 0.97  # transcript similarity above which a read needs no read-through
GAIN_DB = float(CFG["gain_db"])  # working-file level only: `screenplay aroll --lufs` sets the finished track's loudness
TARGET_WPM, WPM_RANGE = CFG["target_wpm"], tuple(CFG["wpm_range"])
DEFAULT_TAIL = float(CFG["tail"])
_must = P / "script" / "must-hear.json"
MUST = json.loads(_must.read_text()) if _must.exists() else {}   # take id -> phrases that must be heard word for word


def said_file(tid):
    """The exact words the current read was asked to say. Lets every later step see a reworded take."""
    return VOICE_DIR / f"{tid}.said.txt"


def read_is_stale(t):
    f = said_file(t["id"])
    return f.exists() and f.read_text().strip() != t["say"].strip()


def clip_is_stale(t):
    a, v = VOICE_DIR / f"{t['id']}.mp3", AVATAR_DIR / f"{t['id']}.mp4"
    return a.exists() and v.exists() and a.stat().st_mtime > v.stat().st_mtime + 1


def missing_phrases(t, heard):
    words = " " + " ".join(spoken(heard)) + " "
    return [ph for ph in MUST.get(t["id"], []) if " " + " ".join(spoken(ph)) + " " not in words]


def shelve(folder, tid, exts, tag):
    """Moves a take's files into alt/ under a dated name. Nothing is deleted."""
    stamp = time.strftime("%H%M%S")
    for ext in exts:
        old = folder / f"{tid}.{ext}"
        if old.exists():
            old.rename(folder / "alt" / f"{tid}.{tag}-{stamp}.{ext}")


def load_takes(ids):
    return _load_takes(P, ids)


def need(*keys):
    missing = [k for k in keys if not CFG.get(k)]
    if missing:
        sys.exit(f"missing in project.json or ~/.config/one-prompt-video/defaults.json: {', '.join(missing)}")


def job_of(path):
    data = json.loads(Path(path).read_text())
    return data[0] if isinstance(data, list) else data


def create(job_type, args, out_json):
    """Runs one Higgsfield job to completion and keeps its JSON. Returns the job dict.

    The account runs 3 jobs at a time across every tool that uses it, so a full queue is normal:
    wait and try again instead of failing the take.
    """
    for attempt in range(90):
        r = run(["higgsfield", "generate", "create", job_type, *args, "--wait", "--wait-timeout", "30m", "--json"])
        if "rate_limit_reached" not in (r.stderr + r.stdout):
            break
        time.sleep(20)
    if r.returncode != 0 or not r.stdout.strip().startswith(("[", "{")):
        raise RuntimeError(f"{job_type} failed: {(r.stderr or r.stdout)[-400:]}")
    out_json.write_text(r.stdout)
    job = job_of(out_json)
    if job.get("status") != "completed" or not job.get("result_url"):
        raise RuntimeError(f"{job_type} ended as {job.get('status')}: {out_json}")
    return job


def words_per_minute(text, secs):
    return len(text.split()) / secs * 60


def voice_one(t):
    """One line in the cloned voice. The model's pace swings between runs (173 to 244 words a minute on
    the same sentence), so a line outside his natural range is read again at another rate and the take
    closest to TARGET_WPM is kept. Earlier reads stay in voice/takes/alt/."""
    mp3, js = VOICE_DIR / f"{t['id']}.mp3", VOICE_DIR / f"{t['id']}.job.json"
    alt = VOICE_DIR / "alt"
    alt.mkdir(exist_ok=True)
    reworded = mp3.exists() and read_is_stale(t)
    if reworded:   # the words changed after this read was made: keep the old read in alt/, read the new words
        shelve(VOICE_DIR, t["id"], ("mp3", "job.json", "ok", "diff", "heard.txt", "said.txt"), "old-words")
    if mp3.exists() and js.exists():
        return t["id"], duration(mp3), "kept"
    rate, tries = int(t.get("speech_rate", CFG["speech_rate"])), []
    for n in range(3):
        a_mp3, a_js = alt / f"{t['id']}.r{rate}.{n}.mp3", alt / f"{t['id']}.r{rate}.{n}.job.json"
        job = create(VOICE_MODEL, ["--prompt", t["say"], "--voice_id", VOICE_ID, "--voice_type", VOICE_TYPE,
                                    "--format", "mp3", "--sample_rate", "48000", "--speech_rate", str(rate)], a_js)
        urllib.request.urlretrieve(job["result_url"], a_mp3)
        wpm = words_per_minute(t["say"], duration(a_mp3))
        tries.append((abs(wpm - TARGET_WPM), wpm, a_mp3, a_js))
        if WPM_RANGE[0] <= wpm <= WPM_RANGE[1]:
            break
        rate = rate - 8 if wpm > WPM_RANGE[1] else rate + 6
    _, wpm, best_mp3, best_js = min(tries)
    shutil.copyfile(best_mp3, mp3)
    shutil.copyfile(best_js, js)
    said_file(t["id"]).write_text(t["say"] + "\n")
    return t["id"], duration(mp3), f"{'re-read (words changed)' if reworded else 'new'}, {wpm:.0f} wpm, {len(tries)} read(s)"


def avatar_one(t):
    mp4, js = AVATAR_DIR / f"{t['id']}.mp4", AVATAR_DIR / f"{t['id']}.job.json"
    if mp4.exists() and js.exists():
        return t["id"], duration(mp4), "kept"
    audio = VOICE_DIR / f"{t['id']}.mp3"
    if duration(audio) > MAX_CLIP - 0.3:   # too long for one clip: two clips joined at a pause
        return avatar_long(t)
    # long enough for the line plus the footage kept after it (the last line holds a beat)
    secs = max(2, min(MAX_CLIP, math.ceil(duration(audio) + max(0.25, float(t.get("tail", DEFAULT_TAIL)) + 0.1))))
    args = ["--prompt", t.get("avatar_prompt", AVATAR_PROMPT), "--image-references", IMAGE_ID,
            "--audio-references", job_of(VOICE_DIR / f"{t['id']}.job.json")["id"],
            "--resolution", CFG["resolution"], "--duration", str(secs), "--generate_audio", "false", "--aspect_ratio", "16:9"]
    job = create(AVATAR_MODEL, args, js)
    urllib.request.urlretrieve(job["result_url"], mp4)
    shelve(AVATAR_DIR, t["id"], ("failed",), "failed")
    return t["id"], duration(mp4), "new"


def quiet_split(mp3):
    """Where a long line is split in two: the quiet moment nearest its middle that leaves both halves
    short enough for one clip (Wan 3.0 jobs with a voice reference fail above 15 s)."""
    r = run(["ffmpeg", "-v", "info", "-i", str(mp3), "-af", "silencedetect=noise=-32dB:d=0.10", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r.stderr)]
    total = duration(mp3)
    gaps = [((a + b) / 2, b - a) for a, b in zip(starts, ends)]
    fits = [(m, length) for m, length in gaps if m <= MAX_CLIP - 0.3 and total - m <= MAX_CLIP - 0.3]
    if not fits:
        raise RuntimeError(f"{mp3.name}: no quiet moment that leaves both halves under {MAX_CLIP} s")
    # the longest pause wins (a sentence end), unless it sits far from the middle
    return max(fits, key=lambda g: g[1] - 0.08 * abs(g[0] - total / 2))[0]


def avatar_long(t):
    """A line longer than one clip: two clips, cut at a pause, joined so the take keeps its full length."""
    tid = t["id"]
    mp4, js, audio = AVATAR_DIR / f"{tid}.mp4", AVATAR_DIR / f"{tid}.job.json", VOICE_DIR / f"{tid}.mp3"
    if mp4.exists() and js.exists():
        return tid, duration(mp4), "kept"
    at = quiet_split(audio)
    jobs, clips = [], []
    for name, cut in (("a", ["-t", f"{at:.3f}"]), ("b", ["-ss", f"{at:.3f}"])):
        part_audio, part_mp4 = AVATAR_DIR / f"{tid}.{name}.mp3", AVATAR_DIR / f"{tid}.{name}.mp4"
        part_js = AVATAR_DIR / f"{tid}.{name}.job.json"
        if not (part_mp4.exists() and part_js.exists()):
            run(["ffmpeg", "-v", "error", "-y", "-i", str(audio), *cut, "-c:a", "libmp3lame", "-q:a", "2", str(part_audio)])
            secs = max(2, min(MAX_CLIP, math.ceil(duration(part_audio) + 0.25)))
            job = create(AVATAR_MODEL, ["--prompt", AVATAR_PROMPT, "--image-references", IMAGE_ID,
                                        "--audio-references", str(part_audio), "--resolution", CFG["resolution"],
                                        "--duration", str(secs), "--generate_audio", "false", "--aspect_ratio", "16:9"], part_js)
            urllib.request.urlretrieve(job["result_url"], part_mp4)
        jobs.append(job_of(part_js))
        clips.append(part_mp4)
    frames_a = round(at * 30)
    r = run(["ffmpeg", "-v", "error", "-y", "-i", str(clips[0]), "-i", str(clips[1]), "-filter_complex",
             f"[0:v]fps=30,scale=1280:720,trim=end_frame={frames_a},setpts=PTS-STARTPTS[a];"
             f"[1:v]fps=30,scale=1280:720,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1[v]",
             "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(mp4)])
    if r.returncode != 0:
        raise RuntimeError(f"{tid}: join failed: {r.stderr[-300:]}")
    js.write_text(json.dumps({"id": tid, "status": "completed", "split_at": round(at, 3), "parts": jobs}, indent=1))
    shelve(AVATAR_DIR, tid, ("failed",), "failed")
    return tid, duration(mp4), f"new, two clips joined at {at:.2f} s"


def fan_out(fn, takes, workers):
    failed = []
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fn, t): t for t in takes}
        for f in cf.as_completed(futures):
            t = futures[f]
            try:
                tid, secs, state = f.result()
                print(f"  {tid}  {secs:6.2f} s  {state}", flush=True)
            except Exception as e:  # keep going; the rest of the batch is independent
                failed.append(t["id"])
                print(f"  {t['id']}  FAILED  {e}", flush=True)
    return failed


norm = spoken   # "$0.50" and "50 cents" compare equal; so do "100,000" and "100000"


def hear(t, mp3=None):
    """Transcribes one voice take. Returns (heard text, similarity 0..1 against what it was asked to say)."""
    mp3 = mp3 or VOICE_DIR / f"{t['id']}.mp3"
    wav = VOICE_DIR / "alt" / f"{t['id']}.{time.time_ns()}.16k.wav"
    wav.parent.mkdir(exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-ar", "16000", "-ac", "1", str(wav)])
    run(["whisper-cli", "-m", str(WHISPER_MODEL), "-l", "en", "-np", "-oj", "-f", str(wav), "-of", str(wav.with_suffix(""))])
    heard = " ".join(s["text"].strip() for s in json.loads(wav.with_suffix(".json").read_text())["transcription"])
    wav.unlink()
    wav.with_suffix(".json").unlink()
    (VOICE_DIR / f"{t['id']}.heard.txt").write_text(heard + "\n")
    return heard, difflib.SequenceMatcher(None, norm(t["say"]), norm(heard)).ratio()


def verdict(t):
    """ok = the voice said the line. A take is ok when whisper hears it almost word for word, or when
    someone has read the difference and approved it (an .ok file next to the take)."""
    ok, diff = VOICE_DIR / f"{t['id']}.ok", VOICE_DIR / f"{t['id']}.diff"
    if read_is_stale(t):   # an approval of the old words says nothing about the new ones
        return False
    if ok.exists():
        return True
    if diff.exists():
        return False
    heard, score = hear(t)
    missing = missing_phrases(t, heard)
    if score >= AUTO_OK and not missing:
        ok.write_text(f"auto {score:.3f}\n")
        return True
    diff.write_text(f"score {score:.3f}\n" + (f"not heard: {' | '.join(missing)}\n" if missing else "") + f"said : {t['say']}\nheard: {heard}\n")
    return False


def revoice(takes):
    """Re-reads lines the transcriber did not hear right: up to 5 reads each, keeps the best one.
    script/must-hear.json maps take id -> phrases that have to be heard word for word (names, numbers, key terms).
    A re-read passes at 0.90 when every one of those phrases is heard (the phrases are the stricter test).
    The finished take is put in place last (after its .ok), so the avatar loop never sees half of it."""
    alt = VOICE_DIR / "alt"
    alt.mkdir(exist_ok=True)
    for t in takes:
        tid, stamp = t["id"], time.strftime("%H%M%S")
        shelve(VOICE_DIR, tid, ("mp3", "job.json", "diff", "ok", "heard.txt", "said.txt"), "before")
        best = None
        for n, rate in enumerate((-6, -10, -6, -12, -8)):
            c_mp3, c_js = alt / f"{tid}.re{stamp}.{n}.mp3", alt / f"{tid}.re{stamp}.{n}.job.json"
            job = create(VOICE_MODEL, ["--prompt", t["say"], "--voice_id", VOICE_ID, "--voice_type", VOICE_TYPE,
                                        "--format", "mp3", "--sample_rate", "48000", "--speech_rate", str(rate)], c_js)
            urllib.request.urlretrieve(job["result_url"], c_mp3)
            heard, score = hear(t, c_mp3)
            said_all = not missing_phrases(t, heard)
            wpm = words_per_minute(t["say"], duration(c_mp3))
            print(f"  {tid} read {n}: score {score:.3f}  phrases {'yes' if said_all else 'NO'}  {wpm:.0f} wpm\n      heard: {heard}", flush=True)
            in_pace = WPM_RANGE[0] - 30 <= wpm <= WPM_RANGE[1]
            rank = (said_all, in_pace, round(score, 2), -abs(wpm - TARGET_WPM))
            if best is None or rank > best[0]:
                best = (rank, c_mp3, c_js, heard, score, said_all)
            if said_all and score >= 0.94 and WPM_RANGE[0] - 15 <= wpm <= WPM_RANGE[1]:
                break
        _, c_mp3, c_js, heard, score, said_all = best
        shutil.copyfile(c_js, VOICE_DIR / f"{tid}.job.json")
        if said_all and score >= 0.90:
            (VOICE_DIR / f"{tid}.ok").write_text(f"re-read, score {score:.3f}, required phrases heard\n")
        else:
            (VOICE_DIR / f"{tid}.diff").write_text(f"score {score:.3f}\nsaid : {t['say']}\nheard: {heard}\n")
        said_file(tid).write_text(t["say"] + "\n")
        shutil.copyfile(c_mp3, VOICE_DIR / f"{tid}.mp3")
        print(f"  {tid} kept: score {score:.3f}, {'ok' if said_all and score >= 0.90 else 'NEEDS A READ'}", flush=True)


def check(takes):
    """Transcribes each line and reports the word differences against what it was asked to say."""
    open_takes = []
    for t in takes:
        mp3 = VOICE_DIR / f"{t['id']}.mp3"
        if not mp3.exists():
            print(f"  {t['id']}  no audio yet")
            open_takes.append(t["id"])
            continue
        if read_is_stale(t):
            print(f"  {t['id']}  STALE: the words changed after this read. Run: build_takes.py voice {t['id']}")
            open_takes.append(t["id"])
            continue
        good = verdict(t)
        secs = duration(mp3)
        flag = "" if secs <= MAX_AUDIO else "  TOO LONG"
        print(f"  {t['id']}  {secs:5.1f} s  {words_per_minute(t['say'], secs):3.0f} wpm  {'ok' if good else 'DIFF'}{flag}")
        if not good:
            open_takes.append(t["id"])
            print("      " + (VOICE_DIR / f"{t['id']}.diff").read_text().replace("\n", "\n      ").rstrip())
    if open_takes:
        print(f"\n{len(open_takes)} of {len(takes)} not passed. Read each DIFF: `revoice <id>` to read again, or approve it by writing voice/takes/<id>.ok")
    return open_takes


def avatar_loop(takes):
    """Keeps making avatar clips as voice takes arrive and pass the check, until every take has one.
    Stops early when nothing new has become ready for 15 minutes (takes waiting on a read-through)."""
    idle_since = time.time()
    with cf.ThreadPoolExecutor(max_workers=2) as pool:
        running = {}
        while True:
            for tid, f in list(running.items()):
                if f.done():
                    del running[tid]
                    try:
                        _, secs, state = f.result()
                        print(f"  {tid}  {secs:6.2f} s  {state}", flush=True)
                    except Exception as e:
                        print(f"  {tid}  FAILED  {e}", flush=True)
                        (AVATAR_DIR / f"{tid}.failed").write_text(str(e))
            todo = [t for t in takes if not (AVATAR_DIR / f"{t['id']}.mp4").exists()
                    and not (AVATAR_DIR / f"{t['id']}.failed").exists() and t["id"] not in running]
            if not todo and not running:
                failed = [t["id"] for t in takes if (AVATAR_DIR / f"{t['id']}.failed").exists() and not (AVATAR_DIR / f"{t['id']}.mp4").exists()]
                if failed:
                    print(f"{len(failed)} clip(s) FAILED: {' '.join(failed)}\n  The error is in avatar/takes/<id>.failed. Try again with: build_takes.py avatar {' '.join(failed)}", flush=True)
                    return failed
                print("all avatar clips done", flush=True)
                return []
            for t in todo:
                if len(running) >= 2:
                    break
                if (VOICE_DIR / f"{t['id']}.mp3").exists() and verdict(t):
                    running[t["id"]] = pool.submit(avatar_one, t)
                    idle_since = time.time()
            if running:
                idle_since = time.time()
            elif time.time() - idle_since > 900:
                waiting = [t["id"] for t in todo]
                print(f"stopping: nothing ready for 15 minutes; waiting on {' '.join(waiting)}", flush=True)
                return waiting
            time.sleep(15)


def assemble(takes):
    """Each take: the clip trimmed to its line, the clean voice file as its audio. Then one file.

    A take's length comes from its voice file alone (rounded up to a whole frame), so the timeline is the
    same whether or not its avatar clip exists yet: a missing clip is filled with the photo, which
    lets the edit be written against final timing while the clips are still rendering."""
    out_dir = P / "avatar" / "assembled"
    out_dir.mkdir(exist_ok=True)
    still = P / CFG["photo"]
    parts, timeline, at, missing = [], [], 0.0, []
    for t in takes:
        v, a = AVATAR_DIR / f"{t['id']}.mp4", VOICE_DIR / f"{t['id']}.mp3"
        frames = math.ceil((duration(a) + float(t.get("tail", DEFAULT_TAIL))) * 30)
        secs = frames / 30
        part = out_dir / f"{t['id']}.mov"
        video_in = ["-i", str(v)] if v.exists() else ["-loop", "1", "-framerate", "30", "-i", str(still)]
        if not v.exists():
            missing.append(t["id"])
        # "freeze_at": the picture holds that frame to the end of the take (the last line, see make_takes.py)
        freeze = f"trim=end_frame={round(float(t['freeze_at']) * 30)},setpts=PTS-STARTPTS," if v.exists() and t.get("freeze_at") else ""
        # voice/takes/filled/<id>.wav (fill_tone.py) is the same line with its silent head, tail and padding filled
        # with the voice's own quiet floor: digital silence between takes sounds like the track switching off
        filled = VOICE_DIR / "filled" / f"{t['id']}.wav"
        if filled.exists() and filled.stat().st_mtime >= a.stat().st_mtime:
            a = filled
        r = run(["ffmpeg", "-v", "error", "-y", *video_in, "-i", str(a),
                 "-filter_complex",
                 f"[0:v]fps=30,{freeze}scale=1920:1080:flags=lanczos,format=yuv420p,tpad=stop_mode=clone:stop_duration=4[v];"
                 f"[1:a]aresample=48000,volume={GAIN_DB}dB,apad,atrim=0:{secs:.6f}[a]",
                 "-map", "[v]", "-map", "[a]", "-frames:v", str(frames),
                 "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-c:a", "pcm_s16le", "-ac", "1", str(part)])
        if r.returncode != 0:
            raise RuntimeError(f"{t['id']}: {r.stderr[-300:]}")
        parts.append(part)
        timeline.append({"id": t["id"], "section": t.get("section"), "start": round(at, 4), "end": round(at + secs, 4),
                         "say": t["say"]})
        at += secs
    lst = out_dir / "concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    cam = P / "avatar" / "camera.mov"
    r = run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(cam)])
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-300:])
    run(["ffmpeg", "-v", "error", "-y", "-i", str(cam), "-vn", "-c:a", "pcm_s16le", str(P / "avatar" / "mic.wav")])
    (P / "avatar" / "takes-timeline.json").write_text(json.dumps(timeline, indent=1))
    print(f"camera.mov  {duration(cam):.2f} s (planned {at:.2f} s) from {len(parts)} takes"
          + (f"; photo placeholder for {len(missing)}: {' '.join(missing)}" if missing else "; every take has its avatar clip"))
    stale = [t["id"] for t in takes if clip_is_stale(t)]
    if stale:
        print(f"WARNING: the read is newer than the clip (lips will not match): {' '.join(stale)}\n"
              f"  Move each <id>.mp4 and <id>.job.json to avatar/takes/alt/, then: build_takes.py avatar {' '.join(stale)}")


def status(takes):
    """Where every take stands. Read: ok (passed or approved), DIFF (needs a read-through), STALE (words
    changed since), new (not checked yet). Clip: ok, FAILED (see <id>.failed), STALE (older than its read)."""
    count = {"reads ok": 0, "clips ok": 0}
    for t in takes:
        tid = t["id"]
        a, v = VOICE_DIR / f"{tid}.mp3", AVATAR_DIR / f"{tid}.mp4"
        if not a.exists():
            read = "-"
        elif read_is_stale(t):
            read = "STALE"
        elif (VOICE_DIR / f"{tid}.ok").exists():
            read = "ok"
        elif (VOICE_DIR / f"{tid}.diff").exists():
            read = "DIFF"
        else:
            read = "new"
        if v.exists():
            clip = "STALE" if clip_is_stale(t) else "ok"
        else:
            clip = "FAILED" if (AVATAR_DIR / f"{tid}.failed").exists() else "-"
        count["reads ok"] += read == "ok"
        count["clips ok"] += clip == "ok"
        print(f"  {tid}  voice {'%5.1f s' % duration(a) if a.exists() else '   -   '} {read:5}  "
              f"avatar {'%5.1f s' % duration(v) if v.exists() else '   -   '} {clip:6}  {t['say'][:52]}")
    print(f"\n{len(takes)} takes: {count['reads ok']} reads ok, {count['clips ok']} clips ok")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, ids = sys.argv[1], sys.argv[2:]
    for d in (VOICE_DIR / "alt", AVATAR_DIR / "alt"):
        d.mkdir(parents=True, exist_ok=True)
    takes = load_takes(ids)
    if cmd in ("voice", "revoice"):
        need("voice_id")
    if cmd.startswith("avatar"):
        need("image_id")
    if cmd == "voice":
        failed = fan_out(voice_one, takes, 2)
    elif cmd == "avatar":
        failed = fan_out(avatar_one, takes, 3)
    elif cmd == "avatar-long":
        failed = fan_out(avatar_long, takes, 1)
    elif cmd == "avatar-loop":
        failed = avatar_loop(takes)
    elif cmd == "revoice":
        if not ids:
            sys.exit("revoice needs take ids: it reads only the takes you name")
        failed = revoice(takes)
    elif cmd == "check":
        failed = check(takes)
    elif cmd == "assemble":
        failed = assemble(takes)
    elif cmd == "status":
        failed = status(takes)
    else:
        sys.exit(__doc__)
    if failed:
        sys.exit(f"failed: {' '.join(failed)}")


if __name__ == "__main__":
    main()
