# Run log: the Fable 5.2 video, Nov 9, 2026

Kept by the orchestrator (Claude Fable 5.2 in T3 Code). Times are US Eastern, from the
machine's clock. Error lines are copied from the tools' own output.

| Time | Event |
|---|---|
| 4:33 PM | Samin's prompt arrives (one message, 201 words). Project folder created. |
| 4:36 PM | Five research workers briefed. Two go to Claude Hub, the others to Claude 300, Claude 100 and Claude 200. |
| 4:37 PM | Samin's second message: "Update all my t3 code and Claude and studf". Not about the video. Tools updated; the T3 Code restart is held so the workers are not stopped. |
| 4:46 PM | Voice cloned from 2 minutes of raw mic audio. Speaker similarity 0.91 against real takes (the Oct 28 sample scored 0.79). |
| 4:50 PM | Avatar pilot: Wan 3.0 (26.25 credits) and Higgsfield Intone (126 credits), same photo, same line. |
| 4:52 PM | Both Claude Hub workers reported failed: `API Error: 400 Claude Code 2.1.280 does not support this model; version 2.1.290 or newer is required. Run 'claude update', or update the Claude desktop app, then try again.` Restarted on Claude 300 and Claude 100. |
| 4:55 PM | Pilot result: Intone cut to a second camera angle and rearranged the room mid-clip. Wan 3.0 chosen. |
| 5:00 PM | Live test of the Claude Code setup: Fable 5.2 main, Haiku 5.5 researcher, Sonnet 5.5 builder and checker. 93.3 s, $1.8176 at API list prices. Log: `proof/live-test-2/run.jsonl`. |
| 5:07 PM | First voice batch: 35 of 38 jobs failed with `"error_type":"rate_limit_reached"` (`"concurrent_jobs_limit":3`); the thumbnail worker was using the same Higgsfield queue. Output kept in `logs/voice-run-1-rate-limited.log`. Wait-and-retry added. |
| 5:14 PM | Fact-check back: 30 ok, 11 soften, 2 wrong, 11 no-claim. 13 lines rewritten before recording. |
| 5:20 PM | Voice restarted on the corrected script. |
| 5:40 PM | All 54 lines recorded. 11 re-read after the transcript check (for example "Fermat's Last Theorem" garbled, "Fable" heard as "Babel"). |
| 6:00 PM | Higgsfield failed every Wan 3.0 job longer than 15 s (three jobs, 17 to 18 s). The 8 long lines are rendered as two clips each and joined at a pause. |
| 6:05 PM | Timeline locked at 9:56. Seven part writers briefed across Claude 300, Claude 100 and Claude 200. |
| 6:38 PM | All seven parts written and merged: 115 scenes, 0 errors. Four reviewers briefed. |
| 6:48 PM | Real T3 Code window captured: "Lineage · 3 running", "Previous agents · 3 failed · 22". |
| 6:57 PM | Four reviews back: 104 notes (25 must, 45 should, 34 nice). No wrong number found. Seven fixers briefed, one per part. |
| 7:16 PM | All seven parts fixed and merged: 109 scenes, 0 errors. |
| 7:22 PM | Last avatar clip in: 54 of 54. The final line was rendered again one second longer so the ending holds on moving footage. |
| 7:27 PM | Talking-head track built from the 54 clips: 9:57. Word timing unchanged from the locked timeline. |
| 7:36 PM | End check: the avatar opens its mouth again 0.7 s after "Have fun." The hold was cut to 0.6 s, so the video ends on a closed-mouth frame. 9:56.7. |
| 7:46 PM | Preview rendered (720p, 365 s). One final-cut reviewer briefed on Claude 300: agent number 32. |
| 8:00 PM | Final-cut review back: ship after 3 musts. No wrong number on screen, the face held in all 54 takes. Faults: two words cut off ("50 cents", "work"), the room differs in a few takes, dead silence between takes. |
| 8:02 PM | Cause of the cut-off words: the voice takes were fine; the pause trimming used word end times that were too early. Every cut scanned for removed sound: 4 found, 4 fixed. |
| 8:24 PM | Seven avatar clips rendered again (Wan 3.0 treats the photo as a reference, so about one clip in six frames the shelf differently). Each new clip checked against the usual room; three needed a second or third try. |
| 8:40 PM | Track rebuilt: gaps filled with the voice's own quiet floor, the last frame holds for 1.8 s. 9:59.0, 0 errors. Final render started. |
| 10:06 PM | Samin's second message about the video: his Korea intro (50 s, 4K, filmed 11:43 AM Korea time). Asks for Auphonic, teases, a globe, and a hand-off to the avatar. |
| 10:07 PM | Intro audio mastered in Auphonic ("Dave Broadcast - Keep SFX"). |
| 10:13 PM | Three word-timing passes disagreed by up to 1.3 s. A forced aligner settled it; 20 short slices transcribed to confirm. |
| 10:20 PM | Globe built (Korea to home, great-circle route, "14 hours behind"). Five preview cards cut from the finished video. |
| 10:30 PM | Intro rendered: 49.9 s, his take whole. Prompt card in the avatar part relabelled "The prompt as it arrived, word for word", because the prompt he says on camera is a later, shorter version. |
| 10:44 PM | Joined: picture copied from both renders, sound rebuilt at -14 LUFS with whooshes and pops. First mix had the effects 16 dB under his voice and 5 ms late; both fixed. 10:48.9, frame-exact, no upload. No new agents: still 32. |
| 10:52 PM | Samin: run the full video through Auphonic and upload through Neo; and start the avatar from "Anthropic just released". The avatar's opener ("that was the real one, I'm an AI clone of him") is cut: the avatar video is rendered from its second line. The intro's last card now reads "Up next: his AI clone" in large type, and the clone preview was swapped for one still in the video. |
| 11:06 PM | Full video (10:40) mastered in Auphonic: -15.4 LUFS, same length, no time shift, all 53 avatar lines and the intro still transcribe correctly. |
| 11:20 PM | Uploaded to YouTube as UNLISTED through BrowserOS neo. Title, description, thumbnail A, "AI was used: yes", monetization on, end screen (agent teams video + subscribe from 10:31), links comment pinned. Not public. |
