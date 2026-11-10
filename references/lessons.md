# What went wrong, and how to see it next time

Every entry happened on the first run (Nov 9 and 10, 2026). Each is written as what you would notice,
why it happens, and what to do. Read the first section before the final checks even if nothing looks
wrong: those four faults passed every check made on single clips and single parts.

## Only visible on the assembled video

**The room jumps between takes.**
The avatar model takes the photo as a reference, not as its first frame (a start image cannot be
combined with a voice reference). About one clip in six redraws the room: a shelf framed wider, an
object moved, the wall a cooler colour. The face and lip sync are fine, so a per-clip check passes.
→ `room_check.py` on all takes, look at the sheet, `rerender_room.py` for the odd ones. Three of seven
needed a second or third try.

**A word loses its ending ("starts at 50 cents" became "starts at 50").**
The voice take was complete. The engine trims pauses using each word's end time, and the transcriber
puts the last word of a sentence too early, so the cut lands inside the word. A transcript of the
source shows nothing wrong.
→ `scan_cuts.py` after every `aroll`. Four hits on the first run. Fix with a later word end in
`words.json`, or a `holds:` line in `cuts.yaml` when an "s" or a breath runs on into the pause.

**The sound switches off between takes.**
Generated reads have exact digital silence at the head, the tail and between phrases. One take alone
sounds clean; fifty cut together sound like a track being muted and unmuted.
→ `fill_tone.py` before `assemble`. It lays the voice's own quiet floor into the silent stretches.

**The transcript of the finished file skips two minutes.**
Whisper on a whole 10-minute file loops and drops stretches. It looks like the video is missing lines.
→ Never check a finished file in one pass. `check_takes.py` transcribes take by take.

## Voice

**35 of 38 voice jobs fail at once with `rate_limit_reached`.**
The account runs three jobs at a time across everything using it, and a thumbnail worker was in the
same queue. → `build_takes.py` waits and retries. Tell media workers to run one job at a time.

**The same sentence comes back at 173 words a minute, then 244.**
The voice model's pace is not stable. → The script re-reads a take that falls outside the presenter's
range and keeps the closest.

**A name or number is said wrong** ("Fable" as "Babel", "agent teams" as "Asian teams", "a week" as "a
weekend", "Fermat's Last Theorem" garbled). A near-miss like "Asian teams" scores 0.93 to 0.98 on the
whole line, so similarity alone passes it. → `must-hear.json` for every name and number (`check` fails
a read that misses one), `revoice`, then reword slightly and re-check the new wording against the source.

## Avatar

**Every job longer than 15 seconds fails.** → Takes of 45 words or fewer fit one clip. Longer reads are
split at a pause into two clips (`build_takes.py` does this), and the join is listed for the final
reviewer.

**A pricier avatar model cut to a second camera angle and rearranged the room mid-clip.** → Pilot the
models on the same photo and line, and watch every second, before choosing.

**The mouth opens again after the last word.** The clip keeps moving past the end of the read, about
0.7 s later. → `freeze_at` on the last take (hold a closed-mouth frame from about 0.5 s after the word),
`tail=1.6`, and a matching `holds:` entry.

## Workers and plans

**Two research workers die in the first minutes:** `API Error: 400 ... does not support this model`.
One of four plans ran an older client that could not run the worker model. → One-line test per plan
before the first wave. Restart failed workers elsewhere with the same brief plus what is already
written.

**A worker says "done" and the file is thin.** → Read the files, not the replies. Give every brief a
done-line the worker can test.

**A writer builds a believable screen of something nobody ran.** → `run-facts.md` says what was not
run. The reviewer brief asks "is there a source for this screen?" The fix is a real capture, which
only the boss can go and get.

**The agent count on screen is wrong by one.** The final reviewer had not run when the closing board
was written. → `receipts.json` is filled last.

## Edit

**Two cards share the panel and both shrink.** The first had no `until`. → Every element ends before
the next begins. `screenplay check` warns: "starts while ... is still up".

**A key visual is hidden for two seconds.** A chapter card covers the screen for 2 s after a chapter
anchor. → Nothing important on those words.

**A label says more than the picture shows.** A card labelled "The full prompt" showed the first two
lines. → It became "The prompt as it arrived, word for word". Read every label as a claim.

**Seven parts, 0 errors, 104 review notes.** `check` passing means the YAML is valid, not that the
video is good. → Sheets, stills, and reviewers who did not write it.

## Opener and join

**Graphics land a second early on his outdoor clip.** Three transcription passes disagreed by up to
1.3 s. → `align_words.py`, then confirm anchors by transcribing short slices.

**An overlay covers his face.** On `talking` scenes the engine centres overlays. → Only `lower` there;
cutaways and cards go on `app` (with `webcam: pip`) and `stage` scenes.

**A dark half second before the globe.** The clip faded itself in and the scene transition faded it
again. → No fade inside clips made for the edit.

**A render that never ends and a 2 GB file.** An `ffmpeg -loop 1` image input has no end. → Always `-t`.

**Sound effects you cannot hear.** Gains chosen by guess put them 16 dB under his voice. → Measure the
effect's peak against the voice in the mix. `join_opener.py` has the measured gains.

**Sound 5 ms late after the join.** `alimiter` returns audio 239 samples late at 48 kHz. → Trimmed in
`join_opener.py`; confirm offset 0 on the result.

**A tease shows a moment that is no longer in the video.** He cut the avatar's first take after the
teases were made. → After any change to the main cut, check every tease.

**An older master is still in the export folder.** A first Auphonic run on the earlier cut finished
before it could be stopped. → Name the stale file in the hand-over; do not delete it without asking.

## His corrections

Three so far (the avatar's spoken "I'm an AI clone" opening, a link he did not ask for, repeated
points). They are rules now: `SKILL.md`, "Rules that came from his corrections". Add to that list when he
corrects something new.

## Shell traps on his Mac (zsh)

- `set -- $r` does not split on spaces. Use `a=${r%%:*}; b=${r##*:}`.
- `echo ====` fails: a word starting with `=` is looked up as a command. Quote it.
- An unquoted `--include=*.ts` fails when nothing matches the glob. Quote patterns.
- There is no `shuf`: `sort -R | head -1`.
