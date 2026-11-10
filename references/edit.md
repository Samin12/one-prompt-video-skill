# The edit

The video is built with the screenplay engine (`screenplay` CLI, `~/SaminOS/Projects/screenplay`). The
assembled avatar track is treated as a recording: the engine cuts it, and every graphic is a scene in
YAML anchored to a spoken word. The engine's own rules are in the `screenplay-edit` skill and
`docs/EDIT-YAML.md`; this file is what is different when the "recording" is an avatar and the edit is
written by seven agents at once.

`W` is the work dir. `screenplay` commands take it as an argument. The skill's own scripts run inside
the project folder `P` (`python3 <skill>/scripts/<name>.py`).

## 1. Lock the timeline

Do this as soon as every voice read has passed and `fill_tone.py` and `assemble` have run, before the
avatar clips exist. The command sequence is in `SKILL.md` ("5 to 7"); this is what each step is for.
The order matters: everything after a step is built on it.

1. **`screenplay init`, then `screenplay transcribe <W>`.** One word list for the whole track,
   `W/words.json`. Word ids (`w123`) are how every scene finds its moment.
2. **`parts.py --words`: the transcript against the script.** It lists every take whose words differ.
   Number formats are folded together already, so what is left is real:
   - a name or term spelled wrong ("Cloud Code"): fix the `text` in `W/words.json` by hand. Writers copy
     on-screen text from `brief.txt`, so a wrong spelling here ends up on screen.
   - a take with words missing: the transcriber dropped or repeated a stretch. Run `transcribe` again
     with `--force` (and try `--whole`, one pass instead of chunks: the first run's final list came from
     `--whole` after the chunked pass). Either mode can slip, which is why this check exists.
   After this step never transcribe again: a new transcript renumbers the words under finished parts.
3. **`screenplay cut <W>`, then edit `W/cuts.yaml`** before anything reads it:
   - `maxGap: 0.3` (the engine writes 0.55; a read voice wants tighter pauses), leave `midGap: 0.9`.
   - A cloned voice has no retakes, so every "retake" under `cuts:` is a false alarm (the first run's was
     three parallel sentences in a list). Copy each into `keep:`.
4. **`screenplay aroll <W>`, then `scan_cuts.py`** until it prints "clean" (section 6). Doing this now
   means the timing the writers work against is the timing that ships.
5. **`screenplay brief <W> > <W>/brief.txt`**: the words with their ids and output times.
6. **`parts.py`**: groups sections into parts of 60 to 115 seconds, writes `W/parts.md`, prints the
   chapter list for the header, and keeps a copy of `words.out.json` as the lock. Use
   `--group "Intro+Why This Matters|What's New|..."` to choose the split yourself. Seven parts for ten
   minutes was right: a part is what one writer can hold and check carefully.

From here on, after any `assemble` or `aroll`, run `check_timing.py`. It lists each place where time was
added or removed. Scenes follow their words, so only a clip that plays across such a place and was cut
to word times is affected; the script says what to do.

## 2. The header

`W/edit.header.yaml` is the top of the edit, shared by every part and edited only by you
(`new_project.py` writes a starter; add the chapter items `parts.py` printed, each with an icon):

```yaml
title: "Claude Fable 5.2 Made This Video From One Prompt"
look: panel
camera: { focus: [0.49, 0.3], zoom: 1.0 }

chapters:
  heading: "Claude Fable 5.2"
  logo: true
  badge: { eyebrow: "AI avatar", intro: "AI avatar, cloned voice" }
  items:
    - { at: w152, title: "Why This Matters", badge: "Why This Matters", icon: lightbulb }
    - { at: w275, title: "What's New", badge: "What's New", icon: sparkles }
```

- `look: panel` is his house layout: the avatar in a tile on the right, a step badge above it, every
  graphic in the left panel.
- **`badge.eyebrow: "AI avatar"` is the disclosure.** It sits above the avatar for the whole video. No
  scene may cover the badge.
- `camera.focus` centres the tile on the face. Set it from a still, once.
- No chapter item for the first section: the video starts on its first word, not on a card.

## 3. The plan

`W/plan.md` is the one document every writer reads in full. `examples/edit-plan.md` is the first run's. It
has four parts:

1. **What this video is**, in one paragraph, including what the tile is (an avatar) and what goes in
   front later.
2. **The bar and the look**: the layout, a finished edit to match, the motion rules (something useful
   changes every 1.5 to 3 s, nothing static past 4 s, each beat at least 2 s, the old element leaves
   before the new one enters, visuals land on the word that names them), the proof rules, the text rules.
3. **Assets**: every folder and what is in it, with the file names. Writers use what is listed and
   nothing else. Scene paths are relative to `W`: research captures are under `proof/` (a link to
   `P/proof`, live test included), and you copy everything else the edit shows into `W/media/`: the
   prompt (`the-prompt.txt`), the photo (`own/`), pilot clips, the three thumbnails, real screenshots of
   the run with a `README.md` beside them saying what each shows. B-roll is written straight to
   `media/broll/`.
