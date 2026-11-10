# Brief for every part writer

<!-- The boss fills every [[FILL: ...]] before the first writer is briefed. -->

You write ONE part of the edit "{{TITLE}}" for {{PRESENTER}}'s
YouTube channel, with the screenplay motion-edit engine (`screenplay` CLI on PATH; engine at
`~/SaminOS/Projects/screenplay`). Work dir `W` = `{{W}}`.
Your part letter and word range are in your task and in `W/parts.md`.

## Read first, all of it
1. `W/plan.md` (the rules of this edit, the assets, and what each take in your part should show),
   `W/parts.md` (your word range and takes), `W/run-facts.md` (the only source for production facts).
2. The engine: `~/.claude/skills/screenplay-edit/SKILL.md`, its `references/METHOD.md`, `taste.md` and
   `concept-visuals.md`, and `~/SaminOS/Projects/screenplay/docs/EDIT-YAML.md` (the format; stories, proof
   cards, replicas). `screenplay replicas <id>` prints a replica's targets and state keys;
   `docs/REPLICAS.md` explains them.
3. Two reference parts from an edit that sets the bar:
   [[FILL: two finished parts, e.g. the skill's `examples/part-D.yaml` (story, proof cards, big numbers) and one from the presenter's last video]].
4. Your words: `W/brief.txt` lines in your range (word ids `w123`). Your facts:
   `{{P}}/script/proof-map.json`
   (per take: the exact figure to show, the proof file, the source pill) and `script/factcheck.md`
   ("On-screen exact figures").

## Do this
1. Look before you write: open every proof PNG you plan to use, read its `.source.json`, measure your crop
   and highlight rects on the image itself (pixels of the PNG). Pull frames from any clip you use
   (`ffmpeg -ss T -i clip -frames:v 1 /tmp/<X>-f.png`) and read `media/broll/INDEX.md` for reveal times.
2. Write `W/lanes/<X>/plan.md`: a table of time / words / what the viewer sees / scene kind, covering every
   second of your range.
3. Write `W/parts/<X>.yaml`: a top-level YAML list of scenes only (`- kind: ...`). The first scene's `at:`
   is your part's first word id; every scene `at:` is a word id; inner anchors may be phrases inside the
   scene or word ids. Never frame numbers or `o:` times.
4. `W/tools/lane.sh <X> check` until it reports 0 errors, and fix the warnings in your range too
   ("starts while ... is still up", "on screen for only", "no visual change for").
5. Review like an editor: `W/tools/lane.sh <X> sheet --every 2s --from <first w id> --to <last w id>` and
   OPEN every sheet image. `W/tools/lane.sh <X> still --at <anchor>` full size on every proof card, story
   beat and replica beat. Ask of each frame: is the thing he is saying visible and readable on a phone? Is
   the panel ever empty or showing a card before its content? Does every on-screen number match the
   source exactly? Is any crop cutting a word? Is the highlight on the right phrase? Fix, re-check,
   re-sheet. Two full rounds at least.
6. Measure coverage: list every stretch of 4 s or more in your range with no visual change, and fix them.

## Hard rules
- Everything on screen is true. Numbers, names and quotes come from the proof files and `run-facts.md`
  only, shown exactly as the source has them. Illustrative values only inside stories, and listed in your
  report. Rebuilt UI (a terminal session, an app window, a run board) says "Recreated" on itself for as
  long as it is up: in the replica's own title or status line (`title: "Claude Code · Recreated"`), or as
  a `badge` actor in a story (`text: "Recreated from the run's own record"`). The engine does not add it.
- Paths in your YAML are relative to `W`. `proof/...` is the project's proof folder (a link). Anything
  else you show is under `media/`.
- If your part holds the closing board, build it from `W/receipts.json` as ONE `table` or `stat` element,
  one row per entry, a `null` value drawn as "…". The boss fills the numbers last and edits that element.
- The avatar stays in the tile on the right, the badge above it stays visible. No em dashes on screen.
  Headlines under 7 words. No "Watch next" card. Never the Claude Club price.
- A chapter card covers the whole screen for the first 2 s after a chapter anchor: do not put a key visual
  on those words (chapter anchors are in `W/edit.header.yaml`; the scene at a chapter anchor starts on it).
- Two elements that overlap split the panel and both shrink: give the first an `until` that ends before
  the next `at`. A proof card must be big enough to read: crop to the paragraph or chart, do not show a
  whole page.
- The camera video in the lane is a placeholder still of the avatar while the real clips render. Do not
  judge the tile; judge the panel. Timing is final (it comes from the voice).
- Only touch `W/parts/<X>.yaml`, `W/lanes/<X>/`, `W/media/<X>/` (new media you make) and `/tmp/<X>-*`. Do
  not render the video. Do not edit engine code, other parts, `edit.header.yaml` or the proof folders. Do
  not start other agents. Never end your turn while a check or sheet is still running.

## Reply (under 300 words)
Scene count; one line per scene group (time, kind, what it shows); every liberty you took (anything
recreated or illustrative); anything on screen you could not verify; open issues; the paths of 3 stills
that show your best and your weakest moment.
