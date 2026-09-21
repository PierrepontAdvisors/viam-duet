#!/usr/bin/env python3
"""Build the class deck's local assets from hackathon-videos/ at the repo root.

Photos: webp or jpg -> img/*.jpg, longest side 2000 px, JPEG quality 85 (Pillow).
Clips:  .mov -> video/team-N.mp4, H.264, 720 px tall, no audio, at most 15 s (ffmpeg).
Outputs that exist are skipped; --force redoes them. Sources that are missing are reported, not fatal,
so the deck builds without the medal photo until it is dropped in.

Run with the hackathon venv:  ../../../code/hackathon/.venv/bin/python build_assets.py
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[2] / "hackathon-videos"          # docs/duet/class -> repo root
MAX_SIDE = 2000
JPEG_QUALITY = 85
CLIP_HEIGHT = 720
CLIP_SECONDS = 15

PHOTOS = [
    ("photo-setup.webp", "img/setup.jpg"),
    ("photo-door.webp", "img/door.jpg"),
    ("photo-crowd.webp", "img/crowd.jpg"),
    ("photo-medal.jpg", "img/medal.jpg"),
]
CLIPS = [                                             # clip order is chronological by filename
    ("IMG_0016.MOV", "video/team-1.mp4"),
    ("IMG_0018.mov", "video/team-2.mp4"),
    ("IMG_0022.mov", "video/team-3.mp4"),
    ("IMG_0024.mov", "video/team-4.mp4"),
]


def jobs(existing: set[str], force: bool) -> list[tuple[str, str, str]]:
    """(kind, src, dst) for every output not in `existing`, or all of them with force. Photos first."""
    out: list[tuple[str, str, str]] = []
    for kind, table in (("photo", PHOTOS), ("clip", CLIPS)):
        for src, dst in table:
            if force or dst not in existing:
                out.append((kind, src, dst))
    return out


def convert_photo(src: Path, dst: Path) -> None:
    from PIL import Image, ImageOps

    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((MAX_SIDE, MAX_SIDE))
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst, "JPEG", quality=JPEG_QUALITY, optimize=True)


def convert_clip(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-t", str(CLIP_SECONDS),
         "-vf", f"scale=-2:{CLIP_HEIGHT}", "-c:v", "libx264", "-crf", "23", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", str(dst)],
        check=True,
    )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="redo outputs that already exist")
    args = ap.parse_args(argv)
    existing = {dst for _, dst in PHOTOS + CLIPS if (HERE / dst).exists()}
    todo = jobs(existing, args.force)
    if not todo:
        print("nothing to do")
        return 0
    missing: list[str] = []
    for kind, src, dst in todo:
        source = SRC / src
        if not source.exists():
            missing.append(src)
            continue
        print(f"{kind}: {src} -> {dst}")
        (convert_photo if kind == "photo" else convert_clip)(source, HERE / dst)
    for name in missing:
        print(f"skipped, source not found: {SRC / name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
