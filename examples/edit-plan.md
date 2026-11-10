# Plan: "Claude Fable 5.2 Made This Video From One Prompt"

Work dir `W` = `~/Borumi Projects/Fable 5.2 screenplay`. Project folder `P` =
`~/SaminOS/10 YouTube/Projects/2026-Q4 Fable 5.2 Release Video`.

## What this video is
Samin is in Korea. He typed one prompt; Claude Fable 5.2 ran as the boss of a team of agents that made the
video. The talking head in the camera tile is an **AI avatar of him with his cloned voice**, and it says so
in its first line. His own candid clip goes in front of this render later (he films it), so this edit
starts cold on the avatar's first word. About 10 minutes, 54 voice takes, 9 sections.

The script is `P/script/script-v2.md` (readable) and `W/brief.txt` (word ids). Every factual line was
checked by an independent agent: `P/script/factcheck.md`, and the claim-to-proof map is
`P/script/proof-map.json` (**build every proof card from the files it lists for your takes, nothing else**;
its "On-screen exact figures" list in factcheck.md says what the screen must show where the voice rounds).

## The bar and the look
- House layout, panel look, from the first frame: avatar in the tile on the right, step badge above it,
  every graphic in the left panel. Never hide or move the tile. The one planned break is the closing
  moment (see part G).
- The bar is his "Paste This Into Claude v2" edit: work dir
  `~/Borumi Projects/paste this into claude code screenplay` (skim `parts/C.yaml` and
  `parts/G.yaml` for how stories, proof cards and replicas are written). Nothing may read sloppy: no empty
  panel, no half-faded card, no label sitting on the text it points at, no word cut at a crop edge.
- Motion: something useful changes every 1.5 to 3 s, nothing static past about 4 s, each beat at least
  2 s, the old element leaves before the new one enters, visuals land on the word that names them.
- Proof first: every claim, number, name and post gets the real capture in an `image` card (`url`,
  `source: "<domain> · captured Nov 9, 2026"`, `crop` to one paragraph or chart, a marker `highlight`
  landing on the spoken word). Measure rects on the PNG yourself and confirm with `screenplay still`.
  When he rounds, the screen shows the exact figure. Real posts are shown as the real captured post
  (`proof/tweets/<slug>.png`), with the key line marked; play the post's saved video or image where there
  is one (`proof/tweets/media/`, muted).
- Analogies are acted out, never written out: a `type: story` scene and/or the pixel-art B-roll in
  `media/broll/` (read `media/broll/INDEX.md`; start a clip so its reveal second lands on the punch word).
  One consistent world. Then a 2 to 4 s clean diagram of the mechanic.
- Text: headlines under 7 words, no em dashes, Title Case chapter names, product names spelled right
  (Claude, Claude Code, Fable 5.2, Opus 5.5, Sonnet 5.5, Haiku 5.5, Higgsfield, T3 Code, Claude Club).
  Never show the Claude Club price. No "Watch next" card.
- Honesty: anything rebuilt (a terminal session, the T3 Code thread, a run board) is built from
  `run-facts.md` and `media/live-test/` only and carries the "Recreated" stamp. No invented numbers, logos,
  quotes or UI. Third-party clips play inside their post card with the source visible.
- The avatar disclosure: the step badge eyebrow reads "AI avatar" for the whole video (it is set in
  `edit.header.yaml`; do not cover the badge).

## Assets
- `proof/official/` (`off-*`, `orch-*`, `fc-*` web captures, `sc-*` system card pages), `proof/tweets/`
  (+ `media/`, `raw/` for full-length posts), `proof/community/`. Each PNG has a `.source.json` (claim,
  url, exact line, normalized highlight box) and a `.json` (page text and highlight rects). The capture
  tool does not draw highlights on the image; you draw them with `highlight`.
- `media/the-prompt.txt`: his real prompt, verbatim (keep the typos).
- `media/own/samin-studio.jpg`: the one real photo the avatar was made from. `media/own/f51-octopus.mp4`
  (9 s, silent) and `.png`: his own Sep 2, 2026 video at 8:43, his real "The Octopus Workflow" slide with
  the real him in the corner (source pill: `youtube.com · Samin Yasar, Sep 2, 2026`).
- `media/pilot/pilots-side-by-side.mp4`: the two avatar pilots (left Wan 3.0, right Intone).
- `media/live-test/`: the real Claude Code test (agent files, the paragraph, the run log, the diff).
- `media/broll/`: six pixel-art clips (lineup-specialist, contractor-plans, contractor-inspect,
  thousand-agents, one-picture, korea-prompt) when `INDEX.md` lists them. If a clip you need is not there
  yet, build the beat as a `story` and say so in your report.
- `media/thumbnail-*.png`: the finished thumbnails, when present.
- Replicas: `terminal` (Claude Code CLI), `t3-code`, `claude-desktop`, `browser`. Run
  `screenplay replicas <id>` for targets and state keys.
- `run-facts.md`: the only source for anything about the production itself.

