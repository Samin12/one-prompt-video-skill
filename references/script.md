# Writing the script

The script is written as takes: one voice read and one avatar clip each. It lives in
`P/script/takes.src.txt`, which is the only place a spoken word is ever changed.

## Takes

```
o06 | The Orchestrator
And here's why it matters for your wallet. Fable 5.2 costs 40 dollars per million tokens coming out. Sonnet 5.5 costs 10. And Haiku 5.5 starts at 50 cents.

c03 | Where This Is Going | tail=1.6 freeze_at=8.63
And if you want to build agent teams like this, watch this video here, or join Claude Club, where he's helping people set this up the right way. Have fun.
```

- First line: `id | section | optional settings`. Ids are a letter for the section and a number (`i01`,
  `n04`). The section name becomes the chapter title, so write it in Title Case, under 5 words.
- One idea per take. **45 words or fewer fits one avatar clip** (the model fails above 15 seconds of
  audio). Up to about 85 words still works, as two clips joined at a pause: one more seam for the final
  reviewer, so keep those few (the first run had 8 in 54). `make_takes.py` lists them and refuses
  anything longer. Plan about 195 words and 5 takes per minute of video.
- Blank lines inside a take are fine (one sentence per paragraph, as he reads). A take ends at the next
  header line.
- **Spoken forms**: "40 dollars", "a dollar eighty-two", "thirty-one hundred", "A P I", "T three Code".
  The voice reads symbols and abbreviations badly, and the fact-checker needs the words as they will be
  heard. The screen shows the exact figure.
- `python3 <skill>/scripts/make_takes.py` (inside `P`) turns the file into `takes.json`. Keep a readable
  copy for him as `script/script-final.md` in teleprompter format (one sentence per paragraph, bold
  section headings), with suggested lines for his own candid clip on top.
- Phrases that must be heard exactly go in `script/must-hear.json`: `{"o06": ["50 cents", "Haiku 5.5"]}`.
  Put every name, product and key number in it, numbers in digits. `build_takes.py check` fails a read
  that misses one.

## Shape of the video

His model-release explainers, measured from his own transcripts, and the shape the first run used:

1. **Intro, 35 to 45 s.** The news in sentence one, what was done with it in sentence two, the list of
   what the viewer gets, "Let's get into it." No greeting, no channel intro, no "I'm an AI clone": the
   avatar starts on the topic.
2. **Why this matters**: an analogy for where the thing sits (the specialist you only bring in for the
   hardest job), then the plain definition.
3. **What's new**: three or four changes, counted out loud, cheapest to explain first, the big one last.
4. **What people are doing with it**: real posts, each one sentence that does not overstate, then the
   pattern they share.
5. **The main idea**, with its analogy acted out (the general contractor), then the mechanism, then the
   real numbers.
6. **Set it up**: the steps, from the run you really did, with what it cost.
7. **When not to use it**: the honest section. "For you if" and "probably not if". The maker's own
   caveats and an independent tester's.
8. **The receipts**: what happened on this run, including what broke.
9. **Where this is going**: one thought, then the next video and Claude Club in one or two sentences.
   "Have fun."

Chapters are these sections. No chapter card on the intro.

## His voice

- Calm, friendly engineer. "You", "you guys". Sentences start with "And", "So", "But", "Okay, so". A long
  chained sentence, then a short one: "Okay, cool." "That's the new part."
- Every new idea opens with a picture or a story, then the plain definition ("is basically..."). Never the
  other way round. Name a concept once and keep the name.
- A short spoken bridge before every section ("Okay, so with that out of the way...").
- Cost and limits stated early and plainly. His own numbers said exactly, with what they mean.
- One line on benchmarks, then the practical part. He does not read tables.
- He speaks at 182 to 198 words a minute. Write for that.
- Words he does not say: delve, utilize, robust, seamless, unleash, elevate, landscape, supercharge,
  revolutionize, "welcome back", "in today's video", "like and subscribe", "thanks for watching". "Insane"
  is for the title, not the voice.
- Never the Claude Club price. The call to action is the last 15 to 30 seconds, plus one soft mention in
  the middle tied to something useful ("they'll be in the community, the link's in the description").

A full measured style pack (25+ verbatim lines, title and thumbnail patterns with view counts) was built
for the first run: `~/SaminOS/10 YouTube/Projects/2026-Q4 Fable 5.2 Release Video/research/04-samin-style.md`.
Still send the style worker (the thumbnail designer needs fresh thumbnails and titles), but give it that
file to start from: its brief has a line for this. It writes `P/research/04-style.md`.

## What the avatar may say

- It speaks as the avatar: "he" is Samin, "I" is the clone, "it" or "the boss" is the run that made the
  video. Keep this straight in every take; the fact-checker reads for it.
- It never says his name: on screen instead.
- It does not repeat what his own opener says. If he will film a clip that introduces the topic, the
  avatar's first take moves on from it.
- It says what broke. The receipts section is the part viewers trust the rest because of.
- Anything it promises ("the files will be in the community") becomes a to-do for him in the hand-over.

## No redundancy

Before the fact-check, read the script once only for repeats:

- a point made in the intro and again in its own section
- a number said twice with different wording
- an analogy explained after it was already acted out
- a section that re-introduces the topic

Cut the weaker one. A 10-minute script that says each thing once beats a 12-minute one that says it twice.

## After the fact-check

Apply every replacement in `takes.src.txt`, run `make_takes.py`, and only then make voice. If a line has
to change after its read exists (the voice cannot say a word, a pause is wrong), change the source file,
re-read that take alone, and check the new wording against the same source: a reword is a new claim.
