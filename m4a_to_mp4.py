#!/usr/bin/env python3
import argparse
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

DEFAULT_AUDIO_EXT = ".m4a"
DEFAULT_IMAGE_EXT = ".png"
DEFAULT_W, DEFAULT_H = 1280, 720
DEFAULT_AUDIO_BPS = "192k"

def have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None

def iter_files(base: Path, pattern: str, recursive: bool) -> Iterable[Path]:
    if recursive:
        yield from base.rglob(pattern)
    else:
        yield from base.glob(pattern)

def build_ffmpeg_cmd(png: Path, m4a: Path, mp4_out: Path,
                     w: int, h: int, audio_bps: str) -> list[str]:
    # Fit image to WxH while preserving aspect; pad to fill; yuv420p for compatibility
    vf = (
        f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"
    )
    return [
        "ffmpeg",
        "-y",                       # overwrite (we handle overwrite policy outside)
        "-loop", "1",
        "-i", str(png),
        "-i", str(m4a),
        "-vf", vf,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", audio_bps,
        "-movflags", "+faststart", # better streaming/startup on the web
        "-shortest",
        str(mp4_out),
    ]

def main():
    parser = argparse.ArgumentParser(
        prog="m4a_to_mp4",
        description=(
            "Batch-convert podcast audio (.m4a) to YouTube-ready .mp4 videos by pairing "
            "each audio with a PNG that has the same base name. "
            "Example: 'Episode01.m4a' + 'Episode01.png' -> 'Episode01.mp4'.\n\n"
            "Rules:\n"
            "  • If matching .mp4 already exists, the .m4a is skipped (unless --overwrite).\n"
            "  • PNG is required; missing image causes a skip.\n"
            "  • Image is auto-fit to 1280x720 with letterbox padding (no distortion).\n"
            "  • Outputs H.264 video + AAC audio with +faststart for YouTube."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Folder to scan (default: current directory).",
    )
    parser.add_argument(
        "-R", "--recursive",
        action="store_true",
        help="Scan subfolders recursively."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing .mp4 files instead of skipping."
    )
    parser.add_argument(
        "--audio-ext",
        default=DEFAULT_AUDIO_EXT,
        help=f"Audio extension to match (default: {DEFAULT_AUDIO_EXT})."
    )
    parser.add_argument(
        "--image-ext",
        default=DEFAULT_IMAGE_EXT,
        help=f"Image extension to match (default: {DEFAULT_IMAGE_EXT})."
    )
    parser.add_argument(
        "--width", type=int, default=DEFAULT_W,
        help=f"Output width (default: {DEFAULT_W})."
    )
    parser.add_argument(
        "--height", type=int, default=DEFAULT_H,
        help=f"Output height (default: {DEFAULT_H})."
    )
    parser.add_argument(
        "--abitrate", default=DEFAULT_AUDIO_BPS,
        help=f"AAC audio bitrate (default: {DEFAULT_AUDIO_BPS})."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be converted without running ffmpeg."
    )

    args = parser.parse_args()
    base = Path(args.folder).resolve()

    print(f"Scan folder: {base}")
    if not base.exists() or not base.is_dir():
        print("ERROR: folder does not exist or is not a directory.")
        return

    if not have_ffmpeg():
        print("ERROR: ffmpeg not found in PATH. Install it and try again.")
        return

    audio_ext = args.audio_ext if args.audio_ext.startswith(".") else "." + args.audio_ext
    image_ext = args.image_ext if args.image_ext.startswith(".") else "." + args.image_ext

    m4a_files = sorted(
        p for p in iter_files(base, f"*{audio_ext}", args.recursive) if p.is_file()
    )
    if not m4a_files:
        print(f"No {audio_ext} files found.")
        return

    converted = 0
    skipped = 0
    errors = 0

    for m4a in m4a_files:
        stem = m4a.stem
        png = m4a.with_name(stem + image_ext)
        mp4_out = m4a.with_name(stem + ".mp4")

        if mp4_out.exists() and not args.overwrite:
            print(f"SKIP (exists): {mp4_out.relative_to(base)}")
            skipped += 1
            continue

        if not png.exists():
            print(f"SKIP (missing image): expects {png.relative_to(base)}")
            skipped += 1
            continue

        cmd = build_ffmpeg_cmd(png, m4a, mp4_out, args.width, args.height, args.abitrate)
        print(f"Convert: {m4a.relative_to(base)} + {png.name} -> {mp4_out.name}")

        if args.dry_run:
            print("  (dry-run) ", " ".join(cmd))
            continue

        try:
            subprocess.run(cmd, check=True)
            converted += 1
        except subprocess.CalledProcessError as e:
            print(f"ERROR converting {m4a.name}: {e}")
            # Clean partial output if any
            try:
                if mp4_out.exists() and mp4_out.stat().st_size < 1024:
                    mp4_out.unlink()
            except Exception:
                pass
            errors += 1

    print(f"\nSummary: converted={converted}  skipped={skipped}  errors={errors}")

if __name__ == "__main__":
    main()