## Part by part (take ids are in parts.md with their word ranges)

### A. Intro and Why This Matters (i01 to i05, w01 to w04)
No chapter card on the intro. The first frame must be readable and make someone stay.
- i01 "that was the real one. I'm not. I'm an AI clone": show how the clone was made, as a tiny build:
  the one real photo (`media/own/samin-studio.jpg`) + "2 minutes of mic audio" (a waveform) → arrows →
  "AI avatar". On "nobody filmed me, and nobody recorded these words": two crossed-out icons (camera,
  microphone).
- i02 "he gave it one prompt. Make the whole video.": the real prompt types on (`prompt` element, the
  first two lines of `media/the-prompt.txt`, verbatim, label "The prompt, word for word"). On "ran as the
  boss ... a team of other agents": a `tree`, root "Fable 5.2, the boss", children from run-facts.md
  (Research, Fact-check, Voice, Avatar, Motion graphics, Thumbnail, B-roll) landing one by one.
- i03 the five things it made, each landing on its word with a REAL preview: a proof capture, a page of
  the script, a waveform, a frame of this edit, a thumbnail (`media/thumbnail-*.png` if present).
- i04 roadmap: four numbered circles, each with a framed preview of that section's best real visual
  (1 the Fermat chart, 2 a post, 3 the contractor B-roll, 4 Anthropic's "start with Opus 5.5" line).
- i05 "where this run broke": two red rows from the run board (the real error text), 2 s, then out.
- Chapter "Why This Matters" at w01. w01 and w02: the company lineup (B-roll `lineup-specialist` reveal on
  "specialist", then a story or row of four people, and the names Haiku, Sonnet, Opus, Fable land on
  them on his words). w03: the docs line "most capable model open to all customers" marked. w04: the
  announcement's "same underlying model" line for Mythos, then "Four things" as a 4-tile grid.

### B. What's New (n01 to n08)
- n01 the @claudeai price post, marks on "$8" / "$40" and "down from $10 and $50"; a small
  before/after (10 → 8, 50 → 40).
- n02 plans: a small table built from the pricing capture (Pro, Max, Ultra: Fable included?), marks on
  "up to half your weekly limit" and the launch-week dates for Pro.
- n03 "up to 30% faster" marked; the @ClaudeDevs fast mode post, "2.5x faster output, for twice the price".
- n04 the FrontierCode 2.0 chart: marks on Fable 5.2 High 45.3% at $6.72 and Opus 5.5 Max 45.5% at
  $12.82. Source line must say the test is Cognition's ("FrontierCode 2.0, run by Cognition").
- n05 a 2 s beat: "It manages other AIs" with a tree growing behind it.
- n06 the Fermat chart from the @claudeai post (the image is in `proof/tweets/media/`): green line to 1.00
  at 30 h on "about 30 hours", orange line flat at 0.26 on "a quarter of the way". Small print under the
  card: "Earlier snapshot, one run. 28.7 hours per Anthropic's engineering blog."
- n07 the announcement paragraph ("over 1,000 subagents ... eight days ... boots on a laptop") with marks
  on each phrase as he says it; B-roll `thousand-agents` (reveal on "a thousand sub-agents").
- n08 mark the word "prototype" in the same paragraph, then the line "Not a smarter chatbot. A *manager*."

### C. What People Are Building (p01 to p05)
Real posts, each as its real capture with the clip playing in or beside it.
- p01 Riley Brown: post + `rileybrown-blender-room-1.mp4` playing; marks "13 camera shots", "10 GPUs",
  "4K". Do not show "$5.75" unless labelled "GPU render cost". The PNG's video frame is black: use the clip.
- p02 Allie K. Miller: post + `alliekmiller-water-map-1.mp4`; marks "more than 5 GB", "3,100 counties",
  "a dozen other AI agents check its work". Never present "Indianapolis is #1" as fact (crop it out).
- p03 Kieran Klaassen: post (use the full version in `raw/` if the main PNG is cut); marks "film
  composer", "at night, in about a week".
- p04 Uber: the customer quote from the announcement (`fc-uber-170-reviewers.png`), marks "10-12 hour
  security audit", "about 170 reviewer agents"; name line "Andrew Mager, Staff Engineer, Uber".
- p05 the pattern: three chips (Long jobs, Big jobs, One model in charge) then the three post cards
  shrink into children of a tree.

### D. The Orchestrator (o01 to o08)
The centre of the video. Analogy first, acted out.
- o01 to o03 the general contractor: B-roll `contractor-plans` (reveal on "they hire an electrician, a
  plumber and a painter"), a work order handed to each (story), B-roll `contractor-inspect` (reveal on
  "inspect the work"), then two meters: a small pricey one ("a few hours of thinking") and a big cheap one
  ("hundreds of hours of doing"). "And that's an orchestrator": the word lands as a title.
- o04 the mechanic as a clean diagram: `tree`/`flow` with Fable 5.2 on top (plans, hands out, checks) and
  Sonnet 5.5 and Haiku 5.5 below, a brief going down and a report coming back.
- o05 his own video: `media/own/f51-octopus.mp4` in a card (his real "The Octopus Workflow" slide).
- o06 the pricing table capture: marks on $40, $10, $0.50 as he says them.
- o07 Anthropic's test: `fc-defect-search-563-alone.png` and `fc-defect-search-165-team.png`, marks on
  $563 and $165; a counter or bar that drops from 563 to 165, "71% less" (the exact figure).
- o08 "about seven and a half points lower": 0.909 vs 0.833 side by side, marked. End on the rule:
  "Hand off the bulk. Keep the judgment."

### E. Set It Up (s01 to s10)
Show how to do it, concretely. Rebuilt screens carry the "Recreated" stamp.
- s01 three ways as three tiles (Claude Code, Projects, T3 Code).
- s02 `terminal` replica: `claude update` then `claude --model fable` typed; proof card "Fable 5.2 requires
  Claude Code v2.1.321 or later". Then the folder `.claude/agents/` with three files appearing.
- s03 the real `researcher.md` (from `media/live-test/agents/`) with `model: haiku` marked; then the real
  paragraph from `media/live-test/prompt.txt` typing on (first 11 lines only, the boss paragraph).
- s04 the real run, rebuilt from the log: main session claude-fable-5-2; researcher claude-haiku-5-5;
  builder claude-sonnet-5-5; checker claude-sonnet-5-5; the one-line diff; "2 tests passed".
- s05 the receipt: 93.3 seconds, total $1.8176, a bar split Fable 5.2 $1.5182 vs workers $0.2994. Label
  "API list prices, one small test".
- s06 Projects: the docs capture, marks on "Coordinator model" and "Thread model", and the
  "rolling out gradually" line. A small tag: "Not on Samin's account yet".
- s07 `t3-code` replica rebuilt from run-facts.md: the parent thread and its delegated workers; then a
  tree: Fable 5.2 → Claude 300, Claude 100, Claude 200, with real worker names under each.
- s08 the brief: five lines light up on his words (Goal, Context, Done when, Output, Do not), built from a
  real brief (`P/BRIEF.md` and the worker table in run-facts.md).
- s09 the system card line "left doable, requested work undone in 6-13% of sessions" marked (small print:
  "Measured on Mythos 5.2, the same underlying model"); then "A vague brief gets you the wrong house" as a
  2 s story callback.
- s10 a `cta` card: "In the description" with the three things (3 agent files, the boss prompt, the brief
  template). No price, no checkout page.

### F. When Not To Use It (x01 to x07)
- x01 the @claudeai post "we recommend starting with Opus 5.5", marked.
- x02 a `compare`: "For you if" (big, messy, takes hours; too big for one chat) vs "Probably not if"
  (quick question, small edit, one piece of writing). B-roll `one-picture`, reveal on "hang one picture".
- x03 the docs line "came out ahead in only two situations", then a 2-row table: Opus 5.5 + Sonnet 5.5
  $139, 0.831 and Fable 5.2 + Sonnet 5.5 $165, 0.833 ("19% more").
- x04 the system card line "half the time" and "but at a higher cost", marked on his words.
- x05 the effort costs: Xhigh 49.1% at $14.19, Max 45.7% at $44.70 (system card page), and Yuchen Jin's
  post "Don't use Fable 5.2 Max man."
- x06 Artificial Analysis: the Max page (#1 of 74 for intelligence, #73 of 73 for cost, $26.54 a task) and
  the Medium page ($3.80 a task). End on "Pick the effort level first."
- x07 Dan Shipper's post, marks on "live in 3 days" and "slow and burns through tokens"; then Anthropic's
  help page line "Fable models use your usage limits faster than other Claude models."

### G. The Receipts and the close (r01 to r04, c01 to c03)
- r01 the run board: a table of the real workers from run-facts.md (worker, plan, model, result). Every
  model cell reads Fable 5.2: mark that column on "not the cheap ones".
- r02 two rows red with the real 400 error text, then the plan cell changes and they turn green.
- r03 the real rate-limit error (`"concurrent_jobs_limit":3`), 35 of 38 red, then a retry sweep to green.
- r04 `media/pilot/pilots-side-by-side.mp4` playing, labels "Wan 3.0 · 26 credits" and "Intone · 126
  credits", a mark when the right one changes angle (about 7 s in). Then proof thumbnails flipping from
  "captured" to "checked". Then the receipts board from `receipts.json` (keep ALL numbers in one `table`
  or `stat` element so the boss can update them before the final render).
- c01 "which model is the smartest" as one model tile alone, then "which model should be the boss, and
  who's on its team" as the tree.
- c02 B-roll `korea-prompt` (reveal on "in Korea"); "he still reviews this": a checklist with one open
  box, "Samin reviews before it goes up".
- c03 his Agent Teams video as a framed preview (`P/refs/thumbnails/178935-*.jpg`), then a Claude Club
  card (name and the starburst only). Last line "Have fun." on a clean frame.
