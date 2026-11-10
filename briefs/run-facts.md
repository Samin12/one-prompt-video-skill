# Run facts: what really happened while this video was made

Written by the orchestrator. Use ONLY these for anything on screen about the production itself. Do not
add workers, numbers or events that are not listed here. Anything rebuilt as a UI replica says
"Recreated" on itself (`WRITER.md` says how). The boss keeps this file current: writers and reviewers
read it as truth.

## The prompt
[[FILL: who sent it, from where, and the path of its verbatim text (`media/the-prompt.txt`, typos kept).]]

## The boss
[[FILL: model id, the app it runs in, the machine. What it did itself (plan, briefs, script, checks).]]

## The workers
| # | Worker | Job | Plan | Result |
|---|---|---|---|---|
[[FILL: one row per worker as it is started. Model in the heading if they all share one.]]

## What broke (all real)
[[FILL: each failure with the tool's own error line, copied, and what was done about it.]]

## The avatar and the voice
[[FILL: voice clone source and its measured similarity; avatar model, resolution, the one photo, take count;
anything the presenter never says and why.]]

## Any live test shown in the video
[[FILL: files, exact commands that were run, time, cost, per-model split. Say what was NOT run, so nobody
draws a screen of it.]]

## Final numbers for the closing board
See `receipts.json` in this folder. Until a number is known its value is `null`, drawn on screen as "…":
never invent one. The agent count is every agent the boss started, including failed starts and the
final-cut reviewer: fill it last, then update the closing board's element in the last part, merge, check.
