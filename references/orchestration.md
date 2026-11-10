# Running the workers

You are the boss: the one model that holds the whole plan. Workers are other agents that each get one
brief and return one result. The video usually teaches this pattern, so run it the way you would want
it shown: the receipts section is built from what you actually did.

## Who does what

**You keep**: the plan, every brief, the script, the live test, every decision after a review, the voice
and avatar scripts, assembly, the final checks, the hand-over. These need the whole picture or are cheap
to do directly.

**Workers get**: anything that is mostly reading (research), mostly making (thumbnails, B-roll, one part
of the edit), or has to be independent of you (the fact-check, every review). Independence is the point
of the last group: the fact-checker found 13 faulty lines in the boss's own script, and the final-cut
reviewer found three faults the boss had looked straight past.

The first run's roster, for scale (a 10-minute video):

| Wave | Workers | Started when |
|---|---|---|
| Research | 5 | minute 3 |
| Fact-check | 1 | script drafted |
| Thumbnails, B-roll | 2 | script checked |
| Part writers | 7 (one per part) | timeline locked |
| Reviewers | 4 (one per 2 parts) | parts merged |
| Fixers | 7 | reviews read and decided |
| Final-cut reviewer | 1 | preview rendered |

Plus two that failed on a plan that could not run the model, two one-line plan tests and one quick
verifier: 32 in all.

## Which model, which plan

- **The worker model is his call.** If the prompt names it ("use Fable with delegates"), use it. If it
  does not, the cheaper pattern the video itself recommends is the default: the strongest model as boss,
  a mid model for writers and fixers, a small one for lookups. Say which you chose and why in the run log.
- **Spread workers across his plans** so no single plan's limit stalls the run. In T3 Code that is
  `delegate_task` with a provider (one per Claude subscription); read `orchestrator_capabilities` once
  first. In plain Claude Code it is subagents. In any harness: a worker starts with only its brief.
- **Test a plan before trusting it.** A one-line task on the worker model, per plan, before the research
  wave. Record what fails and the exact error: it is real material for the video.
- A worker that fails is restarted on another plan with the same brief, plus what the finished workers
  have already written (so it builds on them instead of repeating them).

## Briefs

Templates: `briefs/workers.md`. What every brief has, and why:

- **Read first**: `P/BRIEF.md` (shared rules, the proof-capture command). Shared files beat long task
  messages: rules written once cannot drift between workers.
- **The job, as outputs**: exact file paths and what goes in each. "Write `P/research/01-official.md` with
  these sections" gets a usable file; "research the release" gets an essay.
- **Do not**: touch other paths, start other agents, post anything, end the turn while a command runs.
- **Done when**: a condition the worker can test. Models stop early on long tasks; a done-line they can
  check is what keeps them going to the end.
- **Reply**: a line limit and the exact contents. You will read 30 of these.

For the edit, the rules go in `W/WRITER.md`, `REVIEWER.md`, `FIXER.md` (templates in `briefs/`), and the
task message only says which part and what is special about it.

## Waves, and what you do while they run

Never idle while workers run. The first run's overlaps:

- research running → voice cloned, avatar models piloted, the how-to run for real
- fact-check running → voice script and avatar script written and tested on one take
- avatar clips rendering → timeline locked from the voice alone, parts split, writers briefed
- writers running → thumbnails and B-roll reviewed, real screenshots captured for the receipts
- reviewers running → remaining avatar clips checked against their reads

When a worker finishes, read its output files, not only its reply. Replies say "done"; files show what
was done.

## Keeping count

The closing board of the first video said "1 prompt, 32 agents, 3 Claude plans, 13 lines rewritten". Those
are easy numbers to get wrong, so:

- Add a row to `W/run-facts.md` for every worker as you start it (job, plan, result).
- The agent count includes failed starts and reviewers that have not run yet. Set it last, after you
  decide whether a final reviewer runs, and regenerate the part that shows it.
- "One prompt" stays true only while he sends one. A second message about the video (his opener, a
  change) is a second prompt: keep the claim exact ("everything after this: one prompt").

## The run log

`P/logs/run-log.md`, one row per event, local time from the machine's clock:

```
| 5:07 PM | First voice batch: 35 of 38 jobs failed with `"error_type":"rate_limit_reached"` (`"concurrent_jobs_limit":3`); the thumbnail worker was using the same queue. Wait-and-retry added. |
```

Copy error text from the tool, never from memory. Write the row when the thing happens. This log is what
lets you resume after your context is summarized, and the video's honest section quotes it.

## After a context reset

Read, in this order: `P/logs/run-log.md`, `P/MEMORY.md` if it exists, `W/run-facts.md`, `W/plan.md`. Then
`python3 <skill>/scripts/build_takes.py status` (inside `P`), `screenplay check <W>`, and list `W/review/`. That tells you
which gate you are at without re-deriving anything.
