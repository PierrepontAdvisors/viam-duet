import asyncio
import struct

import cv2
import numpy as np

from duet import camera


def dep_bytes(depth: np.ndarray) -> bytes:
    h, w = depth.shape
    return b"DEPTHMAP" + struct.pack(">QQ", w, h) + depth.astype(">u2").tobytes()


class Img:
    def __init__(self, name, mime, data):
        self.name, self.mime_type, self.data = name, mime, data


class FakeCam:
    def __init__(self):
        self.calls = 0
        color = np.full((60, 80, 3), 200, np.uint8)
        color[10:20, 10:20] = 0
        self.jpg = cv2.imencode(".jpg", color)[1].tobytes()
        self.dep = dep_bytes(np.full((60, 80), 700, np.uint16))

    async def get_images(self):
        self.calls += 1
        return [Img("color", "image/jpeg", self.jpg), Img("depth", "image/vnd.viam.dep", self.dep)], None


def test_decode_depth_roundtrip():
    d = np.arange(12, dtype=np.uint16).reshape(3, 4) * 100
    out = camera.decode_depth(dep_bytes(d))
    assert out.dtype == np.uint16 and out.shape == (3, 4) and out[2, 3] == 1100


def test_grab_frame_returns_color_and_depth():
    f = asyncio.run(camera.grab_frame(FakeCam()))
    assert f.color.shape == (60, 80, 3) and f.depth.shape == (60, 80) and f.depth[0, 0] == 700


def test_median_capture_still_works():
    out = asyncio.run(camera.median_capture(FakeCam(), n=3, delay_s=0.0))
    assert out.shape == (60, 80, 3) and out[0, 0, 0] > 150 and out[15, 15, 0] < 50


def test_frame_source_polls_and_keeps_a_short_history():
    async def scenario():
        cam = FakeCam()
        src = camera.FrameSource(cam, fps=50, history_s=0.2)
        await src.start()
        await asyncio.sleep(0.3)
        latest = src.latest()
        recent = src.recent(0.1)
        await src.stop()
        return cam, src, latest, recent
    cam, src, latest, recent = asyncio.run(scenario())
    assert cam.calls >= 5
    assert latest is not None and latest.depth is not None
    assert 1 <= len(recent) <= 8
    assert all(f.t <= latest.t for f in src.frames) and latest.t - src.frames[0].t <= 0.25


def test_frame_source_survives_a_camera_error():
    class FlakyCam(FakeCam):
        async def get_images(self):
            self.calls += 1
            if self.calls == 2:
                raise RuntimeError("camera hiccup")
            return [Img("color", "image/jpeg", self.jpg), Img("depth", "image/vnd.viam.dep", self.dep)], None

    async def scenario():
        src = camera.FrameSource(FlakyCam(), fps=50)
        await src.start()
        await asyncio.sleep(0.2)
        await src.stop()
        return src
    src = asyncio.run(scenario())
    assert src.errors == 1 and "hiccup" in src.last_error and src.latest() is not None
