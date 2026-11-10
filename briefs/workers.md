# Worker briefs

Templates for every agent the boss starts. Each one is a whole message: a worker sees nothing of the
boss's conversation, so the brief carries the goal, what to read, exactly what to write and where, what
not to touch, and what "done" means. Fill the `<...>` parts. Keep the closing lines of each (DONE WHEN,
the reply limit): they are what stops a worker early, sprawling, or reporting in prose you cannot use.
The do-nots every worker shares (write only in the paths named, no other agents, nothing posted, nothing
deleted) are in `P/BRIEF.md`, which every brief tells the worker to read first.

Order of use: research wave (1 to 5, at once) → fact-checker (6) → thumbnail and B-roll (7, 8, alongside
voice and avatar) → part writers (9) → reviewers (10) → fixers (11) → final-cut reviewer (12).

Paths: `P` is the project folder, `W` the screenplay work dir. `W/proof` is a link to `P/proof`, so a
capture saved as `P/proof/official/x.png` is `proof/official/x.png` in the edit.

---

## 1. Official facts (primary sources, with proof)

```
You are a research worker for a YouTube explainer about <TOPIC> (<released/announced DATE>). First read the
shared brief: `<P>/BRIEF.md` (it defines `P`, the hard rules and the proof-capture command). Follow it exactly.

YOUR JOB: the official facts, from primary sources only, with proof screenshots.

1. Read in full: <the announcement URL>, <the paper / system card / spec, with the sections that matter>,
   <release notes>, <pricing and docs pages>, <the launch video: get its transcript>. Check the maker's
   news page and blog for companion posts published the same day.
2. Write `P/research/01-official.md`. Every bullet ends with (source URL) and, for numbers and quotes, the
   exact source sentence in quotes:
   - One-paragraph plain-English summary of what it is and where it sits in the line-up.
   - What's new against the last version: every concrete change, with exact figures and what they were
     compared against.
   - Pricing and availability: exact prices now and before, what each plan gets, where it runs.
   - <the video's central subject, e.g. multi-agent use>: everything the maker says about it, with exact
     wording and caveats.
   - The maker's own guidance on when to use it and when to use something cheaper (exact quotes).
   - Limits and weaknesses the maker itself states.
   - "Easy to get wrong": places where the day's coverage is sloppy or contradicts the primary source.
   - A table of the 12 most video-worthy facts: the fact in one spoken sentence, exact source line, URL,
     proof screenshot file.
3. Capture proof screenshots for those facts into `P/proof/official/` with the capture command in the brief
   (crop with --selector/--extend so the proving paragraph or table is readable at panel size), each with
   its `.source.json`. For PDF facts, render the page (`pdftoppm -r 200 -f N -l N -png`) and crop to the
   paragraph or chart; write the highlight box yourself. Also grab clean captures of the announcement hero,
   the pricing table and the main chart. Open every PNG and confirm it is readable and proves the claim.
4. Write `P/proof/official/proof-index.json`: an array of every capture's source record in that folder.

DONE WHEN: `01-official.md` has every section above, each of the 12 table facts has a capture you have
opened, and `proof-index.json` lists every capture in the folder. Never end your turn while a capture is
still running. Reply in 25 lines or fewer: the 10 facts you are most confident in, anything you could not
verify, and any claim in the brief's "known starting points" that turned out wrong or imprecise.
```

## 2. Real posts (what people are doing with it)

```
You are a research worker for a YouTube explainer about <TOPIC>. First read `<P>/BRIEF.md`. Follow it exactly.

YOUR JOB: find the best real posts on X showing things people are doing with <TOPIC>, and capture them as
on-screen proof. Read-only: never like, reply, follow or post.

How to search: the BrowserOS neo browser MCP tools (already logged into X) in your OWN new tab; if you do
not have them, the `tandem` browser MCP, then web search with `site:x.com "<TOPIC>"`. Useful queries (Top
and Latest): `"<TOPIC>"`, `"<TOPIC>" min_faves:200`, `"<TOPIC>" built`, `"<TOPIC>" has:videos`,
`from:<maker's account>`, plus well-known builders and the maker's staff. Check the replies and quotes of
<the launch post URL> for demos.

Collect 30+ candidates, then pick the best 15 to 20:
- Concrete demos and results, ideally with an image or video.
- Posts from the maker with launch facts.
- 3 to 5 credible honest or critical takes (limits, cost, where it is not worth it).
- Skip engagement bait, hype with no substance, "leaks", anything about an older version, anything NSFW
  or political.

