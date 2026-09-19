"""Session memory in the layout `duet.turn` already uses: a folder per session with a photo per
turn, the plan SVGs, session.json (plus sessions/current.json), and the ffmpeg stitch of the
photos into session.mp4 when the piece is done."""
from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from duet import config as cfg

FFMPEG = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
FFPROBE = shutil.which("ffprobe") or "/opt/homebrew/bin/ffprobe"


class Recorder:
    def __init__(self, session_id: str | None = None, root: Path = cfg.SESSIONS_DIR, settings: dict | None = None):
        self.id = session_id or datetime.now().strftime("%Y%m%d-%H%M%S")
        self.root = root
        self.dir = root / self.id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.photos: list[Path] = []
        self.frames: list[Path] = []
        self.latest_frame: Path | None = None
        self.meta: dict = {"id": self.id, "started": self.id, "turn": 0, "last_photo": None,
                           "history": [], "turns": [], **(settings or {})}

    def save_photo(self, turn: int, who: str, bgr: np.ndarray, frame: np.ndarray | None = None) -> Path:
        """The warped board photo and, when given, the raw landscape camera frame beside it as
        `turn-NN-<who>-frame.jpg`. The page and the video prefer the frame: it has no seam at the board edge."""
        path = self.dir / f"turn-{turn:02d}-{who}.jpg"
        if not cv2.imwrite(str(path), bgr, [cv2.IMWRITE_JPEG_QUALITY, 90]):
            raise OSError(f"could not write {path}")
        self.photos.append(path)
        self.meta["last_photo"] = path.name
        self.latest_frame = None
        if frame is not None:
            fpath = self.dir / f"turn-{turn:02d}-{who}-frame.jpg"
            if not cv2.imwrite(str(fpath), frame, [cv2.IMWRITE_JPEG_QUALITY, 90]):
                raise OSError(f"could not write {fpath}")
            self.frames.append(fpath)
            self.latest_frame = fpath
        return path

    def save_svg(self, turn: int, svg_text: str) -> Path:
        path = self.dir / f"plan-{turn:02d}.svg"
        path.write_text(svg_text)
        return path

    def record_turn(self, turn: int, **fields) -> None:
        """Per-turn details under `turns`; sees/adds/source also go into `history` in turn.py's shape."""
        entry = next((t for t in self.meta["turns"] if t["turn"] == turn), None)
        if entry is None:
            entry = {"turn": turn}
            self.meta["turns"].append(entry)
        entry.update(fields)
        if turn >= 1 and "sees" in entry and "adds" in entry:
            hist = {"sees": entry["sees"], "adds": entry["adds"], "source": entry.get("source", "claude")}
            while len(self.meta["history"]) < turn:
                self.meta["history"].append({"sees": "", "adds": "", "source": ""})
            self.meta["history"][turn - 1] = hist

    def set_turn(self, turn: int) -> None:
        self.meta["turn"] = turn

    def update(self, **settings) -> None:
        self.meta.update(settings)

    def write(self) -> Path:
        text = json.dumps(self.meta, indent=2, default=str) + "\n"
        path = self.dir / "session.json"
        path.write_text(text)
        current = self.root / "current.json"
        try:
            owner = json.loads(current.read_text())["id"]
        except (OSError, ValueError, KeyError):
            owner = None
        if owner is None or owner == self.id:
            current.write_text(text)
        return path

    @property
    def latest_photo(self) -> Path | None:
        return self.photos[-1] if self.photos else None

    def stitch(self, per_frame_s: float = 1.0, hold_last_s: float = 2.0) -> Path | None:
        """One frame per turn, the last one held. Uses the landscape camera frames when every turn
        has one, else the warped photos. The concat demuxer only honors the final duration when the
        last file is listed once more after it; ffmpeg 9's demuxer also runs long past that stated
        total by about a second regardless, so the encode is hard-capped to the exact frame count."""
        sources = self.frames if self.frames and len(self.frames) == len(self.photos) else self.photos
        if not sources:
            return None
        listing = self.dir / "frames.txt"
        lines: list[str] = []
        for p in sources[:-1]:
            lines += [f"file '{p.resolve()}'", f"duration {per_frame_s}"]
        last = sources[-1].resolve()
        lines += [f"file '{last}'", f"duration {hold_last_s}", f"file '{last}'"]
        listing.write_text("\n".join(lines) + "\n")
        out = self.dir / "session.mp4"
        fps = 10
        total_frames = round((per_frame_s * (len(sources) - 1) + hold_last_s) * fps)
        try:
            subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p", "-r", str(fps),
                            "-frames:v", str(total_frames),
                            "-c:v", "libx264", "-movflags", "+faststart", str(out)],
                           check=True, capture_output=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
            print(f"stitch failed, keeping the stills: {(getattr(exc, 'stderr', '') or str(exc)).strip()[:400]}")
            return None
        listing.unlink(missing_ok=True)
        return out


def video_duration_s(path: Path) -> float:
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         check=True, capture_output=True, text=True)
    return float(out.stdout.strip())


def video_size(path: Path) -> tuple[int, int]:
    """(width, height) of the first video stream."""
    out = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", str(path)], check=True, capture_output=True, text=True)
    w, h = out.stdout.strip().split(",")[:2]
    return int(w), int(h)
