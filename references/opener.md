# His own clip in front

He films a short candid clip (on a phone or a pocket camera, wherever he is) and it opens the video. It
is the one part that is really him, and it is what makes the avatar honest: the viewer meets the real
one first, then is told the clone is next.

Build it as **its own screenplay work dir** and join the two renders. Never add it to the front of the
main timeline: every word id in the main edit would shift, and with them every graphic and every clip a
writer cut to word times. A separate render also leaves the checked main picture untouched.

`WI` below is the opener's work dir: `~/Borumi Projects/<Name> intro screenplay`, next to the main one.

## 1. Take it in

Save his clip in `P/footage/` under a dated name first (he usually sends a Drive link or drops a file);
the original is never edited.

```bash
mkdir -p <WI>/src <WI>/media
ffprobe <clip>                                   # DJI and phone clips are often 23.976 fps, 4K, HEVC, sometimes rotated
ffmpeg -i <clip> -vf "fps=30,scale=1920:1080:flags=lanczos" -c:v libx264 -crf 14 -an <WI>/src/camera.mp4
ffmpeg -i <clip> -vn -ac 1 -ar 48000 <WI>/src/raw.wav
```

- Match the main video's frame rate and size exactly, or the join cannot copy the picture.
- Run the sound through Auphonic before anything else (the `youtube-publish` skill's
  `scripts/auphonic_master.sh` shows the calls and the preset). Outdoor sound needs it, and word timing
  is done on the cleaned file.
- Watch the whole clip and write down what he says, including anything that differs from what really
  happened (see the last section).

## 2. Words

```bash
screenplay init <WI> --camera <WI>/src/camera.mp4 --mic <WI>/src/intro-auphonic.wav
screenplay transcribe <WI> --whole               # one pass is fine for a clip under a minute; read the words
uv run --with torch --with torchaudio --with soundfile python3 <skill>/scripts/align_words.py <WI>
screenplay cut <WI>                              # writes cuts.yaml: edit it as below
screenplay aroll <WI>
screenplay brief <WI>
```

The transcriber's word times are fine on a clean cloned voice. On his outdoor clip three passes
disagreed by up to 1.3 seconds, and graphics landed on the wrong words. `align_words.py` keeps the words
and replaces their times with a forced alignment. Then check five or six anchors by cutting a 2-second
slice around each and transcribing only the slice.

In `<WI>/cuts.yaml`, before `aroll`, keep his take whole: `maxGap: 5`, `midGap: 5`, and move anything
under `cuts:` into `keep:`. It is a candid moment, and trimming it makes it sound edited. Add
`holds: [{after: s<last>, keep: 0.6}]` so the clip plays out to his last frame.

## 3. The look

```yaml
title: "Intro"
look: reference
theme: velour
camera: { focus: [0.5, 0.35], zoom: 1.0 }
```

`look: reference` gives three framings that work on real footage:

| Scene | What the viewer sees | Use for |
|---|---|---|
| `kind: talking` | his footage, full frame | the first second, and whenever he is the point |
| `kind: app` with `screen:` and `webcam: pip` | a full-frame cutaway, him in the corner | the real page he names, a tease of the video |
| `kind: stage` with `layout: hero-left` or `center` and `webcam: pip` | him large on the left with a card, or a diagram with him in the corner | a checklist, a story, the globe |

On a `talking` scene the engine centres any overlay, which covers his face. Use only `lower` (a name
strap) there, and move everything else to an `app` or `stage` scene.

## 4. What goes in it

The first run's 50 seconds, as a pattern:

1. **One second of nothing.** The place he is in is the hook. No graphic on "Hey, guys."
2. **The thing he names, real.** "Anthropic just dropped..." cuts to the real announcement page, zoomed
   on its title, him in the corner.
3. **A name strap** on the first long stretch of him talking: his name, where he is.
4. **The idea in one picture**: phone, arrow, the model.
5. **Teases**: two or three short flashes of the finished video while he says what it will do.
   `make_teases.py` frames each one as a card tagged "LATER IN THIS VIDEO", so nobody thinks
   the video has started. Only tease moments that are in the final cut, and check again if the cut
   changes.
6. **What he asked for, as a checklist** that ticks as he says each item.
7. **The globe**, if distance is part of the story: `globe.py` draws the route from where he is
   to where the work happened. It is a diagram, so both places must be true, and no clock times unless
   the footage was shot at that time.
8. **The hand-off**: the last card says, in large type, that his AI clone is next. This is the
   disclosure the viewer will remember. The avatar then starts on the topic.

Both scripts need `<WI>/src/canvas-bg.png`, a still of the engine's empty canvas, so their frames match
the rest. Before you write the real scenes, give `edit.yaml` one empty scene and take a still of it:

```yaml
scenes:
  - { kind: stage, at: w0, layout: center, webcam: hidden, elements: [] }
```

```bash
screenplay still <WI> --at o:1 -o <WI>/src/canvas-bg.png
```

Give the globe no fade of its own. The scene's transition already fades it in, and two fades leave a
dark half second.

## 5. Join

```bash
screenplay render <WI> -o <WI>/out/intro-v1.mp4
python3 <skill>/scripts/join_opener.py --intro <WI>/out/intro-v1.mp4 --main "<W>/out/<Title> v1.mp4" \
    --out "<P>/Exports/<date> <Title> (with intro).mp4" \
    --intro-work <WI> --whoosh s1,s4,s5 --pop w38,w94 \
    --main-work <W> --main-srt "<W>/out/<Title> v1.srt" --handoff "The Clone Takes Over"
```

It copies both pictures without re-encoding, rebuilds the sound once at one loudness, mixes his sound
effects in, and writes the joined captions and chapter list. Sound effects go on hard cuts (whoosh) and
on things that appear (pop), by scene id, word id or second.

If the main video was rendered from a later anchor (he cut the avatar's first take), pass
`--skip-frames N` so chapters and captions shift by the frames that are no longer there.

Then check, because a join is where sync is lost:

- Frame count of the result = intro frames + main frames.
- Three frames from each half, compared with the two renders: identical.
- The sound against the picture at the join and at the end: offset 0. (The limiter hands sound back
  239 samples late; the script trims it. Confirm with a cross-correlation of the result against the
  two sources.)
- Sound effects are audible. Measure a whoosh's peak against his voice. The first mix was 16 dB under
  the voice, which is the same as not being there.
- `python3 <skill>/scripts/check_takes.py <result> --offset <intro seconds>`, inside `P` (add
  `--skip-takes N` if takes were cut).

## 6. When what he says is not what happened

He is talking off the cuff, hours or days after the real events. In the first run he re-told the prompt
on camera in a shorter form, and said the video would be published to his channel by the run itself.

- Do not put his on-camera version on screen as the record. The checklist of his spoken asks was titled
  "The ask", and the real prompt, shown later in the avatar part, stayed labelled "The prompt as it
  arrived, word for word".
- Do not correct him on screen either. Label neutrally and keep the true record where it already is.
- Tell him, in the hand-over, exactly which sentence differs and how. He decides whether it matters.

## 7. After the join

Update the hand-over, the chapter list and the description (which part is him, which is the avatar). If
he then asks for Auphonic and the upload, that is the `youtube-publish` skill, on the joined file.
Master the joined file once; do not master the halves separately and join after.
