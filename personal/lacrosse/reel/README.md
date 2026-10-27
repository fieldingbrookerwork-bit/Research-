# Highlight reel toolkit

Two scripts for turning game film into a recruiting reel quickly. Python 3
standard library only (no pip installs); needs `ffmpeg` and `ffprobe` 6.x.

| Script | Does |
|---|---|
| `scan.py` | Contact sheets of a whole game (a frame every 2 s, time burned in) to find plays by eye |
| `make_reel.py` | Builds the reel from a JSON spec: title card, clips with a spotlight freeze, end card |

## 1. Scan a game

```
python3 scan.py film/game1.mp4 sheets/game1
```

This writes `sheet_0-00-00.jpg`, `sheet_0-00-32.jpg`, and so on. Each sheet is 16 frames
covering 32 seconds, and each tile shows its source time (H:MM:SS). Flip through the
sheets, and write down the time of every play worth a look. Options:
`--every 1` for denser frames, `--start 25:00 --end 40:00` for one stretch of the game.

A 90-minute 1080p game takes about 3 minutes on a 4-core machine, and 4K about 8 minutes.
Each frame is fetched with its own seek, so the whole game is not decoded. When a file
has keyframes far apart (more than 5 s), the script switches to one linear pass because
that is faster for such files. It picks the method by itself.

## 2. Write the spec

Copy this into `reel.json` next to the film (relative paths are relative to the spec):

```json
{"output": "reel.mp4",
 "title": {"lines": ["FIRST LAST", "Class of 2028 | Close Defense", "6'5\" 226 lb",
                     "School | Club", "GPA x.xx", "email | phone"],
           "photo": "headshot.jpg", "seconds": 5},
 "end":   {"lines": ["FIRST LAST", "email | phone", "Full game film: <link>"], "seconds": 4},
 "clips": [
   {"src": "film/game1.mp4", "start": "12:31.5", "end": "12:39",
    "spot": {"x": 812, "y": 455}, "note": "Takeaway"},
   {"src": "film/game2.mp4", "start": "1:02:10", "end": "1:02:18", "spot": {"x": 1400, "y": 610}}
 ]}
```

- **Times:** `"12:31.5"` (M:SS), `"1:02:10"` (H:MM:SS) or plain seconds `751.5`. Clips
  play in the order listed.
- **Title and end cards:** the first line is large and bold, the second is highlighted,
  and the rest are smaller. Quotes and apostrophes (`6'5"`) are fine. In JSON, write `"`
  inside a string as `\"`. A long name wraps onto two lines, and over-long lines shrink to fit.
  `photo` is optional. It sits in the left third and needs to be JPG or PNG (iPhone
  HEIC: export it as JPG first).
- **spot:** where he is on the clip's first frame, in pixels of the source video. To
  get the numbers, run

  ```
  python3 make_reel.py reel.json --grids
  ```

  This writes the exact first frame of each clip, with a labelled 100-pixel grid, to
  `reel_work/grids/`. Read x and y off the grid. An existing spot is drawn as a cyan
  cross, so you can check it. A spotlight freezes that frame for 1.5 s, darkens
  everything outside a circle and draws a yellow ring around him. The clip then plays
  normally. Add `"r": 100` to the spot for a bigger ring (the default is 70 pixels).
- **note** (optional): a small caption at lower left during the freeze and the first 2 s.

## 3. Build

```
python3 make_reel.py reel.json
```

The script prints each segment and finishes with the reel's duration and file size.
Every part is 1920x1080, 30 fps, H.264 with AAC audio, and silent audio is added where
the film has none. Cuts start on the exact frame asked for. Built segments are cached in
`reel_work/`, so after reordering clips or editing one, only the changed parts are
re-encoded (`--fresh` rebuilds everything). Building from scratch takes about 0.7 s
per second of reel from 1080p film and about 2 s per second from 4K, so a 2.5-minute
reel takes roughly 2 to 5 minutes. Problems such as a missing file, end before start,
a time past the end of the video, or a spot outside the frame are all listed at once
before anything is encoded.

Watch the result all the way through before sending it.

## Recruiting reel rules

- **2 to 3 minutes.** Put the best 5 clips first, because many coaches stop early.
- **Spotlight every clip** so the coach knows who to watch from the first frame.
- **Start each clip 2 to 3 s before the play and end right after it.**
- **No music required.** Game audio, or silence, is fine.
- **Title card:** name, class, position, size, school, club, GPA, and contact (email and phone).
- **Send a full game link alongside the reel.** Coaches evaluating defenders want to
  see positioning off the ball, which a highlight reel cannot show. The end card
  carries that link too.

## Notes and limits

- Rotated phone video, portrait or 4:3 film, non-square pixels, interlaced camcorder
  film, variable frame rate and 25/29.97/60 fps sources are all handled: the picture
  is fitted inside 16:9 with black bars, and spot coordinates follow the same mapping.
- iPhone HDR (HLG) film is converted to normal video automatically, but this has only
  been checked on test footage. If the colours look off, export the film as
  "Most Compatible"/SDR, or turn off HDR Video before filming.
- Fonts: Inter if installed, otherwise DejaVu (Linux) or Arial (Mac/Windows).
  Set `"fonts": {"bold": "...ttf", "regular": "...ttf"}` in the spec to change them.
