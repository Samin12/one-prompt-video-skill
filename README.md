# one-prompt-video skill

A Claude Code skill that turns one prompt into a finished, fact-checked YouTube explainer presented by
an AI avatar of the creator in a cloned voice. Claude Fable runs as the boss and hands the work to
worker agents.

It is the method behind "Claude Fable 5.2 Made This Video From One Prompt" (Nov 2026): a 10-minute
video, 32 agents, 4 hours 19 minutes from prompt to file.

## What a run does

1. **Research** with five workers at once. Every claim gets a screenshot of the real page.
2. **Runs the how-to for real**, so nothing is shown that nobody did.
3. **Script**, written as short takes in the creator's voice.
4. **Independent fact-check** before any voice is made. The first run's found 13 faulty lines.
5. **Voice and avatar** on Higgsfield: one cloned-voice read and one avatar clip per take.
6. **Motion graphics** on the screenplay engine: one writer per part, all at once, then reviewers who
   did not write it, then fixers.
7. **Checks that only work on the whole video**: the room drifting between avatar clips, cuts that eat
   the end of a word, dead silence between takes.
8. **A final-cut review** by one more agent, the final render, thumbnails and a hand-over.

Then, when asked: the creator's own candid clip in front, Auphonic, and an unlisted upload.

Three rules run through all of it: everything on screen is true and sourced, the viewer is told the
presenter is an AI avatar, and nothing goes public without the creator.

## What is in here

| Path | What |
|---|---|
| [`SKILL.md`](SKILL.md) | the run, phase by phase, with the gate each phase must pass |
| [`references/`](references) | orchestration, the truth standard, the script, voice and avatar, the edit, the opener, and every fault from the first run |
| [`briefs/`](briefs) | the shared brief and a template for each of the 12 kinds of worker |
| [`scripts/`](scripts) | the pipeline: takes, voice, avatar clips, room check, cut scan, parts, timing lock, opener join, final check |
| [`examples/`](examples) | the first run's script, edit plan, one finished part and run log |
| [`config.example.json`](config.example.json) | the presenter's settings (voice clone id, photo, avatar prompt) |

## Install

```bash
git clone https://github.com/Samin12/one-prompt-video-skill ~/one-prompt-video-skill
ln -s ~/one-prompt-video-skill ~/.claude/skills/one-prompt-video
mkdir -p ~/.config/one-prompt-video
cp ~/one-prompt-video-skill/config.example.json ~/.config/one-prompt-video/defaults.json   # then fill it in
```

Then ask Claude Code: "make a full video about X from this prompt".

## Needs

- Claude Code with a model strong enough to run a team (built on Claude Fable 5.2), and a way to start
  worker agents: subagents, or T3 Code delegates spread over several Claude plans.
- The Higgsfield CLI, logged in, with about 250 credits per minute of video, and a saved voice clone.
- The screenplay engine (`screenplay` CLI) and its `screenplay-edit` skill.
- `ffmpeg`, `whisper-cli` with the large-v3-turbo model, `uv`, Python 3.11+ with Pillow, `node`,
  `yt-dlp`, and `pdftoppm` (poppler) for facts inside PDFs.
- A proof-capture script (the skill uses editroom's `capture_proof.mjs`).
- For the opener's sound effects: Borumi's built-in whoosh and pop.
- For mastering and upload: the `youtube-publish` skill.

## Honest limits

- It was written from one full run and its scripts were tested against that run's files. A second full
  run from this skill has not been done yet.
- The room check was tuned on one studio photo. Look at its sheet before trusting it.
- No agent can hear. Every sound check is a measurement or a transcript; a person should listen once
  before publishing.
- The avatar and voice models change fast. Pilot them again when a new one ships.