For every picked post:
- Record in `P/research/02-posts.md`: URL, author and @handle, who they are (one line, from their profile),
  date and time, the full text verbatim, likes/reposts/views at capture time, what media it has, what it
  shows in one plain sentence, a "say it on camera" line (one sentence that does not overstate), a category,
  a quality score 1 to 5. Mark anything you could not fully verify.
- Capture it into `P/proof/posts/<handle>-<short-slug>.png` with `--highlight "<the key phrase>"` and write
  its `.source.json`. Open each PNG. Save a demo video or image to `P/proof/posts/media/` when you can do so
  without logging in anywhere new (`yt-dlp`), and note its path.

Also write `P/proof/posts/proof-index.json` and, at the top of `02-posts.md`, a ranked "top 10 for the
video" grouped into 3 or 4 themes.

DONE WHEN: 15 or more picked posts each have a record, a capture you have opened and a `.source.json`,
and the ranked top 10 is at the top of `02-posts.md`. Reply in 25 lines or fewer: the top 10 (author and
what it shows), how many you verified, and any that look too good to be true.
```

## 3. The how-to (the thing the viewer will copy)

```
You are a research worker for a YouTube explainer about <TOPIC>. First read `<P>/BRIEF.md`. Follow it exactly.

YOUR JOB: exactly how a viewer does <THE THING THE VIDEO TEACHES>, from the official docs, with every command,
file and setting, and the real costs.

1. Read <the docs pages>. Write `P/research/03-howto.md`: each way of doing it, step by step, with the
   exact commands and file contents, what each costs (prices from the pricing page, with the source
   sentence), the maker's own test numbers if they published any, and what the docs say NOT to do.
2. Say for each way whether you ran it or only read about it. Do not describe a screen you did not see.
3. Capture proof for every number and every "the docs say" line into `P/proof/official/howto-*.png`, each
   with its `.source.json`, and list them in `P/proof/official/howto-index.json` (another worker owns
   `proof-index.json` in that folder: do not edit it).

DONE WHEN: every way has its steps, its cost with the source sentence, and "ran it" or "read only"; every
number has a capture you have opened. Reply in 15 lines or fewer: the simplest way that works, its real
cost, and what you could not verify.
```

The boss then RUNS the simplest way for real and keeps the files and the log in `P/proof/live-test/`
(the commands typed, the output, the time, the cost). A how-to nobody ran does not go on screen as if it
happened.

## 4. The presenter's style

```
You are a research worker for a YouTube explainer for <PRESENTER>'s channel. First read `<P>/BRIEF.md`.

YOUR JOB: a style pack so the script sounds like <PRESENTER> and the thumbnail looks like his videos.
Everything comes from his real videos and files, nothing invented. All local reading is read-only.

Where to look: <his profile and channel notes>, his recent videos (titles, views, thumbnails,
descriptions: `ytstudio` or `yt-dlp --flat-playlist -J <channel>/videos`), transcripts of the 3 or 4
videos closest to this one (`yt-dlp --write-auto-subs --skip-download`), and existing local style
material: <paths to his editing skills' reference files, brand notes, earlier thumbnail work>.
Download the thumbnails of his 12 most recent long videos and his 8 best recent ones to
`P/refs/thumbnails/` (`<views>-<slug>.jpg`), and make one contact sheet of them all,
`P/refs/thumbnails/_sheet.jpg` (5 across, the view count under each).
<If an earlier style pack exists: "Start from `<path to it>`. Check it against his newest videos and
update it instead of starting from nothing; redo the titles, the thumbnail concepts and the downloads.">

Write `P/research/04-style.md`:
1. Voice guide: how he really talks, with 25+ verbatim lines (openers, transitions, how he introduces a
   concept, how he explains with an analogy, how he states a caveat, his call to action, his sign-off).
   Sentence length, favourite words, words he never uses, how he handles numbers. A do / don't list.
2. Structure guide: the beat-by-beat shape of his explainers with timestamps from the real transcripts,
   and what his best performers share.
3. Title patterns: his last 25 titles with views, the patterns that win, 10 truthful options for this video.
4. Thumbnail style spec from the downloaded thumbnails (open the images): layout, text, palette with hex
   values, what changes between his best and worst. Then 4 concepts for this video, ranked.
