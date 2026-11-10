---
name: one-prompt-video
description: Turn one prompt into a finished, fact-checked YouTube explainer presented by an AI avatar of Samin in his cloned voice, the way "Claude Fable 5.2 Made This Video From One Prompt" was made (Nov 2026). Claude Fable runs as the boss and hands the work to worker agents - research with real proof captures, script, an independent fact-check, Higgsfield voice and avatar takes, screenplay-engine motion graphics by parallel part writers, independent reviewers and fixers, a final-cut review, thumbnails - then adds his own candid opener, masters in Auphonic and uploads unlisted. Use this whenever Samin asks for a whole video from a prompt or while he is away - "make a video about X", "make a full video from this prompt", "make an avatar video", "clone me and make the video", "run a long task and make the video", "do it like the Fable 5.2 video" - and also to resume or redo one stage of such a video - "add my intro to the front", "redo that line", "the room changes in a take", "start the avatar from...", "re-render and upload".
---

# One-prompt video

One message from Samin in, a finished explainer out: researched, fact-checked, presented by an AI avatar
of him in his cloned voice, edited with motion graphics, with thumbnails. You are the boss. You plan,
write every brief, write the script, decide what the reviews mean, and assemble. Workers do the reading,
the graphics and the checking.

First run, Nov 9, 2026: a 10-minute video, 32 agents, 2,061 Higgsfield credits, 4 h 19 min from prompt to
file, then 45 min to put his opener on it. `examples/` holds that run's script, plan, one finished part
and the run log.

## Three promises

Everything below serves these. They are why a video like this can go out under his name.

1. **Everything on screen is true.** Outside facts are captures of the real page with the source under
   them. Numbers are the source's numbers. Anything about the production is in `run-facts.md` because it
   happened. Anything rebuilt says "Recreated" on itself. An agent that needs a number it cannot find
   leaves the beat simpler; it never fills the gap. See `references/truth.md`.
2. **It says what it is.** The presenter is an AI avatar with a cloned voice, and the viewer is told: a
   badge above the avatar for the whole video, the hand-off from his opener, the description, YouTube's
   AI label.
3. **Nothing goes public without him.** No upload, post, comment or link until he says so, and then
   unlisted. He makes it public.

## Names used everywhere

- `P`: the project folder. For Samin `~/SaminOS/10 YouTube/Projects/YYYY-Qn <Name>/`. It holds
  `project.json`, the script, research, proof, voice, avatar clips, logs and exports.
- `W`: the screenplay work dir, `~/Borumi Projects/<Name> screenplay`. It holds the edit. Paths inside
  scenes are relative to `W`. `W/proof` is a link to `P/proof`; everything else the edit shows is in
  `W/media/`.
- `<skill>`: this folder. **Every `scripts/` command is run inside `P`** as
  `python3 <skill>/scripts/<name>.py` (or from anywhere with `--project <P>`). `screenplay` commands take
  the work dir as an argument. Each script prints its usage with no arguments or `--help`.

## Before the first worker (about 10 minutes)

1. **Read the prompt for four things**: the topic, the twist (why this video exists), which model he
   wants as workers, and what he will film himself. Note the length he asked for (plan 195 spoken words
   and about 5 takes per minute).
2. **Settings.** `~/.config/one-prompt-video/defaults.json` holds his voice clone id, his photo's upload id
   and the avatar prompt (`config.example.json` shows the keys). No voice clone or photo yet: make them
   first, `references/voice-avatar.md`.
3. **Check the tools before you depend on them**: `higgsfield account status`, `screenplay --help`,
   `whisper-cli`, `ffmpeg`, `uv`, `node`, `yt-dlp`, `pdftoppm` (poppler; only for facts inside PDFs), and
   the proof-capture script named in `briefs/BRIEF.md`. Send each plan you mean to use a one-line task on
   the worker model: in the first run one of four plans could not run that model, and two research
   workers died on it.
4. **Credits.** Budget about 250 Higgsfield credits per minute of finished video. If the account is
   short, never buy credits and never switch to a cheaper avatar model without a pilot. Do every phase
   that costs nothing (1 to 4, the thumbnail concepts, the edit plan), stop before voice, and say so in
   the hand-over with the number he needs.
5. **Scaffold**: `python3 <skill>/scripts/new_project.py "<working title>" --project <P> --work <W>`. Then
   save his prompt word for word, typos and all, as `W/media/the-prompt.txt` (it goes on screen), and
   fill every `[[FILL: ...]]` in `P/BRIEF.md`.
6. **Start the run log** (`P/logs/run-log.md`): one line per event, with the tool's own error text. It is
   your memory after a context reset, and the video's "receipts" section is built from it.

## The run

Each phase ends at a gate. Do not pass a gate on a worker's word: open the file, the image, the still.

