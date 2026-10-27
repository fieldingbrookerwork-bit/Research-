#!/usr/bin/env python3
"""Build a recruiting highlight reel from a JSON spec with ffmpeg.

    python3 make_reel.py SPEC.json            build the reel
    python3 make_reel.py SPEC.json --fresh    rebuild every segment (ignore cache)
    python3 make_reel.py SPEC.json --grids    write each clip's first frame with a
                                              pixel grid, to read spot x/y off

Spec (relative paths are resolved against the spec file's folder):

    {"output": "reel.mp4",
     "title": {"lines": ["FIRST LAST", "Class of 2028 | Close Defense", ...],
               "photo": "headshot.jpg", "seconds": 5},
     "end":   {"lines": ["FIRST LAST", "email | phone", "Full game film: <link>"],
               "seconds": 4},
     "clips": [{"src": "game1.mp4", "start": "12:31.5", "end": "12:39",
                "spot": {"x": 812, "y": 455}, "note": "Takeaway"}]}

Optional: "spot": {"x", "y", "r"} where r is the ring radius in output pixels
(default 70); top-level "fonts": {"bold": path, "regular": path}.

Every segment is rendered at 1920x1080, 30 fps CFR, yuv420p, x264 CRF 20
(preset medium) with 48 kHz stereo audio, then the segments are joined with a
stream copy and AAC 128k audio into an MP4 with +faststart. Built segments are
cached in reel_work/ next to the output; unchanged ones are reused.

Python 3 standard library only; needs ffmpeg and ffprobe (6.x) on PATH.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

W, H, FPS = 1920, 1080, 30
SR = 48000
SPF = SR // FPS              # audio samples per video frame (1600)
FREEZE_FRAMES = 45           # spotlight freeze: 1.5 s
NOTE_SECONDS = 2.0           # note shows for the freeze plus this much playback
RING_RADIUS = 70             # output pixels (1080p frame)
RING_HALF_WIDTH = 5          # ring is 10 px wide
DARKEN = 0.55                # how much the area outside the ring is darkened
PREROLL = 2.0                # seek this far before a cut, then trim exactly
BG = "0x0b0f14"
ACCENT = "0xFFDD00"
ACCENT_RGB = (255, 221, 0)
SUBTEXT = "0xC9D1D9"
PHOTO_BOX = (540, 860)       # max photo size inside the left third (640 px)
WORK_DIR = "reel_work"       # segment cache + grids, next to the output

FONT_DIRS = {
    "bold": [
        "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ],
    "regular": [
        "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ],
}

VIDEO_ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
             "-profile:v", "high", "-g", "60", "-x264-params", "stitchable=1",
             "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
             "-color_range", "tv", "-fps_mode", "cfr", "-r", str(FPS)]
AUDIO_PCM = ["-c:a", "pcm_s16le", "-ar", str(SR), "-ac", "2"]

TOP_KEYS = {"output", "title", "end", "clips", "fonts"}
CARD_KEYS = {"lines", "photo", "seconds"}
CLIP_KEYS = {"src", "start", "end", "spot", "note"}
SPOT_KEYS = {"x", "y", "r"}


class ReelError(Exception):
    pass


# ------------------------------------------------------------------ helpers

def parse_time(value, what):
    """751.5, '751.5', '12:31.5' or '1:02:31.5' -> seconds."""
    if isinstance(value, bool):
        raise ReelError(f"{what}: bad time {value!r}")
    if isinstance(value, (int, float)):
        seconds = float(value)
    else:
        try:
            parts = [float(p) for p in str(value).strip().split(":")]
        except ValueError:
            raise ReelError(f"{what}: bad time {value!r} (use seconds, M:SS.s or H:MM:SS.s)")
        if not 1 <= len(parts) <= 3:
            raise ReelError(f"{what}: bad time {value!r} (use seconds, M:SS.s or H:MM:SS.s)")
        seconds = 0.0
        for p in parts:
            seconds = seconds * 60 + p
    if seconds < 0:
        raise ReelError(f"{what}: time {value!r} is negative")
    return seconds


def fmt_time(t):
    """Seconds -> M:SS.ss (or H:MM:SS.ss)."""
    cs = int(round(t * 100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s = f"{rem // 100:02d}.{rem % 100:02d}"
    return f"{h}:{m:02d}:{s}" if h else f"{m}:{s}"


def fesc(value):
    """Escape a string for use as a filter option value inside a filtergraph."""
    v = str(value)
    for ch in "\\':":          # level 1: option value
        v = v.replace(ch, "\\" + ch)
    v = v.replace("\\", "\\\\").replace("'", "\\'")   # level 2: filtergraph
    for ch in "[],;":
        v = v.replace(ch, "\\" + ch)
    return v


def run(cmd, what):
    proc = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, errors="replace")
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-15:])
        raise ReelError(f"{what}: ffmpeg failed:\n{tail}")
    return proc


def even(v):
    return max(2, int(round(v / 2.0)) * 2)


def write_text(path, text):
    # drawtext reads this verbatim (expansion=none): quotes, %, \ are all safe.
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(str(text).replace("\r", "").strip("\n"))
    return path


# ------------------------------------------------------------------ probing

_probe_cache = {}


def probe(path):
    if path in _probe_cache:
        return _probe_cache[path]
    proc = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams",
                           "-of", "json", path],
                          stdin=subprocess.DEVNULL, capture_output=True, text=True,
                          errors="replace")
    if proc.returncode != 0:
        raise ReelError(f"cannot read {path}: {proc.stderr.strip()[-300:]}")
    data = json.loads(proc.stdout or "{}")
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"
                  and not s.get("disposition", {}).get("attached_pic")), None)
    if video is None:
        raise ReelError(f"no video stream in {path}")
    audio = next((s for s in streams if s.get("codec_type") == "audio"
                  and int(s.get("channels", 0) or 0) > 0), None)
    rotation = 0
    for sd in video.get("side_data_list", []) or []:
        if "rotation" in sd:
            rotation = int(round(float(sd["rotation"])))
    if not rotation and "rotate" in video.get("tags", {}):
        rotation = int(video["tags"]["rotate"])
    w, h = int(video["width"]), int(video["height"])
    sar = 1.0
    m = re.match(r"^(\d+):(\d+)$", str(video.get("sample_aspect_ratio", "")))
    if m and int(m.group(1)) > 0 and int(m.group(2)) > 0:
        sar = int(m.group(1)) / int(m.group(2))
    if abs(rotation) % 180 == 90:      # ffmpeg auto-rotates: frames arrive swapped
        w, h, sar = h, w, 1.0 / sar
    duration = None
    for src in (video, data.get("format", {})):     # the video's own length first
        try:
            duration = float(src["duration"])
            break
        except (KeyError, TypeError, ValueError):
            pass
    info = {
        "w": w, "h": h, "sar": sar,
        "vindex": int(video["index"]),
        "aindex": int(audio["index"]) if audio else None,
        "duration": duration,
        "interlaced": video.get("field_order") in ("tt", "bb", "tb", "bt"),
        "hdr": video.get("color_transfer") in ("arib-std-b67", "smpte2084"),
    }
    _probe_cache[path] = info
    return info


def geometry(info):
    """Scale-to-fit + centred pad into 1920x1080: (sw, sh, px, py)."""
    aspect = info["w"] * info["sar"] / info["h"]
    if aspect >= W / H:
        sw, sh = W, min(H, even(W / aspect))
    else:
        sw, sh = min(W, even(H * aspect)), H
    return sw, sh, (W - sw) // 4 * 2, (H - sh) // 4 * 2


def map_spot(info, x, y):
    """Source-frame pixel -> output-frame pixel, through the same scale + pad."""
    sw, sh, px, py = geometry(info)
    return (px + (x + 0.5) * sw / info["w"] - 0.5,
            py + (y + 0.5) * sh / info["h"] - 0.5)


# ------------------------------------------------------------------ spec

def resolve(base, p):
    p = os.path.expanduser(str(p))
    return os.path.normpath(p if os.path.isabs(p) else os.path.join(base, p))


def load_plan(spec_path):
    try:
        with open(spec_path, encoding="utf-8") as fh:
            spec = json.load(fh)
    except FileNotFoundError:
        raise ReelError(f"spec not found: {spec_path}")
    except json.JSONDecodeError as exc:
        raise ReelError(f"{spec_path} is not valid JSON: {exc}")
    if not isinstance(spec, dict):
        raise ReelError("the spec must be a JSON object")
    base = os.path.dirname(os.path.abspath(spec_path))
    errors, warnings = [], []

    def unknown(obj, allowed, where):
        if isinstance(obj, dict):
            for k in sorted(set(obj) - allowed):
                warnings.append(f"{where}: unknown key {k!r} ignored "
                                f"(expected one of: {', '.join(sorted(allowed))})")

    unknown(spec, TOP_KEYS, "spec")
    if not spec.get("output"):
        errors.append('"output" is missing')
    output = resolve(base, spec.get("output") or "reel.mp4")

    fonts = {}
    custom = spec.get("fonts") or {}
    if not isinstance(custom, dict):
        errors.append('"fonts" must look like {"bold": "file.ttf", "regular": "file.ttf"}')
        custom = {}
    for kind in ("bold", "regular"):
        if custom.get(kind):
            path = resolve(base, custom[kind])
            if not os.path.isfile(path):
                errors.append(f"fonts.{kind}: file not found: {path}")
            fonts[kind] = path
        else:
            fonts[kind] = next((p for p in FONT_DIRS[kind] if os.path.isfile(p)), None)

    segments = []

    def card(key, default_seconds, fade):
        obj = spec.get(key)
        if obj is None:
            warnings.append(f'no "{key}" card in the spec')
            return
        if not isinstance(obj, dict):
            errors.append(f'"{key}" must be an object with "lines"')
            return
        unknown(obj, CARD_KEYS, key)
        lines = obj.get("lines")
        if (not isinstance(lines, list) or not lines
                or not all(isinstance(s, str) for s in lines) or not any(s.strip() for s in lines)):
            errors.append(f'{key}.lines must be a non-empty list of strings')
            lines = ["?"]
        photo = None
        if obj.get("photo"):
            photo = resolve(base, obj["photo"])
            if not os.path.isfile(photo):
                errors.append(f"{key}.photo: file not found: {photo}")
            else:
                try:
                    probe(photo)
                except ReelError:
                    errors.append(f"{key}.photo: ffmpeg cannot read {photo} "
                                  "(HEIC? export it as JPG or PNG)")
        seconds = obj.get("seconds", default_seconds)
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or seconds <= 0:
            errors.append(f"{key}.seconds must be a positive number")
            seconds = default_seconds
        segments.append({"kind": "card", "name": key, "lines": lines, "photo": photo,
                         "frames": max(1, int(round(seconds * FPS))), "fade": fade})

    card("title", 5, "in")
    clips = spec.get("clips")
    if not isinstance(clips, list) or not clips:
        errors.append('"clips" must be a non-empty list')
        clips = []
    for i, c in enumerate(clips, 1):
        where = f"clip {i}"
        if not isinstance(c, dict):
            errors.append(f"{where}: must be an object")
            continue
        unknown(c, CLIP_KEYS, where)
        if not c.get("src"):
            errors.append(f'{where}: "src" is missing')
            continue
        src = resolve(base, c["src"])
        where = f"clip {i} ({os.path.basename(src)})"
        if not os.path.isfile(src):
            errors.append(f"{where}: source file not found: {src}")
            continue
        try:
            start = parse_time(c.get("start"), f"{where} start")
            end = parse_time(c.get("end"), f"{where} end")
        except ReelError as exc:
            errors.append(str(exc))
            continue
        if end <= start:
            errors.append(f"{where}: end {fmt_time(end)} is not after start {fmt_time(start)}")
            continue
        try:
            info = probe(src)
        except ReelError as exc:
            errors.append(f"{where}: {exc}")
            continue
        dur = info["duration"]
        if dur is not None and start >= dur:
            errors.append(f"{where}: start {fmt_time(start)} is past the end of the video "
                          f"({fmt_time(dur)})")
            continue
        if dur is not None and end > dur + 0.05:
            errors.append(f"{where}: end {fmt_time(end)} is past the end of the video "
                          f"({fmt_time(dur)})")
            continue
        frames = int(round((end - start) * FPS))
        if frames < 1:
            errors.append(f"{where}: shorter than one frame")
            continue
        spot = None
        if c.get("spot") is not None:
            s = c["spot"]
            unknown(s, SPOT_KEYS, f"{where} spot")
            try:
                x, y = float(s["x"]), float(s["y"])
                r = float(s.get("r", RING_RADIUS))
            except (TypeError, KeyError, ValueError):
                errors.append(f'{where}: spot must look like {{"x": 812, "y": 455}}')
                continue
            if not (0 <= x < info["w"] and 0 <= y < info["h"]):
                errors.append(f"{where}: spot ({x:g}, {y:g}) is outside the source frame "
                              f"({info['w']}x{info['h']}; coordinates are source pixels)")
                continue
            if not 10 <= r <= 400:
                errors.append(f"{where}: spot r must be between 10 and 400 output pixels")
                continue
            ox, oy = map_spot(info, x, y)
            spot = {"x": x, "y": y, "r": r, "ox": round(ox, 2), "oy": round(oy, 2)}
        note = c.get("note")
        if note is not None and not isinstance(note, str):
            errors.append(f"{where}: note must be a string")
            continue
        if info["hdr"]:
            warnings.append(f"{where}: HDR source; tone-mapping it to SDR")
        segments.append({"kind": "clip", "name": f"clip {i}", "src": src, "start": start,
                         "end": end, "clip_frames": frames, "spot": spot,
                         "note": note.strip() if note and note.strip() else None,
                         "frames": frames + (FREEZE_FRAMES if spot else 0)})
    card("end", 4, "out")

    for kind in ("bold", "regular"):
        if fonts[kind] is None and not custom.get(kind):
            warnings.append(f"no {kind} font file found; falling back to fontconfig 'Sans'")
    for w in warnings:
        print(f"warning: {w}")
    if errors:
        raise ReelError("problems in the spec:\n  - " + "\n  - ".join(errors))
    return output, segments, fonts


# ------------------------------------------------------------------ filters

def font_opt(path, bold):
    if path:
        return "fontfile=" + fesc(path)
    return "font=" + fesc("Sans:style=Bold" if bold else "Sans")


def measure_widths(items):
    """Rendered pixel width of each (font, bold, size, textfile), via drawtext."""
    chain = ["color=c=black:s=64x64:r=1:d=1"]
    for i, (font, bold, size, tf) in enumerate(items, 1):
        chain.append(f"drawtext={font_opt(font, bold)}:textfile={fesc(tf)}:expansion=none:"
                     f"fontsize={size}:x=0:y='print({i * 1000000}+text_w)'")
    proc = run(["ffmpeg", "-nostdin", "-hide_banner", "-v", "info", "-f", "lavfi",
                "-i", ",".join(chain), "-frames:v", "1", "-f", "null", "-"], "measuring text")
    widths = {}
    for m in re.finditer(r"(?m)^(?:\[[^\]]*\]\s*)?(\d{7,})\.\d+\s*$", proc.stderr):
        v = int(m.group(1))
        widths[v // 1000000] = v % 1000000
    return [widths.get(i, 0) for i in range(1, len(items) + 1)]


def card_graph(seg, fonts, txtdir, key, has_photo):
    n = seg["frames"]
    cx, maxw = (1280, 1120) if has_photo else (960, 1640)
    name_style = (fonts["bold"], True, 100, "white")
    rows = []                                   # [kind, text, style]
    for i, text in enumerate(seg["lines"]):
        if i == 0:
            rows.append(["name", text.strip(), name_style])
        elif i == 1:
            rows.append(["sub", text, (fonts["bold"], True, 54, ACCENT)])
        else:
            rows.append(["detail", text, (fonts["regular"], False, 46, SUBTEXT)])

    def measure():
        items = [(j, write_text(os.path.join(txtdir, f"{key}_{j}.txt"), text), st)
                 for j, (_, text, st) in enumerate(rows) if text.strip()]
        widths = measure_widths([(st[0], st[1], st[2], tf) for _, tf, st in items])
        return {j: (tf, w) for (j, tf, _), w in zip(items, widths)}

    measured = measure()
    # A name too wide at full size goes onto two lines (split at the space
    # nearest the middle) instead of shrinking below the line under it.
    name = rows[0][1]
    if 0 in measured and measured[0][1] > maxw and " " in name:
        k = min((i for i, ch in enumerate(name) if ch == " "), key=lambda i: abs(i - len(name) / 2))
        rows[0:1] = [["name", name[:k].strip(), name_style], ["name", name[k + 1:].strip(), name_style]]
        measured = measure()

    sizes = []
    for j, (kind, text, st) in enumerate(rows):
        tf, w = measured.get(j, (None, 0))
        sizes.append(max(18, int(st[2] * maxw / w * 0.98)) if tf and w > maxw else st[2])
    name_size = min(s for (kind, _, _), s in zip(rows, sizes) if kind == "name")
    sizes = [name_size if kind == "name" else s for (kind, _, _), s in zip(rows, sizes)]

    # Vertical layout (baselines), then centre the block on the frame.
    y, draws, rule_y = 0.0, [], None
    for j, ((kind, text, (font, bold, _, color)), size) in enumerate(zip(rows, sizes)):
        if kind == "name":
            base = y + 0.76 * size
            y = base + 0.30 * size
            if j + 1 < len(rows) and rows[j + 1][0] != "name":   # accent rule under the name
                rule_y = y + 10
                y = rule_y + 6 + 30
        else:
            base = y + 0.86 * size
            y = base + 0.50 * size
        if j in measured:
            draws.append((measured[j][0], font, bold, size, color, base))
    top = (H - (y - 0.15 * sizes[-1])) / 2.0
    vf = []
    if rule_y is not None:
        vf.append(f"drawbox=x={cx - 60}:y={int(round(top + rule_y))}:w=120:h=6:"
                  f"color={ACCENT}:t=fill")
    for tf, font, bold, size, color, base in draws:
        vf.append(f"drawtext={font_opt(font, bold)}:textfile={fesc(tf)}:expansion=none:"
                  f"fontsize={size}:fontcolor={color}:y_align=baseline:"
                  f"x={cx}-text_w/2:y={int(round(top + base))}")
    if seg["fade"] == "in":
        vf.append("fade=t=in:st=0:d=0.5")
    else:
        vf.append(f"fade=t=out:st={max(0.0, n / FPS - 0.75):.3f}:d=0.75")
    vf.append("scale=out_color_matrix=bt709:out_range=tv,format=yuv420p")

    g = [f"color=c={BG}:s={W}x{H}:r={FPS},trim=end_frame={n},format=rgb24[bg]"]
    if has_photo:
        g.append(f"[0:v]scale={PHOTO_BOX[0]}:{PHOTO_BOX[1]}:force_original_aspect_ratio=decrease,"
                 f"format=rgba[ph]")
        g.append(f"[bg][ph]overlay=x=({W // 3}-overlay_w)/2:y=({H}-overlay_h)/2:format=rgb[bg2]")
        src = "bg2"
    else:
        src = "bg"
    g.append(f"[{src}]" + ",".join(vf) + "[v]")
    g.append(f"anullsrc=r={SR}:cl=stereo,atrim=end_sample={n * SPF}[a]")
    return ";".join(g)


def source_chain(info, start):
    """Input args + filter prefix that deliver the source from exactly `start`."""
    preroll = min(start, PREROLL)
    seek = start - preroll
    args = ["-ss", f"{seek:.6f}"] if seek > 0 else []
    vf = []
    if preroll > 0:
        vf.append(f"trim=start={max(0.0, preroll - 0.001):.6f},setpts=PTS-{preroll:.6f}/TB")
    if info["interlaced"]:
        vf.append("bwdif=mode=send_frame:deint=interlaced")
    if info["hdr"]:
        # Phone HDR (HLG/PQ) -> SDR: reference white (203 nit) maps to SDR white,
        # brighter highlights roll off. A round trip SDR->HLG->SDR came back within
        # 1% mean brightness; the common npl=100 + hable recipe came back 20% dark.
        vf.append("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,"
                  "tonemap=tonemap=mobius:param=0.8:desat=0,"
                  "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
    af = []
    if preroll > 0:
        af.append(f"atrim=start={preroll:.6f},asetpts=PTS-{preroll:.6f}/TB")
    return args, vf, af


def spot_mask(spot):
    """RGBA overlay: outside the ring darkened, a yellow ring with a dark outline."""
    cx, cy, r, hw = spot["ox"], spot["oy"], spot["r"], RING_HALF_WIDTH
    common = (f"st(0,hypot(X-{cx:.2f},Y-{cy:.2f}));st(1,abs(ld(0)-{r:.2f}));"
              f"st(2,{DARKEN}*clip(ld(0)-{r:.2f}+0.5,0,1));"
              f"st(3,0.85*clip({hw + 2.5}-ld(1),0,1));"
              f"st(4,clip({hw + 0.5}-ld(1),0,1));"
              f"st(5,ld(3)+(1-ld(3))*ld(2));"
              f"st(6,ld(4)+(1-ld(4))*ld(5))")

    def chan(c):
        return f"'{common};if(gt(ld(6),0.002),ld(4)*{c}/ld(6),0)'"

    r_, g_, b_ = ACCENT_RGB
    return (f"color=c=black@0:s={W}x{H}:r=1:d=1,format=gbrap,"
            f"geq=r={chan(r_)}:g={chan(g_)}:b={chan(b_)}:a='{common};255*ld(6)',"
            f"scale=out_color_matrix=bt709:out_range=tv,format=yuva420p")


def clip_graph(seg, fonts, txtdir, key):
    info = probe(seg["src"])
    n, total = seg["clip_frames"], seg["frames"]
    args, pre_v, pre_a = source_chain(info, seg["start"])
    sw, sh, px, py = geometry(info)
    freeze = FREEZE_FRAMES if seg["spot"] else 0
    # tpad: if the source ends a hair early, hold its last frame so every
    # segment has exactly the planned frame count (keeps the joins CFR).
    v = pre_v + [f"fps={FPS}:start_time=0", "tpad=stop=-1:stop_mode=clone", f"trim=end_frame={n}",
                 f"scale={sw}:{sh}:out_color_matrix=bt709:out_range=tv", "setsar=1",
                 f"pad={W}:{H}:{px}:{py}:color=black", "format=yuv420p"]
    if freeze:
        v.append(f"tpad=start={freeze}:start_mode=clone")
    g = [f"[0:{info['vindex']}]" + ",".join(v) + "[v0]"]
    last = "v0"
    if seg["spot"]:
        g.append(spot_mask(seg["spot"]) + "[mask]")
        g.append(f"[v0][mask]overlay=x=0:y=0:enable='lt(n,{freeze})':format=yuv420[v1]")
        last = "v1"
    if seg["note"]:
        tf = write_text(os.path.join(txtdir, f"{key}_note.txt"), seg["note"])
        g.append(f"[{last}]drawtext={font_opt(fonts['bold'], True)}:textfile={fesc(tf)}:"
                 f"expansion=none:fontsize=40:fontcolor=white:box=1:boxcolor=black@0.62:"
                 f"boxborderw=14:x=56:y=h-th-64:"
                 f"enable='lt(t,{freeze / FPS + NOTE_SECONDS:.3f})'[v2]")
        last = "v2"
    g.append(f"[{last}]null[v]")
    clip_samples, total_samples = n * SPF, total * SPF
    if info["aindex"] is not None:
        a = pre_a + [f"aresample={SR}:async=1:first_pts=0",
                     "aformat=sample_fmts=s16:channel_layouts=stereo",
                     f"atrim=end_sample={clip_samples}", f"apad=whole_len={clip_samples}",
                     "afade=t=in:ss=0:ns=480",
                     f"afade=t=out:start_sample={max(0, clip_samples - 480)}:ns=480"]
        if freeze:
            a.append(f"adelay=delays={freeze * SPF}S:all=1")
        a += [f"apad=whole_len={total_samples}", f"atrim=end_sample={total_samples}"]
        g.append(f"[0:{info['aindex']}]" + ",".join(a) + "[a]")
    else:
        g.append(f"anullsrc=r={SR}:cl=stereo,atrim=end_sample={total_samples}[a]")
    return args + ["-i", seg["src"]], ";".join(g)


# ------------------------------------------------------------------ build

def segment_key(seg, fonts, script_hash):
    h = hashlib.sha1(script_hash)
    public = {k: v for k, v in seg.items() if k not in ("name",)}
    h.update(json.dumps(public, sort_keys=True, default=str).encode())
    for path in [seg.get("src"), seg.get("photo"), fonts["bold"], fonts["regular"]]:
        if path and os.path.isfile(path):
            st = os.stat(path)
            h.update(f"|{os.path.abspath(path)}|{st.st_size}|{st.st_mtime_ns}".encode())
    return h.hexdigest()[:16]


def build_segment(seg, out, fonts, txtdir, key):
    if seg["kind"] == "card":
        inputs = ["-i", seg["photo"]] if seg["photo"] else []
        graph = card_graph(seg, fonts, txtdir, key, bool(seg["photo"]))
    else:
        inputs, graph = clip_graph(seg, fonts, txtdir, key)
    tmp = out + ".part.mov"
    try:
        run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", *inputs,
             "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
             "-frames:v", str(seg["frames"]), *VIDEO_ENC, *AUDIO_PCM, "-f", "mov", tmp],
            seg["name"])
        os.replace(tmp, out)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def describe(seg):
    if seg["kind"] == "card":
        extra = ", photo" if seg["photo"] else ""
        return f"{seg['name']} card ({len(seg['lines'])} lines{extra})"
    bits = [f"{os.path.basename(seg['src'])} {fmt_time(seg['start'])}-{fmt_time(seg['end'])}"]
    if seg["spot"]:
        s = seg["spot"]
        bits.append(f"spot ({s['x']:g},{s['y']:g})->({s['ox']:.0f},{s['oy']:.0f})")
    if seg["note"]:
        bits.append(f"note: {seg['note']}")
    return f"{seg['name']}: " + ", ".join(bits)


def concat(seg_files, output, title):
    listing = output + ".concat.txt"
    with open(listing, "w", encoding="utf-8") as fh:
        for f in seg_files:
            fh.write("file '" + os.path.abspath(f).replace("'", "'\\''") + "'\n")
    tmp = output + ".part.mp4"
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
           "-f", "concat", "-safe", "0", "-i", listing, "-map", "0:v:0", "-map", "0:a:0",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-ar", str(SR), "-ac", "2",
           "-movflags", "+faststart"]
    if title:
        cmd += ["-metadata", f"title={title}"]
    try:
        run(cmd + ["-f", "mp4", tmp], "joining segments")
        os.replace(tmp, output)
    finally:
        for f in (listing, tmp):
            if os.path.exists(f):
                os.remove(f)


def final_stats(path):
    proc = run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0",
                "-show_entries", "stream=nb_read_packets:format=duration,size",
                "-of", "json", path], "checking the output")
    data = json.loads(proc.stdout)
    return (float(data["format"]["duration"]), int(data["format"]["size"]),
            int(data["streams"][0]["nb_read_packets"]))


def build(spec_path, fresh):
    output, segments, fonts = load_plan(spec_path)
    work = os.path.join(os.path.dirname(output), WORK_DIR)
    txtdir = os.path.join(work, "text")
    os.makedirs(txtdir, exist_ok=True)
    with open(os.path.abspath(__file__), "rb") as fh:
        script_hash = hashlib.sha1(fh.read()).digest()

    total = sum(s["frames"] for s in segments)
    print(f"Plan: {len(segments)} segments, {fmt_time(total / FPS)} total")
    files = []
    for i, seg in enumerate(segments, 1):
        key = segment_key(seg, fonts, script_hash)
        out = os.path.join(work, f"seg_{key}.mov")
        label = f"[{i}/{len(segments)}] {describe(seg)} [{fmt_time(seg['frames'] / FPS)}]"
        if os.path.exists(out) and not fresh:
            print(f"{label}  cached")
        else:
            t0 = time.time()
            print(f"{label}  building...", end="", flush=True)
            build_segment(seg, out, fonts, txtdir, key)
            print(f" {time.time() - t0:.1f} s")
        files.append(out)

    title = None
    if segments and segments[0]["kind"] == "card" and segments[0]["name"] == "title":
        title = " | ".join(s for s in segments[0]["lines"][:2] if s.strip())
    t0 = time.time()
    concat(files, output, title)
    duration, size, frames = final_stats(output)
    expected = total / FPS
    print(f"Joined in {time.time() - t0:.1f} s")
    print(f"Reel: {output}")
    print(f"  duration {fmt_time(duration)} ({duration:.3f} s; segments sum to {expected:.3f} s), "
          f"{frames} frames, {size / 1e6:.1f} MB")
    if abs(duration - expected) > 0.2 or frames != total:
        print(f"warning: output differs from the plan ({frames} frames vs {total} planned)")
        return 1
    if not 120 <= expected <= 180:
        print("note: recruiting reels work best at 2 to 3 minutes")
    print(f"Segment cache: {work} (safe to delete)")
    return 0


# ------------------------------------------------------------------ grids

def grids(spec_path):
    """Write each clip's first frame at source resolution with a labelled grid."""
    output, segments, fonts = load_plan(spec_path)
    outdir = os.path.join(os.path.dirname(output), WORK_DIR, "grids")
    os.makedirs(outdir, exist_ok=True)
    for seg in segments:
        if seg["kind"] != "clip":
            continue
        info = probe(seg["src"])
        args, pre_v, _ = source_chain(info, seg["start"])
        fs = max(14, info["h"] // 54)
        vf = pre_v + ["format=rgb24", "drawgrid=w=50:h=50:t=1:c=white@0.15",
                      "drawgrid=w=100:h=100:t=1:c=white@0.45"]
        font = font_opt(fonts["bold"], True)
        for x in range(100, info["w"], 100):
            vf.append(f"drawtext={font}:text={x}:fontsize={fs}:fontcolor=yellow:"
                      f"box=1:boxcolor=black@0.6:boxborderw=2:x={x + 3}:y=3")
        for y in range(100, info["h"], 100):
            vf.append(f"drawtext={font}:text={y}:fontsize={fs}:fontcolor=yellow:"
                      f"box=1:boxcolor=black@0.6:boxborderw=2:x=3:y={y + 3}")
        if seg["spot"]:
            x, y = int(seg["spot"]["x"]), int(seg["spot"]["y"])
            vf += [f"drawbox=x={x - 30}:y={y - 1}:w=61:h=3:color=cyan:t=fill",
                   f"drawbox=x={x - 1}:y={y - 30}:w=3:h=61:color=cyan:t=fill"]
        n = seg["name"].replace(" ", "")
        out = os.path.join(outdir, f"{n}_{os.path.splitext(os.path.basename(seg['src']))[0]}"
                                   f"_{fmt_time(seg['start']).replace(':', '-')}.png")
        run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", *args,
             "-i", seg["src"], "-map", f"0:{info['vindex']}", "-vf", ",".join(vf),
             "-frames:v", "1", out], f"{seg['name']} grid")
        print(f"{seg['name']}: {out}  ({info['w']}x{info['h']} source pixels)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build a recruiting highlight reel from a JSON spec.")
    ap.add_argument("spec", help="reel spec (JSON)")
    ap.add_argument("--fresh", action="store_true", help="rebuild every segment")
    ap.add_argument("--grids", action="store_true",
                    help="only write each clip's first frame with a pixel grid (for spot x/y)")
    args = ap.parse_args(argv)
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            print(f"make_reel.py: error: {tool} not found on PATH", file=sys.stderr)
            return 2
    try:
        return grids(args.spec) if args.grids else build(args.spec, args.fresh)
    except ReelError as exc:
        print(f"\nmake_reel.py: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
