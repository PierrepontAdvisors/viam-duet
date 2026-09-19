"""Frames from the wrist camera: decoding, a background poller, and the median turn capture.
Turn photos are only taken from the look pose."""
from __future__ import annotations

import asyncio
import contextlib
import struct
from collections import deque
from dataclasses import dataclass
from time import monotonic

import cv2
import numpy as np

DEPTH_MAGIC = b"DEPTHMAP"


def decode_color(img) -> np.ndarray:
    """A NamedImage's JPEG/PNG bytes as a BGR array."""
    return cv2.imdecode(np.frombuffer(img.data, dtype=np.uint8), cv2.IMREAD_COLOR)


def decode_depth(data: bytes) -> np.ndarray:
    """Viam's raw depth map: 8-byte magic, width and height as big-endian uint64, then big-endian
    uint16 millimeters, row-major. Zero means no reading."""
    if data[:8] != DEPTH_MAGIC:
        raise ValueError("not a Viam depth map")
    w, h = struct.unpack(">QQ", data[8:24])
    return np.frombuffer(data, dtype=">u2", offset=24, count=w * h).reshape(h, w).astype(np.uint16)


def _mime(img) -> str:
    return str(getattr(img.mime_type, "value", img.mime_type)).lower()


@dataclass(frozen=True)
class Frame:
    color: np.ndarray
    depth: np.ndarray | None
    t: float


async def grab_frame(cam) -> Frame:
    """One color frame and, when the camera sends one, its aligned depth frame."""
    images, _ = await cam.get_images()
    color = depth = None
    for img in images:
        mime = _mime(img)
        if color is None and ("jpeg" in mime or "png" in mime):
            color = decode_color(img)
        elif "dep" in mime:
            depth = decode_depth(img.data)
    if color is None:
        raise RuntimeError("the camera returned no color image")
    if depth is not None and depth.shape != color.shape[:2]:
        # a mismatched depth stream degrades to the color check instead of crashing the hand check
        depth = None
    return Frame(color, depth, monotonic())


async def grab_color(cam) -> np.ndarray:
    return (await grab_frame(cam)).color


async def median_capture(cam, n: int = 5, delay_s: float = 0.1) -> np.ndarray:
    """Per-pixel median of n frames: removes sensor noise and a passing flicker."""
    frames = []
    for _ in range(n):
        frames.append(await grab_color(cam))
        await asyncio.sleep(delay_s)
    return np.median(np.stack(frames), axis=0).astype(np.uint8)


class FrameSource:
    """Polls the camera in the background at about `fps` and keeps the latest frame plus a short
    history for the stillness reading. A camera error is counted and polling continues."""

    def __init__(self, cam, fps: float = 5.0, history_s: float = 3.0, grab_timeout_s: float = 2.0):
        self.cam = cam
        self.period = 1.0 / fps
        self.history_s = history_s
        self.grab_timeout_s = grab_timeout_s
        self.frames: deque[Frame] = deque()
        self.errors = 0
        self.last_error: str | None = None
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._task is not None and not self._task.done():
            return
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

    async def _loop(self) -> None:
        while True:
            try:
                frame = await asyncio.wait_for(grab_frame(self.cam), self.grab_timeout_s)
                self.frames.append(frame)
                while self.frames and frame.t - self.frames[0].t > self.history_s:
                    self.frames.popleft()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.errors += 1
                self.last_error = str(exc)
            await asyncio.sleep(self.period)

    def latest(self, max_age_s: float = 1.0) -> Frame | None:
        if not self.frames:
            return None
        frame = self.frames[-1]
        if monotonic() - frame.t > max_age_s:
            return None
        return frame

    def recent(self, seconds: float) -> list[Frame]:
        cutoff = monotonic() - seconds
        return [f for f in self.frames if f.t >= cutoff]

    async def capture_median(self, n: int = 5, delay_s: float = 0.1) -> np.ndarray:
        return await median_capture(self.cam, n, delay_s)