| # | Phase | Who | Gate to pass |
|---|---|---|---|
| 1 | Research, with proof captures | 5 workers at once | every claim you want has a capture you have opened |
| 2 | Run the how-to for real | you | the files, the log, the time and the cost are in `P/proof/live-test/` |
| 3 | Script | you | reads like him out loud; no take over 85 words; no point made twice |
| 4 | Fact-check | 1 worker | every `wrong` and `soften` line rewritten; `proof-map.json` complete |
| 5 | Voice | you (script) | `build_takes.py check` passes every take, or you have read and approved its diff |
| 6 | Lock the timeline, start the avatar clips | you (script) | `parts.py --words` differences all read; `scan_cuts.py` clean; `parts.md` written |
| 7 | Thumbnails and B-roll | 2 workers, alongside 5 to 8 | you opened every file at full size |
| 8 | Motion graphics | 1 writer per part, at once | merged edit: 0 errors; you read every contact sheet |
| 9 | Review and fix | 1 reviewer per 2 parts, then 1 fixer per part | every `must` and `should` done, seen in a still |
| 10 | Real avatar track | you (scripts) | `status` shows every clip ok; room check clean; `scan_cuts.py` and `check_timing.py` clean |
| 11 | Preview, final-cut review, final render | 1 reviewer, then you | `SHIP`, or every must fixed and seen; `check_takes.py` on the final file |
| 12 | Hand over | you | he has the file, the thumbnails, the upload sheet and the list of things only he can do |

One brief template per worker, in this order: `briefs/workers.md`. How to start workers, spread them over
his plans and keep count: `references/orchestration.md`.

### 1 to 4. From prompt to a script that is true

- Start all five research workers in one go: official facts, real posts, the how-to, his style, reactions
  and limits. The posts worker needs a browser that is logged in to X: give it a plan that has one.
  A style pack from an earlier video saves the style worker most of its time (`references/script.md`).
- While they read, do the how-to yourself (phase 2). A method nobody ran is not shown as if it was.
- Write the script as takes in `P/script/takes.src.txt` (format and voice rules:
  `references/script.md`), then `python3 <skill>/scripts/make_takes.py`.
- The fact-checker did not write the script and does not trust it. In the first run it found 2 wrong lines
  and 11 overstated ones in the boss's own draft. Rewrite all of them before any voice is made: a wrong
  word is free to fix now and costs a voice read, an avatar clip and a re-timed edit later.

### 5 to 7. Voice, timeline, avatar

The whole sequence, in order. What each step does and what to do when it complains:
`references/voice-avatar.md` (reads and clips) and `references/edit.md` (the lock).

```bash
cd <P>
python3 <skill>/scripts/build_takes.py voice             # one read per take
python3 <skill>/scripts/build_takes.py check             # every read against the script and script/must-hear.json
python3 <skill>/scripts/build_takes.py revoice n06 x04   # read the failed ones again
uv run --with numpy --with soundfile python3 <skill>/scripts/fill_tone.py
python3 <skill>/scripts/build_takes.py assemble          # avatar/camera.mov + mic.wav; the photo stands in for clips
python3 <skill>/scripts/build_takes.py avatar-loop       # in the background: a clip per take, 2 at a time

screenplay init <W> --camera <P>/avatar/camera.mov --mic <P>/avatar/mic.wav
screenplay transcribe <W>
python3 <skill>/scripts/parts.py --words                 # transcript against script; fix spellings in W/words.json
screenplay cut <W>                                       # then edit W/cuts.yaml: maxGap 0.3, false "retakes" into keep:
screenplay aroll <W>
uv run --with numpy --with soundfile python3 <skill>/scripts/scan_cuts.py    # fix, aroll again, until "clean"
screenplay brief <W> > <W>/brief.txt
python3 <skill>/scripts/parts.py                         # W/parts.md, the chapter anchors, and the timing lock
```

The timeline comes from the voice alone, so it is final before a single clip exists, and the writers
work while the clips render (about 3 minutes each). After this point never transcribe again: every
graphic is anchored to those word ids.

Thumbnail and B-roll workers share Higgsfield's queue of 3 jobs with the avatar clips. Their briefs tell
them to run one job at a time; `build_takes.py` waits out a full queue instead of failing.

### 8 and 9. Graphics, reviewed by someone else

- Write `W/plan.md` (the look, the assets, what each take should show: `examples/edit-plan.md`), fill
  `W/edit.header.yaml` with the chapters `parts.py` printed, and keep `W/run-facts.md` true. Fill the
  `[[FILL]]`s in `W/WRITER.md` and `REVIEWER.md`. Copy what the edit will show into `W/media/` (pilot
  clips, the three thumbnails, real screenshots of the run).
- One writer per part, all at once, each in its own lane (`tools/lane.sh <X> check|sheet|still`). A writer
  touches only its part.
