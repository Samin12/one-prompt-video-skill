# Voice and avatar

Everything here runs through the Higgsfield CLI (`higgsfield`, already logged in) and
`build_takes.py`. Run it inside the project folder `P`: `python3 <skill>/scripts/build_takes.py <command>`.
The commands below leave that prefix off.

## Settings

`~/.config/one-prompt-video/defaults.json` (see `config.example.json`) holds what belongs to the presenter,
not to one video: `voice_id`, `image_id`, `photo_source`, `avatar_prompt`, his speaking rate. A project's
`project.json` can override any of them.

## One-time setup: the voice

- Clone from about 2 minutes of his **raw microphone audio** from a recent video (a clean stretch of
  him talking, no music). The CLI can list voices but not create one: make the clone with the Higgsfield
  connector's `create_voice` tool (upload the audio first) or in the Higgsfield web app, then
  `higgsfield voices list --json` gives its id. Cloned voices have the type `element`.
- **Measure it before trusting it.** Speaker similarity (resemblyzer via `uv run`) of a generated line
  against three real takes. The clone used in the first run scored 0.91; two real takes of him score
  0.985 against each other; an older clone made from a 28-second sample scored 0.79 and was dropped.
- Make one test line with a name and a number in it and transcribe it.

## One-time setup: the photo

One real photo of him in his studio, 16:9, head centred, both shoulders in frame, the room in focus.
`higgsfield upload create <photo>` returns the `image_id`. The avatar prompt should name what is in the
photo that must not change (his shirt, the microphone, the shelf, the lighting): the model treats the
photo as a reference, and what the prompt does not pin down it feels free to redraw.

## Pick the avatar model with a pilot, once per model generation

Same photo, same voice line, each candidate model, about 15 seconds. Look at every second of each. In
the first run Higgsfield Intone (126 credits) cut to a second camera angle and rearranged the room in the
middle of the clip; Wan 3.0 (26 credits) held one take. Wan 3.0 at 720p was used. Keep both pilot clips:
they are good material for the video.

Wan 3.0 facts that shape the pipeline:

- With a voice reference, jobs **above 15 seconds fail**. `build_takes.py` splits a longer read at a pause
  and joins two clips.
- A start image cannot be combined with a voice reference, so every clip is generated *from* the photo,
  not *starting on* it. That is why the room drifts (below).
- `--generate_audio false`: the clip's own sound is not used; the clean read is laid back over it.
- The account runs **3 jobs at a time**, across every tool and worker using it. A full queue returns
  `rate_limit_reached`; the script waits 20 s and tries again.

## The reads

```bash
build_takes.py voice            # 2 at a time; a read outside 170..232 wpm is read again at another rate
build_takes.py check            # whisper each read; writes <id>.ok or <id>.diff; exit code 1 while any take is open
build_takes.py revoice n06 x04  # up to 5 reads each; keeps the best
build_takes.py status           # per take: read ok / DIFF / STALE, clip ok / FAILED / STALE
```

- The model's pace swings between runs (173 to 244 words a minute on the same sentence). The script
  keeps the read closest to his real pace.
- `check` passes a take when the transcript matches the script (0.97) **and** every phrase listed for it
  in `script/must-hear.json` is heard. Money and thousands are compared as spoken ("50 cents" matches
  "$0.50"), other numbers are not ("thirty-one hundred" will not match "3,100"): write must-hear phrases
  with digits, the way a transcriber does.
- Read every `.diff` yourself. The first run's real ones: "Fermat's Last Theorem" garbled, "agent teams"
  heard as "Asian teams", "a week" as "a weekend", a dropped clause, "Fable" as "Babel".
- `revoice` passes a re-read at 0.90 when every must-hear phrase is heard: the phrases are the stricter
  test. When five reads cannot get a phrase right, reword it slightly in `takes.src.txt` ("a week" became
  "about one week") and check the new wording against the source.
