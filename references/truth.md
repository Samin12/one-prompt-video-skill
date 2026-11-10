# The truth standard

The video is presented by something that is not him, saying words he did not say. The only thing that
makes that acceptable is that every fact in it can be traced, and that it never pretends to be more real
than it is. Treat the video as evidence someone will check.

## Four kinds of thing on screen

| Kind | Where it comes from | How it is marked |
|---|---|---|
| An outside fact (a price, a benchmark, a quote, a post) | a capture of the real page or post, made that day, logged out | browser bar or post card, source pill "`<domain> · captured <date>`", a highlight on the exact words |
| A fact about this production (how many workers, what failed, what it cost) | `W/run-facts.md`, the run log, the live-test files | "From the run log", or the real screenshot or file itself |
| A diagram or analogy (a tree, a contractor story, a globe) | you, to explain | nothing, as long as every label on it is true |
| Something rebuilt to look like an app | `run-facts.md` and real output only | the word "Recreated" on it for as long as it is up: in the replica's title or status line, or a badge beside it (the writer adds it; `briefs/WRITER.md`) |

If a beat fits none of the four, it does not go on screen.

## Rules that follow

- **The screen shows the exact figure when the voice rounds.** He says "about seven and a half points";
  the screen says "7.5 points lower" beside the source's sentence. The fact-checker's "On-screen exact
  figures" list is the editors' source.
- **A number never appears without what it is a number of.** "$5.75" is "the GPU render cost". "$563" is
  "Fable 5.2 alone, High effort". A qualifier the fact-check added stays readable for as long as the
  number is up.
- **Say whose test it is.** A benchmark run by one lab is not "the maker's own test".
- **Never show a screen of something nobody ran.** If the docs name a command you did not run, show the
  docs. If a feature is not on his account, say "not on his account yet" on the card.
- **Never rebuild what you can capture.** A real screenshot of the app with private parts cropped out
  beats a replica. Before capturing his real windows, check what else is in frame (other threads, names,
  emails) and crop or wait.
- **Real posts are the real captured post**, with the author visible, not a retyped quote. A demo video
  plays inside its post card with the source showing.
- **Stories may use made-up values** (a taxi meter, a fare) because nobody takes them as data. A writer
  lists every such value in its report.
- **Teases only tease what is in the final cut.** If the cut changes, check every tease again.
- **Thumbnail and title claims are held to the same standard.** "One prompt" is allowed only while it is
  true.

## The fact-check

Runs after the script is written and before any voice is made (`briefs/workers.md` section 6). It
returns a verdict per take and `proof-map.json`, which maps every claim to the proof file that shows it.
Writers build graphics only from that map. After it:

1. Rewrite every `wrong` and `soften` take, usually with the checker's replacement sentence.
2. Note the three or four takes it was least sure of in `script/must-hear.json` terms too: names and
   numbers that must be heard exactly.
3. If you reword a line later (for the voice, for pace), check the new wording against the same source.
   A reword is a new claim.

## Disclosure

- A badge above the avatar reads "AI avatar" for the whole video (`chapters.badge` in the edit header).
- The hand-off from his own clip says the clone is next, in large type.
- The description says which part is the avatar.
- YouTube's "altered or synthetic content" question is answered Yes.
- His name is on screen, not spoken, unless the cloned voice's pronunciation of it has been checked
  against a real recording of him saying it.

## What you tell him

In the hand-over, without softening: what is generated, what is rebuilt, anything his own clip says that
differs from what happened, anything that will go stale (launch-week prices, a dated offer), and every
check that was a measurement rather than a person watching or listening.
