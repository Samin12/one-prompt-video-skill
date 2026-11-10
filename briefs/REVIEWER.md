# Brief for every visual reviewer

<!-- The boss fills every [[FILL: ...]] before the first reviewer is briefed. -->

You review a stretch of the edit "{{TITLE}}" ({{PRESENTER}}'s
YouTube channel) before it is rendered. You did not make it. Work dir `W` =
`{{W}}`. Your stretch (parts and output times) is in your
task. You return numbered, concrete fixes. You do not fix anything yourself.

## What you are looking at
- The avatar in the camera tile is an AI clone of {{PRESENTER}} with a cloned voice (the video says so). In
  the contact sheets and stills some tile frames are a still photo: avatar clips are still rendering.
  Do not review the tile, except to flag anything in the panel that covers it or the badge above it.
- Left panel: motion graphics written by the part writers (`W/parts/*.yaml`, merged into
  `W/edit.yaml`). The words are in `W/brief.txt` (word ids), the takes and their times in `W/parts.md`.
- The rules the writers had: `W/WRITER.md` and `W/plan.md`. The facts: `W/run-facts.md` (the production
  itself) and, in the project folder
  `{{P}}/script/`,
  `proof-map.json` and `factcheck.md` (section "On-screen exact figures").
- House style and taste: `~/.claude/skills/screenplay-edit/references/taste.md` and `METHOD.md`
  (section "What NOT to do"). The bar is [[FILL: the work dir of a finished edit that sets the standard; its `out/` has the render]].

## How to look
1. Contact sheets of the whole edit, one frame every 2 s, are in `W/.screenplay/sheet-*.jpg`
   (24 frames each, time stamp under each frame). OPEN every sheet that covers your stretch.
2. For anything you cannot read or judge at sheet size, take a full-size still:
   `screenplay still "W" --at o:<seconds> -o /tmp/review-<yourname>/<seconds>.png` (run from any folder;
   `o:` is output time in seconds). Take one for EVERY proof card, table, replica and story in your
   stretch, at the moment its key word is said (find the second in `W/brief.txt` / `W/parts.md`), and
   open it. Budget: up to about 60 stills.
3. For motion and timing, look at a denser strip when a beat matters:
   `screenplay sheet "W" --every 0.5s --from o:<a> --to o:<b> -o /tmp/review-<yourname>/strip-<a>.jpg`.

## What to check, for every shot
- **Says what he says.** Is the thing he is saying at that second visible, and is it the biggest thing
  on screen? Does a visual arrive late, early, or stay after he has moved on?
- **Readable on a phone.** Imagine the frame at 1/3 size. Flag text under about 22 px in the final
  frame, low contrast, proof cards showing a whole page instead of one paragraph, crops that cut a word
  or a number, a highlight sitting on the wrong phrase or beside it.
- **True.** Every number, name, date and quote on screen must match `proof-map.json` /
  `factcheck.md` / `run-facts.md` exactly. Open the proof file when in doubt. Flag anything that is
  not in those sources: a made-up label presented as a fact, UI text in a replica nobody verified, a
  number that differs from the source, and this video's known traps: [[FILL: the fact-check's list, e.g. a test
  credited to the wrong lab, a cost shown without what it is the cost of, a screen of a feature nobody ran]].
  Never the Claude Club price. Rebuilt UI must say "Recreated".
- **Sloppy.** Empty or near-empty panel, a card before its content, half-faded or overlapping
  elements, a label on top of the text it points at, two things fighting for the eye, anything
  static for more than about 4 s, a chapter card covering a key visual, the same layout five times
  in a row, misspelled product names ([[FILL: every product name in this video, spelled right]]),
  em dashes, headlines over 7 words.
- **Joins.** The first and last 4 s of each part: does the hand-over to the next part work, or does
  something linger, repeat or clash?
- **The big picture, once.** For each part: one sentence on whether a viewer who only watched (sound
  off) would get the point of that section.

## Output
Write `W/review/v1/fixes-<your stretch>.md`:
- A numbered list. Each item: the part letter in brackets, the output time (m:ss.s), the scene (quote a
  few of its words or its element type), what is wrong, and the concrete fix ("crop to the second
  paragraph and mark '$165'", "end the callout on 'Sonnet'", "replace the label 'X' with 'Y'"). Tag
  each item `must` (wrong, untrue, unreadable or broken), `should` (clearly better), or `nice`.
- Then "What works" (3 to 6 lines, so the fixers do not break it).
- Then the paths of the stills that show your `must` items.
Do not edit any file in `W` other than your review file. Do not start other agents. Do not render the
video. Never end your turn while a still or sheet command is running.

Reply (under 250 words): counts of must / should / nice, your five most important items, and one
sentence per part on whether it would work with the sound off.
