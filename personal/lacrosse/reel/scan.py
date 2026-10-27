#!/usr/bin/env python3
"""Timestamped contact sheets for finding plays in game film by eye.

    python3 scan.py VIDEO OUTDIR [--every 2] [--start T] [--end T]
                                 [--method auto|seek|linear] [--jobs N]

Writes 1920x1080 JPEG sheets of 4x4 tiles (480x270 each), one source frame
every --every seconds, with the source time (H:MM:SS) burned into each tile.
Each sheet is named after the time of its first tile: sheet_0-12-32.jpg starts
at 0:12:32 and, at the default 2 s spacing, covers the next 32 seconds.

Times accept seconds (751.5), M:SS(.s) or H:MM:SS(.s).

Methods:
  seek    one ffmpeg per sheet, each of the 16 frames opened with its own
          input seek, so only the stretch from the keyframe before each sample
          is decoded. Sheets run in parallel (--jobs).
  linear  one ffmpeg that decodes the whole range and keeps a frame every N s.
  auto    (default) probe the keyframe spacing: seek when keyframes are at
          most --every apart (each sample then decodes under one GOP),
          otherwise linear.

Python 3 standard library only; needs ffmpeg and ffprobe on PATH.
"""
import argparse
import concurrent.futures
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

COLS, ROWS = 4, 4
TILE_W, TILE_H = 480, 270
PER_SHEET = COLS * ROWS
SEEK_THREADS = "1"        # decoder threads per input in seek mode (sheets run in parallel)

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


class ScanError(Exception):
    pass


# ---------------------------------------------------------------- helpers

def parse_time(value):
    """'751.5', '12:31.5', '1:02:31' or a number -> seconds (float)."""
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    try:
        parts = [float(p) for p in text.split(":")]
    except ValueError:
        raise ScanError(f"bad time {value!r}: use seconds, M:SS or H:MM:SS")
    if not 1 <= len(parts) <= 3 or any(p < 0 for p in parts):
        raise ScanError(f"bad time {value!r}: use seconds, M:SS or H:MM:SS")
    seconds = 0.0
    for p in parts:
        seconds = seconds * 60 + p
    return seconds


def hms(t, tenths=False):
    """Seconds -> H:MM:SS (or H:MM:SS.t)."""
    if tenths:
        d = int(round(t * 10))
        return f"{d // 36000}:{d // 600 % 60:02d}:{d // 10 % 60:02d}.{d % 10}"
    s = int(round(t))
    return f"{s // 3600}:{s // 60 % 60:02d}:{s % 60:02d}"


def fesc(value):
    """Escape a string for use as a filter option value inside a filtergraph."""
    v = str(value)
    for ch in "\\':":          # level 1: option value
        v = v.replace(ch, "\\" + ch)
    v = v.replace("\\", "\\\\").replace("'", "\\'")   # level 2: filtergraph
    for ch in "[],;":
        v = v.replace(ch, "\\" + ch)
    return v


def font_option():
    for path in FONT_CANDIDATES:
        if os.path.isfile(path):
            return "fontfile=" + fesc(path)
    return "font=Sans"           # let fontconfig choose


def run(cmd):
    proc = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-12:])
        raise ScanError(f"{os.path.basename(cmd[0])} failed:\n{tail}")
    return proc.stdout


def probe(video):
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0",
               "-show_entries", "stream=width,height:format=duration",
               "-of", "default=noprint_wrappers=1", video])
    info = dict(line.split("=", 1) for line in out.splitlines() if "=" in line)
    if "width" not in info:
        raise ScanError(f"no video stream in {video}")
    try:
        duration = float(info.get("duration", "nan"))
    except ValueError:
        duration = float("nan")
    if not duration > 0:
        raise ScanError(f"cannot read the duration of {video}")
    return duration


def keyframe_spacing(video, start):
    """Median keyframe spacing (s) over ~30 s of packets; reads, does not decode."""
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0",
               "-read_intervals", f"{start:.3f}%+30",
               "-show_entries", "packet=pts_time,flags", "-of", "csv=p=0", video])
    keys = []
    for line in out.splitlines():
        fields = line.split(",")
        if len(fields) >= 2 and "K" in fields[1]:
            try:
                keys.append(float(fields[0]))
            except ValueError:
                pass
    keys.sort()
    gaps = [b - a for a, b in zip(keys, keys[1:]) if b > a]
    return statistics.median(gaps) if gaps else float("inf")


TILE_CHAIN = (f"scale={TILE_W}:{TILE_H}:force_original_aspect_ratio=decrease,"
              f"pad={TILE_W}:{TILE_H}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p")


def label_filter(textfile, expand):
    return (f"drawtext={font_option()}:textfile={fesc(textfile)}:"
            f"expansion={'normal' if expand else 'none'}:fontsize=26:fontcolor=white:"
            f"box=1:boxcolor=black@0.65:boxborderw=6:x=8:y=8,"
            f"drawbox=x=0:y=0:w=iw:h=ih:color=black:t=2")


# ---------------------------------------------------------------- methods

