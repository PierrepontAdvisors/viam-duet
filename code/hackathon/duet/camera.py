"""Frames from the wrist camera. Turn photos are only taken from the look pose."""
from __future__ import annotations

import asyncio

import cv2
import numpy as np
from viam.components.camera import Camera


def decode_color(img) -> np.ndarray:
    """A NamedImage's JPEG/PNG bytes as a BGR array."""
    return cv2.imdecode(np.frombuffer(img.data, dtype=np.uint8), cv2.IMREAD_COLOR)


async def grab_color(cam: Camera) -> np.ndarray:
    images, _ = await cam.get_images()
    for img in images:
        mime = str(getattr(img.mime_type, "value", img.mime_type)).lower()
        if "jpeg" in mime or "png" in mime:
            return decode_color(img)
    raise RuntimeError("the camera returned no color image")


async def median_capture(cam: Camera, n: int = 5, delay_s: float = 0.1) -> np.ndarray:
    """Per-pixel median of n frames: removes sensor noise and a passing flicker."""
    frames = []
    for _ in range(n):
        frames.append(await grab_color(cam))
        await asyncio.sleep(delay_s)
    return np.median(np.stack(frames), axis=0).astype(np.uint8)