- Merge (`tools/merge.sh`), `screenplay check <W>`, `screenplay sheet <W> --every 2s`, and read every
  sheet yourself before any reviewer does.
- Reviewers never review their own work. One per two parts. They return numbered items tagged
  `must` / `should` / `nice`; they fix nothing.
- You read every review, then decide. A reviewer says what is wrong; you say what replaces it and fetch
  what the fix needs (the first run swapped a rebuilt app window for a real screenshot, and a made-up
  brief for the real one). Then one fixer per part.

### 10 and 11. The checks that only work on the whole thing

Four faults passed every per-clip and per-part check in the first run and were caught only on the
assembled video (`references/lessons.md`, first section). Each now has a script.

```bash
cd <P>
python3 <skill>/scripts/build_takes.py status            # every clip "ok": none FAILED, none STALE
uv run --with numpy --with opencv-python-headless python3 <skill>/scripts/room_check.py      # the room drifts between takes
uv run --with numpy --with opencv-python-headless python3 <skill>/scripts/rerender_room.py w03 r03
python3 <skill>/scripts/build_takes.py assemble && screenplay aroll <W>
uv run --with numpy --with soundfile python3 <skill>/scripts/scan_cuts.py                      # a cut ate the end of a word
python3 <skill>/scripts/check_timing.py                  # did any word move since the lock
screenplay render <W> --preview -o <W>/out/preview-v1.mp4
python3 <skill>/scripts/review_aids.py                   # then brief the final-cut reviewer (briefs/workers.md, 12)
screenplay render <W> -o "<W>/out/<Title> v1.mp4"
python3 <skill>/scripts/check_takes.py "<W>/out/<Title> v1.mp4"                                # the file says the script
```

The final-cut reviewer is one more agent: put it in the agent count on the closing board before the
preview render. Its verdicts: `SHIP` (render the final), `SHIP AFTER MUSTS` (fix each must, look at each
fix in a preview of that stretch, then render), `DO NOT SHIP` (fix, a whole new preview, a new reviewer).

### 12. Hand over

In `P/Exports/`:

- the video, `YYYY-MM-DD <Title>.mp4`, with its `.srt` and chapter list
- `upload-sheet.md`: three title options (the style pack's patterns), the description (which part is the
  avatar, chapters, only the links he named), the thumbnail you would pick and why, and "altered or
  synthetic content: Yes"
- `HANDOVER.md`: the files, what is real and what is generated, what he should know before publishing
  (anything dated, any line reworded for the voice, anything on screen that could be misread), who
  checked what, what it cost, what is not done, and everything the video promises that he now has to
  do. Say plainly what no one has done: no agent has heard the audio.

## After the video: his opener, Auphonic, upload

- **His own candid clip in front**: build it as a separate screenplay work dir and join the two renders.
  Never prepend it to the main timeline (word ids would shift under every graphic).
  `references/opener.md`.
- **Auphonic and YouTube**: the `youtube-publish` skill does both, only when he says "upload", and
  unlisted. Its defaults are for his sponsored videos, so for this kind of video: no sponsor block and
  no paid-promotion tick unless he names a sponsor, a pinned comment only with links he named, and
  answer YouTube's altered-content question "Yes" on the Details step (that skill has no step for it).

## Rules that came from his corrections

- **No redundancy.** One point, once. The avatar does not repeat what his opener just said, and a later
  section does not re-explain an earlier one. He flags this more than anything else.
- **The avatar starts on the topic.** He cut a 9-second "that was the real one, I'm an AI clone" opening
  from the first video. Disclosure lives on screen; a spoken line, if any, is one sentence.
- **If his clip says something that is not what happened**, do not restate it as fact in a graphic.
  Label neutrally, keep the real record elsewhere in the video, and tell him. (He re-told the prompt on
  camera five hours after sending the real one; the checklist was titled "The ask" and the real text
  stayed labelled "as it arrived".)
- **No links he did not ask for.** He removed an affiliate link added "because he usually has it".
- **The avatar never says a name the voice cannot be checked on.** His own name goes on screen instead.
- **Replies to him**: short, plain, speakable, ending with "What's next" listing only what he must do.

## Reference files

| Read | When |
|---|---|
| `references/orchestration.md` | before starting any worker: plans, models, briefs, counting, the run log |
| `references/truth.md` | before the script, and again before writing `plan.md` |
| `references/script.md` | writing the takes |
| `references/voice-avatar.md` | voice clone, reads, avatar clips, the room check, limits, costs |
| `references/edit.md` | the lock, the header, the plan, parts and lanes, review, the end of the video |
| `references/opener.md` | he sends his own clip for the front |
| `references/lessons.md` | something looks or sounds wrong, or before the final checks |
| `briefs/workers.md` | writing any worker's brief |
