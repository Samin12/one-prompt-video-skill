# Brief for every fixer

You fix ONE part of the edit "{{TITLE}}" after an independent
visual review. Work dir `W` = `{{W}}`. Your part
letter, your review file and the boss's decisions are in your task.

## Read first
1. `W/WRITER.md`: the rules and the tools every part writer worked under. They all still apply to you
   (what you may touch, how to check, the hard rules, the engine docs to read).
2. `W/plan.md` (your part's section), `W/parts.md` (your word range), `W/run-facts.md`.
3. Your part as it stands: `W/parts/<X>.yaml`, and the writer's notes in `W/lanes/<X>/` (some writers
   generate the YAML from a source file or script in the lane; if `lanes/<X>/` has one, edit the source
   and regenerate, or your change will be overwritten: say which you did).
4. The review: every item tagged with your part letter in the review file named in your task. Open the
   stills it points to.

## Do this
1. Fix every `must` and every `should`. Fix a `nice` when it is cheap and safe. Where the boss's
   decisions in your task differ from the reviewer's suggestion, the boss's decision wins.
2. Do not break what works: the review's "What works" list, the timing of beats nobody complained
   about, the first and last scene boundaries of your part (your part still starts on its first word id).
3. After each group of fixes: `W/tools/lane.sh <X> check` (0 errors; no new warnings in your range), then
   a full-size still of every beat you changed (`W/tools/lane.sh <X> still --at <anchor> -o /tmp/<X>-fix/...`)
   and OPEN it. A fix is done when the still shows it, not when the YAML says it.
4. One last pass: `W/tools/lane.sh <X> sheet --every 2s --from <first w id> --to <last w id>` and open
   every sheet, to catch anything the fixes disturbed.

Everything on screen stays true: numbers and quotes exactly as in the proof files, `run-facts.md`, and
any `README.md` the boss left beside real captures in `W/media/` (it says what each capture shows and
where it came from). If a fix needs a fact you cannot find there, do not invent it: leave the beat honest
and simpler, and say so.

## Reply (under 250 words)
A list: review item number, `fixed` / `fixed differently` / `not fixed`, and a few words on what the
viewer now sees. Then anything new you noticed, and the paths of 3 stills of your biggest fixes.
Never end your turn while a check, still or sheet is running. Do not start other agents. Do not render.
