# Duet plan 4: Overnight build without the arm (trigger, loop, page, memory) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Everything the day-1 session left for day 2 that needs no machine: the turn trigger (hand, stillness, dock dots), a session loop that replaces the terminal `turn start`/`turn next` prompts, the session record with a stitched video, the FastAPI server with a plain functional page, and a `--fake` runner that replays the real day-1 boards through the whole pipeline so the loop and page are verified on the Mac tonight.

**Architecture:** Builds on the code committed during day 1 (`claude_turn.propose`, `planner.validate/finalize`, `styles.haring.style/fallback`, `svg.write`, `turn.py`'s `warp/map_strokes/all_ink`, `calibrate`, `vision`, `controller`), which this plan does not modify. New modules: `trigger.py` (pure state machine), `recorder.py` (session folder in the same layout `turn.py` uses, plus ffmpeg), `session.py` (one asyncio task, one method per state, every dependency injected), `fakes.py` (a fake camera that composites real board photos into a real look-pose frame, a fake arm, a canned brain), `web.py` and `static/index.html`, `run.py`. `camera.py` gains depth decoding and a background frame poller; `vision.py` gains the trigger readings. This plan supersedes plans 2 and 3, which were written before the day-1 code landed. Spec: `docs/superpowers/specs/2026-09-18-duet-design.md`, especially section 15 (day-1 changes).

**Tech Stack:** Python 3.12 venv at `code/hackathon/.venv`: viam-sdk 0.80.0, numpy, opencv-python-headless, scikit-image, skan, shapely 2.1, anthropic 1.7.0, pydantic 2.13, fastapi 0.141, uvicorn 0.53, websockets 17, httpx (Starlette's TestClient), pytest. ffmpeg 9 at `/opt/homebrew/bin/ffmpeg`. All installed.

**Working conventions for every task:**
- Run everything from `code/hackathon` with the venv: `cd "/Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/code/hackathon" && source .venv/bin/activate`.
- Git: branch `feat/duet-design`. Commit with `git add <exact files>`; never `git add -A` or `git add .`. Another session ("Website UI mockups") is working in this same tree tonight and owns `duet/static/index.html`'s design; it has an uncommitted change to the repo root `.gitignore` that must not be staged. Never commit `.env`. Messages use `<type>: <description>`.
- Nothing here touches the machine.
- Facts about the day-1 state used below: board 176 x 240 mm at 4 px/mm (warped board 704 x 960 px); the look pose is straight down with the camera about 450 mm up, so the corner quad is about 490 px wide and one image pixel is about 0.5 mm; `calibration.json` has `marks_image`, `board_tl_index` (3), `cam_to_robot` (a per-axis fit from camera-board mm to robot-board mm), and no depth plane. Fixtures in `tests/fixtures/`: `look_frame.jpg` (raw 1280 x 720 look-pose frame, marks about 21 px from the calibrated spots, which `find_corner_marks` absorbs), `exchange-00-start.jpg`, `exchange-01-human.jpg`, `exchange-01-robot.jpg` (real warped boards from the first hardware exchange: 13 human strokes, x 36 to 136, y 83 to 185), `exchange-01-plan.svg`, `board_blank.jpg`. `tests/conftest.py` provides them as `look_frame`, `exchange_start`, `exchange_human`, `exchange_robot`, `board_blank`, `calibration`.
- APIs from day 1 used as-is: `claude_turn.propose(client, board_bgr, human_cam, history, length_setting, exchange, exchange_total) -> TurnResult(proposal, source, latency_s, error)` (synchronous, up to 45 s); `claude_turn.Proposal/Stroke/Pt` (Pydantic, every Stroke field required); `claude_turn.make_client()`; `planner.validate(strokes: list[dict], existing_ink, budget_mm)`; `planner.finalize(styled, existing_ink, budget_mm)`; `haring.style(strokes, energy=) -> (polylines, color)`; `haring.fallback(human) -> (polylines, color)`; `svg.write(path, human, drawn, queued, color)`; `turn.warp(frame, cal)`, `turn.map_strokes(strokes, cal)`, `turn.all_ink(board, cal)`; `vision.cam_to_robot(polylines, cal)`; `Controller.draw(polylines, budget_mm, budget_s) -> DrawResult(strokes_done, drawn_mm, seconds, blocked)`, `Controller.events` (queue of `{"type": "progress", "stroke": i, "drawn_mm": d}`), `Controller.hand_check`, `go_look/pick_marker/return_marker/stop/recover/clear_error`, `held_mode`; `camera.median_capture(cam)`; constants `cfg.BUDGET_MM/BUDGET_S/COVERAGE_END/HELD_MODE/DOCK_SLOTS/COLOR_HEX/STILL_*/HELD_QUIET_S/HAND_*/SIGNATURE_MM/FIXTURES_DIR`.

---

### Task 1: Depth decoding, frame poller, and the trigger's readings

**Files:**
- Modify: `code/hackathon/duet/camera.py` (rewrite; keeps `decode_color`, `grab_color`, `median_capture`)
- Modify: `code/hackathon/duet/vision.py` (append)
- Modify: `code/hackathon/duet/calibrate.py` (add offline `--plane` and `--dock` verbs; leave the live verbs alone)
- Test: `code/hackathon/tests/test_camera.py`, `code/hackathon/tests/test_readings.py`

- [ ] **Step 1: Write the failing tests**

`code/hackathon/tests/test_camera.py`:

```python
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
            return await super().get_images()

    async def scenario():
        src = camera.FrameSource(FlakyCam(), fps=50)
        await src.start()
        await asyncio.sleep(0.2)
        await src.stop()
        return src
    src = asyncio.run(scenario())
    assert src.errors == 1 and "hiccup" in src.last_error and src.latest() is not None
```

`code/hackathon/tests/test_readings.py`:

```python
import math

import cv2
import numpy as np

from duet import config as cfg
from duet import vision


def quad_in(frame, calibration):
    return vision.find_corner_marks(frame, expected=calibration["marks_image"])


def homography_for(quad, calibration):
    return vision.board_homography(vision.board_quad(quad, calibration["board_tl_index"]))


def test_real_exchange_diffs_to_the_visitors_strokes(exchange_start, exchange_human):
    mask, coverage = vision.new_ink(exchange_human, exchange_start)
    polylines = vision.trace(mask)
    assert 10 <= len(polylines) <= 16 and 0.015 < coverage < 0.03
    xs = [x for pl in polylines for x, _ in pl]
    ys = [y for pl in polylines for _, y in pl]
    assert 30 <= min(xs) <= 40 and 130 <= max(xs) <= 140
    assert 78 <= min(ys) <= 88 and 180 <= max(ys) <= 190
    assert int(vision.new_ink(exchange_start, exchange_human)[0].sum()) == 0   # nothing got darker the other way


def test_mm_per_px_at_the_look_pose_is_about_half_a_millimeter(look_frame, calibration):
    quad = quad_in(look_frame, calibration)
    assert 0.45 <= vision.mm_per_px(quad) <= 0.56


def test_to_board_mm_maps_the_marks_to_the_board_corners(look_frame, calibration):
    quad = quad_in(look_frame, calibration)
    board = vision.board_quad(quad, calibration["board_tl_index"])
    pts = vision.to_board_mm(homography_for(quad, calibration), [tuple(p) for p in board])
    expected = [(0, 0), (cfg.BOARD_W_MM, 0), (cfg.BOARD_W_MM, cfg.BOARD_H_MM), (0, cfg.BOARD_H_MM)]
    assert all(abs(a - b) < 0.01 for p, ref in zip(pts, expected) for a, b in zip(p, ref))


def test_plane_fit_on_a_synthetic_tilted_plane():
    h, w = 120, 160
    ys, xs = np.mgrid[0:h, 0:w]
    depth = (600 + 0.5 * xs - 0.25 * ys).astype(np.uint16)
    depth[5:10, 5:10] = 0                       # holes are ignored
    depth[50:60, 50:60] = 3000                   # glare on the board reflects the ceiling: far readings must not skew the fit
    a, b, c = vision.fit_plane(depth, np.ones((h, w), np.uint8))
    assert abs(a - 0.5) < 0.02 and abs(b + 0.25) < 0.02 and abs(c - 600) < 2


def test_reference_depth_lowers_the_expected_surface_inside_the_dock():
    dock = [[10, 10], [30, 10], [30, 30], [10, 30]]
    ref = vision.reference_depth((40, 40), (0.0, 0.0, 700.0), [(dock, 30.0)])
    assert ref[5, 5] == 700 and ref[20, 20] == 670


def test_hand_present_depth_on_synthetic_frames():
    h, w = 120, 160
    expected = vision.plane_depth((h, w), (0.0, 0.0, 700.0))
    depth = np.full((h, w), 700, np.uint16)
    region = np.ones((h, w), np.uint8)
    assert vision.hand_present_depth(depth, region, expected, mm2_per_px=1.0) is False
    depth[40:80, 40:100] = 640                   # 60 mm above the plane, 2400 px = 2400 mm²
    assert vision.hand_present_depth(depth, region, expected, mm2_per_px=1.0) is True
    assert vision.hand_present_depth(depth, region, expected, mm2_per_px=0.5) is False   # too small at half the scale
    depth[:] = 700
    depth[40:80, 40:100] = 690                   # only 10 mm up: a sheet of paper, not a hand
    assert vision.hand_present_depth(depth, region, expected, mm2_per_px=1.0) is False


def test_hand_present_color_on_the_real_look_frame(look_frame, calibration):
    quad = quad_in(look_frame, calibration)
    region = vision.polygon_mask(look_frame.shape, [quad.tolist()])
    mm2 = vision.mm_per_px(quad) ** 2
    cx, cy = int(quad[:, 0].mean()), int(quad[:, 1].mean())
    skin = (90, 120, 170)      # a medium skin tone: its gray level (140) is within 15 of the board's (127)
    assert vision.hand_present_color(look_frame, look_frame, region, mm2) is False
    inked = look_frame.copy()                                       # a visitor's marker lines: thin, must not count
    for k in range(6):
        cv2.line(inked, (cx - 100, cy - 60 + 20 * k), (cx + 100, cy - 40 + 20 * k), (30, 30, 170), 3)
    assert vision.hand_present_color(inked, look_frame, region, mm2) is False
    hand = inked.copy()                                             # a hand: about 65 x 45 mm of skin over the board
    cv2.ellipse(hand, (cx, cy), (65, 45), 20, 0, 360, skin, -1)
    assert vision.hand_present_color(hand, look_frame, region, mm2) is True
    fingertip = look_frame.copy()                                   # a 9 mm dot of the same skin: too small
    cv2.circle(fingertip, (cx, cy), 9, skin, -1)
    assert vision.hand_present_color(fingertip, look_frame, region, mm2) is False


def green_frame(cx, cy, r=6):
    f = np.full((200, 300, 3), 235, np.uint8)
    cv2.circle(f, (cx, cy), r, (60, 170, 60), -1)   # a green end plug
    return f


def test_dock_dots_home_moved_missing(look_frame, calibration):
    h = homography_for(quad_in(look_frame, calibration), calibration)
    slots = {"green": {"xy": [150, 100], "hsv_lo": [40, 60, 60], "hsv_hi": [85, 255, 255]}}
    home = vision.dock_dots(green_frame(150, 100), slots, h)["green"]
    assert home.status == "home" and math.hypot(*home.displacement_mm) < 1.0
    moved = vision.dock_dots(green_frame(150 + 16, 100), slots, h)["green"]     # 16 px is about 8 mm here
    assert moved.status == "moved" and 4 < math.hypot(*moved.displacement_mm) < 14
    missing = vision.dock_dots(np.full((200, 300, 3), 235, np.uint8), slots, h)["green"]
    assert missing.status == "missing"


def test_still_needs_two_frames_and_a_quiet_scene():
    a = np.full((90, 160, 3), 128, np.uint8)
    b = a.copy()
    b[20:40, 20:60] = 200
    assert vision.still([a]) is False
    assert vision.still([a, a.copy(), a.copy()]) is True
    assert vision.still([a, b]) is False
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_camera.py tests/test_readings.py -q`
Expected: failures on `camera.decode_depth`, `camera.grab_frame`, `camera.FrameSource`, `vision.board_homography`, and the other new names; `test_real_exchange_diffs_to_the_visitors_strokes` may already pass.

- [ ] **Step 3: Rewrite `camera.py`**

`code/hackathon/duet/camera.py`:

```python
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

    def __init__(self, cam, fps: float = 5.0, history_s: float = 3.0):
        self.cam = cam
        self.period = 1.0 / fps
        self.history_s = history_s
        self.frames: deque[Frame] = deque()
        self.errors = 0
        self.last_error: str | None = None
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
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
                frame = await grab_frame(self.cam)
                self.frames.append(frame)
                while self.frames and frame.t - self.frames[0].t > self.history_s:
                    self.frames.popleft()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.errors += 1
                self.last_error = str(exc)
            await asyncio.sleep(self.period)

    def latest(self) -> Frame | None:
        return self.frames[-1] if self.frames else None

    def recent(self, seconds: float) -> list[Frame]:
        if not self.frames:
            return []
        cutoff = self.frames[-1].t - seconds
        return [f for f in self.frames if f.t >= cutoff]

    async def capture_median(self, n: int = 5, delay_s: float = 0.1) -> np.ndarray:
        return await median_capture(self.cam, n, delay_s)
```

- [ ] **Step 4: Append the readings to `vision.py`**

Add `import math` and `from dataclasses import dataclass` to the imports at the top of `code/hackathon/duet/vision.py`, then append at the end of the file:

```python


# ---- trigger readings: homography helpers, hand from depth or color, dock dots, stillness --------

def board_homography(quad_board_order: np.ndarray) -> np.ndarray:
    """3x3 map from image pixels to warped-board pixels (PX_PER_MM, origin at the board's top-left)."""
    w, h = BOARD_PX
    dst = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
    return cv2.getPerspectiveTransform(np.asarray(quad_board_order, dtype=np.float32), dst)


def to_board_mm(homography: np.ndarray, pts_px: list[Point]) -> list[Point]:
    """Image pixels to camera-board millimeters through the corner-mark homography."""
    out = cv2.perspectiveTransform(np.array([pts_px], dtype=np.float32), homography)[0]
    return [(float(x) / PX_PER_MM, float(y) / PX_PER_MM) for x, y in out]


def mm_per_px(quad_image: np.ndarray) -> float:
    """Average scale at the look pose: the board's area over the corner quad's pixel area."""
    area_px = abs(cv2.contourArea(np.asarray(quad_image, dtype=np.float32)))
    return math.sqrt(cfg.BOARD_W_MM * cfg.BOARD_H_MM / area_px)


def polygon_mask(shape_hw: tuple[int, int], polygons: list) -> np.ndarray:
    """1 inside any of the polygons (lists of (x, y) image points), 0 elsewhere."""
    m = np.zeros(shape_hw[:2], dtype=np.uint8)
    for poly in polygons:
        cv2.fillPoly(m, [np.asarray(poly, dtype=np.int32)], 1)
    return m


def fit_plane(depth: np.ndarray, mask: np.ndarray) -> tuple[float, float, float]:
    """Least-squares plane z = a*x + b*y + c through the valid readings inside `mask`. Readings far
    from the median (glare on the board reflects the ceiling and reads as meters) are dropped, and
    the fit is repeated without outliers."""
    ys, xs = np.nonzero((mask > 0) & (depth > 0))
    z = depth[ys, xs].astype(np.float64)
    if z.size < 100:
        raise ValueError("not enough valid depth readings inside the region")
    keep = np.abs(z - np.median(z)) < 80
    a = np.column_stack([xs, ys, np.ones_like(xs)]).astype(np.float64)
    coef, *_ = np.linalg.lstsq(a[keep], z[keep], rcond=None)
    keep = np.abs(a @ coef - z) < 15
    if keep.sum() >= 100:
        coef, *_ = np.linalg.lstsq(a[keep], z[keep], rcond=None)
    return float(coef[0]), float(coef[1]), float(coef[2])


def plane_depth(shape_hw: tuple[int, int], plane: tuple[float, float, float]) -> np.ndarray:
    a, b, c = plane
    ys, xs = np.mgrid[0:shape_hw[0], 0:shape_hw[1]]
    return (a * xs + b * ys + c).astype(np.float32)


def reference_depth(shape_hw: tuple[int, int], plane: tuple[float, float, float],
                    offsets: list[tuple[list, float]]) -> np.ndarray:
    """The surface a hand is measured against: the board plane, raised by `offset_mm` inside each
    polygon (the dock's putty stands above the board plane, so its own top is the reference there)."""
    ref = plane_depth(shape_hw, plane)
    for polygon, offset_mm in offsets:
        ref[polygon_mask(shape_hw, [polygon]) > 0] -= float(offset_mm)
    return ref


def _big_blob(mask: np.ndarray, mm2_per_px: float, area_mm2: float) -> bool:
    n, _, stats, _ = cv2.connectedComponentsWithStats(mask)
    return any(stats[i, cv2.CC_STAT_AREA] * mm2_per_px >= area_mm2 for i in range(1, n))


def hand_present_depth(depth: np.ndarray, region_mask: np.ndarray, expected_depth: np.ndarray,
                       mm2_per_px: float, height_mm: float = cfg.HAND_HEIGHT_MM,
                       area_mm2: float = cfg.HAND_AREA_MM2) -> bool:
    """True if a connected blob inside the region sits more than `height_mm` above the expected
    surface and covers at least `area_mm2`. Zero depth (no reading) never counts."""
    above = ((depth > 0) & (depth.astype(np.float32) < expected_depth - height_mm) & (region_mask > 0)).astype(np.uint8)
    above = cv2.morphologyEx(above, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    return _big_blob(above, mm2_per_px, area_mm2)


def hand_present_color(current: np.ndarray, reference: np.ndarray, region_mask: np.ndarray, mm2_per_px: float,
                       thresh: int = cfg.HAND_DIFF_THRESH, open_px: int = cfg.HAND_OPEN_PX,
                       area_mm2: float = cfg.HAND_AREA_MM2) -> bool:
    """The backup when no depth plane is calibrated: compare the frame with the reference frame
    taken at the look pose after the robot's last turn. The difference is the largest of the three
    color channels, because on this camera's exposure the board reads mid-gray (about 127) and a
    medium skin tone has nearly the same gray level while its blue channel is far lower. New marker
    lines are thin and vanish under the opening; a hand is a big changed blob."""
    cur = cv2.GaussianBlur(current, (5, 5), 0)
    ref = cv2.GaussianBlur(reference, (5, 5), 0)
    diff = cv2.absdiff(cur, ref).max(axis=2)
    changed = ((diff > thresh) & (region_mask > 0)).astype(np.uint8)
    changed = cv2.morphologyEx(changed, cv2.MORPH_OPEN, np.ones((open_px, open_px), np.uint8))
    return _big_blob(changed, mm2_per_px, area_mm2)


@dataclass(frozen=True)
class DotReading:
    status: str                              # "home" | "moved" | "missing"
    displacement_mm: tuple[float, float]     # where the dot is relative to its recorded spot, camera-board axes


def dock_dots(frame_bgr: np.ndarray, slots: dict, homography: np.ndarray,
              tol_mm: float = cfg.DOT_TOLERANCE_MM, roi_px: int = 45) -> dict[str, DotReading]:
    """Per docked marker: is its colored end plug at the recorded image spot? `slots` comes from
    calibration.json: {"green": {"xy": [x, y], "hsv_lo": [...], "hsv_hi": [...]}}. The displacement
    is measured through the board homography so it is in board axes, ready for the pick correction."""
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    out: dict[str, DotReading] = {}
    for name, slot in slots.items():
        ex, ey = slot["xy"]
        x0, y0 = max(int(ex - roi_px), 0), max(int(ey - roi_px), 0)
        sub = hsv[y0:int(ey + roi_px), x0:int(ex + roi_px)]
        mask = cv2.inRange(sub, np.array(slot["hsv_lo"], np.uint8), np.array(slot["hsv_hi"], np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, _, stats, cents = cv2.connectedComponentsWithStats(mask)
        best = max(range(1, n), key=lambda i: stats[i, cv2.CC_STAT_AREA], default=None)
        if best is None or stats[best, cv2.CC_STAT_AREA] < cfg.DOT_MIN_AREA_PX:
            out[name] = DotReading("missing", (0.0, 0.0))
            continue
        fx, fy = float(cents[best][0]) + x0, float(cents[best][1]) + y0
        (bx, by), (rx, ry) = to_board_mm(homography, [(fx, fy), (float(ex), float(ey))])
        d = (bx - rx, by - ry)
        out[name] = DotReading("home" if math.hypot(*d) <= tol_mm else "moved", d)
    return out


def still(frames: list[np.ndarray], thresh: float = cfg.STILL_THRESH) -> bool:
    """True when every consecutive pair of frames differs by less than `thresh` on average (gray,
    downsampled). Fewer than two frames is not still: there is nothing to compare."""
    if len(frames) < 2:
        return False
    small = [cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (160, 90), interpolation=cv2.INTER_AREA) for f in frames]
    return all(float(np.mean(cv2.absdiff(a, b))) < thresh for a, b in zip(small, small[1:]))
```

- [ ] **Step 5: Add the offline calibration verbs**

In `code/hackathon/duet/calibrate.py`, add these two lines to the usage block in the module docstring (after the `--fit` lines):

```
    python -m duet.calibrate --plane FILE    OFFLINE: fit the board plane for the depth hand check from a saved
                                             depth map (captures/depth.dep from explore.py, taken at the look pose)
    python -m duet.calibrate --dock x0 y0 x1 y1
                                             OFFLINE: record the dock tub's image rectangle for the hand check
```

and add this function above `main`:

```python
def offline(argv: list[str]) -> bool:
    """The verbs that need no camera. Returns True when one ran."""
    cal = load_calibration()
    if "--dock" in argv:
        i = argv.index("--dock")
        x0, y0, x1, y1 = (int(v) for v in argv[i + 1:i + 5])
        cal["dock_region_image"] = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
        save_calibration(cal)
        print(f"dock region saved: x {x0}..{x1}, y {y0}..{y1}")
        return True
    if "--plane" in argv:
        from duet.camera import decode_depth
        path = Path(argv[argv.index("--plane") + 1])
        depth = np.load(path)["depth"] if path.suffix == ".npz" else decode_depth(path.read_bytes())
        quad = np.array(cal["marks_image"], dtype=np.float32)
        center = quad.mean(axis=0)
        padded = [[float(x + 25 * np.sign(x - center[0])), float(y + 25 * np.sign(y - center[1]))] for x, y in quad]
        plane = vision.fit_plane(depth, vision.polygon_mask(depth.shape, [padded]))
        cal.update({"plane": list(plane), "board_region_image": padded, "mm_per_px": vision.mm_per_px(quad)})
        expected = vision.plane_depth(depth.shape, plane)
        inside = (vision.polygon_mask(depth.shape, [padded]) > 0) & (depth > 0)
        resid = np.abs(depth[inside].astype(np.float32) - expected[inside])
        print(f"plane z = {plane[0]:.4f} x + {plane[1]:.4f} y + {plane[2]:.1f}; "
              f"median residual {np.median(resid):.1f} mm, {np.mean(resid < 15) * 100:.0f}% of readings within 15 mm")
        if "dock_region_image" in cal:
            dock = (vision.polygon_mask(depth.shape, [cal["dock_region_image"]]) > 0) & (depth > 0)
            cal["dock_offset_mm"] = float(np.median(expected[dock] - depth[dock].astype(np.float32)))
            print(f"dock surface sits {cal['dock_offset_mm']:.0f} mm above the board plane (hand check reference)")
        save_calibration(cal)
        return True
    return False
```

and make `main` start with:

```python
def main(argv: list[str]) -> None:
    CAPTURES.mkdir(exist_ok=True)
    if offline(argv):
        return
    if "--fit" in argv:
```

(The rest of `main` is unchanged.) Check the offline path with a synthetic depth file:

```bash
python - <<'EOF'
import json, numpy as np
from duet import config as cfg
cal = json.loads(cfg.CALIBRATION_PATH.read_text())
np.savez_compressed("/tmp/fake_depth.npz", depth=np.full((720, 1280), 450, np.uint16))
EOF
cp duet/data/calibration.json /tmp/calibration.backup.json && python -m duet.calibrate --plane /tmp/fake_depth.npz && cp /tmp/calibration.backup.json duet/data/calibration.json && git diff --stat duet/data/calibration.json
```
Expected: a printed flat plane at 450 mm and then `calibration.json` restored (the diff stat prints nothing). The real plane is fitted in the morning from a depth frame taken at the look pose.

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python -m pytest tests/test_camera.py tests/test_readings.py tests/test_vision.py -q`
Expected: all pass. If `test_hand_present_color_on_the_real_look_frame` fails on the lines case, print the biggest blob's area: marker lines 3 px wide must vanish under the 9 px opening; if they survive, the blur is merging them, so raise `HAND_OPEN_PX` to 11 in `config.py` rather than loosening the area.

- [ ] **Step 7: Commit**

```bash
git add duet/camera.py duet/vision.py duet/calibrate.py tests/test_camera.py tests/test_readings.py
git commit -m "feat: depth decode, frame poller, hand and dock-dot readings, offline plane calibration"
```

---

### Task 2: Trigger state machine

**Files:**
- Create: `code/hackathon/duet/trigger.py`
- Test: `code/hackathon/tests/test_trigger.py`

- [ ] **Step 1: Write the failing tests**

`code/hackathon/tests/test_trigger.py`:

```python
from duet.trigger import Event, Reading, Trigger


def r(t, hand=False, still=True, **dots):
    return Reading(t=t, hand=hand, still=still, dots=dots)


def run(trigger, readings):
    return [(x.t, trigger.update(x)) for x in readings]


def test_dock_fires_after_a_marker_leaves_and_returns_and_the_scene_settles():
    tr = Trigger("dock", quiet_s=1.5)
    events = run(tr, [r(0, green="home"), r(1, green="missing", still=False), r(2, green="missing"),
                      r(3, green="home"), r(4, green="home"), r(4.6, green="home")])
    assert [e for _, e in events if e] == [Event("fire")]
    assert events[-1][0] == 4.6


def test_dock_does_not_fire_if_no_marker_ever_left():
    tr = Trigger("dock", quiet_s=1.5)
    assert all(e is None for _, e in run(tr, [r(t, green="home") for t in range(10)]))


def test_dock_hand_or_motion_restarts_the_quiet_timer():
    tr = Trigger("dock", quiet_s=1.5)
    events = run(tr, [r(0, green="missing"), r(1, green="home"), r(2, green="home", hand=True),
                      r(3, green="home"), r(4, green="home"), r(4.4, green="home"), r(4.6, green="home")])
    assert [t for t, e in events if e == Event("fire")] == [4.6]


def test_dock_moved_marker_asks_for_a_reseat_then_fires_once_home():
    tr = Trigger("dock", quiet_s=1.0)
    events = run(tr, [r(0, green="missing"), r(1, green="moved"), r(2, green="moved"), r(3, green="missing"),
                      r(4, green="home"), r(5, green="home"), r(6, green="home")])
    assert [e for _, e in events if e] == [Event("reseat", ("green",)), Event("reseat_ok"), Event("fire")]


def test_dock_with_no_calibrated_dots_never_fires():
    tr = Trigger("dock", quiet_s=0.5)
    assert all(e is None for _, e in run(tr, [r(t) for t in range(6)]))


def test_held_fires_after_activity_then_quiet():
    tr = Trigger("held", quiet_s=2.0)
    events = run(tr, [r(0), r(1, still=False), r(2, hand=True), r(3), r(4), r(5), r(5.5)])
    assert [t for t, e in events if e == Event("fire")] == [5]


def test_held_never_fires_on_an_untouched_board():
    tr = Trigger("held", quiet_s=2.0)
    assert all(e is None for _, e in run(tr, [r(t) for t in range(10)]))


def test_reset_after_fire_requires_new_activity():
    tr = Trigger("held", quiet_s=1.0)
    events = run(tr, [r(0, still=False), r(1), r(2), r(3), r(4), r(5)])
    assert [t for t, e in events if e == Event("fire")] == [2]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_trigger.py -q`
Expected: `ModuleNotFoundError: No module named 'duet.trigger'`

- [ ] **Step 3: Write `trigger.py`**

`code/hackathon/duet/trigger.py`:

```python
"""When does the human's turn end? A pure state machine over readings from `vision`.

Dock rule: at least one docked marker went missing since the last turn; now every marker is home,
the scene is still and no hand is visible, and that has held for STILL_S. A marker that is home but
out of position asks for a reseat instead.

Held rule: something happened since the last turn (motion or a hand); now the scene is still with
no hand, and that has held for HELD_QUIET_S. The session then diffs the board and goes back to
waiting if no new ink is found.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from duet import config as cfg


@dataclass(frozen=True)
class Reading:
    t: float
    hand: bool
    still: bool
    dots: dict[str, str] = field(default_factory=dict)   # slot -> "home" | "moved" | "missing"; empty in held mode


@dataclass(frozen=True)
class Event:
    kind: str                        # "fire" | "reseat" | "reseat_ok"
    slots: tuple[str, ...] = ()


class Trigger:
    def __init__(self, handoff: str, quiet_s: float | None = None):
        if handoff not in ("dock", "held"):
            raise ValueError(f"handoff must be 'dock' or 'held', not {handoff!r}")
        self.handoff = handoff
        self.quiet_s = quiet_s if quiet_s is not None else (cfg.STILL_S if handoff == "dock" else cfg.HELD_QUIET_S)
        self.reset()

    def reset(self) -> None:
        self.armed = False               # something happened since the last turn
        self.quiet_since: float | None = None
        self.reseat = False

    def update(self, r: Reading) -> Event | None:
        settled, event = self._dock(r) if self.handoff == "dock" else self._held(r)
        if event is not None:
            return event
        if not settled:
            self.quiet_since = None
            return None
        if self.quiet_since is None:
            self.quiet_since = r.t
            return None
        if r.t - self.quiet_since >= self.quiet_s:
            self.reset()
            return Event("fire")
        return None

    def _dock(self, r: Reading) -> tuple[bool, Event | None]:
        if any(s == "missing" for s in r.dots.values()):
            self.armed = True
        moved = tuple(sorted(name for name, s in r.dots.items() if s == "moved"))
        if moved:
            self.quiet_since = None
            if self.reseat:
                return False, None
            self.reseat = True
            return False, Event("reseat", moved)
        if self.reseat:
            self.reseat = False
            self.quiet_since = None
            return False, Event("reseat_ok")
        all_home = bool(r.dots) and all(s == "home" for s in r.dots.values())
        return self.armed and all_home and r.still and not r.hand, None

    def _held(self, r: Reading) -> tuple[bool, Event | None]:
        if r.hand or not r.still:
            self.armed = True
        return self.armed and r.still and not r.hand, None
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_trigger.py -q`
Expected: `8 passed`

- [ ] **Step 5: Commit**

```bash
git add duet/trigger.py tests/test_trigger.py
git commit -m "feat: turn trigger state machine for dock and held handoffs"
```

---

### Task 3: Recorder

**Files:**
- Create: `code/hackathon/duet/recorder.py`
- Test: `code/hackathon/tests/test_recorder.py`

The folder layout and `session.json` keys match what `duet/turn.py` writes (`turn-00-start.jpg`, `turn-NN-human.jpg`, `turn-NN-robot.jpg`, `plan-NN.svg`, `session.json` with `id, length, exchanges, turn, history, last_photo, started`; plus `sessions/current.json`), so `python -m duet.turn status` keeps working on sessions the loop records. The recorder adds per-turn details under `turns` and the ffmpeg stitch.

- [ ] **Step 1: Write the failing tests**

`code/hackathon/tests/test_recorder.py`:

```python
import json

import numpy as np

from duet.recorder import Recorder, video_duration_s, video_size


def frame(shade):
    """A portrait board photo, like the warped 704 x 960 boards."""
    return np.full((128, 96, 3), shade, np.uint8)


def raw(shade):
    """A landscape camera frame, like the 1280 x 720 look-pose frames."""
    return np.full((96, 128, 3), shade, np.uint8)


def test_photos_svgs_and_json_land_in_the_session_folder(tmp_path):
    rec = Recorder("abc", root=tmp_path, settings={"length": "short", "exchanges": 3})
    p0 = rec.save_photo(0, "start", frame(240))
    p1 = rec.save_photo(1, "human", frame(200))
    rec.save_svg(1, "<svg/>")
    rec.record_turn(1, sees="A line.", adds="A sun.", source="claude")
    rec.record_turn(1, coverage=0.02)
    rec.set_turn(1)
    rec.write()
    assert p0.name == "turn-00-start.jpg" and p1.name == "turn-01-human.jpg"
    assert rec.latest_photo == p1
    assert (tmp_path / "abc" / "plan-01.svg").read_text() == "<svg/>"
    meta = json.loads((tmp_path / "abc" / "session.json").read_text())
    assert meta["id"] == "abc" and meta["length"] == "short" and meta["exchanges"] == 3
    assert meta["turn"] == 1 and meta["last_photo"] == "turn-01-human.jpg" and meta["started"] == "abc"
    assert meta["history"] == [{"sees": "A line.", "adds": "A sun.", "source": "claude"}]
    assert meta["turns"] == [{"turn": 1, "sees": "A line.", "adds": "A sun.", "source": "claude", "coverage": 0.02}]
    assert json.loads((tmp_path / "current.json").read_text())["id"] == "abc"


def test_stitch_makes_a_video_one_second_per_turn_with_the_last_held(tmp_path):
    rec = Recorder("vid", root=tmp_path)
    for i, shade in enumerate((240, 200, 160)):
        rec.save_photo(i, "robot", frame(shade))
    out = rec.stitch()
    assert out is not None and out.exists() and out.stat().st_size > 1000
    assert abs(video_duration_s(out) - 4.0) < 0.35     # 1 + 1 + 2 s hold on the last frame


def test_stitch_with_no_photos_is_none(tmp_path):
    assert Recorder("empty", root=tmp_path).stitch() is None


def test_camera_frames_are_saved_beside_the_photos_and_make_a_landscape_video(tmp_path):
    rec = Recorder("fr", root=tmp_path)
    for i, shade in enumerate((240, 200, 160)):
        rec.save_photo(i, "robot", frame(shade), frame=raw(shade))
    assert (tmp_path / "fr" / "turn-01-robot-frame.jpg").exists()
    assert rec.latest_frame.name == "turn-02-robot-frame.jpg" and rec.latest_photo.name == "turn-02-robot.jpg"
    out = rec.stitch()
    assert video_size(out) == (128, 96)                    # the landscape frames, not the portrait photos
    assert abs(video_duration_s(out) - 4.0) < 0.35
    rec.save_photo(3, "final", frame(120))                  # a turn without a frame: the stitch falls back to photos
    assert rec.latest_frame is None and video_size(rec.stitch()) == (96, 128)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_recorder.py -q`
Expected: `ModuleNotFoundError: No module named 'duet.recorder'`

- [ ] **Step 3: Write `recorder.py`**

`code/hackathon/duet/recorder.py`:

```python
"""Session memory in the layout `duet.turn` already uses: a folder per session with a photo per
turn, the plan SVGs, session.json (plus sessions/current.json), and the ffmpeg stitch of the
photos into session.mp4 when the piece is done."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from duet import config as cfg

FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"


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
        cv2.imwrite(str(path), bgr, [cv2.IMWRITE_JPEG_QUALITY, 90])
        self.photos.append(path)
        self.meta["last_photo"] = path.name
        self.latest_frame = None
        if frame is not None:
            fpath = self.dir / f"turn-{turn:02d}-{who}-frame.jpg"
            cv2.imwrite(str(fpath), frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
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
        if "sees" in entry and "adds" in entry:
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
        (self.root / "current.json").write_text(text)
        return path

    @property
    def latest_photo(self) -> Path | None:
        return self.photos[-1] if self.photos else None

    def stitch(self, per_frame_s: float = 1.0, hold_last_s: float = 2.0) -> Path | None:
        """One frame per turn, the last one held. Uses the landscape camera frames when every turn
        has one, else the warped photos. The concat demuxer only honors the final duration when the
        last file is listed once more after it."""
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
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p", "-r", "10",
                        "-c:v", "libx264", "-movflags", "+faststart", str(out)], check=True)
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_recorder.py -q`
Expected: `4 passed`. If the duration is off by a whole second, ffmpeg 9's concat handling changed: try dropping the repeated last-file line and re-measure; keep whichever gives 4 s.

- [ ] **Step 5: Commit**

```bash
git add duet/recorder.py tests/test_recorder.py
git commit -m "feat: session recorder in turn.py's layout with an ffmpeg stitch"
```

---

### Task 4: Fakes and the session loop

**Files:**
- Modify: `code/hackathon/duet/claude_turn.py` (one field on `Proposal`, one sentence in the prompt; nothing else)
- Create: `code/hackathon/duet/fakes.py`
- Create: `code/hackathon/duet/session.py`
- Test: `code/hackathon/tests/test_session.py`

- [ ] **Step 0: Give the proposal a `quip`**

The page's visitor view shows Claude's few words in a speech bubble; the full `sees`/`adds` stay on the operator view. In `code/hackathon/duet/claude_turn.py` change the import `from pydantic import BaseModel` to `from pydantic import BaseModel, Field`, and add one field to `Proposal` after `adds`:

```python
    quip: str = Field(description="a few warm, encouraging words to the person, under eight words, no coordinates")
```

and append this sentence to the `SYSTEM` prompt's paragraph that begins "Your job each turn" (right after "then give the strokes as data."):

```
Also give a quip: a few warm, encouraging words to the person, under eight words, no coordinates.
```

`python -m pytest tests/test_planner_haring.py -q` must still pass (it does not build a Proposal). The `turn.py` terminal loop ignores the field. `Proposal(...)` constructions in the fakes below include `quip`.

- [ ] **Step 1: Write the failing tests**

`code/hackathon/tests/test_session.py`:

```python
import asyncio
import json

import pytest

from duet import config as cfg
from duet.fakes import FakeBrain, FakeController, FakeFrames
from duet.recorder import Recorder
from duet.session import EventBus, HandGuard, Session, Settings


def drain(q):
    out = []
    while not q.empty():
        out.append(q.get_nowait())
    return out


def build(tmp_path, look_frame, exchange_start, calibration, **settings):
    frames = FakeFrames(look_frame, calibration)
    frames.show_board(exchange_start)
    ctl = FakeController(frames)
    st = Settings(**settings)
    rec = Recorder("t", root=tmp_path, settings=st.record())
    bus = EventBus()
    q = bus.subscribe()
    s = Session(st, frames, ctl, FakeBrain(), rec, bus, calibration, guard=HandGuard(frames, calibration), poll_s=0.01)
    return s, frames, ctl, rec, q


async def until_state(session, state, timeout=10):
    """Wait until the session is in `state` now (only for states that yield while in them)."""
    async with asyncio.timeout(timeout):
        while session.state != state:
            await asyncio.sleep(0.01)


async def until_seen(session, state, count=1, timeout=10):
    """Wait until `state` has been entered `count` times (capture runs the fake camera and vision without yielding)."""
    async with asyncio.timeout(timeout):
        while session.states_seen.count(state) < count:
            await asyncio.sleep(0.01)


async def cancel(task):
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


def test_one_full_exchange_on_the_real_day_1_boards(tmp_path, look_frame, exchange_start, exchange_human, exchange_robot, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held")
        frames.robot_boards = [exchange_robot]          # what the fake arm "draws": the real robot photo
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        frames.show_board(exchange_human)               # the visitor drew the real creature
        s.pass_turn()
        await asyncio.wait_for(task, 60)
        return s, ctl, rec, drain(q)
    s, ctl, rec, events = asyncio.run(scenario())
    assert s.states_seen == ["look", "human_turn", "capture", "interpret", "plan", "robot_draw", "look", "finish", "finished"]
    kinds = [c[0] for c in ctl.calls]
    assert kinds[0] == "go_look" and kinds.count("draw") == 2       # the plan, then the signature
    for name in ("turn-00-start.jpg", "turn-00-start-frame.jpg", "turn-01-human.jpg", "turn-01-human-frame.jpg",
                 "turn-01-robot.jpg", "turn-01-final.jpg", "turn-01-final-frame.jpg", "plan-01.svg", "session.mp4"):
        assert (rec.dir / name).exists(), name
    shot = next(e for e in events if e["type"] == "shot")
    assert shot["who"] == "start" and shot["frame_url"].endswith("turn-00-start-frame.jpg")
    meta = json.loads((rec.dir / "session.json").read_text())
    assert meta["turn"] == 1 and meta["exchanges"] == 1 and meta["history"][0]["source"] == "claude"
    assert meta["history"][0]["sees"].startswith("A creature")
    types = [e["type"] for e in events]
    for t in ("state", "human", "interpretation", "plan", "progress", "shot", "video"):
        assert t in types, t
    interp = next(e for e in events if e["type"] == "interpretation")
    assert interp["quip"] == "What a creature! Here comes the sun." and interp["source"] == "claude"
    human = next(e for e in events if e["type"] == "human")
    assert 10 <= len(human["new"]) <= 16
    xs = [x for pl in human["new"] for x, _ in pl]
    assert 30 <= min(xs) <= 45 and 130 <= max(xs) <= 145              # robot-board mm (cam_to_robot applied)
    plan = next(e for e in events if e["type"] == "plan")
    assert plan["polylines"] and plan["color"] == cfg.COLOR_HEX["green"]
    assert ctl.drawn[0] == plan["polylines"][:len(ctl.drawn[0])]


def test_no_new_ink_returns_to_the_human_turn(tmp_path, look_frame, exchange_start, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held")
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        s.pass_turn()                                   # nothing was drawn
        await until_seen(s, "human_turn", count=2)
        await cancel(task)
        return s, ctl, drain(q)
    s, ctl, events = asyncio.run(scenario())
    assert s.states_seen[-3:] == ["human_turn", "capture", "human_turn"]
    assert not any(c[0] == "draw" for c in ctl.calls)
    assert any(e["type"] == "human" and e.get("found") is False for e in events)


def test_held_trigger_fires_from_the_frames_alone(tmp_path, look_frame, exchange_start, exchange_human, calibration, monkeypatch):
    monkeypatch.setattr(cfg, "HELD_QUIET_S", 0.3)
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held")
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        frames.jitter(0.2)                              # a hand moving over the board
        await asyncio.sleep(0.1)
        frames.show_board(exchange_human)
        await until_seen(s, "capture", timeout=5)       # fires 0.3 s after the scene settles, no pass needed
        await cancel(task)
        return s
    s = asyncio.run(scenario())
    assert "capture" in s.states_seen


def test_pause_and_resume_recover_the_arm(tmp_path, look_frame, exchange_start, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held")
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        await s.pause()
        await until_state(s, "paused")
        s.resume()
        await until_state(s, "human_turn")
        await cancel(task)
        return s, ctl
    s, ctl = asyncio.run(scenario())
    kinds = [c[0] for c in ctl.calls]
    assert "stop" in kinds and "recover" in kinds and kinds.index("stop") < kinds.index("recover")


def test_a_fault_in_the_brain_pauses_with_the_error_on_the_bus(tmp_path, look_frame, exchange_start, exchange_human, calibration):
    class BrokenBrain:
        async def propose(self, board, human_cam, history, length, exchange, total):
            raise RuntimeError("no network")

    async def scenario():
        frames = FakeFrames(look_frame, calibration)
        frames.show_board(exchange_start)
        bus = EventBus()
        q = bus.subscribe()
        st = Settings(exchanges=1, handoff="held")
        s = Session(st, frames, FakeController(frames), BrokenBrain(), Recorder("f", root=tmp_path, settings=st.record()),
                    bus, calibration, poll_s=0.01)
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        frames.show_board(exchange_human)
        s.pass_turn()
        await until_state(s, "paused")
        await cancel(task)
        return s, drain(q)
    s, events = asyncio.run(scenario())
    assert "no network" in s.last_error
    assert any(e["type"] == "error" and "no network" in e["message"] for e in events)


def test_settings_are_validated_at_the_boundary(tmp_path, look_frame, exchange_start, calibration):
    s, *_ = build(tmp_path, look_frame, exchange_start, calibration)
    with pytest.raises(ValueError):
        s.update_settings(length="huge")
    with pytest.raises(ValueError):
        s.update_settings(exchanges=21)
    assert s.update_settings(length="medium", exchanges=4).exchanges == 4
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_session.py -q`
Expected: `ModuleNotFoundError: No module named 'duet.fakes'`

- [ ] **Step 3: Write `fakes.py`**

`code/hackathon/duet/fakes.py`:

```python
"""Stand-ins for the camera, the arm, and Claude, shared by the tests and `run.py --fake`.

The fake camera holds a real look-pose frame and composites a board image into it through the
frame's own corner marks, so corner detection, the warp, the diff, and the trace all run for real
on real photos. `show_board` swaps in a board photo (a visitor's turn); `mark`/`add_ink` draw on
the current board; `jitter` makes the scene not still for a while."""
from __future__ import annotations

import asyncio
from time import monotonic

import cv2
import numpy as np

from duet import config as cfg
from duet import vision
from duet.camera import Frame
from duet.claude_turn import Proposal, Pt, Stroke, TurnResult
from duet.controller import DrawResult
from duet.strokes import Polyline, length

INK_BGR = {"human": (30, 30, 170), "green": (40, 140, 40), "red": (30, 30, 170), "blue": (200, 60, 40)}


class FakeFrames:
    def __init__(self, frame_bgr: np.ndarray, calibration: dict):
        self.frame = frame_bgr.copy()
        quad = vision.find_corner_marks(frame_bgr, expected=calibration["marks_image"])
        board_quad = vision.board_quad(quad, calibration["board_tl_index"])
        w, h = vision.BOARD_PX
        self.m = vision.board_homography(board_quad)
        self.m_inv = np.linalg.inv(self.m)
        inner = np.zeros((h, w), np.uint8)
        b = int(12 * vision.PX_PER_MM)                  # keep the frame's own corner marks and rim
        inner[b:h - b, b:w - b] = 255
        self.mask = cv2.warpPerspective(inner, self.m_inv, (frame_bgr.shape[1], frame_bgr.shape[0])) > 0
        self.board = vision.warp_to_board(frame_bgr, board_quad)
        self.robot_boards: list[np.ndarray] = []      # replay: what the board looks like after each robot turn
        self.depth = None
        self.jitter_until = 0.0
        self.n = 0
        self._compose()

    def _compose(self) -> None:
        back = cv2.warpPerspective(self.board, self.m_inv, (self.frame.shape[1], self.frame.shape[0]))
        img = self.frame.copy()
        img[self.mask] = back[self.mask]
        self.image = img

    def show_board(self, board_bgr: np.ndarray) -> None:
        self.board = board_bgr.copy()
        self._compose()

    def draw(self, polylines: list[Polyline], bgr: tuple, thickness: int) -> None:
        for pl in polylines:
            if len(pl) >= 2:
                pts = np.array([[x * vision.PX_PER_MM, y * vision.PX_PER_MM] for x, y in pl], np.int32)
                cv2.polylines(self.board, [pts], False, bgr, thickness, cv2.LINE_AA)
        self._compose()

    def mark(self, polylines: list[Polyline]) -> None:
        """The visitor draws, in red marker like the day-1 boards."""
        self.draw(polylines, INK_BGR["human"], 3)

    def add_ink(self, polylines: list[Polyline], color: str) -> None:
        """The robot drew these strokes (or, in replay, show the next real robot photo)."""
        if self.robot_boards:
            self.show_board(self.robot_boards.pop(0))
        else:
            self.draw(polylines, INK_BGR.get(color, (40, 40, 40)), 2)

    def jitter(self, seconds: float) -> None:
        self.jitter_until = monotonic() + seconds

    def _frame(self) -> Frame:
        img = self.image
        if monotonic() < self.jitter_until:
            self.n += 1
            img = cv2.add(self.image, np.full_like(self.image, 12 if self.n % 2 else 0))
        return Frame(img, self.depth, monotonic())

    def latest(self) -> Frame:
        return self._frame()

    def recent(self, seconds: float) -> list[Frame]:
        return [self._frame(), self._frame()]

    async def capture_median(self, n: int = 5, delay_s: float = 0.0) -> np.ndarray:
        return self.image.copy()


class FakeController:
    def __init__(self, frames: FakeFrames | None = None, stroke_s: float = 0.02):
        self.frames = frames
        self.stroke_s = stroke_s
        self.calls: list[tuple] = []
        self.drawn: list[list[Polyline]] = []
        self.events: asyncio.Queue = asyncio.Queue()
        self.hand_check = None
        self.held_mode = cfg.HELD_MODE
        self.last_error: str | None = None
        self.needs_lift = False

    async def go_look(self) -> None:
        self.calls.append(("go_look",))

    async def pick_marker(self, slot: str, displacement_mm=(0.0, 0.0)) -> None:
        self.calls.append(("pick", slot, displacement_mm))

    async def return_marker(self, slot: str) -> None:
        self.calls.append(("return", slot))

    async def draw(self, polylines: list[Polyline], budget_mm: float, budget_s: float, z_offset_mm: float = 0.0) -> DrawResult:
        self.calls.append(("draw", len(polylines)))
        t0, drawn, done = monotonic(), 0.0, 0
        for i, pl in enumerate(polylines):
            if drawn >= budget_mm or monotonic() - t0 >= budget_s:
                break
            await asyncio.sleep(self.stroke_s)
            drawn += length(pl)
            done += 1
            await self.events.put({"type": "progress", "stroke": i, "drawn_mm": drawn})
        self.drawn.append([list(pl) for pl in polylines[:done]])
        if self.frames is not None:
            self.frames.add_ink(polylines[:done], "green")
        return DrawResult(done, drawn, monotonic() - t0)

    async def stop(self) -> None:
        self.calls.append(("stop",))

    async def recover(self) -> None:
        self.calls.append(("recover",))

    async def clear_error(self) -> None:
        self.calls.append(("clear_error",))

    async def status(self) -> dict:
        return {"fake": True, "calls": len(self.calls)}


def _stroke(**fields) -> Stroke:
    base = dict(kind="polyline", points=[], cx=0.0, cy=0.0, r=0.0, start_deg=0.0, end_deg=0.0, attached=False)
    base.update(fields)
    return Stroke(**base)


class FakeBrain:
    """Canned proposals that read the mark's position: a sun above it, then a ground line under it.
    Same call shape as the real brain: propose(board, human_cam, history, length, exchange, total)."""

    def __init__(self, latency_s: float = 0.02):
        self.latency_s = latency_s
        self.n = 0

    async def propose(self, board, human_cam, history, length, exchange, total) -> TurnResult:
        await asyncio.sleep(self.latency_s)
        self.n += 1
        xs = [x for pl in human_cam for x, _ in pl] or [cfg.BOARD_W_MM / 2]
        ys = [y for pl in human_cam for _, y in pl] or [cfg.BOARD_H_MM / 2]
        cx, top, bottom = sum(xs) / len(xs), min(ys), max(ys)
        lo, hi_x, hi_y = cfg.INSET_MM + 10, cfg.BOARD_W_MM - cfg.INSET_MM - 10, cfg.BOARD_H_MM - cfg.INSET_MM - 10
        if self.n % 2:
            p = Proposal(sees="A creature sprawls across the board, looking up.", adds="A sun above it, to give the scene a sky.",
                         quip="What a creature! Here comes the sun.", color="green",
                         strokes=[_stroke(kind="circle", cx=min(max(cx, lo + 14), hi_x - 14), cy=max(lo + 14, top - 32), r=12.0)])
        else:
            y = min(hi_y, bottom + 25)
            p = Proposal(sees="The scene has a sun now.", adds="A ground line under the creature.",
                         quip="Let's give it ground to stand on.", color="green",
                         strokes=[_stroke(kind="polyline", points=[Pt(x=lo, y=y), Pt(x=hi_x, y=y)])])
        return TurnResult(p, "claude", self.latency_s, None)
```

- [ ] **Step 4: Write `session.py`**

`code/hackathon/duet/session.py`:

```python
"""The turn loop: one asyncio task, one method per state, the only module that calls the others in
sequence. It replaces the Enter prompts of `duet.turn` with the trigger, and every dependency comes
in through the constructor so tests and `run.py --fake` can swap the camera, the arm, and Claude."""
from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass, replace

import numpy as np

from duet import config as cfg
from duet import planner, svg, vision
from duet.claude_turn import TurnResult
from duet.controller import Blocked
from duet.strokes import Polyline, length
from duet.styles import haring
from duet.trigger import Reading, Trigger
from duet.turn import all_ink, map_strokes

ARTISTS = ("haring",)
RETRY_AFTER_FAULT = {"look": "look", "human_turn": "human_turn", "capture": "human_turn", "interpret": "human_turn",
                     "plan": "human_turn", "robot_draw": "look", "finish": "look"}
HAND_WAIT_S = 30
SETTLE_AFTER_LOOK_S = 0.8      # the camera image settles after the arm stops, as in duet.turn
FALLBACK_QUIP = "Lost my words. Drawing anyway!"   # the speech bubble when Claude did not answer


@dataclass(frozen=True)
class Settings:
    artist: str = cfg.ARTIST
    length: str = "short"
    exchanges: int = 5
    mode: str = "duet"
    handoff: str = "held" if cfg.HELD_MODE else "dock"

    def check(self) -> "Settings":
        if self.artist not in ARTISTS:
            raise ValueError(f"artist must be one of {ARTISTS}")
        if self.length not in cfg.BUDGET_MM:
            raise ValueError(f"length must be one of {tuple(cfg.BUDGET_MM)}")
        if not isinstance(self.exchanges, int) or not 1 <= self.exchanges <= 20:
            raise ValueError("exchanges must be a whole number from 1 to 20")
        if self.mode != "duet":
            raise ValueError("only duet mode exists yet")
        if self.handoff not in ("held", "dock"):
            raise ValueError("handoff must be 'held' or 'dock'")
        return self

    def record(self) -> dict:
        """The keys duet.turn keeps in session.json."""
        return {"length": self.length, "exchanges": self.exchanges}


class EventBus:
    """Fan-out of session events to any number of subscribers (the page's sockets, tests, the log)."""
    SNAPSHOT = ("calib", "state", "dock", "human", "interpretation", "plan", "progress", "shot", "video", "error")

    def __init__(self):
        self.subs: list[asyncio.Queue] = []
        self.last: dict[str, dict] = {}

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self.subs.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        if q in self.subs:
            self.subs.remove(q)

    def emit(self, type: str, **data) -> dict:
        msg = {"type": type, **data}
        self.last[type] = msg
        for q in list(self.subs):
            q.put_nowait(msg)
        return msg

    def snapshot(self) -> list[dict]:
        return [self.last[k] for k in self.SNAPSHOT if k in self.last]


class HandGuard:
    """The controller's hand check. The camera rides the wrist, so a reading is only valid at the
    look pose; the session flips `at_look` as the arm leaves and returns. With a calibrated depth
    plane the check is depth-based; otherwise it compares the frame with the reference frame the
    session took at the look pose after the robot's last turn. No reading at all counts as a hand."""

    def __init__(self, frames, calibration: dict):
        self.frames = frames
        self.cal = calibration
        self.at_look = False
        self.reference: np.ndarray | None = None
        self.depth_ready = all(k in calibration for k in ("plane", "board_region_image", "mm_per_px"))
        self._region = None
        self._expected = None
        self._mm2 = None

    @property
    def mode(self) -> str:
        return "depth" if self.depth_ready else "color"

    def _prepare(self, shape_hw) -> None:
        if self._region is not None:
            return
        quad = np.array(self.cal["marks_image"], np.float32)
        polygons = [self.cal.get("board_region_image") or quad.tolist()]
        if self.cal.get("dock_region_image"):
            polygons.append(self.cal["dock_region_image"])
        self._region = vision.polygon_mask(shape_hw, polygons)
        self._mm2 = float(self.cal.get("mm_per_px") or vision.mm_per_px(quad)) ** 2
        if self.depth_ready:
            offsets = [(self.cal["dock_region_image"], self.cal.get("dock_offset_mm", 0.0))] if self.cal.get("dock_region_image") else []
            self._expected = vision.reference_depth(shape_hw, tuple(self.cal["plane"]), offsets)

    def reading(self, frame) -> bool | None:
        """True or False from a look-pose frame; None when no reading can be made."""
        if frame is None:
            return None
        self._prepare(frame.color.shape[:2])
        if self.depth_ready and frame.depth is not None:
            return vision.hand_present_depth(frame.depth, self._region, self._expected, self._mm2)
        if self.reference is None:
            return None
        return vision.hand_present_color(frame.color, self.reference, self._region, self._mm2)

    async def __call__(self) -> bool:
        if not self.at_look:
            return False
        r = self.reading(self.frames.latest())
        return True if r is None else r


class Session:
    def __init__(self, settings: Settings, frames, ctl, brain, rec, bus: EventBus, calibration: dict,
                 guard: HandGuard | None = None, poll_s: float = 0.2):
        self.settings = settings.check()
        self.frames, self.ctl, self.brain, self.rec, self.bus, self.cal = frames, ctl, brain, rec, bus, calibration
        self.guard = guard
        self.poll_s = poll_s
        if guard is not None:
            ctl.hand_check = guard
        self.state = "idle"
        self.states_seen: list[str] = []
        self.turn = 0                       # completed exchanges
        self.at_look = False
        self.previous_photo: np.ndarray | None = None
        self.coverage = 0.0
        self.human_ink: list[Polyline] = []      # robot-board mm, all of the visitor's strokes so far
        self.robot_ink: list[Polyline] = []
        self.human_new_cam: list[Polyline] = []  # this turn's strokes in camera-board mm (what Claude reads)
        self.human_new: list[Polyline] = []      # the same in robot-board mm
        self.history: list[dict] = []
        self.plan: list[Polyline] = []
        self.color = cfg.DOCK_SLOTS[0]
        self.result: TurnResult | None = None
        self.last_error: str | None = None
        self.dock_status: dict[str, str] = {}
        self.dot_displacement: dict[str, tuple[float, float]] = {}
        self._running = asyncio.Event()
        self._running.set()
        self._pass = asyncio.Event()
        self._resume_to = "human_turn"
        self._homography: np.ndarray | None = None

    # ---- controls, called from the page ------------------------------------------------------
    def update_settings(self, **changes) -> Settings:
        self.settings = replace(self.settings, **changes).check()
        self.rec.update(**self.settings.record())
        self.emit_state()
        return self.settings

    async def pause(self) -> None:
        self._running.clear()
        await self.ctl.stop()

    def resume(self) -> None:
        self._running.set()

    def pass_turn(self) -> None:
        self._pass.set()

    async def clear_error(self) -> None:
        await self.ctl.clear_error()
        self.last_error = None
        self.emit_state()

    # ---- events --------------------------------------------------------------------------------
    def emit_state(self) -> None:
        guard = "off" if self.guard is None else f"{self.guard.mode} at the look pose"
        self.bus.emit("state", state=self.state, turn=self.turn, coverage=round(self.coverage, 3),
                      error=self.last_error, at_look=self.at_look, hand_guard=guard, session=self.rec.id,
                      **asdict(self.settings))

    def _set(self, state: str) -> None:
        self.state = state
        self.states_seen.append(state)
        self.emit_state()

    def _emit_shot(self, who: str) -> None:
        """`who` is "start", "human", "robot" or "final", so the page can label thumbnails without parsing
        the URL. `frame_url` is the raw landscape camera frame of the same capture, when one was saved."""
        p = self.rec.latest_photo
        if p is not None:
            f = self.rec.latest_frame
            self.bus.emit("shot", url=f"/sessions/{self.rec.id}/{p.name}", turn=self.turn, who=who,
                          frame_url=f"/sessions/{self.rec.id}/{f.name}" if f is not None else None)

    def _set_look(self, value: bool) -> None:
        self.at_look = value
        if self.guard is not None:
            self.guard.at_look = value

    # ---- the loop ------------------------------------------------------------------------------
    async def run(self) -> None:
        try:
            self._set("look")
            await self.ctl.go_look()
            self._set_look(True)
            self.previous_photo, frame = await self._capture_board()
            self.rec.save_photo(0, "start", self.previous_photo, frame)
            self._emit_shot("start")
            self._set("human_turn")
            while self.state != "finished":
                if not self._running.is_set():
                    if self.state != "paused":
                        self._resume_to = RETRY_AFTER_FAULT.get(self.state, "human_turn")
                        self._set("paused")
                    await self._running.wait()
                    try:
                        await self.ctl.recover()
                    except Exception as exc:
                        self.last_error = f"recover failed: {type(exc).__name__}: {exc}"
                        self.bus.emit("error", message=self.last_error)
                        self._running.clear()
                        continue
                    self.last_error = None
                    self._set(self._resume_to)
                    continue
                try:
                    nxt = await getattr(self, f"_state_{self.state}")()
                except Exception as exc:
                    self.last_error = f"{type(exc).__name__}: {exc}"
                    self.bus.emit("error", message=self.last_error)
                    self._running.clear()
                    continue
                self._set(nxt)
        finally:
            self.rec.write()

    def _board_homography(self) -> np.ndarray:
        if self._homography is None:
            quad = vision.board_quad(np.array(self.cal["marks_image"], np.float32), self.cal["board_tl_index"])
            self._homography = vision.board_homography(quad)
        return self._homography

    def _reading(self, frame) -> Reading:
        colors = [f.color for f in self.frames.recent(cfg.STILL_WINDOW_S)]
        hand = self.guard.reading(frame) if self.guard is not None else None
        dots: dict[str, str] = {}
        if self.settings.handoff == "dock" and self.cal.get("dots"):
            readings = vision.dock_dots(frame.color, self.cal["dots"], self._board_homography())
            dots = {k: v.status for k, v in readings.items()}
            self.dot_displacement = {k: v.displacement_mm for k, v in readings.items()}
            if dots != self.dock_status:
                self.dock_status = dots
                self.bus.emit("dock", slots=dots, reseat=[])
        return Reading(t=frame.t, hand=bool(hand), still=vision.still(colors), dots=dots)

    async def _state_human_turn(self) -> str:
        trig = Trigger(self.settings.handoff)
        self._pass.clear()
        while True:
            if not self._running.is_set():
                return "human_turn"
            if self._pass.is_set():
                self._pass.clear()
                return "capture"
            await asyncio.sleep(self.poll_s)
            frame = self.frames.latest()
            if frame is None:
                continue
            event = trig.update(self._reading(frame))
            if event is None:
                continue
            if event.kind == "fire":
                return "capture"
            self.bus.emit("dock", slots=self.dock_status, reseat=list(event.slots) if event.kind == "reseat" else [])

    async def _capture_board(self) -> tuple[np.ndarray, np.ndarray]:
        """A median capture at the look pose: the warped board and the raw frame it came from. Also
        refreshes the hand guard's reference frame, since the arm is at the look pose and nobody is drawing."""
        await asyncio.sleep(SETTLE_AFTER_LOOK_S if self.poll_s >= 0.1 else 0.0)
        frame = await self.frames.capture_median()
        quad = vision.find_corner_marks(frame, expected=self.cal["marks_image"])
        drift = max(float(np.hypot(*(np.asarray(q) - np.asarray(e)))) for q, e in zip(quad, self.cal["marks_image"]))
        if drift > 40:
            self.bus.emit("error", message=f"board shifted {drift * self._mm_per_px():.0f} mm since calibration; re-run calibrate")
        if self.guard is not None:
            self.guard.reference = frame
        return vision.warp_to_board(frame, vision.board_quad(quad, self.cal["board_tl_index"])), frame

    def _mm_per_px(self) -> float:
        return float(self.cal.get("mm_per_px") or vision.mm_per_px(np.array(self.cal["marks_image"], np.float32)))

    async def _state_capture(self) -> str:
        photo, frame = await self._capture_board()
        mask, coverage = vision.new_ink(photo, self.previous_photo)
        new_cam = vision.trace(mask)
        if not new_cam:
            self.bus.emit("human", polylines=self.human_ink, new=[], found=False)
            return "human_turn"
        self.human_new_cam = new_cam
        self.human_new = vision.cam_to_robot(new_cam, self.cal)
        self.human_ink = self.human_ink + self.human_new
        self.coverage = coverage
        self.previous_photo = photo
        self.rec.save_photo(self.turn + 1, "human", photo, frame)
        self._emit_shot("human")
        self.bus.emit("human", polylines=self.human_ink, new=self.human_new, found=True)
        return "interpret"

    async def _state_interpret(self) -> str:
        self.result = await self.brain.propose(self.previous_photo, self.human_new_cam, self.history,
                                               self.settings.length, self.turn + 1, self.settings.exchanges)
        p = self.result.proposal
        self.bus.emit("interpretation", sees=p.sees if p else "", adds=p.adds if p else "",
                      quip=(getattr(p, "quip", "") or FALLBACK_QUIP) if p else FALLBACK_QUIP,
                      source=self.result.source, latency_s=round(self.result.latency_s, 2), error=self.result.error)
        return "plan"

    async def _state_plan(self) -> str:
        budget = cfg.BUDGET_MM[self.settings.length]
        ink = all_ink(self.previous_photo, self.cal)
        r = self.result
        if r is not None and r.proposal is not None:
            strokes = map_strokes([s.model_dump() for s in r.proposal.strokes], self.cal)
            styled, self.color = haring.style(planner.validate(strokes, ink, budget),
                                              energy=1.0 if self.settings.length == "long" else 0.5)
            sees, adds, source = r.proposal.sees, r.proposal.adds, r.source
        else:
            styled, self.color = haring.fallback(self.human_new)
            sees, adds, source = "(fallback)", "outline and ticks around your mark", "fallback"
        self.plan = planner.finalize(styled, ink, budget)
        self.history = self.history + [{"sees": sees, "adds": adds, "source": source}]
        turn = self.turn + 1
        self.rec.save_svg(turn, svg.render(ink, self.robot_ink, self.plan, self.color))
        self.rec.record_turn(turn, sees=sees, adds=adds, source=source, latency_s=round(r.latency_s, 2) if r else None,
                             error=r.error if r else None, color=self.color,
                             planned_mm=round(sum(length(pl) for pl in self.plan)))
        self.bus.emit("plan", polylines=self.plan, color=cfg.COLOR_HEX.get(self.color, "#222222"), budget_mm=budget)
        return "robot_draw"

    async def _wait_hands_clear(self) -> None:
        """Right before the arm leaves the look pose: wait for the hand to go, then mark the guard
        blind until the next go_look (the wrist camera no longer sees the board it was checked against)."""
        if self.guard is None:
            return
        for _ in range(HAND_WAIT_S):
            if not await self.guard():
                break
            self.bus.emit("error", message="hand over the board or dock: waiting before the arm moves")
            await asyncio.sleep(1.0)
        else:
            raise Blocked("hand over the board or dock for 30 s")
        self._set_look(False)

    async def _forward_progress(self, task: asyncio.Task) -> None:
        while not task.done():
            try:
                ev = await asyncio.wait_for(self.ctl.events.get(), 0.1)
            except asyncio.TimeoutError:
                continue
            self.bus.emit("progress", stroke=ev["stroke"], drawn_mm=round(ev["drawn_mm"]))
        while not self.ctl.events.empty():
            ev = self.ctl.events.get_nowait()
            self.bus.emit("progress", stroke=ev["stroke"], drawn_mm=round(ev["drawn_mm"]))

    async def _draw(self, polylines: list[Polyline], budget_mm: float, budget_s: float):
        await self._wait_hands_clear()
        await self.ctl.pick_marker(self.color, self.dot_displacement.get(self.color, (0.0, 0.0)))
        task = asyncio.create_task(self.ctl.draw(polylines, budget_mm, budget_s))
        await self._forward_progress(task)
        result = await task
        await self.ctl.return_marker(self.color)
        return result

    async def _state_robot_draw(self) -> str:
        if not self.plan:
            return "look"
        result = await self._draw(self.plan, cfg.BUDGET_MM[self.settings.length], cfg.BUDGET_S[self.settings.length])
        self.robot_ink = self.robot_ink + [list(pl) for pl in self.plan[:result.strokes_done]]
        if result.blocked:
            self.bus.emit("error", message="a hand was seen between strokes; the turn ended early")
        return "look"

    async def _state_look(self) -> str:
        await self.ctl.go_look()
        self._set_look(True)
        self.turn += 1
        photo, frame = await self._capture_board()
        _, self.coverage = vision.new_ink(photo, self.previous_photo)
        self.previous_photo = photo
        self.rec.save_photo(self.turn, "robot", photo, frame)
        self._emit_shot("robot")
        self.rec.record_turn(self.turn, coverage=round(self.coverage, 3))
        self.rec.set_turn(self.turn)
        self.rec.write()
        if self.turn >= self.settings.exchanges or self.coverage >= cfg.COVERAGE_END:
            return "finish"
        return "human_turn"

    async def _state_finish(self) -> str:
        ox, oy = cfg.BOARD_W_MM - cfg.INSET_MM - 12, cfg.BOARD_H_MM - cfg.INSET_MM - 12
        signature = [[(ox + x, oy + y) for x, y in pl] for pl in cfg.SIGNATURE_MM]
        self.bus.emit("plan", polylines=signature, color=cfg.COLOR_HEX.get(self.color, "#222222"), budget_mm=100)
        await self._draw(signature, 100.0, 20.0)
        self.robot_ink = self.robot_ink + signature
        await self.ctl.go_look()
        self._set_look(True)
        photo, frame = await self._capture_board()
        self.previous_photo = photo
        self.rec.save_photo(self.turn, "final", photo, frame)
        self._emit_shot("final")
        self.rec.write()
        video = await asyncio.to_thread(self.rec.stitch)
        self.bus.emit("video", url=f"/sessions/{self.rec.id}/session.mp4", path=str(video))
        return "finished"
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_session.py -q`
Expected: `6 passed`. The full-exchange test runs the real trace and ffmpeg and takes several seconds. If the traced x-range assertion misses by a couple of millimeters, print `human["new"]` and adjust the bounds; large offsets mean `FakeFrames._compose` or the `cam_to_robot` step is wrong, not the bounds.

- [ ] **Step 6: Commit**

```bash
git add duet/fakes.py duet/session.py tests/test_session.py
git commit -m "feat: session turn loop with event bus, hand guard, and fakes that replay real boards"
```

---

### Task 5: Web server and a plain functional page

**Files:**
- Create: `code/hackathon/duet/web.py`
- Create: `code/hackathon/duet/static/index.html`
- Test: `code/hackathon/tests/test_web.py`

The page is deliberately plain: the "Website UI mockups" session owns its design and will restyle it against the same protocol. Do not spend effort on looks; spend it on every message type being handled.

- [ ] **Step 1: Write the failing tests**

`code/hackathon/tests/test_web.py`:

```python
import numpy as np
from starlette.testclient import TestClient

from duet import web
from duet.camera import Frame
from duet.session import EventBus


class StubSession:
    state, turn, plan, at_look, color = "human_turn", 1, [], False, "green"

    def __init__(self):
        self.changes, self.actions = [], []

    def update_settings(self, **changes):
        if changes.get("length") == "bogus":
            raise ValueError("length must be short, medium or long")
        self.changes.append(changes)

    async def pause(self):
        self.actions.append("pause")

    def resume(self):
        self.actions.append("resume")

    def pass_turn(self):
        self.actions.append("pass")

    async def clear_error(self):
        self.actions.append("clear_error")


class StubFrames:
    def latest(self):
        return Frame(np.full((60, 80, 3), 128, np.uint8), None, 0.0)


def test_page_serves_with_dev_mode_and_data_el_names(tmp_path):
    app = web.make_app(StubSession(), StubFrames(), EventBus(), sessions_dir=tmp_path)
    with TestClient(app) as client:
        r = client.get("/")
        assert r.status_code == 200 and "<title>Duet" in r.text
        assert 'data-el="' in r.text and "dev-badge" in r.text
        assert "/stream.mjpg" in r.text and "/ws" in r.text


def test_ws_sends_the_snapshot_then_takes_commands(tmp_path):
    bus = EventBus()
    bus.emit("state", state="human_turn", turn=1)
    bus.emit("plan", polylines=[[[1, 1], [2, 2]]], color="#000")
    stub = StubSession()
    app = web.make_app(stub, StubFrames(), bus, sessions_dir=tmp_path)
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            first, second = ws.receive_json(), ws.receive_json()
            assert [first["type"], second["type"]] == ["state", "plan"]
            ws.send_json({"type": "set", "length": "medium", "exchanges": "4"})
            ws.send_json({"type": "pass"})
            ws.send_json({"type": "set", "length": "bogus"})
            err = ws.receive_json()
            assert err["type"] == "error" and "length" in err["message"]
            ws.send_json({"type": "nonsense"})
            assert ws.receive_json()["type"] == "error"
    assert stub.changes == [{"length": "medium", "exchanges": 4}]
    assert stub.actions == ["pass"]


def test_mjpeg_part_is_a_multipart_jpeg_chunk():
    part = web.mjpeg_part(np.full((60, 80, 3), 128, np.uint8))
    assert part.startswith(b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: ")
    assert part.endswith(b"\r\n") and b"\xff\xd8" in part


def test_session_files_and_health_are_served(tmp_path):
    (tmp_path / "s1").mkdir()
    (tmp_path / "s1" / "turn-01-human.jpg").write_bytes(b"\xff\xd8\xff")
    app = web.make_app(StubSession(), StubFrames(), EventBus(), sessions_dir=tmp_path)
    with TestClient(app) as client:
        assert client.get("/sessions/s1/turn-01-human.jpg").status_code == 200
        assert client.get("/health").json()["state"] == "human_turn"


def test_calibration_is_served_and_leads_the_snapshot(tmp_path, calibration):
    bus = EventBus()
    bus.emit("state", state="idle", turn=0)
    app = web.make_app(StubSession(), StubFrames(), bus, sessions_dir=tmp_path, calibration=calibration)
    with TestClient(app) as client:
        cal = client.get("/calibration.json").json()
        assert cal["marks_image"] == calibration["marks_image"] and cal["board_mm"] == [176.0, 240.0]
        assert cal["image_size"] == [1280, 720] and cal["cam_to_robot"] == calibration["cam_to_robot"]
        with client.websocket_connect("/ws") as ws:
            assert [ws.receive_json()["type"], ws.receive_json()["type"]] == ["calib", "state"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_web.py -q`
Expected: `ModuleNotFoundError: No module named 'duet.web'`

- [ ] **Step 3: Write `web.py`**

`code/hackathon/duet/web.py`:

```python
"""The page's server: the static page, one WebSocket carrying every session event and the page's
commands, an MJPEG stream of the camera with the planned strokes overlaid at the look pose, and the
session files. Local screen only; the public tunnel is P1."""
from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from duet import config as cfg
from duet import vision

STATIC = cfg.PACKAGE_DIR / "static"
ALLOWED_SETTINGS = ("artist", "length", "exchanges", "mode", "handoff")
STREAM_PERIOD_S = 0.2
IMAGE_SIZE = (1280, 720)       # the RealSense color stream the calibration was made on


def hex_to_bgr(color: str) -> tuple[int, int, int]:
    c = color.lstrip("#")
    return int(c[4:6], 16), int(c[2:4], 16), int(c[0:2], 16)


def mjpeg_part(bgr: np.ndarray, quality: int = 70) -> bytes:
    ok, jpg = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("could not encode a stream frame")
    data = jpg.tobytes()
    return (b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(len(data)).encode()
            + b"\r\n\r\n" + data + b"\r\n")


def make_app(session, frames, bus, sessions_dir: Path = cfg.SESSIONS_DIR, calibration: dict | None = None) -> FastAPI:
    app = FastAPI(title="Duet")
    sessions_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/sessions", StaticFiles(directory=str(sessions_dir)), name="sessions")
    h_inv = None
    calib: dict = {}
    if calibration and "marks_image" in calibration:
        quad = vision.board_quad(np.array(calibration["marks_image"], np.float32), calibration["board_tl_index"])
        h_inv = np.linalg.inv(vision.board_homography(quad))
        # The page registers its own layers onto the camera image with this; see the mockup session's protocol.
        calib = {"marks_image": calibration["marks_image"], "board_tl_index": calibration["board_tl_index"],
                 "board_mm": [cfg.BOARD_W_MM, cfg.BOARD_H_MM], "image_size": list(IMAGE_SIZE),
                 "cam_to_robot": calibration.get("cam_to_robot")}
        bus.emit("calib", **calib)

    @app.get("/")
    async def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/health")
    async def health():
        return {"state": session.state, "turn": session.turn}

    @app.get("/calibration.json")
    async def calibration_json():
        return calib

    async def handle(cmd: dict) -> dict | None:
        kind = cmd.get("type")
        if kind == "set":
            changes = {k: v for k, v in cmd.items() if k in ALLOWED_SETTINGS}
            try:
                if "exchanges" in changes:
                    changes["exchanges"] = int(changes["exchanges"])
                session.update_settings(**changes)
            except (ValueError, TypeError) as exc:
                return {"type": "error", "message": f"setting refused: {exc}"}
            return None
        if kind == "pause":
            await session.pause()
        elif kind == "resume":
            session.resume()
        elif kind == "pass":
            session.pass_turn()
        elif kind == "clear_error":
            await session.clear_error()
        else:
            return {"type": "error", "message": f"unknown command {kind!r}"}
        return None

    @app.websocket("/ws")
    async def ws(sock: WebSocket):
        await sock.accept()
        q = bus.subscribe()
        pump: asyncio.Task | None = None
        try:
            for msg in bus.snapshot():
                await sock.send_json(msg)

            async def forward():
                while True:
                    await sock.send_json(await q.get())
            pump = asyncio.create_task(forward())
            while True:
                reply = await handle(await sock.receive_json())
                if reply is not None:
                    await sock.send_json(reply)
        except WebSocketDisconnect:
            pass
        finally:
            if pump is not None:
                pump.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await pump
            bus.unsubscribe(q)

    def overlay(img: np.ndarray) -> np.ndarray:
        if h_inv is None or not session.plan or not session.at_look:
            return img
        out = img.copy()
        color = hex_to_bgr(cfg.COLOR_HEX.get(getattr(session, "color", "green"), "#222222"))
        for pl in session.plan:
            if len(pl) < 2:
                continue
            pts = np.array([[[x * vision.PX_PER_MM, y * vision.PX_PER_MM] for x, y in pl]], np.float32)
            cv2.polylines(out, [cv2.perspectiveTransform(pts, h_inv)[0].astype(np.int32)], False, color, 2, cv2.LINE_AA)
        return out

    async def mjpeg(with_overlay: bool):
        while True:
            f = frames.latest()
            if f is not None:
                yield mjpeg_part(overlay(f.color) if with_overlay else f.color)
            await asyncio.sleep(STREAM_PERIOD_S)

    @app.get("/stream.mjpg")
    async def stream(overlay_on: int = Query(1, alias="overlay")):
        """`?overlay=0` skips the server-side stroke overlay, for a page that draws its own layers."""
        return StreamingResponse(mjpeg(bool(overlay_on)), media_type="multipart/x-mixed-replace; boundary=frame")

    return app
```

- [ ] **Step 4: Write the page**

`code/hackathon/duet/static/index.html`:

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Duet</title>
<style>
  :root { --ink: #1b221d; --paper: #f7f6f2; --line: #d9d6ce; --green: #1b8f3a; --accent: #2743e3; --warn: #b3261e; }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--paper); color: var(--ink); font: 15px/1.4 system-ui, -apple-system, sans-serif; }
  header { display: flex; align-items: center; gap: 16px; padding: 12px 16px; border-bottom: 1px solid var(--line); background: #fff; }
  header h1 { margin: 0; font-size: 18px; letter-spacing: .04em; }
  .pill { padding: 4px 10px; border-radius: 999px; background: #eee; font-weight: 600; font-size: 13px; text-transform: uppercase; letter-spacing: .08em; }
  .pill[data-state="human_turn"] { background: #e3f6e8; color: var(--green); }
  .pill[data-state="robot_draw"], .pill[data-state="plan"], .pill[data-state="interpret"], .pill[data-state="capture"], .pill[data-state="look"] { background: #e6e9ff; color: var(--accent); }
  .pill[data-state="paused"] { background: #fde7e5; color: var(--warn); }
  .counter { margin-left: auto; font-size: 28px; font-weight: 700; }
  .counter small { font-size: 13px; font-weight: 500; color: #666; margin-left: 6px; }
  main { display: grid; gap: 16px; padding: 16px; grid-template-columns: 1fr; }
  @media (min-width: 900px) { main { grid-template-columns: 1.3fr 1fr 1fr; } .span2 { grid-column: span 2; } }
  section { background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 12px; min-width: 0; }
  section h2 { margin: 0 0 8px; font-size: 12px; text-transform: uppercase; letter-spacing: .1em; color: #666; }
  img, video, svg { display: block; width: 100%; border-radius: 8px; background: #eee; }
  .quip { font-size: 15px; font-style: italic; color: var(--green); margin: 0 0 8px; }
  .sees { font-size: 20px; font-weight: 600; margin: 0 0 6px; }
  .adds { font-size: 17px; margin: 0; }
  .source { margin-top: 8px; font-size: 12px; color: #666; }
  .source.fallback { color: var(--warn); font-weight: 600; }
  .controls { display: grid; gap: 10px; grid-template-columns: 1fr 1fr; }
  .controls label { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: #666; }
  .controls select, .controls input { font: inherit; padding: 6px 8px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
  .seg { display: flex; gap: 4px; }
  .seg button { flex: 1; }
  button { font: inherit; padding: 8px 10px; border: 1px solid var(--line); border-radius: 8px; background: #fff; cursor: pointer; }
  button.on { background: var(--ink); color: #fff; border-color: var(--ink); }
  button.danger { border-color: var(--warn); color: var(--warn); }
  .row { display: flex; gap: 8px; flex-wrap: wrap; grid-column: span 2; }
  .error { grid-column: span 2; min-height: 1.4em; color: var(--warn); font-size: 13px; }
  .hidden { display: none !important; }
  .muted { color: #888; font-size: 13px; }
  body.dev [data-el]{outline:1px dashed rgba(39,67,227,.4);outline-offset:-1px;}
  body.dev [data-el]:hover{outline:2px solid #2743E3;background:rgba(39,67,227,.07);cursor:crosshair;}
  .dev-badge{position:fixed;top:12px;left:50%;transform:translateX(-50%);z-index:2147483000;display:none;padding:7px 14px;font:600 11px/1 system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#fff;background:#2743E3;border-radius:999px;box-shadow:0 6px 20px rgba(39,67,227,.35);}
  body.dev .dev-badge{display:block;}
  .dev-label{position:fixed;z-index:2147483001;display:none;pointer-events:none;padding:4px 8px;font:600 11px/1 system-ui,sans-serif;color:#fff;background:#1B221D;border-radius:6px;white-space:nowrap;}
  .dev-toast{position:fixed;bottom:70px;left:50%;transform:translateX(-50%) translateY(10px);z-index:2147483002;opacity:0;padding:9px 16px;font:600 12px/1 system-ui,sans-serif;color:#fff;background:#1B2FA8;border-radius:999px;transition:opacity .2s,transform .2s;pointer-events:none;}
  .dev-toast.show{opacity:1;transform:translateX(-50%) translateY(0);}
</style>
</head>
<body>
<header data-el="header">
  <h1 data-el="title">Duet</h1>
  <span class="pill" id="state" data-state="idle" data-el="state pill">connecting</span>
  <span class="muted" id="conn" data-el="connection status"></span>
  <span class="muted" id="guard" data-el="hand guard status"></span>
  <div class="counter" data-el="exchange counter"><span id="turn">0</span> of <span id="total">5</span><small id="length">short</small></div>
</header>
<main>
  <section class="span2" data-el="live camera panel">
    <h2>Live camera</h2>
    <img id="stream" src="/stream.mjpg" alt="wrist camera" data-el="live camera stream">
  </section>
  <section data-el="interpretation panel">
    <h2>Claude</h2>
    <p class="quip" id="quip" data-el="quip bubble"></p>
    <p class="sees" id="sees" data-el="sees sentence">Waiting for the first mark.</p>
    <p class="adds" id="adds" data-el="adds sentence"></p>
    <div class="source" id="source" data-el="interpretation source"></div>
  </section>
  <section data-el="vector plan panel">
    <h2>Plan</h2>
    <svg id="plan" viewBox="0 0 176 240" data-el="vector plan svg">
      <rect width="176" height="240" fill="#fff"/>
      <rect x="15" y="15" width="146" height="210" fill="none" stroke="#e5e5e5" stroke-width=".5"/>
      <g id="g-human" fill="none" stroke="#222" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"></g>
      <g id="g-done" fill="none" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"></g>
      <g id="g-queued" fill="none" stroke-width="1" stroke-dasharray="3 2" stroke-linecap="round" stroke-linejoin="round"></g>
    </svg>
    <div class="muted" id="planmeta" data-el="plan meta"></div>
  </section>
  <section data-el="last turn panel">
    <h2>Last turn</h2>
    <img id="shot" alt="last turn photo" data-el="last turn photo">
  </section>
  <section data-el="controls panel">
    <h2>Controls</h2>
    <div class="controls">
      <label data-el="artist picker">Artist
        <select id="artist"><option value="haring">Keith Haring</option></select>
      </label>
      <label data-el="exchange count input">Exchanges
        <input id="exchanges" type="number" min="1" max="20" value="5">
      </label>
      <label data-el="length setting">Length
        <div class="seg" id="lengths">
          <button data-v="short" data-el="length button — short">Short</button>
          <button data-v="medium" data-el="length button — medium">Medium</button>
          <button data-v="long" data-el="length button — long">Long</button>
        </div>
      </label>
      <label data-el="marker handoff toggle">Marker
        <div class="seg" id="handoffs">
          <button data-v="held" data-el="handoff button — held">Held</button>
          <button data-v="dock" data-el="handoff button — dock">Dock</button>
        </div>
      </label>
      <div class="row">
        <button id="pause" data-el="pause button">Pause</button>
        <button id="resume" class="hidden" data-el="resume button">Resume</button>
        <button id="pass" data-el="pass turn button">Pass turn</button>
        <button id="clear" class="danger" data-el="clear arm error button">Clear arm error</button>
      </div>
      <div class="error" id="error" data-el="error line"></div>
    </div>
  </section>
  <section data-el="session video panel">
    <h2>Session video</h2>
    <video id="video" controls class="hidden" data-el="session video"></video>
    <p class="muted" id="videonote" data-el="session video note">Stitched when the piece is done.</p>
    <a id="videolink" class="hidden" download data-el="session video download link">Download</a>
  </section>
</main>

<div class="dev-badge">DEV MODE · click an element to copy its name · press D to exit</div>
<div class="dev-label" id="devLabel"></div>
<div class="dev-toast" id="devToast"></div>

<script>
(function () {
  const $ = (id) => document.getElementById(id);
  const S = { human: [], plan: null, progress: -1 };
  let ws = null;

  function connect() {
    ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws');
    ws.onopen = () => { $('conn').textContent = ''; };
    ws.onclose = () => { $('conn').textContent = 'reconnecting…'; setTimeout(connect, 1000); };
    ws.onmessage = (e) => handle(JSON.parse(e.data));
  }
  function send(msg) { if (ws && ws.readyState === 1) ws.send(JSON.stringify(msg)); }

  function points(pl) { return pl.map(p => p[0].toFixed(2) + ',' + p[1].toFixed(2)).join(' '); }
  function polys(group, list, stroke) {
    group.innerHTML = '';
    if (stroke) group.setAttribute('stroke', stroke);
    for (const pl of list) {
      if (pl.length < 2) continue;
      const el = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
      el.setAttribute('points', points(pl));
      group.appendChild(el);
    }
  }
  function drawPlan() {
    polys($('g-human'), S.human);
    if (!S.plan) { polys($('g-done'), []); polys($('g-queued'), []); $('planmeta').textContent = ''; return; }
    const n = S.progress + 1;
    polys($('g-done'), S.plan.polylines.slice(0, n), S.plan.color);
    polys($('g-queued'), S.plan.polylines.slice(n), S.plan.color);
    $('planmeta').textContent = n + ' of ' + S.plan.polylines.length + ' strokes drawn · budget ' + S.plan.budget_mm + ' mm';
  }
  function seg(id, value) {
    for (const b of $(id).querySelectorAll('button')) b.classList.toggle('on', b.dataset.v === value);
  }
  function handle(m) {
    switch (m.type) {
      case 'state':
        $('state').textContent = m.state.replace('_', ' ');
        $('state').dataset.state = m.state;
        $('turn').textContent = m.turn;
        $('total').textContent = m.exchanges;
        $('length').textContent = m.length;
        $('guard').textContent = 'hand check: ' + m.hand_guard;
        if (document.activeElement !== $('exchanges')) $('exchanges').value = m.exchanges;
        seg('lengths', m.length); seg('handoffs', m.handoff);
        $('pass').classList.toggle('hidden', m.handoff !== 'held');
        $('pause').classList.toggle('hidden', m.state === 'paused');
        $('resume').classList.toggle('hidden', m.state !== 'paused');
        $('error').textContent = m.error || '';
        break;
      case 'human':
        S.human = m.polylines || [];
        if (m.found === false) $('error').textContent = 'No new ink found; still your turn.';
        drawPlan();
        break;
      case 'plan':
        S.plan = m; S.progress = -1; drawPlan();
        break;
      case 'progress':
        S.progress = m.stroke; drawPlan();
        break;
      case 'interpretation':
        $('quip').textContent = m.quip || '';
        $('sees').textContent = m.sees || (m.source === 'fallback' ? 'Claude was unavailable this turn.' : '');
        $('adds').textContent = m.adds || '';
        $('source').textContent = m.source === 'claude' ? ('Claude, ' + m.latency_s + ' s') : ('Fallback grammar: ' + (m.error || ''));
        $('source').className = 'source ' + m.source;
        break;
      case 'shot':
        $('shot').src = m.url + '?t=' + Date.now();
        break;
      case 'video':
        $('video').src = m.url; $('video').classList.remove('hidden');
        $('videonote').classList.add('hidden');
        $('videolink').href = m.url; $('videolink').classList.remove('hidden');
        break;
      case 'dock':
        if (m.reseat && m.reseat.length) $('error').textContent = 'Please reseat the ' + m.reseat.join(', ') + ' marker in its cap.';
        break;
      case 'error':
        $('error').textContent = m.message;
        break;
    }
  }

  $('artist').onchange = () => send({ type: 'set', artist: $('artist').value });
  $('exchanges').onchange = () => send({ type: 'set', exchanges: parseInt($('exchanges').value, 10) });
  $('lengths').onclick = (e) => { const v = e.target.dataset.v; if (v) send({ type: 'set', length: v }); };
  $('handoffs').onclick = (e) => { const v = e.target.dataset.v; if (v) send({ type: 'set', handoff: v }); };
  $('pause').onclick = () => send({ type: 'pause' });
  $('resume').onclick = () => send({ type: 'resume' });
  $('pass').onclick = () => send({ type: 'pass' });
  $('clear').onclick = () => send({ type: 'clear_error' });
  connect();
})();
</script>
<script>
(function(){
  var label=document.getElementById('devLabel'),toast=document.getElementById('devToast'),tT=null;
  function isDev(){return document.body.classList.contains('dev');}
  function copy(t){if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t)['catch'](fb);}else fb();
    function fb(){var a=document.createElement('textarea');a.value=t;a.style.position='fixed';a.style.opacity='0';document.body.appendChild(a);a.select();try{document.execCommand('copy');}catch(e){}document.body.removeChild(a);}}
  function toastMsg(m){toast.textContent=m;toast.classList.add('show');if(tT)clearTimeout(tT);tT=setTimeout(function(){toast.classList.remove('show');},1400);}
  document.addEventListener('keydown',function(e){var t=e.target;if(t&&t.matches&&t.matches('input,textarea,select,[contenteditable]'))return;
    if(e.key==='d'||e.key==='D'){document.body.classList.toggle('dev');if(!isDev())label.style.display='none';}});
  document.addEventListener('mousemove',function(e){if(!isDev()){label.style.display='none';return;}
    var el=e.target.closest?e.target.closest('[data-el]'):null;
    if(el){label.textContent=el.getAttribute('data-el');label.style.display='block';
      label.style.left=Math.min(e.clientX+12,window.innerWidth-label.offsetWidth-8)+'px';label.style.top=(e.clientY+14)+'px';}
    else label.style.display='none';});
  document.addEventListener('click',function(e){if(!isDev())return;
    var el=e.target.closest?e.target.closest('[data-el]'):null;if(!el)return;
    e.preventDefault();e.stopPropagation();var n=el.getAttribute('data-el');copy(n);toastMsg('Copied: '+n);},true);
})();
</script>
</body>
</html>
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_web.py -q`
Expected: `5 passed`

- [ ] **Step 6: Commit**

```bash
git add duet/web.py duet/static/index.html tests/test_web.py
git commit -m "feat: FastAPI server with WebSocket, MJPEG stream, and a plain functional Duet page"
```

---

### Task 6: The runner, fake mode with the real day-1 boards, and the browser check

**Files:**
- Create: `code/hackathon/duet/run.py`
- Test: `code/hackathon/tests/test_run.py`

- [ ] **Step 1: Write the failing test**

`code/hackathon/tests/test_run.py`:

```python
from duet import run


def test_parser_defaults_and_fake_flags():
    a = run.build_parser().parse_args([])
    assert (a.fake, a.claude, a.port, a.length, a.exchanges, a.handoff, a.replay) == (False, False, 8000, "short", 5, "held", "20260918-190258")
    b = run.build_parser().parse_args(["--fake", "--claude", "--port", "8765", "--length", "long", "--exchanges", "3",
                                       "--handoff", "dock", "--replay", "20260918-185927"])
    assert (b.fake, b.claude, b.port, b.length, b.exchanges, b.handoff, b.replay) == (True, True, 8765, "long", 3, "dock", "20260918-185927")


def test_replay_boards_come_in_turn_order(tmp_path):
    for name in ("turn-00-start.jpg", "turn-02-human.jpg", "turn-01-human.jpg", "turn-01-robot.jpg", "turn-02-robot.jpg"):
        (tmp_path / name).write_bytes(b"")
    start, humans, robots = run.replay_paths(tmp_path)
    assert start.name == "turn-00-start.jpg"
    assert [p.name for p in humans] == ["turn-01-human.jpg", "turn-02-human.jpg"]
    assert [p.name for p in robots] == ["turn-01-robot.jpg", "turn-02-robot.jpg"]
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_run.py -q`
Expected: `ModuleNotFoundError: No module named 'duet.run'`

- [ ] **Step 3: Write `run.py`**

`code/hackathon/duet/run.py`:

```python
"""Start Duet: the camera poller, the controller, Claude, the session loop, and the page.

    python -m duet.run                      the real machine; page at http://localhost:8000
    python -m duet.run --fake               no machine: a fake camera replays the real day-1 boards from
                                            sessions/20260918-190258 (a fake visitor "draws" each human turn,
                                            a fake arm "draws" each robot turn), canned proposals, the page live
    python -m duet.run --fake --claude      the same replay, but the real Claude call on the real boards
    python -m duet.run --fake --replay 20260918-185927
    python -m duet.run --length medium --exchanges 3 --handoff dock --port 8080

Stop with Ctrl-C. Every event is also printed to the terminal, so the trigger can be watched without the page.
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
import re
from pathlib import Path

import cv2
import uvicorn

from duet import claude_turn
from duet import config as cfg
from duet.recorder import Recorder
from duet.session import EventBus, HandGuard, Session, Settings
from duet.web import make_app


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="run Duet")
    p.add_argument("--fake", action="store_true", help="no machine: replay real boards through a fake camera and arm")
    p.add_argument("--claude", action="store_true", help="with --fake: call the real Claude anyway")
    p.add_argument("--replay", default="20260918-190258", help="with --fake: the session folder whose boards are replayed")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--length", choices=tuple(cfg.BUDGET_MM), default="short")
    p.add_argument("--exchanges", type=int, default=5)
    p.add_argument("--handoff", choices=("held", "dock"), default="held" if cfg.HELD_MODE else "dock")
    return p


def replay_paths(folder: Path) -> tuple[Path, list[Path], list[Path]]:
    """The start photo and the human and robot photos of a recorded session, in turn order."""
    def turn(p: Path) -> int:
        return int(re.match(r"turn-(\d+)-", p.name).group(1))
    humans = sorted(folder.glob("turn-*-human.jpg"), key=turn)
    robots = sorted(folder.glob("turn-*-robot.jpg"), key=turn)
    return folder / "turn-00-start.jpg", humans, robots


class ClaudeBrain:
    """The real Claude turn, off the event loop so the page and camera keep moving while it thinks."""

    def __init__(self):
        self.client = claude_turn.make_client()

    async def propose(self, board, human_cam, history, length, exchange, total):
        return await asyncio.to_thread(claude_turn.propose, self.client, board, human_cam, history, length, exchange, total)


async def log_events(bus: EventBus) -> None:
    q = bus.subscribe()
    while True:
        m = await q.get()
        t = m["type"]
        if t == "state":
            print(f"[state] {m['state']}  turn {m['turn']} of {m['exchanges']}  {m['length']}/{m['handoff']}  "
                  f"hand check {m['hand_guard']}" + (f"  ERROR {m['error']}" if m.get("error") else ""), flush=True)
        elif t == "interpretation":
            print(f"[claude] {m['source']} {m['latency_s']} s: {m['sees']} {m['adds']} {m.get('error') or ''}", flush=True)
        elif t == "plan":
            print(f"[plan] {len(m['polylines'])} strokes, budget {m['budget_mm']} mm", flush=True)
        elif t in ("error", "dock", "video", "human"):
            print(f"[{t}] " + json.dumps({k: v for k, v in m.items() if k not in ("type", "polylines", "new")}), flush=True)


async def fake_visitor(bus: EventBus, frames, humans: list[Path]) -> None:
    """Each human turn: wait a moment, move a hand over the board for a second, then show the next
    real human-turn board and hold still, so the held trigger fires by itself."""
    q = bus.subscribe()
    boards = list(humans)
    while True:
        m = await q.get()
        if m["type"] == "state" and m["state"] == "human_turn":
            await asyncio.sleep(2.0)
            if not boards:
                print("[visitor] out of recorded turns; the board is yours", flush=True)
                return
            frames.jitter(1.2)
            await asyncio.sleep(0.6)
            frames.show_board(cv2.imread(str(boards.pop(0))))
            print("[visitor] drew a mark", flush=True)


async def main(args: argparse.Namespace) -> None:
    cal = json.loads(cfg.CALIBRATION_PATH.read_text())
    settings = Settings(length=args.length, exchanges=args.exchanges, handoff=args.handoff)
    bus = EventBus()
    rec = Recorder(settings=settings.record())
    machine = frames = ctl = None
    tasks: list[asyncio.Task] = []
    if args.fake:
        from duet.fakes import FakeBrain, FakeController, FakeFrames
        start, humans, robots = replay_paths(cfg.SESSIONS_DIR / args.replay)
        frames = FakeFrames(cv2.imread(str(cfg.FIXTURES_DIR / "look_frame.jpg")), cal)
        frames.show_board(cv2.imread(str(start)))
        frames.robot_boards = [cv2.imread(str(p)) for p in robots]
        ctl = FakeController(frames, stroke_s=0.3)
        brain = ClaudeBrain() if args.claude else FakeBrain(latency_s=1.0)
        tasks.append(asyncio.create_task(fake_visitor(bus, frames, humans)))
    else:
        from viam.components.camera import Camera
        import viam_conn
        from duet.calib import BoardToRobot, load_poses
        from duet.camera import FrameSource
        from duet.controller import Controller
        machine = await viam_conn.connect()
        frames = FrameSource(Camera.from_robot(machine, viam_conn.CAMERA))
        await frames.start()
        poses = load_poses()
        ctl = Controller(machine, poses, BoardToRobot.from_poses(poses))
        ctl.held_mode = args.handoff == "held"
        brain = ClaudeBrain()
    guard = HandGuard(frames, cal)
    session = Session(settings, frames, ctl, brain, rec, bus, cal, guard=guard)
    app = make_app(session, frames, bus, calibration=cal)
    server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=args.port, log_level="warning"))
    print(f"Duet on http://localhost:{args.port}  source={'fake replay of ' + args.replay if args.fake else 'armfarm22'} "
          f"brain={type(brain).__name__} hand_check={guard.mode} session={rec.dir}", flush=True)
    tasks += [asyncio.create_task(session.run()), asyncio.create_task(log_events(bus))]
    try:
        await server.serve()
    finally:
        for t in tasks:
            t.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await t
        if machine is not None:
            await frames.stop()
            await machine.close()


if __name__ == "__main__":
    asyncio.run(main(build_parser().parse_args()))
```

- [ ] **Step 4: Run the test, then the fake loop from the terminal**

Run: `python -m pytest tests/test_run.py -q`
Expected: `2 passed`

Run in the background: `python -m duet.run --fake --port 8765 --exchanges 3`
Expected within about a minute of log lines: `[state] look`, `[state] human_turn`, `[visitor] drew a mark`, `[state] capture`, `[human] {"found": true}`, `[state] interpret`, `[claude] claude 1.0 s: A creature sprawls ...`, `[plan] N strokes`, `[state] robot_draw`, `[state] look`, `[state] human_turn` ... and after three exchanges `[state] finish`, `[video] {...session.mp4}`, `[state] finished`. No `[error]` lines except at most one `board shifted` (the fixture frame's marks are 21 px, about 10 mm, from the calibrated spots; the threshold is 40 px so it should not appear).

- [ ] **Step 5: Browser check of the page (the stage 7 exit test)**

With the fake run still going, open `http://localhost:8765` in the built-in browser. Take a screenshot during a robot turn and one after the session finishes. Check with `read_page` or `find`:
- The state pill changes (`human turn`, `robot draw`, `finished`) and the counter reads `1 of 3`, `2 of 3`, `3 of 3`.
- The Claude panel shows the `sees` and `adds` sentences and `Claude, 1.0 s`.
- The plan SVG shows the black human polylines (the real creature) and green plan strokes, dashed ones turning solid as `progress` arrives.
- The live camera image loads (MJPEG) and the last-turn photo updates.
- The video element appears at the end and plays.
- Press D: the badge appears, hovering shows `data-el` names.
- Change the exchange count in the controls: the header counter updates on the next `state` event.
Save the two screenshots to `captures/page-robot-turn.png` and `captures/page-finished.png` (gitignored; for the morning summary). Then stop the server.

- [ ] **Step 6: Run the replay once with the real Claude**

Run: `python -m duet.run --fake --claude --port 8765 --exchanges 2 --length short`
Expected: `[claude] claude <latency> s: <sees> <adds>` lines whose sentences describe the day-1 creature (compare with `sessions/20260918-190258/session.json`), latencies under 12 s, and the session finishing with a video. Copy the two sentence pairs into the morning notes (Task 7). If a turn falls back with a timeout, note the latency; the day-1 measurement was 7.4 to 7.6 s on short turns.

- [ ] **Step 7: Commit**

```bash
git add duet/run.py tests/test_run.py
git commit -m "feat: run.py wires the machine or a replay of real boards into the session loop and the page"
```

---

### Task 7: Notes, README, morning checklist

**Files:**
- Modify: `code/hackathon/README.md`
- Modify: `notes/hackathon/04-plan.md` (append)
- Create: `notes/hackathon/05-morning-checklist.md`

- [ ] **Step 1: README rows**

Append to the table in `code/hackathon/README.md`:

```markdown
| `duet/` | The Duet drawing robot. `python -m duet.<module>`; each module's docstring has its usage. Day 1: `teach`, `stroke_bench`, `dock_test`, `aim`, `calibrate`, `claude_turn`, `turn` (terminal loop). Night 1: `trigger`, `session`, `recorder`, `web`, `run`, `fakes` |
| `duet/run.py` | `python -m duet.run` starts everything against the machine with the page on http://localhost:8000; `--fake` replays the real day-1 boards through a fake camera and arm; `--fake --claude` adds the real Claude call |
| `tests/fixtures/` | A real look-pose frame and the boards of the first hardware exchange, used by the tests and by `run.py --fake` |
| `sessions/` | One folder per session (gitignored): turn photos, plan SVGs, `session.json`, `session.mp4` |
```

- [ ] **Step 2: Overnight results in the plan notes**

Append to `notes/hackathon/04-plan.md`:

```markdown

## Overnight results (2026-09-18 night, no machine)
- **Trigger (stage 6):** `duet/trigger.py` state machine (dock and held rules, reseat), readings in `vision.py`: stillness, dock dots by color, hand by depth against a fitted board plane, and a color backup that compares the frame with the reference taken after the robot's turn (marker lines vanish under a 9 px opening; a hand is a blob over 2000 mm²). No depth frame exists at the straight-down look pose yet, so the backup is what runs until `calibrate --plane` is run on one.
- **Loop (stage 8):** `duet/session.py` replaces `turn next`'s Enter prompts: look, human turn (trigger), capture, interpret, plan, robot draw, look, finish, with pause and resume, and the same session files as `duet.turn`. The arm only leaves the look pose after a clear hand check; between strokes there is no valid reading from the wrist camera (a static webcam over the table would fix that; Viam offered webcams).
- **Page (stage 7):** `duet/web.py` and a plain `static/index.html` (the mockup session restyles it; protocol in the session record of "Website UI mockups"). `python -m duet.run --fake` replays the day-1 boards through the whole pipeline with the page live. Screenshots in `captures/page-*.png`.
- **Memory (stage 9):** `duet/recorder.py` writes the session folder and stitches `session.mp4` (1 s per turn, 2 s hold).
- **Real Claude on the replay:** <two sentence pairs and latencies from `python -m duet.run --fake --claude --exchanges 2`>.
- **Config:** `CLEARANCE_MM` is now 5.0 as section 15 of the spec says (it was 3.0 in code). Constants for the trigger live at the end of `config.py`.
```

Fill the blank from Task 6, Step 6 before committing.

- [ ] **Step 3: Morning checklist**

`notes/hackathon/05-morning-checklist.md`:

```markdown
# Morning checklist (Sat 2026-09-19)

Everything below needs the machine. Order matters; each line is a few minutes. E-stop within reach before the first arm move.

## Before the arm moves (10 min)
- [ ] `python explore.py`: connected, resources listed, E-stop not latched. This also saves `captures/depth.dep`; take it at the look pose (see below) for the hand check.
- [ ] `git log --oneline -15` to see what landed overnight; `python -m pytest -q` green.
- [ ] `python -m duet.teach show`, then `python -m duet.teach verify`: every taught pose still reached.
- [ ] Wipe the board. `python -m duet.calibrate --check` at the look pose: marks re-found, drift small. If the board moved: `python -m duet.calibrate --tl D`, draw the two squares with `stroke_bench 20 --at 15 15` and `--at 120 180`, then `calibrate --check` and `--fit 15,15,20 120,180,20`.

## Hand check (10 min)
- [ ] With the arm at the look pose, run `python explore.py` (it saves the depth frame as `captures/depth.dep`), then `python -m duet.calibrate --dock x0 y0 x1 y1` with the tub's rectangle read off `captures/calib_frame.jpg`, then `python -m duet.calibrate --plane captures/depth.dep`. The page's header then says `hand check: depth at the look pose`. Without this step the color backup runs, which is fine for the demo.
- [ ] `python -m duet.run --handoff held`, open http://localhost:8000. Hold a hand over the board: the terminal must not fire a turn while it is there. Draw a mark, take the hand away: the turn fires after 2 s. That is the stage 6 exit.

## One full exchange from the page (20 min)
- [ ] Held mode first (`teach load` if the pen is not in the gripper). `python -m duet.run --exchanges 3 --length short`. Draw, step back, watch: capture, Claude's sentence, the plan preview, the arm drawing, the look pose, "human turn" again. The stage 8 exit is one exchange without touching the terminal.
- [ ] If a move is refused or the arm faults: the page shows paused; fix the cause, Clear arm error, Resume.
- [ ] Dock mode only if there is time: record the green dot with `"dots": {"green": {"xy": [x, y], "hsv_lo": [40, 60, 60], "hsv_hi": [85, 255, 255]}}` in `calibration.json` (pixel position from `captures/calib_frame.jpg` with the marker capped in the tub), then `--handoff dock`.

## Rest of the morning
- [ ] Let a session finish: the video appears on the page and in `sessions/<id>/session.mp4`.
- [ ] Three sessions in a row on Short. Tune `PEN_DOWN_OFFSET_MM`, the Claude timeouts in `claude_turn.TIMEOUT_S`, and the prompt from what the boards look like.
- [ ] Freeze code by 14:30. Demo script: Short, 3 exchanges, one clear shape, let Claude's sentence carry the room.
- [ ] If time allows: ask Viam staff for a webcam on a stand over the table and give `HandGuard` a second frame source, so the hand check works while the arm draws; collision sensitivity 5 on the arm.
```

- [ ] **Step 4: Full suite, then commit**

Run: `python -m pytest -q`
Expected: all green.

```bash
git add code/hackathon/README.md notes/hackathon/04-plan.md notes/hackathon/05-morning-checklist.md
git commit -m "docs: overnight results, run instructions, and the morning hardware checklist"
```
