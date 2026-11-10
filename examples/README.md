# Examples from the first run

Four real files from "Claude Fable 5.2 Made This Video From One Prompt" (Nov 9 and 10, 2026). They show
the level of detail to aim for. Do not copy their facts into another video: every number in them was
true for that release on that day.

| File | What it is | Where its twin lives in a project |
|---|---|---|
| `takes.src.txt` | the script as 54 takes, after the fact-check | `P/script/takes.src.txt` |
| `edit-plan.md` | the plan every part writer read: the look, the assets, what each take shows | `W/plan.md` |
| `part-D.yaml` | one finished part (85 seconds, "The Orchestrator"): a story acted out with B-roll, proof cards, big numbers | `W/parts/D.yaml` |
| `run-log.md` | the boss's log, from the prompt to the upload | `P/logs/run-log.md` |

Things in them that later changed:

- Take `i01` (the avatar saying "that was the real one, I'm an AI clone of him") was cut by Samin after
  he filmed his own opener. The video's avatar part starts at `i02`. See "Rules that came from his
  corrections" in `SKILL.md`.
- The header of `takes.src.txt` says the avatar clip limit is 30 s. It turned out to be 15 s with a
  voice reference; takes above that are rendered as two clips.
- `part-D.yaml` points at media that is not in this repo (`media/D/...`, `proof/...`). It is here to be
  read, not rendered.