4. **Part by part, take by take**: what the viewer should see on each line. Name the proof file, the
   exact words to mark, the B-roll clip and its reveal second. This is the direction; the writer's job is
   to build it well. A plan that says "show the pricing" gets seven different videos.

Plan the one or two places where the layout breaks (the first run: the last ten seconds go full screen
on the avatar with the closing board). Everything else stays in the house layout.

## 4. Parts and lanes

Each writer owns `W/parts/<X>.yaml`, a plain list of scenes. Two small scripts in `W/tools/` (copied
there by `new_project.py`) keep seven writers out of each other's way:

```bash
tools/lane.sh C check                                 # builds lanes/C/edit.yaml from the header + parts/C.yaml, then checks it
tools/lane.sh C sheet --every 2s --from w544 --to w716
tools/lane.sh C still --at w560
tools/merge.sh                                        # edit.yaml from the header and every part, in order
```

A lane is a private copy of the work dir that shares the media by symlink, so a writer can check and
look at its own part while the others are half-written. Writers never render video and never touch
`edit.header.yaml`.

After the merge: `screenplay check <W>` must report 0 errors, then
`screenplay sheet <W> --every 2s` and read every sheet yourself. The first run: 115 scenes from seven
writers, merged with 0 errors, and still 104 review notes.

## 5. Review and fix

- One reviewer per two parts, briefed with `W/REVIEWER.md`. They look at sheets and full-size stills
  with the script beside them and return numbered notes, each tagged `must`, `should` or `nice`, each
  with a time and a still. They change nothing.
- Read every note. For each `must` and `should` decide the fix and get what it needs. Reviewers find
  what is wrong; they often cannot know what is true. The first run's best fixes came from the boss:
  a rebuilt app window replaced by a screenshot of the real one, a made-up worker brief replaced by the
  real brief's text.
- One fixer per part, briefed with `W/FIXER.md` and that part's decided list. Merge, check, sheet, and
  look at a still of every fixed item.
- Keep each round's reviews in `W/review/v1/`, `v2/`. Before a risky change, copy the file you are about
  to change next to them (`G.before-final-fixes.yaml`).

## 6. The real avatar track

When `build_takes.py status` shows every clip ok and the room check is clean
(`references/voice-avatar.md`): `assemble`, `screenplay aroll <W>`, `scan_cuts.py`, `check_timing.py`
(the block in `SKILL.md`, "10 and 11"). Do not run `init` again: `source.json` already points at
`camera.mov`, and `assemble` writes the new picture to the same file.

`scan_cuts.py` prints the fix for each hit: a later `end` for one word in `words.json`, or a `holds:`
line in `cuts.yaml`. Then `aroll` again. Neither renumbers anything, but each adds a little time at that
spot, which `check_timing.py` will list. The sound did not change between the lock and now, so if
`scan_cuts.py` was clean at the lock it is clean here; `check_timing.py` should print that nothing moved.

Loudness: the engine levels the track to -16 LUFS (`aroll --lufs`). His videos go out near -14, and
Auphonic sets the final level anyway, so leave this alone unless the file is going out without Auphonic.

## 7. The end of the video

- The closing board's numbers live in `W/receipts.json`, so there is one place to keep them true. The
  engine does not read that file: the last part's writer builds the board as one `table` or `stat`
  element from its rows and types "…" for each `null`. Before the preview render, fill the file, put the
  same values into that element, merge and check. The agent count includes failed starts and the
  final-cut reviewer.
- The last take holds on a closed mouth (`tail` and `freeze_at`, `references/voice-avatar.md`) with a
  `holds:` entry after its last word.
- No "Watch next" card baked in. YouTube's end screen goes over the last 20 seconds, so keep the right
  side of the closing frames calm.

## 8. Preview, final review, render

`screenplay render <W> --preview` writes a 720p file in about 6 minutes for a 10-minute video.
`review_aids.py` then writes where each take starts and where two-clip takes join, for the reviewer.

Brief one reviewer (`briefs/workers.md`, 12; its rules are `W/FINAL-REVIEW.md`). It is the only agent
that judges the video as a video: every take's face and room, every cut, the sound between takes, the
first and last five seconds. It returns `SHIP`, `SHIP AFTER MUSTS` or `DO NOT SHIP` with a numbered
list. For `SHIP AFTER MUSTS`, fix each must, render that stretch as a preview
(`--preview --from <anchor> --to <anchor>`) and look at it. Then the final render, which also writes the
`.srt` and `.chapters.txt`, and `check_takes.py` on the finished file.

`check_takes.py` transcribes the finished file take by take and lists every difference from the script.
Number formats are normal. A missing or changed word is a fault in the cut, not in the voice: go back
to `scan_cuts.py`.

To render from a later point (he cuts the first take, or one section changed): `--from <anchor>`. The
chapters and captions the engine writes are for the whole timeline, so shift them yourself, or let
`join_opener.py --skip-frames` do it.
