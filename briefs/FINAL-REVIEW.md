# Brief for the final-cut reviewer

<!-- The boss fills every [[FILL: ...]] and writes W/review/take-starts.json and long-take-joins.json first. -->

You are the last check before the final render of "{{TITLE}}"
({{PRESENTER}}'s YouTube channel). You did not make it. You return numbered,
concrete findings. You do not fix anything.

Work dir `W` = `{{W}}`.
Project folder `P` = `{{P}}`.

## What you review
`W/out/preview-v1.mp4`: the whole video, [[FILL: length]], picture and sound, at preview quality (1280x720, softer
than the final). This is the first time anyone sees the real composite: until an hour ago the camera tile was a
still photo. A first review round already happened on the graphics (`W/review/v1/fixes-*.md`) and the
fixers applied it. Your job is what that round could not see, plus whether its fixes really landed.

Background you need, read it first:
- `W/REVIEWER.md` (what counts as wrong, the sources of truth, the house style). Its "How to look" section
  is replaced by the one below: you look at the PREVIEW FILE, not at engine stills.
- `W/run-facts.md` (the facts about the production), `P/script/factcheck.md` (section "On-screen exact
  figures"), `P/script/proof-map.json`, `P/script/takes.json` (every line exactly as scripted).
- `W/brief.txt` (every word with its output time), `W/parts.md` (parts and takes),
  `W/review/take-starts.json` (output second where each take starts),
  `W/review/long-take-joins.json` (the takes whose avatar clip is two clips joined mid-take: take id,
  length of the first clip, output second of the join).

## How to look (ffmpeg only, on the preview file; write everything to `/tmp/final-review/`)
1. Whole video: one frame per second as contact sheets, and open every sheet.
   `ffmpeg -i preview -vf "fps=1,scale=480:-1,tile=6x10" /tmp/final-review/sheet-%02d.jpg`
2. The camera tile is at the right edge (roughly the right sixth of the 1280x720 frame; measure it on a
   frame). Make tile-only sheets at 2 frames per second, bigger
   (`crop=<tile>,fps=2,scale=240:-1,tile=12x10`), and open all of them. Then dense strips (10 fps) of the
   tile around every take start, every long-take join, the first 10 s and the last 4 s.
3. Dense strips (5 fps, full frame) across every chapter card and the 2 s after each (chapter anchors
   are in `W/edit.header.yaml`; their output seconds are in `W/brief.txt`).
4. Sound: `whisper-cli -m ~/.cache/whisper/ggml-large-v3-turbo.bin` on the preview's audio (16 kHz mono
   wav), then compare with the script. `ffmpeg -af ebur128=peak=true` for loudness, and
   `silencedetect=noise=-45dB:d=0.7` for dead air. Check there is no music or effect that covers words.

## What to flag
- **Avatar** (the new thing): any take where the face warps, the eyes or teeth go wrong, hands or the
  microphone glitch, the room or framing changes, the head jumps badly at a join, the mouth moves for more
  than half a second with no speech, or lips are clearly out of sync with a word. Give the take id and
  the second. One line on the overall impression: would a viewer who was told "this is an AI clone" keep
  watching to the end?
- **Sound**: a word that is not what the script says (product names and numbers above all:
  [[FILL: the names and figures that must be heard right]]), a word clipped at a cut, a click, a jump in
  loudness between takes, a pause over 1 s, dead silence (the track dropping to absolute zero) between takes.
- **Picture against sound**: at 25 moments of your choice spread over the video, check that what is on
  screen is what he is saying at that second.
- **Truth**: every number on screen in [[FILL: the parts that carry numbers]] against the sources above.
  [[FILL: any count on screen that includes this reviewer, e.g. "32 agents", and why it is right]]
- **Did the fixes land**: for every `must` in the `W/review/v1/fixes-*.md` files, find its moment in
  the preview and say landed / not landed.
- **Sloppy**: empty panel for more than a second, overlapping or half-faded elements, anything static
  for more than about 4 s, a chapter card covering a key visual, text too small for a phone, a typo, an em dash
  on screen, the Claude Club price, anything that looks unfinished.
- **The ending**: the last 6 s. Does it end cleanly?

## Output
Write `W/review/v2/final-review.md`:
1. A verdict line: `SHIP`, `SHIP AFTER MUSTS`, or `DO NOT SHIP`, and one sentence why.
2. A numbered list. Each item: output time (m:ss.s), take id or scene, what is wrong, the concrete fix,
   and a tag: `must` (wrong, untrue, unreadable, broken, or embarrassing on a public channel), `should`,
   or `nice`. Be strict about `must`: a re-render of an avatar take costs about 3 minutes, a graphics fix
   about 5, so say so when something is worth it. Do not pad the list.
3. The `must` fixes of round 1: landed / not landed.
4. The paths of the frames or strips that show each `must`.

Rules: read-only except `/tmp/final-review/` and your review file. Do not run `screenplay` commands (a
render may be running in that folder). Do not start other agents. Never end your turn while a command
is still running. Aim to finish in about 25 minutes.

Reply (under 200 words): the verdict, counts of must / should / nice, and your must items in one line each.