5. Assets found: photos of him, logo files, fonts, earlier prompts.
6. Edit conventions the editor must respect, as a 15-line checklist.

DONE WHEN: `04-style.md` has all six sections, the 25+ lines are verbatim from transcripts you name, and
the thumbnails and `_sheet.jpg` are saved. Reply in 15 lines or fewer: the transcripts you used, the top
thumbnail concept, the top 3 titles.
```

## 5. Reactions and limits (the independent view)

```
You are a research worker for a YouTube explainer about <TOPIC>. First read `<P>/BRIEF.md`.

YOUR JOB: the independent view. What early testers, press and the community say, how it compares, what it
costs in practice, and honestly when it is NOT worth using. Other workers are writing the posts on X
(`P/research/02-posts.md`) and the how-to (`03-howto.md`) at this same moment. Do not wait for them. When
your own reading is done, skim whichever of the two exists by then, do not repeat it, and note anything
that contradicts it.

Work through the actual pages (not search snippets): <press URLs>, <independent benchmark sites>, <community
threads: Reddit via old.reddit.com or the .json endpoint, Hacker News, credible first-look videos>.

Write `P/research/05-reactions.md`:
- The 8 to 10 strongest independent findings (who, what they tested, the result in one plain sentence,
  exact quote, URL, how much weight it deserves this early).
- A comparison table against the alternatives on price, speed and the benchmarks with real published
  numbers. Every cell sourced or marked "not published".
- Real-world cost and limits, each labelled official or user report.
- Complaints people are actually hitting, with quotes. Separate "widely reported" from "one person said".
- "When it does NOT make sense": a sourced list, plus the best counter-arguments.
- Myth versus fact: 5 things people are getting wrong today.
- Capture 8 to 12 proof screenshots of the most quotable items into `P/proof/community/`, each with its
  `.source.json`, and write `proof-index.json`.

DONE WHEN: `05-reactions.md` has every section above with a URL on every finding, and 8 or more captures
you have opened are in `P/proof/community/` with their source records. Reply in 20 lines or fewer: the 5
findings most worth saying on camera, the most important caveat, and anything that conflicts with the
maker's own claims.
```

---

## 6. Fact-checker (after the script, before any voice)

```
You are the independent fact-checker for a YouTube explainer about <TOPIC>. You did not write the script and
you do not trust it yet. First read `<P>/BRIEF.md`.