def sheet_seek(video, times, out_path, work, tenths):
    """One sheet: 16 inputs, each opened with an accurate input seek."""
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y"]
    graph = []
    for i, t in enumerate(times):
        cmd += ["-threads", SEEK_THREADS, "-ss", f"{t:.3f}", "-i", video]
        label = os.path.join(work, f"{os.path.basename(out_path)}.{i}.txt")
        with open(label, "w", encoding="utf-8") as fh:
            fh.write(hms(t, tenths))
        graph.append(f"[{i}:v]trim=end_frame=1,{TILE_CHAIN},{label_filter(label, False)}[t{i}]")
    for i in range(len(times), PER_SHEET):
        graph.append(f"color=c=black:s={TILE_W}x{TILE_H}:r=1:d=1,format=yuv420p,setsar=1[t{i}]")
    graph.append("".join(f"[t{i}]" for i in range(PER_SHEET))
                 + f"xstack=inputs={PER_SHEET}:grid={COLS}x{ROWS}[out]")
    cmd += ["-filter_complex", ";".join(graph), "-map", "[out]",
            "-frames:v", "1", "-q:v", "3", out_path]
    run(cmd)


def sheet_name(t, tenths):
    return "sheet_" + hms(t, tenths).replace(":", "-") + ".jpg"


def scan_linear(video, start, span, every, outdir, work, tenths):
    """Whole range in one ffmpeg: decode everything, keep one frame per step."""
    off = f"(t+{start + 0.0005:.4f})"
    text = (f"%{{eif:trunc({off}/3600):d}}:%{{eif:mod(trunc({off}/60),60):d:2}}:"
            f"%{{eif:mod(trunc({off}),60):d:2}}")
    if tenths:
        text += f".%{{eif:mod(trunc({off}*10),10):d}}"
    label = os.path.join(work, "label.txt")
    with open(label, "w", encoding="utf-8") as fh:
        fh.write(text)
    vf = (f"fps=1/{every:g},{TILE_CHAIN},{label_filter(label, True)},"
          f"tile={COLS}x{ROWS}")
    pattern = os.path.join(work, "lin_%05d.jpg")
    run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
         "-ss", f"{start:.3f}", "-t", f"{span:.3f}", "-i", video,
         "-vf", vf, "-q:v", "3", pattern])
    written = []
    for k, src in enumerate(sorted(f for f in os.listdir(work) if f.startswith("lin_"))):
        dst = os.path.join(outdir, sheet_name(start + k * PER_SHEET * every, tenths))
        shutil.move(os.path.join(work, src), dst)
        written.append(dst)
    return written


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Timestamped 4x4 contact sheets for finding plays in game film.")
    ap.add_argument("video")
    ap.add_argument("outdir")
    ap.add_argument("--every", type=float, default=2.0, help="seconds between frames (default 2)")
    ap.add_argument("--start", default="0", help="start time (default 0)")
    ap.add_argument("--end", default=None, help="end time (default: end of video)")
    ap.add_argument("--method", choices=["auto", "seek", "linear"], default="auto")
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1),
                    help="sheets built in parallel by the seek method")
    args = ap.parse_args(argv)

    try:
        if not os.path.isfile(args.video):
            raise ScanError(f"video not found: {args.video}")
        if not args.every > 0:
            raise ScanError("--every must be > 0")
        for tool in ("ffmpeg", "ffprobe"):
            if not shutil.which(tool):
                raise ScanError(f"{tool} not found on PATH")
        duration = probe(args.video)
        start = parse_time(args.start)
        end = duration if args.end is None else min(parse_time(args.end), duration)
        if start >= end:
            raise ScanError(f"start {hms(start)} is not before end {hms(end)} "
                            f"(video is {hms(duration)} long)")
        # Last sample a little before EOF so every seek still finds a frame.
        last_ok = min(end, duration - 0.25)
        times = []
        k = 0
        while start + k * args.every <= last_ok + 1e-9 and start + k * args.every < end:
            times.append(round(start + k * args.every, 3))
            k += 1
        if not times:
            raise ScanError("no sample times in the requested range")
        tenths = any(abs(t - round(t)) > 0.05 for t in times)
        sheets = [times[i:i + PER_SHEET] for i in range(0, len(times), PER_SHEET)]

        method = args.method
        gop = None
        if method == "auto":
            gop = keyframe_spacing(args.video, start)
            method = "seek" if gop <= args.every + 1e-6 else "linear"

        os.makedirs(args.outdir, exist_ok=True)
        work = tempfile.mkdtemp(prefix="scan_")
        t0 = time.time()
        try:
            if method == "seek":
                written, failures = [], []
                with concurrent.futures.ThreadPoolExecutor(max(1, args.jobs)) as pool:
                    futures = {}
                    for sheet in sheets:
                        out = os.path.join(args.outdir, sheet_name(sheet[0], tenths))
                        futures[pool.submit(sheet_seek, args.video, sheet, out, work, tenths)] = out
                    for fut in concurrent.futures.as_completed(futures):
                        try:
                            fut.result()
                            written.append(futures[fut])
                        except ScanError as exc:
                            failures.append(f"{os.path.basename(futures[fut])}: {exc}")
                if failures:
                    raise ScanError("some sheets failed:\n" + "\n".join(failures))
            else:
                written = scan_linear(args.video, start, end - start, args.every,
                                      args.outdir, work, tenths)
        finally:
            shutil.rmtree(work, ignore_errors=True)
        elapsed = time.time() - t0
    except ScanError as exc:
        print(f"scan.py: error: {exc}", file=sys.stderr)
        return 2

    gop_note = f", keyframes every {gop:.2f} s" if gop not in (None, float("inf")) else ""
    print(f"{len(written)} sheets, {len(times)} frames ({hms(times[0])} to {hms(times[-1])}, "
          f"every {args.every:g} s) -> {args.outdir}")
    print(f"method {method}{gop_note}; {elapsed:.1f} s "
          f"({elapsed / max(1e-9, end - start) * 3600:.0f} s per hour of film)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