- Approve a diff you have read and accept by writing `<id>.ok` next to it. The avatar loop only takes
  passed or approved reads.
- **Changing a take's words** (in `takes.src.txt`, then `make_takes.py`) makes its read STALE: `check`
  and the avatar loop refuse it, and `voice <id>` reads the new words. The old read moves to `alt/`.

Then fill the silence: `uv run --with numpy --with soundfile python3 <skill>/scripts/fill_tone.py`. The
reads have exact digital silence before, after and between phrases; cut together it sounds like the
sound switching off between takes. The script mixes the voice's own quiet floor into the silent stretches.
Run it again after any re-read.

## The clips

```bash
build_takes.py avatar-loop      # in the background: 2 at a time (one slot of the account's 3 stays free), as reads pass
build_takes.py avatar i01 i02   # or by id, 3 at a time
```

About 3 minutes and 26 credits per 15-second clip. The first run spent 2,061 credits in all for ten
minutes: clips, reads, pilots, thumbnails, B-roll and re-renders.

- The loop ends with "all avatar clips done", or with the ids that failed and exit code 1. A failed job
  leaves `avatar/takes/<id>.failed` holding the error; `avatar <id>` tries it again.
- It stops by itself after 15 minutes with nothing ready (takes still waiting on a read-through) and
  lists them. Start it again when they pass.
- To redo a clip, move its `.mp4` and `.job.json` into `avatar/takes/alt/` and run `avatar <id>` again.
  Never delete an earlier render: the alt folder is how you compare.
- A clip older than its read is STALE in `status` (the read was redone after the clip): redo the clip.

## Assemble

`build_takes.py assemble` writes `avatar/camera.mov`, `mic.wav` and `takes-timeline.json`.

Each take's length comes from its read alone, so the timeline is identical whether or not its clip
exists yet (a missing clip is the photo). Run it as soon as the reads pass, lock the edit's timeline on
it, and run it again when all clips are in.

The last take: give it `tail=1.6` and a `freeze_at` in `takes.src.txt`. The clip keeps moving after the
last word and the mouth opens again about 0.7 s later; hold the frame from about 0.5 s after the word
(look at a 10 fps strip of the end to choose the second), and add a matching `holds:` entry in
`W/cuts.yaml` so the engine keeps the tail.

## The room check

```bash
uv run --with numpy --with opencv-python-headless python3 <skill>/scripts/room_check.py
uv run --with numpy --with opencv-python-headless python3 <skill>/scripts/rerender_room.py w03 r03 x07.a
```

About one clip in six comes back in a slightly different room: the shelf framed wider, an object
appeared or moved, the wall cooler. Nothing about the face or the lip sync is wrong, so no per-clip check
sees it; cut together, the room jumps. `room_check.py` measures patches of room around the presenter
against the median of all takes, ranks every clip as a multiple of its limit, and writes a sheet of the
odd ones (`avatar/qa/room-odd.jpg`, first row is the usual room).

- **Above 2x**: render it again. `rerender_room.py` tries up to three times and keeps the closest.
- **Between 1x and 2x**: open the sheet. Keep it if you cannot see the difference at tile size.
- If good takes are flagged in one patch, the presenter is moving through it: move that patch in
  `room_regions` (project.json) to a part of the frame he never crosses, and run the check again.

The check was tuned on one studio. Look at the sheet before believing either answer.

## Lip sync and joins

Check lip sync on a strip, not a number: 15 frames a second of the mouth across a real silence in the
read (find the silence in the audio, not in the transcript). The mouth should be closed through it. Do
this for a few takes per batch and for every re-render. The joins inside two-clip takes read as ordinary
jump cuts in the tile; `review_aids.py` lists where they are for the final reviewer.

## Costs seen

| Item | Credits |
|---|---|
| Wan 3.0 clip, 15 s, 720p | about 26 |
| Voice read | about 1 to 2 |
| Avatar pilot on a pricier model | 126 |
| Whole first video, everything | 2,061 |