WHAT TO CHECK: `P/script/takes.json` (<N> takes; `say` is exactly what an AI avatar will speak in the
presenter's cloned voice; numbers are written in spoken form). The presenter on screen is an AI avatar: the
screen says so for the whole video, and the avatar does not announce it. "He" means <PRESENTER>; "it" (the
boss) means the run that made the video. Flag any take that makes a point an earlier take already made.

EVIDENCE YOU MAY USE (read these, then go to the original source whenever a note is ambiguous or two notes
disagree): `P/research/01-official.md` to `05-reactions.md`, the proof captures with their source records
(every `P/proof/*/*.source.json`), and the live test in `P/proof/live-test/`. Facts about this production that
only the orchestrator can vouch for (accept as given, but flag wording that overstates them):
<the list, plainly: what was prompted, what ran where, what failed and how it was handled>.

FOR EVERY TAKE decide: `ok` (every claim is supported as worded), `soften` (true but overstated, missing a
qualifier, or rounded too far), `wrong` (not supported or contradicted), or `no-claim`. Check each number
against the exact source line (spoken rounding is fine when the screen can show the exact figure: say what
that figure is). Check names, who said what, dates, "the maker says" against what the maker wrote, and that
nothing said about this version is really about another one. Check <the riskiest take ids> with extra care.

WRITE two files:
1. `P/script/factcheck.md`: a table (take id, verdict, exact source sentence with URL, proof files, note),
   then "Must fix before recording" with a replacement sentence for every `wrong` or `soften` take, in the
   same plain spoken style and about the same length, then "On-screen exact figures" (what the screen must
   show where the voice rounds).
2. `P/script/proof-map.json`: for each take id, `{"verdict": ..., "claims": [{"text": ..., "exact": "<figure or
   quote the screen should show>", "proof": ["<path relative to P>"], "url": ..., "source_pill": "<domain> ·
   captured <date>", "highlight": [x, y, w, h] or null}]}`. Use only proof files that exist; capture a missing
   one into `P/proof/official/fc-<slug>.png` and list what you added. The editors build every graphic from
   this file, so it must be complete and exact.

Do not edit `takes.json`, `takes.src.txt` or any research file. Do not start other agents.

DONE WHEN: every take has a verdict, every `wrong`/`soften` has a replacement sentence, and every factual
take has at least one existing proof file in `proof-map.json`. Reply in 25 lines or fewer: counts per
verdict, the full "Must fix" list (take id, problem, replacement), and any proof you had to add.
```

## 7. Thumbnail designer

```
You are the thumbnail designer for a YouTube video on <PRESENTER>'s channel about <TOPIC>. First read
`<P>/BRIEF.md`, then the style pack: `P/research/04-style.md` (titles, thumbnail style spec with hex values,
the ranked concepts, the assets list). His real thumbnails are in `P/refs/thumbnails/`: open the contact
sheet (`_sheet.jpg`) and his five best at full size.

GOAL: three finished, upload-ready thumbnails (1280x720 PNG under 2 MB, plus a 2560x1440 master of each)
that look like they belong beside his best performers, plus one comparison sheet. Working title:
"<TITLE>". The twist: <one sentence>.

Make these three: <A, B, C from the style pack's concepts: template, headline words, elements>.

HOW: generate the plate with an image model using his real thumbnails as style references (Higgsfield CLI:
`higgsfield model list --image`, `higgsfield generate cost ...`, `higgsfield generate create <model> --prompt
"..." --image-references <file> --aspect_ratio 16:9 --wait --json`). Check the cost before each generation
and keep the whole job under <N: 60 is plenty; the first run's three thumbnails used 14> credits. Then composite the exact official logos, and the text where the
model's lettering is not clean, yourself (Pillow). Never ship an invented or warped logo, misspelled text,
or a wrong version number. Never draw launch art from memory: download the real image. Keep the bottom-right
corner clear for the time stamp.
SHARED QUEUE: the account runs 3 jobs at a time and the avatar clips have priority. Run ONE job at a time;
on `rate_limit_reached` wait 30 s and try again.

Review like a viewer: shrink each to 320x180 and 168x94 and open those. Make `P/thumbnail/_side-by-side.jpg`
(your three beside four of his best at the same size). Two review rounds at least; say what you changed.

Honesty: a claim on the thumbnail is allowed only when the video really did that. No fake numbers or UI.

OUTPUT in `P/thumbnail/`: the three PNGs (`thumbnail-A.png`, `-B`, `-C`), masters in `masters/`, prompts in
`work/prompts.md`, `_comparison.jpg` (your three next to each other at full size), `_side-by-side.jpg`, and
`README.md` (your pick and why, what is generated and what is
composited in each, credits spent, anything not perfect).

DONE WHEN: three PNGs at 1280x720, every word spelled right, logos are the real marks, each readable at
168x94, README states your pick. Reply in 10 lines or fewer.
```

## 8. B-roll maker (analogies acted out)

```
You make the story B-roll for a YouTube explainer on <PRESENTER>'s channel about <TOPIC>. First read `<P>/BRIEF.md`.

GOAL: <N> short pixel-art clips in the look of his earlier videos (animated 16-bit pixel art in a curved CRT
frame, one consistent world, the same recurring protagonist), each acting out one spoken line, with the
visual change (the "reveal") landing at a known second so the editor can time it to the punch word.
Output: `<W>/media/broll/`.

READ FIRST (his established method): `~/.claude/skills/screenplay-demo-edit/references/broll-higgsfield.md`
and `intro-and-stories.md`, `~/.claude/skills/screenplay-edit/references/concept-visuals.md`, and the last
video's library as the style and character reference: <path to its media/broll/ folder: INDEX.md, the
sheets, and the prompts and keyframes in its src/broll/. For Samin the newest is
`~/Borumi Projects/Fable 5.2 screenplay/media/broll/`>. Reuse the same protagonist by passing those
keyframes as references. The script:
`P/script/script-final.md`.

THE CLIPS (about 5 s each, 16:9, no readable text, no real brand marks, no real people):
<for each: slug, the spoken line, the scene, and "Reveal about X s: what changes">

HOW: keyframe image first, then image-to-video, with the models the reference doc names. SHARED QUEUE: run
ONE Higgsfield job at a time; on `rate_limit_reached` wait 30 s and try again. Check the cost before each
job, keep the task under <N: price one clip first with `higgsfield generate cost`, then allow each clip
three tries> credits. Encode finals h264, 30 fps, 1 s GOP, no audio, 1920x1080.

REVIEW: for each clip make `<slug>-sheet.jpg` (one frame every 0.5 s) and OPEN it. Same protagonist, CRT
frame, no garbled text, the reveal really happens and when (measure the second), nothing uncanny. Up to 2
retries each.

OUTPUT: the clips, their sheets, and `INDEX.md` (slug, file, duration, what is in it, reveal second, spoken
line). Prompts, keyframes and job ids in `<W>/src/broll/`. Touch nothing else in `W`.

DONE WHEN: every clip has a sheet and an INDEX.md row with a measured reveal time. Reply in 10 lines or fewer.
```

---

## 9. Part writer (one per part, all at once)

The rules live in `W/WRITER.md`; the task message only names the part and what is special about it.

```
You are the writer of PART <X> of a video edit. Your full brief is the file `<W>/WRITER.md`: read it first and
follow it exactly (it tells you what else to read, how to test, the hard rules, and the reply format).

Your part: **<X>, "<section names>"**. Word range `<w first>` to `<w last>` (output time <a> to <b>, <n> s).
Takes <ids> (see `W/parts.md`, section "Part <X>", and `W/plan.md`, section "<X>"). <The chapter is anchored
at `<w>` (its card covers the first 2 s).> The next part starts at `<w next>`.

Specific to this part:
- <the one or two beats that carry this part, and which asset each uses (a B-roll clip and its reveal second,
  a real capture, a live-test file)>
- <every number in this part with its proof file, and "when he says a number it is the biggest thing on
  screen, on the real capture or directly beside it">
- <how the part ends>
```

## 10. Visual reviewer (one per stretch of 2 parts, all at once, never a writer)

```
You are a visual reviewer for a video edit. Your full brief is the file `<W>/REVIEWER.md`: read it first and
follow it exactly.

Your stretch: **parts <X> and <Y>**, output time <a> to <b>. Contact sheets `sheet-<i>.jpg` to `sheet-<j>.jpg`
cover it. Write your review to `W/review/v1/fixes-<X>-<Y>.md`. Use `/tmp/review-<XY>/` for your stills.

Extra attention for this stretch:
- <the figures to check one by one, quoted from factcheck.md's "On-screen exact figures">
- <anything the writers flagged as weak in their own reports: ask the reviewer to judge it at full size>
- <any stretch where the picture may not match the words>
```

## 11. Fixer (one per part with findings, all at once)

```
You are the fixer for PART <X> of a video edit. Your full brief is the file `<W>/FIXER.md`: read it first and
follow it exactly.

Your part: **<X>** (`W/parts/<X>.yaml`, words `<w first>` to `<w last>`, <a> to <b>, "<section>"). Your review
file: `W/review/v1/fixes-<...>.md`, every item tagged [<X>].

The boss's decisions for this part (they win over the reviewer's suggestions where they differ):
- <for each must: exactly what the viewer should see instead, with the real file to use>
- Everything else in the review: fix as the reviewer suggests. Do not change <what the review says works>.
```

The boss reads every review before writing these. A reviewer says what is wrong; the boss decides what
replaces it, and gathers anything real that the fix needs first (a real screenshot instead of a rebuilt
window, the real brief instead of a made-up one).

## 12. Final-cut reviewer (one, after the preview render, never anyone who worked on the edit)

Fill the `[[FILL]]`s in `W/FINAL-REVIEW.md` and run `scripts/review_aids.py` first. Count this agent in the
closing board before the preview is rendered: it is one of "the agents the boss started".

```
You are the final-cut reviewer of a finished video. Your full brief is the file `<W>/FINAL-REVIEW.md`: read
it first and follow it exactly.

The file to review: `<W>/out/preview-v1.mp4` (<length>). Write your review to
`<W>/review/v2/final-review.md`. Use `/tmp/final-review/` for your frames and strips.

Extra attention:
- <takes whose clip was rendered again, or whose read was reworded late: ids and why>
- <the last take: it should end on a closed mouth and hold>
- <anything you are unsure of yourself: say it, and ask for a judgement at full size>
```

`SHIP`: render the final. `SHIP AFTER MUSTS`: fix every must, look at each fix in a preview of that
stretch, then render the final. `DO NOT SHIP`: fix, render a whole new preview, and brief a NEW final
reviewer (one more agent on the count).
