# Duet plan 2 of 3: Perception and brain (stages 4 to 6, offline) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Everything between the camera and the arm that can be built and proven without the machine: depth decoding and a frame poller, the trigger's readings (dock dots, hand, stillness) and state machine, the Claude proposal with validation and Haring styling, and a bench that runs saved boards through Claude and measures latency.

**Architecture:** Pure functions in `vision.py` and `planner.py` tested on synthetic and saved frames; small classes with injected clients (`FrameSource` over a fake camera, `ClaudeTurn` over a fake Anthropic client). The Pydantic `Proposal` schema lives in `proposal.py` so `claude_turn` and `planner` share it without importing each other. Spec: `docs/superpowers/specs/2026-09-18-duet-design.md`, sections 6, 7 and stages 4 to 6. Plan 1 (`2026-09-18-duet-1-foundation.md`) built `strokes`, `calib`, `controller`, and the corner-mark warp in `vision.py` already.

**Tech Stack:** Python 3.12 venv at `code/hackathon/.venv`: viam-sdk 0.80.0, numpy, opencv-python-headless, scikit-image, skan, shapely 2.1, anthropic 1.7.0, pydantic 2.13, pytest. All already installed on 2026-09-18 evening.

**Working conventions for every task:**
- Run everything from `code/hackathon` with the venv active: `cd "/Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/code/hackathon" && source .venv/bin/activate`.
- Scripts run as modules: `python -m duet.claude_bench`.
- Git: stay on `feat/duet-design`. Commit messages use `<type>: <description>`. Never commit `.env` (it now holds `ANTHROPIC_API_KEY` as well as the Viam credentials).
- Nothing in this plan touches the machine. Every step runs on the Mac alone. Steps that would need the arm or the live camera are listed at the end under "Morning hardware steps" and are not executed here.
- Board constants: the writing surface is 176 x 240 mm (`cfg.BOARD_W_MM`, `cfg.BOARD_H_MM`), 4 px/mm, so a warped board image is 704 x 960 px. Board x runs along the short edge.
- Real fixtures: `captures/look.jpg` (17:50, board with a 60 mm square at the center) and `captures/calib_frame.jpg` (18:40, that square wiped, a 20 mm square at board (15, 15)) were both taken from the look pose. `duet/data/calibration.json` holds the corner marks for that pose. `captures/look.dep` is the depth frame from the same pose (`DEPTHMAP` magic, big-endian uint64 width and height, big-endian uint16 millimeters; the board sits at about 680 to 750 mm, tilted). The differences between the two photos already diff and trace to one polyline with the existing code, so stage 4's exit test is met by the fixture test in Task 1.

---

### Task 1: Constants, fixtures, SVG rendering

**Files:**
- Modify: `code/hackathon/duet/config.py` (append)
- Create: `code/hackathon/duet/svg.py`
- Create: `code/hackathon/tests/fixtures/look_before.jpg`, `look_after.jpg`, `look_depth.npz`, `board_blank.jpg`
- Create: `code/hackathon/tests/conftest.py`
- Test: `code/hackathon/tests/test_svg.py`, `code/hackathon/tests/test_vision_fixtures.py`

- [ ] **Step 1: Append the plan 2 constants to `config.py`**

Append to `code/hackathon/duet/config.py`:

```python

# ---- perception and brain (plan 2) -----------------------------------------------------------
FIXTURES_DIR = PACKAGE_DIR.parent / "tests" / "fixtures"

DOCK_SLOTS = ("green",)         # markers in the dock; single-marker rig decided 2026-09-18
COLOR_HEX = {"green": "#1b8f3a", "red": "#c62828", "blue": "#1e56c9", "black": "#222222"}

CLEARANCE_MM = 3.0              # unattached robot strokes keep this far from existing ink
DOT_TOLERANCE_MM = 3.0          # a docked marker's dot further than this from its recorded spot is "moved"
DOT_MIN_AREA_PX = 30            # smaller color blobs are noise, not a marker's end plug

STILL_WINDOW_S = 0.6            # frames compared for the stillness reading
STILL_THRESH = 3.0              # mean absolute gray difference between frames that still counts as still
STILL_S = 1.5                   # dock rule: markers home, still, no hand for this long
HELD_QUIET_S = 2.0              # held rule: still and no hand for this long after activity

HAND_HEIGHT_MM = 25.0           # anything this far above the board plane, over the board or dock, is a hand
HAND_AREA_MM2 = 2000.0
COVERAGE_END = 0.33             # the session ends when this fraction of the drawable area is inked

CLAUDE_MODEL = "claude-opus-5"
CLAUDE_TIMEOUT_S = 8.0
CLAUDE_MAX_TOKENS = 6000        # a Long proposal is a few dozen strokes of JSON
CLAUDE_EFFORT = "low"

ARTIST = "haring"
HARING = {"pass_gap_mm": 1.5, "tick_every_mm": 25.0, "tick_min_mm": 8.0, "tick_max_mm": 15.0,
          "outline_offset_mm": 6.0}
# A small glyph the robot signs with, in mm relative to its own top-left; the session places it in a corner.
SIGNATURE_MM = [[(0.0, 8.0), (4.0, 0.0), (8.0, 8.0)], [(2.0, 5.0), (6.0, 5.0)]]
```

- [ ] **Step 2: Copy the real captures into committed fixtures**

Run:
```bash
mkdir -p tests/fixtures && cp captures/look.jpg tests/fixtures/look_before.jpg && cp captures/calib_frame.jpg tests/fixtures/look_after.jpg && python - <<'EOF'
import struct, json, numpy as np, cv2
from pathlib import Path
from duet import vision
d = Path("captures/look.dep").read_bytes()
w, h = struct.unpack(">QQ", d[8:24])
depth = np.frombuffer(d, dtype=">u2", offset=24, count=w * h).reshape(h, w).astype(np.uint16)
np.savez_compressed("tests/fixtures/look_depth.npz", depth=depth)
cal = json.loads(Path("duet/data/calibration.json").read_text())
f = cv2.imread("tests/fixtures/look_after.jpg")
q = vision.find_corner_marks(f, expected=cal["marks_image"])
board = vision.warp_to_board(f, vision.board_quad(q, cal["board_tl_index"]))
cv2.imwrite("tests/fixtures/board_blank.jpg", board, [cv2.IMWRITE_JPEG_QUALITY, 92])
print(depth.shape, board.shape)
EOF
ls -la tests/fixtures
```
Expected: `(720, 1280) (960, 704, 3)` and four files. `look_depth.npz` should be well under 1 MB.

- [ ] **Step 3: Write the shared fixtures file**

`code/hackathon/tests/conftest.py`:

```python
import json

import cv2
import numpy as np
import pytest

from duet import config as cfg


@pytest.fixture(scope="session")
def calibration() -> dict:
    return json.loads(cfg.CALIBRATION_PATH.read_text())


@pytest.fixture(scope="session")
def look_before() -> np.ndarray:
    return cv2.imread(str(cfg.FIXTURES_DIR / "look_before.jpg"))


@pytest.fixture(scope="session")
def look_after() -> np.ndarray:
    return cv2.imread(str(cfg.FIXTURES_DIR / "look_after.jpg"))


@pytest.fixture(scope="session")
def look_depth() -> np.ndarray:
    return np.load(cfg.FIXTURES_DIR / "look_depth.npz")["depth"]


@pytest.fixture(scope="session")
def board_blank() -> np.ndarray:
    return cv2.imread(str(cfg.FIXTURES_DIR / "board_blank.jpg"))
```

- [ ] **Step 4: Write the failing tests**

`code/hackathon/tests/test_svg.py`:

```python
from duet import config as cfg
from duet import svg


def test_render_has_viewbox_in_board_millimeters_and_one_polyline_per_stroke():
    out = svg.render([{"id": "human", "color": "#222222", "polylines": [[(10, 10), (50, 10)], [(10, 20), (50, 60)]]},
                      {"id": "plan", "color": "#1b8f3a", "dashed": True, "polylines": [[(60, 60), (80, 80)]]}])
    assert out.startswith("<svg")
    assert f'viewBox="0 0 {cfg.BOARD_W_MM:.0f} {cfg.BOARD_H_MM:.0f}"' in out
    assert out.count("<polyline") == 3
    assert 'id="plan"' in out and "stroke-dasharray" in out
    assert "10.00,10.00 50.00,10.00" in out


def test_render_skips_degenerate_polylines():
    out = svg.render([{"id": "x", "color": "#000", "polylines": [[(1, 1)], []]}])
    assert "<polyline" not in out
```

`code/hackathon/tests/test_vision_fixtures.py`:

```python
from duet import vision


def warp(frame, calibration):
    quad = vision.find_corner_marks(frame, expected=calibration["marks_image"])
    return vision.warp_to_board(frame, vision.board_quad(quad, calibration["board_tl_index"]))


def test_real_captures_diff_to_the_small_square_drawn_by_the_robot(look_before, look_after, calibration):
    before, after = warp(look_before, calibration), warp(look_after, calibration)
    mask, coverage = vision.new_ink(after, before)
    polylines = vision.trace(mask)
    assert 500 < int((mask > 0).sum()) < 5000
    assert coverage < 0.01
    assert len(polylines) >= 1
    xs = [x for pl in polylines for x, _ in pl]
    ys = [y for pl in polylines for _, y in pl]
    assert 14 <= min(xs) <= 18 and 30 <= max(xs) <= 37     # the 20 mm square at board (15, 15)
    assert 14 <= min(ys) <= 18 and 26 <= max(ys) <= 37     # its bottom edge fades into the glare stripe


def test_wiped_ink_is_not_new_ink(look_before, look_after, calibration):
    before, after = warp(look_before, calibration), warp(look_after, calibration)
    mask, _ = vision.new_ink(after, before)   # the 60 mm center square was wiped between the two: it got lighter, not darker
    ys, xs = (mask > 0).nonzero()
    center = (xs > 50 * vision.PX_PER_MM) & (xs < 130 * vision.PX_PER_MM) & (ys > 60 * vision.PX_PER_MM) & (ys < 180 * vision.PX_PER_MM)
    assert not center.any()
```

- [ ] **Step 5: Run the tests to verify they fail**

Run: `python -m pytest tests/test_svg.py tests/test_vision_fixtures.py -q`
Expected: `ModuleNotFoundError: No module named 'duet.svg'` for the SVG file; the fixture tests may already pass (the vision code exists), which is fine.

- [ ] **Step 6: Write `svg.py`**

`code/hackathon/duet/svg.py`:

```python
"""SVG rendering of polylines in board millimeters, for previews, the page, and the session record."""
from __future__ import annotations

from duet import config as cfg
from duet.strokes import Polyline


def _points(pl: Polyline) -> str:
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pl)


def render(layers: list[dict], width_mm: float = cfg.BOARD_W_MM, height_mm: float = cfg.BOARD_H_MM) -> str:
    """layers: [{"id": "human", "color": "#hex", "polylines": [...], "width": 1.0, "dashed": False}, ...].
    The drawable inset is drawn as a faint rectangle so previews show where strokes may go."""
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_mm:.0f} {height_mm:.0f}" width="100%">',
        f'<rect width="{width_mm:.0f}" height="{height_mm:.0f}" fill="#ffffff"/>',
        f'<rect x="{cfg.INSET_MM:.0f}" y="{cfg.INSET_MM:.0f}" width="{width_mm - 2 * cfg.INSET_MM:.0f}" '
        f'height="{height_mm - 2 * cfg.INSET_MM:.0f}" fill="none" stroke="#dddddd" stroke-width="0.5"/>',
    ]
    for layer in layers:
        dash = ' stroke-dasharray="3 2"' if layer.get("dashed") else ""
        parts.append(f'<g id="{layer.get("id", "")}" fill="none" stroke="{layer["color"]}" '
                     f'stroke-width="{layer.get("width", 1.0)}" stroke-linecap="round" stroke-linejoin="round"{dash}>')
        for pl in layer["polylines"]:
            if len(pl) >= 2:
                parts.append(f'<polyline points="{_points(pl)}"/>')
        parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts)
```

- [ ] **Step 7: Run the tests to verify they pass**

Run: `python -m pytest tests/test_svg.py tests/test_vision_fixtures.py -q`
Expected: `4 passed`. If the fixture bounds fail by a millimeter or two, print `polylines` and widen the bound in the test to what the real trace gives; the point of the test is that the square, and only the square, is found.

- [ ] **Step 8: Commit**

```bash
git add duet/config.py duet/svg.py tests/conftest.py tests/test_svg.py tests/test_vision_fixtures.py tests/fixtures/
git commit -m "feat: plan 2 constants, real-capture fixtures, SVG rendering"
```

---

### Task 2: Depth decoding, frame poller, and the trigger's readings

**Files:**
- Modify: `code/hackathon/duet/camera.py`
- Modify: `code/hackathon/duet/vision.py` (append; small refactor of `warp_to_board`)
- Modify: `code/hackathon/duet/calibrate.py` (offline `--plane` and `--dock` verbs)
- Modify: `code/hackathon/duet/data/calibration.json` (generated by the script)
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


def quad_and_h(calibration):
    quad = np.array(calibration["marks_image"], dtype=np.float32)
    board = vision.board_quad(quad, calibration["board_tl_index"])
    return quad, vision.board_homography(board)


def test_mm_per_px_from_the_real_quad_is_about_a_third_of_a_millimeter(calibration):
    quad, _ = quad_and_h(calibration)
    assert 0.6 <= vision.mm_per_px(quad) <= 1.0   # ~210 px across a 176 mm board at the look pose


def test_to_board_mm_maps_the_marks_to_the_board_corners(calibration):
    quad, h = quad_and_h(calibration)
    board = vision.board_quad(quad, calibration["board_tl_index"])
    pts = vision.to_board_mm(h, [tuple(p) for p in board])
    assert all(abs(a - b) < 0.01 for p, ref in zip(pts, [(0, 0), (cfg.BOARD_W_MM, 0), (cfg.BOARD_W_MM, cfg.BOARD_H_MM), (0, cfg.BOARD_H_MM)]) for a, b in zip(p, ref))


def test_plane_fit_on_a_synthetic_tilted_plane():
    h, w = 120, 160
    ys, xs = np.mgrid[0:h, 0:w]
    depth = (600 + 0.5 * xs - 0.25 * ys).astype(np.uint16)
    depth[5:10, 5:10] = 0                       # holes are ignored
    depth[50:60, 50:60] = 3000                   # a glare reflection reads far away and must not skew the fit
    a, b, c = vision.fit_plane(depth, np.ones((h, w), np.uint8))
    assert abs(a - 0.5) < 0.02 and abs(b + 0.25) < 0.02 and abs(c - 600) < 2


def test_hand_present_on_synthetic_depth():
    h, w = 120, 160
    expected = vision.plane_depth((h, w), (0.0, 0.0, 700.0))
    depth = np.full((h, w), 700, np.uint16)
    region = np.ones((h, w), np.uint8)
    assert vision.hand_present(depth, region, expected, mm2_per_px=1.0) is False
    depth[40:80, 40:100] = 640                   # 60 mm above the plane, 2400 px = 2400 mm²
    assert vision.hand_present(depth, region, expected, mm2_per_px=1.0) is True
    assert vision.hand_present(depth, region, expected, mm2_per_px=0.5) is False   # too small at half the scale
    depth[:] = 700
    depth[40:80, 40:100] = 690                   # only 10 mm up: a sheet of paper, not a hand
    assert vision.hand_present(depth, region, expected, mm2_per_px=1.0) is False


def test_reference_depth_lowers_the_expected_surface_inside_the_dock():
    dock = [[10, 10], [30, 10], [30, 30], [10, 30]]
    ref = vision.reference_depth((40, 40), (0.0, 0.0, 700.0), [(dock, 30.0)])
    assert ref[5, 5] == 700 and ref[20, 20] == 670


def test_no_hand_in_the_real_look_depth(look_depth, calibration):
    quad, _ = quad_and_h(calibration)
    region = vision.polygon_mask(look_depth.shape, [calibration["board_region_image"], calibration["dock_region_image"]])
    expected = vision.reference_depth(look_depth.shape, tuple(calibration["plane"]),
                                      [(calibration["dock_region_image"], calibration.get("dock_offset_mm", 0.0))])
    mm2 = vision.mm_per_px(quad) ** 2
    assert vision.hand_present(look_depth, region, expected, mm2) is False
    with_hand = look_depth.copy()
    cx, cy = int(quad[:, 0].mean()), int(quad[:, 1].mean())
    with_hand[cy - 30:cy + 30, cx - 40:cx + 40] = 600      # a hand-sized blob 100 mm above the board
    assert vision.hand_present(with_hand, region, expected, mm2) is True


def green_frame(cx, cy, r=6):
    f = np.full((200, 300, 3), 235, np.uint8)
    cv2.circle(f, (cx, cy), r, (60, 170, 60), -1)   # a green end plug
    return f


def test_dock_dots_home_moved_missing(calibration):
    _, h = quad_and_h(calibration)
    slots = {"green": {"xy": [150, 100], "hsv_lo": [40, 60, 60], "hsv_hi": [85, 255, 255]}}
    scale = vision.mm_per_px(np.array(calibration["marks_image"], np.float32))
    home = vision.dock_dots(green_frame(150, 100), slots, h)["green"]
    assert home.status == "home" and math.hypot(*home.displacement_mm) < 1.0
    moved = vision.dock_dots(green_frame(150 + int(8 / scale), 100), slots, h)["green"]
    assert moved.status == "moved" and 4 < math.hypot(*moved.displacement_mm) < 14   # 8 mm nominal; perspective varies the scale off-board
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
Expected: failures on `camera.decode_depth`, `camera.grab_frame`, `camera.FrameSource`, `vision.board_homography`, and the rest (AttributeError / KeyError on `board_region_image`).

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

- [ ] **Step 4: Append the readings to `vision.py` and route the warp through a shared homography**

In `code/hackathon/duet/vision.py`, replace the existing `warp_to_board` function with:

```python
def board_homography(quad_board_order: np.ndarray) -> np.ndarray:
    """3x3 map from image pixels to warped-board pixels (PX_PER_MM, origin at the board's top-left)."""
    w, h = BOARD_PX
    dst = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
    return cv2.getPerspectiveTransform(np.asarray(quad_board_order, dtype=np.float32), dst)


def warp_to_board(bgr: np.ndarray, quad_board_order: np.ndarray) -> np.ndarray:
    """Flat top-down board image at PX_PER_MM, origin at the board's top-left."""
    return cv2.warpPerspective(bgr, board_homography(quad_board_order), BOARD_PX)


def to_board_mm(homography: np.ndarray, pts_px: list[Point]) -> list[Point]:
    """Image pixels to board millimeters through the corner-mark homography."""
    arr = np.array([pts_px], dtype=np.float32)
    out = cv2.perspectiveTransform(arr, homography)[0]
    return [(float(x) / PX_PER_MM, float(y) / PX_PER_MM) for x, y in out]


def mm_per_px(quad_image: np.ndarray) -> float:
    """Average scale at the look pose: the board's area over the corner quad's pixel area."""
    area_px = abs(cv2.contourArea(np.asarray(quad_image, dtype=np.float32)))
    return math.sqrt(cfg.BOARD_W_MM * cfg.BOARD_H_MM / area_px)
```

and add `import math` and `from dataclasses import dataclass` to the imports at the top. Then append at the end of the file:

```python


# ---- trigger readings: hand from depth, dock dots, stillness -------------------------------------

def polygon_mask(shape_hw: tuple[int, int], polygons: list) -> np.ndarray:
    """1 inside any of the polygons (lists of (x, y) image points), 0 elsewhere."""
    m = np.zeros(shape_hw[:2], dtype=np.uint8)
    for poly in polygons:
        cv2.fillPoly(m, [np.asarray(poly, dtype=np.int32)], 1)
    return m


def fit_plane(depth: np.ndarray, mask: np.ndarray) -> tuple[float, float, float]:
    """Least-squares plane z = a*x + b*y + c through the valid readings inside `mask`. Readings far
    from the median (glare on the board reflects the ceiling and reads as several meters) are
    dropped before the fit, and the fit is repeated without outliers."""
    ys, xs = np.nonzero((mask > 0) & (depth > 0))
    z = depth[ys, xs].astype(np.float64)
    if z.size < 100:
        raise ValueError("not enough valid depth readings inside the region")
    med = np.median(z)
    keep = np.abs(z - med) < 80
    a = np.column_stack([xs, ys, np.ones_like(xs)]).astype(np.float64)
    coef, *_ = np.linalg.lstsq(a[keep], z[keep], rcond=None)
    resid = np.abs(a @ coef - z)
    keep = resid < 15
    if keep.sum() >= 100:
        coef, *_ = np.linalg.lstsq(a[keep], z[keep], rcond=None)
    return float(coef[0]), float(coef[1]), float(coef[2])


def plane_depth(shape_hw: tuple[int, int], plane: tuple[float, float, float]) -> np.ndarray:
    a, b, c = plane
    ys, xs = np.mgrid[0:shape_hw[0], 0:shape_hw[1]]
    return (a * xs + b * ys + c).astype(np.float32)


def reference_depth(shape_hw: tuple[int, int], plane: tuple[float, float, float],
                    offsets: list[tuple[list, float]]) -> np.ndarray:
    """The surface a hand is measured against: the board plane, lowered by `offset_mm` inside each
    polygon (the dock's putty stands above the board plane, so its own surface is the reference there)."""
    ref = plane_depth(shape_hw, plane)
    for polygon, offset_mm in offsets:
        ref[polygon_mask(shape_hw, [polygon]) > 0] -= float(offset_mm)
    return ref


def hand_present(depth: np.ndarray, region_mask: np.ndarray, expected_depth: np.ndarray,
                 mm2_per_px: float, height_mm: float = cfg.HAND_HEIGHT_MM,
                 area_mm2: float = cfg.HAND_AREA_MM2) -> bool:
    """True if a connected blob inside the region sits more than `height_mm` above the expected
    surface and covers at least `area_mm2`. Zero depth (no reading) never counts."""
    above = ((depth > 0) & (depth.astype(np.float32) < expected_depth - height_mm) & (region_mask > 0)).astype(np.uint8)
    above = cv2.morphologyEx(above, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, _, stats, _ = cv2.connectedComponentsWithStats(above)
    return any(stats[i, cv2.CC_STAT_AREA] * mm2_per_px >= area_mm2 for i in range(1, n))


@dataclass(frozen=True)
class DotReading:
    status: str                              # "home" | "moved" | "missing"
    displacement_mm: tuple[float, float]     # where the dot is relative to its recorded spot, board axes


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

- [ ] **Step 5: Add the offline calibration verbs and run them**

In `code/hackathon/duet/calibrate.py`, replace the docstring's usage lines with:

```python
"""Camera calibration from the look pose: find the four corner marks, record where they are and
which one is the board's top-left, and save a warped board image to check.

    python -m duet.calibrate                 detect the marks and save captures/calib_marks.jpg with labels A-D
    python -m duet.calibrate --tl C          record the calibration with image corner C as the board's top-left
    python -m duet.calibrate --check         re-detect within the calibrated regions and save the warped board
    python -m duet.calibrate --plane FILE    OFFLINE: fit the board plane for the hand check from a saved
                                             depth map (captures/look.dep or tests/fixtures/look_depth.npz)
    python -m duet.calibrate --dock x0 y0 x1 y1
                                             OFFLINE: record the dock tub's image rectangle for the hand check

The arm must be at the look pose for the live verbs. Board top-left is the corner you touched off as `corner tl`.
"""
```

and replace `main` with:

```python
def offline(argv: list[str]) -> bool:
    """The verbs that need no camera. Returns True when one ran."""
    cal = load_calibration()
    if "--plane" in argv:
        path = Path(argv[argv.index("--plane") + 1])
        if path.suffix == ".npz":
            depth = np.load(path)["depth"]
        else:
            from duet.camera import decode_depth
            depth = decode_depth(path.read_bytes())
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
    if "--dock" in argv:
        i = argv.index("--dock")
        x0, y0, x1, y1 = (int(v) for v in argv[i + 1:i + 5])
        cal["dock_region_image"] = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
        save_calibration(cal)
        print(f"dock region saved: x {x0}..{x1}, y {y0}..{y1}")
        return True
    return False


def main(argv: list[str]) -> None:
    if offline(argv):
        return
    CAPTURES.mkdir(exist_ok=True)
    frame = asyncio.run(capture())
    cv2.imwrite(str(CAPTURES / "calib_frame.jpg"), frame)
    if "--check" in argv:
        cal = load_calibration()
        quad = vision.find_corner_marks(frame, expected=cal["marks_image"])
        drift = max(float(np.hypot(*(np.array(q) - np.array(e)))) for q, e in zip(quad, cal["marks_image"]))
        board = vision.warp_to_board(frame, vision.board_quad(quad, cal["board_tl_index"]))
        cv2.imwrite(str(CAPTURES / "calib_board.jpg"), board)
        print(f"marks re-found; max drift {drift:.1f} px ({drift / vision.PX_PER_MM:.2f} mm). "
              f"Warped board saved to captures/calib_board.jpg")
        return
    quad = vision.find_corner_marks(frame)
    cv2.imwrite(str(CAPTURES / "calib_marks.jpg"), annotate(frame, quad))
    print("marks (image order A=top-left, B=top-right, C=bottom-right, D=bottom-left):",
          [(n, round(float(x)), round(float(y))) for n, (x, y) in zip(LABELS, quad)])
    if "--tl" not in argv:
        print("saved captures/calib_marks.jpg. Re-run with --tl <letter> to record which mark is the board's top-left.")
        return
    letter = argv[argv.index("--tl") + 1].upper()
    if letter not in LABELS:
        raise SystemExit("--tl needs A, B, C, or D")
    k = LABELS.index(letter)
    cal = load_calibration()
    cal.update({
        "marks_image": [[float(x), float(y)] for x, y in quad],
        "board_tl_index": k,
        "px_per_mm": vision.PX_PER_MM,
        "board_mm": [cfg.BOARD_W_MM, cfg.BOARD_H_MM],
    })
    save_calibration(cal)
    board = vision.warp_to_board(frame, vision.board_quad(quad, k))
    cv2.imwrite(str(CAPTURES / "calib_board.jpg"), board)
    print(f"calibration saved to {cfg.CALIBRATION_PATH}; warped board in captures/calib_board.jpg")
```

(The `--tl` branch now merges into the existing file instead of overwriting it, so a re-calibration of the marks keeps the plane and regions.)

Run (the dock rectangle first, so the plane step can measure the dock's height):
```bash
python -m duet.calibrate --dock 880 330 1020 505 && python -m duet.calibrate --plane tests/fixtures/look_depth.npz && cat duet/data/calibration.json
```
Expected: a plane with `c` around 700 and a median residual of a few millimeters; a dock offset of a few tens of millimeters; `calibration.json` gains `dock_region_image`, `plane`, `board_region_image`, `mm_per_px`, `dock_offset_mm`. The dock rectangle was read off `captures/calib_frame.jpg` (the tub is clear plastic on a white desk, so it is a guess to within 20 px; the morning check re-measures it with the marker in the tub).

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python -m pytest tests/test_camera.py tests/test_readings.py tests/test_vision.py -q`
Expected: all pass. If `test_no_hand_in_the_real_look_depth` fails on the no-hand case, print the largest blob's area from `hand_present` (temporarily) and check whether the marker held in the gripper at the bottom of the frame lies inside `dock_region_image`; shrink the rectangle rather than raising the thresholds.

- [ ] **Step 7: Commit**

```bash
git add duet/camera.py duet/vision.py duet/calibrate.py duet/data/calibration.json tests/test_camera.py tests/test_readings.py
git commit -m "feat: depth decode, frame poller, hand and dock-dot readings, board plane calibration"
```

---

### Task 3: Trigger state machine

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
    fires = [t for t, e in events if e == Event("fire")]
    assert fires == [4.6]


def test_dock_moved_marker_asks_for_a_reseat_then_fires_once_home():
    tr = Trigger("dock", quiet_s=1.0)
    events = run(tr, [r(0, green="missing"), r(1, green="moved"), r(2, green="moved"), r(3, green="missing"),
                      r(4, green="home"), r(5, green="home"), r(6, green="home")])
    kinds = [e for _, e in events if e]
    assert kinds == [Event("reseat", ("green",)), Event("reseat_ok"), Event("fire")]


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
        if self.handoff == "dock":
            settled, event = self._dock(r)
        else:
            settled, event = self._held(r)
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

### Task 4: Proposal schema and the planner

**Files:**
- Create: `code/hackathon/duet/proposal.py`
- Create: `code/hackathon/duet/planner.py`
- Test: `code/hackathon/tests/test_planner.py`

- [ ] **Step 1: Write the failing tests**

`code/hackathon/tests/test_planner.py`:

```python
import math

from shapely.geometry import LineString, Polygon

from duet import config as cfg
from duet import planner
from duet.proposal import Proposal, Stroke, to_polyline
from duet.strokes import length


def poly(*pts, attached=False):
    return Stroke(kind="polyline", points=[[x, y] for x, y in pts], attached=attached)


def test_proposal_parses_from_the_json_claude_returns():
    p = Proposal.model_validate({"sees": "A fish.", "adds": "Bubbles.", "color": "green",
                                 "strokes": [{"kind": "circle", "cx": 90, "cy": 60, "r": 5, "attached": False},
                                             {"kind": "polyline", "points": [[20, 20], [40, 40]]}]})
    assert p.strokes[0].kind == "circle" and p.strokes[1].attached is False


def test_circle_and_arc_become_polylines():
    c = to_polyline(Stroke(kind="circle", cx=50, cy=50, r=10))
    assert c[0] == c[-1] and len(c) == 37
    assert all(abs(math.dist(p, (50, 50)) - 10) < 1e-6 for p in c)
    a = to_polyline(Stroke(kind="arc", cx=50, cy=50, r=10, start_deg=0, end_deg=90))
    assert len(a) >= 5 and abs(a[0][0] - 60) < 1e-6 and abs(a[-1][1] - 60) < 1e-6


def test_clip_keeps_only_the_part_inside_the_inset():
    out = planner.clip([(0, 100), (100, 100)], planner.drawable_polygon())
    assert out == [[(cfg.INSET_MM, 100.0), (100.0, 100.0)]]
    assert planner.clip([(0, 0), (5, 5)], planner.drawable_polygon()) == []


def test_clip_splits_a_stroke_that_leaves_and_re_enters():
    w = cfg.BOARD_W_MM
    out = planner.clip([(30, 100), (w + 10, 100), (w + 10, 120), (30, 120)], planner.drawable_polygon())
    assert len(out) == 2


def test_unattached_stroke_next_to_ink_is_pushed_clear():
    ink = [[(80, 50), (80, 150)]]
    out = planner.validate([poly((82, 60), (82, 140))], ink, 10_000)
    assert len(out) == 1
    assert all(x >= 80 + cfg.CLEARANCE_MM for x, _ in out[0])


def test_unattached_stroke_crossing_ink_is_dropped_but_attached_is_kept():
    ink = [[(80, 50), (80, 150)]]
    assert planner.validate([poly((60, 100), (100, 100))], ink, 10_000) == []
    kept = planner.validate([poly((60, 100), (100, 100), attached=True)], ink, 10_000)
    assert kept == [[(60.0, 100.0), (100.0, 100.0)]]


def test_budget_cuts_in_order():
    strokes = [poly((20, 20), (120, 20)), poly((20, 40), (120, 40)), poly((20, 60), (120, 60))]
    out = planner.validate(strokes, [], 150)
    assert len(out) == 2 and length(out[0]) == 100 and abs(length(out[1]) - 50) < 1e-6
    assert out[0][0][1] == 20 and out[1][0][1] == 40


def test_validate_with_no_ink_and_no_strokes():
    assert planner.validate([], [], 100) == []
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_planner.py -q`
Expected: `ModuleNotFoundError: No module named 'duet.proposal'`

- [ ] **Step 3: Write `proposal.py`**

`code/hackathon/duet/proposal.py`:

```python
"""What Claude returns each turn, as a Pydantic schema for structured output. Flat on purpose: one
Stroke model with a `kind` field, so the JSON schema stays simple for the model to satisfy."""
from __future__ import annotations

import math
from typing import Literal

from pydantic import BaseModel, Field

from duet.strokes import Polyline


class Stroke(BaseModel):
    kind: Literal["polyline", "circle", "arc"]
    points: list[list[float]] = Field(default_factory=list,
                                      description="polyline vertices as [x, y] in board millimeters; empty for circle and arc")
    cx: float = Field(default=0.0, description="circle or arc center x in mm")
    cy: float = Field(default=0.0, description="circle or arc center y in mm")
    r: float = Field(default=0.0, description="circle or arc radius in mm")
    start_deg: float = Field(default=0.0, description="arc start angle, degrees, 0 = +x, 90 = +y (down)")
    end_deg: float = Field(default=0.0, description="arc end angle in degrees")
    attached: bool = Field(default=False, description="true if this stroke is meant to touch existing ink")


class Proposal(BaseModel):
    sees: str = Field(description="one sentence: what the drawing is now")
    adds: str = Field(description="one sentence: what you add and why")
    color: str = Field(description="one of the colors offered this turn")
    strokes: list[Stroke]


def to_polyline(s: Stroke) -> Polyline:
    if s.kind == "polyline":
        return [(float(x), float(y)) for x, y in (p for p in s.points if len(p) == 2)]
    if s.kind == "circle":   # k % 36 closes the ring exactly: the last point is the first, bit for bit
        return [(s.cx + s.r * math.cos(2 * math.pi * (k % 36) / 36), s.cy + s.r * math.sin(2 * math.pi * (k % 36) / 36))
                for k in range(37)]
    sweep = s.end_deg - s.start_deg
    n = max(4, int(abs(sweep) / 10))
    return [(s.cx + s.r * math.cos(math.radians(s.start_deg + sweep * k / n)),
             s.cy + s.r * math.sin(math.radians(s.start_deg + sweep * k / n))) for k in range(n + 1)]
```

- [ ] **Step 4: Write `planner.py`**

`code/hackathon/duet/planner.py`:

```python
"""Validation of a proposal: clip to the drawable area, keep clear of existing ink, cut to the
budget. Pure geometry on board millimeters; the artist styler runs after this."""
from __future__ import annotations

import math

from shapely.affinity import translate
from shapely.geometry import LineString, MultiLineString, Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from duet import config as cfg
from duet.proposal import Stroke, to_polyline
from duet.strokes import Polyline, cut_to_budget


def drawable_polygon() -> Polygon:
    return box(cfg.INSET_MM, cfg.INSET_MM, cfg.BOARD_W_MM - cfg.INSET_MM, cfg.BOARD_H_MM - cfg.INSET_MM)


def _pieces(geom: BaseGeometry) -> list[Polyline]:
    if geom.is_empty:
        return []
    if isinstance(geom, LineString):
        pl = [(float(x), float(y)) for x, y in geom.coords]
        return [pl] if len(pl) >= 2 and geom.length >= 1.0 else []
    if isinstance(geom, MultiLineString):
        return [p for part in geom.geoms for p in _pieces(part)]
    if hasattr(geom, "geoms"):   # GeometryCollection: keep the line parts, drop points
        return [p for part in geom.geoms for p in _pieces(part)]
    return []


def clip(pl: Polyline, area: Polygon) -> list[Polyline]:
    """The parts of a polyline inside `area`, each as its own polyline."""
    if len(pl) < 2:
        return []
    return _pieces(LineString(pl).intersection(area))


def push_clear(pl: Polyline, ink_buffer: BaseGeometry, area: Polygon, step: float = cfg.CLEARANCE_MM) -> Polyline | None:
    """Shift a stroke away from nearby ink in steps of `step`, up to four times. None if it still
    touches the ink or would leave the drawable area: such a stroke is dropped."""
    line = LineString(pl)
    if not line.intersects(ink_buffer):
        return pl
    c, ic = line.centroid, ink_buffer.centroid
    vx, vy = c.x - ic.x, c.y - ic.y
    n = math.hypot(vx, vy)
    if n < 1e-6:
        vx, vy, n = 0.0, -1.0, 1.0
    for k in range(1, 5):
        moved = translate(line, xoff=vx / n * step * k, yoff=vy / n * step * k)
        if not moved.intersects(ink_buffer) and area.contains(moved):
            return [(float(x), float(y)) for x, y in moved.coords]
    return None


def validate(strokes: list[Stroke], existing_ink: list[Polyline], budget_mm: float) -> list[Polyline]:
    """Proposal strokes to drawable polylines: shapes to polylines, clipped to the inset, unattached
    strokes pushed CLEARANCE_MM clear of existing ink or dropped, order kept, cut at the budget."""
    area = drawable_polygon()
    lines = [LineString(pl) for pl in existing_ink if len(pl) >= 2]
    ink = unary_union(lines).buffer(cfg.CLEARANCE_MM) if lines else None
    out: list[Polyline] = []
    for s in strokes:
        for piece in clip(to_polyline(s), area):
            if ink is not None and not s.attached:
                piece = push_clear(piece, ink, area)
                if piece is None:
                    continue
            out.append(piece)
    return cut_to_budget(out, budget_mm)
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_planner.py -q`
Expected: `8 passed`

- [ ] **Step 6: Commit**

```bash
git add duet/proposal.py duet/planner.py tests/test_planner.py
git commit -m "feat: proposal schema and planner validation with tests"
```

---

### Task 5: Haring styler and fallback

**Files:**
- Create: `code/hackathon/duet/styles/__init__.py`
- Create: `code/hackathon/duet/styles/haring.py`
- Test: `code/hackathon/tests/test_haring.py`

- [ ] **Step 1: Write the failing tests**

`code/hackathon/tests/test_haring.py`:

```python
from shapely.geometry import LineString, Point, Polygon

from duet import config as cfg
from duet.strokes import length
from duet.styles import haring

LINE = [[(50.0, 50.0), (100.0, 50.0)]]


def test_each_stroke_becomes_two_passes_then_ticks():
    out = haring.style(LINE, 10_000)
    gap = cfg.HARING["pass_gap_mm"]
    assert abs(out[0][0][1] - (50 + gap / 2)) < 1e-6 and abs(out[1][0][1] - (50 - gap / 2)) < 1e-6
    assert out[1][0][0] == 100.0            # the second pass returns along the stroke
    assert len(out) == 2 + 2                 # 50 mm at one tick per 25 mm at energy 0.5
    for tick in out[2:]:
        assert cfg.HARING["tick_min_mm"] - 1e-6 <= length(tick) <= cfg.HARING["tick_max_mm"] + 1e-6


def test_tick_count_and_length_grow_with_energy():
    calm, wild = haring.style(LINE, 10_000, energy=0.0), haring.style(LINE, 10_000, energy=1.0)
    assert len(wild) > len(calm)
    assert length(wild[2]) > length(calm[2])


def test_direction_tilts_the_ticks():
    straight = haring.style(LINE, 10_000, direction=0.0)[2]
    tilted = haring.style(LINE, 10_000, direction=45.0)[2]
    dx0, dx1 = straight[1][0] - straight[0][0], tilted[1][0] - tilted[0][0]
    assert abs(dx0) < 1e-6 and abs(dx1) > 1.0


def test_styled_output_respects_the_budget():
    out = haring.style([[(30.0, 30.0), (150.0, 30.0), (150.0, 200.0)]], 90)
    assert sum(length(pl) for pl in out) <= 90 + 1e-6


def test_fallback_outlines_the_human_mark_and_stays_drawable():
    mark = [[(60.0, 60.0), (100.0, 60.0)]]
    out = haring.fallback(mark, 10_000)
    ring = Polygon(out[0])
    assert ring.is_valid and ring.contains(LineString(mark[0]))
    assert len(out) > 1                       # ticks follow the outline
    for tick in out[1:]:
        assert not ring.contains(Point(tick[1]))   # every tick points outward, away from the mark
    for pl in out:
        for x, y in pl:
            assert cfg.INSET_MM - 1e-6 <= x <= cfg.BOARD_W_MM - cfg.INSET_MM + 1e-6
            assert cfg.INSET_MM - 1e-6 <= y <= cfg.BOARD_H_MM - cfg.INSET_MM + 1e-6


def test_fallback_with_no_mark_is_empty():
    assert haring.fallback([], 400) == []
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_haring.py -q`
Expected: `ModuleNotFoundError: No module named 'duet.styles'`

- [ ] **Step 3: Write the package and the styler**

`code/hackathon/duet/styles/__init__.py`: empty file.

`code/hackathon/duet/styles/haring.py`:

```python
"""Keith Haring's grammar: one bold continuous outline plus short radiating ticks. Bold means two
passes PASS_GAP apart; ticks radiate from the line every TICK_EVERY mm, alternating sides, their
length and count set by `energy` and their angle tilted by `direction` (degrees). Pure."""
from __future__ import annotations

import math

from shapely.geometry import LineString, Point
from shapely.ops import unary_union

from duet import config as cfg
from duet.planner import clip, drawable_polygon
from duet.strokes import Polyline, cut_to_budget, length

H = cfg.HARING


def _normals(pl: Polyline) -> list[tuple[float, float]]:
    """Unit normal per vertex, the average of the adjoining segments' left-hand normals."""
    segs = []
    for a, b in zip(pl, pl[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1.0
        segs.append((-dy / n, dx / n))
    out = []
    for i in range(len(pl)):
        parts = [s for s in (segs[i - 1] if i > 0 else None, segs[i] if i < len(segs) else None) if s]
        nx, ny = sum(p[0] for p in parts) / len(parts), sum(p[1] for p in parts) / len(parts)
        n = math.hypot(nx, ny) or 1.0
        out.append((nx / n, ny / n))
    return out


def offset(pl: Polyline, d: float) -> Polyline:
    return [(x + nx * d, y + ny * d) for (x, y), (nx, ny) in zip(pl, _normals(pl))]


def _along(pl: Polyline, s: float) -> tuple[tuple[float, float], tuple[float, float]]:
    """Point and unit normal at arc length `s` along the polyline."""
    walked = 0.0
    for a, b in zip(pl, pl[1:]):
        d = math.dist(a, b)
        if walked + d >= s and d > 0:
            t = (s - walked) / d
            dx, dy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), (-dy, dx)
        walked += d
    a, b = pl[-2], pl[-1]
    d = math.dist(a, b) or 1.0
    return b, (-(b[1] - a[1]) / d, (b[0] - a[0]) / d)


def ticks(pl: Polyline, energy: float = 0.5, direction: float = 0.0, alternate: bool = True,
          side: float = 1.0) -> list[Polyline]:
    """Short strokes radiating from the polyline. `alternate` flips sides tick by tick (the style);
    with `alternate=False` every tick goes to `side` (the fallback outline wants them all outward)."""
    if len(pl) < 2:
        return []
    every = H["tick_every_mm"] / (0.5 + energy)
    size = H["tick_min_mm"] + (H["tick_max_mm"] - H["tick_min_mm"]) * energy
    total = length(pl)
    out: list[Polyline] = []
    s = every / 2
    rad = math.radians(direction)
    while s < total:
        p, (nx, ny) = _along(pl, s)
        tx, ty = nx * math.cos(rad) - ny * math.sin(rad), nx * math.sin(rad) + ny * math.cos(rad)
        out.append([p, (p[0] + tx * size * side, p[1] + ty * size * side)])
        s += every
        if alternate:
            side = -side
    return out


def style(strokes: list[Polyline], budget_mm: float, energy: float = 0.5, direction: float = 0.0) -> list[Polyline]:
    """Validated strokes in Haring's grammar, cut to the budget: all the bold passes first (so the
    figure lands even on a Short turn), then the ticks."""
    out: list[Polyline] = []
    for pl in strokes:
        if len(pl) < 2:
            continue
        gap = H["pass_gap_mm"] / 2
        out.append(offset(pl, gap))
        out.append(list(reversed(offset(pl, -gap))))
    for pl in strokes:
        out.extend(ticks(pl, energy, direction))
    return cut_to_budget(out, budget_mm)


def fallback(human_ink: list[Polyline], budget_mm: float, energy: float = 0.5, direction: float = 0.0) -> list[Polyline]:
    """When Claude is unavailable: an outline offset around the new mark plus ticks, in the grammar alone."""
    lines = [LineString(pl) for pl in human_ink if len(pl) >= 2]
    if not lines:
        return []
    shape = unary_union(lines).buffer(H["outline_offset_mm"]).simplify(0.5)
    polys = list(shape.geoms) if hasattr(shape, "geoms") else [shape]
    area = drawable_polygon()
    out: list[Polyline] = []
    for poly in polys:
        ring = [(float(x), float(y)) for x, y in poly.exterior.coords]
        # A ring that fits inside the drawable area stays whole (closed); one that crosses the edge is clipped into arcs.
        pieces = [ring] if area.contains(LineString(ring)) else clip(ring, area)
        out.extend(pieces)
        for piece in pieces:
            # Ticks must point away from the mark: try the first tick and flip every tick if it lands inside the outline.
            probe = ticks(piece, energy, direction, alternate=False, side=1.0)
            side = -1.0 if probe and poly.contains(Point(probe[0][1])) else 1.0
            out.extend(t for t in ticks(piece, energy, direction, alternate=False, side=side) if area.contains(LineString(t)))
    return cut_to_budget(out, budget_mm)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_haring.py -q`
Expected: `6 passed`

- [ ] **Step 5: Commit**

```bash
git add duet/styles/ tests/test_haring.py
git commit -m "feat: Haring styler and fallback grammar with tests"
```

---

### Task 6: The Claude turn and the latency bench

**Files:**
- Create: `code/hackathon/duet/claude_turn.py`
- Create: `code/hackathon/duet/claude_bench.py`
- Create: `code/hackathon/tests/fixtures/boards/*.jpg` (generated)
- Test: `code/hackathon/tests/test_claude_turn.py`

- [ ] **Step 1: Write the failing tests**

`code/hackathon/tests/test_claude_turn.py`:

```python
import asyncio
import base64
import json

import anthropic
import httpx2
import numpy as np
import pytest

from duet import claude_turn as ct
from duet import config as cfg
from duet.proposal import Proposal, Stroke


def ctx(**over):
    base = dict(human=[[(40.0, 60.0), (120.0, 60.0)]], history=[], artist="haring", colors=["green"],
                length="short", budget_mm=400.0, exchange=2, total=5)
    base.update(over)
    return ct.TurnContext(**base)


class Reply:
    def __init__(self, proposal, stop_reason="end_turn"):
        self.parsed_output = proposal
        self.stop_reason = stop_reason
        self.usage = type("U", (), {"input_tokens": 1200, "output_tokens": 300,
                                    "cache_read_input_tokens": 0, "cache_creation_input_tokens": 900})()


class FakeClient:
    """Only the attribute path ClaudeTurn uses: client.beta.messages.parse(**kwargs)."""
    def __init__(self, reply=None, error=None, delay_s=0.0):
        self.reply, self.error, self.delay_s = reply, error, delay_s
        self.kwargs = None
        outer = self

        class Messages:
            async def parse(self, **kwargs):
                outer.kwargs = kwargs
                await asyncio.sleep(outer.delay_s)
                if outer.error is not None:
                    raise outer.error
                return outer.reply
        self.beta = type("Beta", (), {"messages": Messages()})()


GOOD = Proposal(sees="A horizon line.", adds="A sun above it.", color="green",
                strokes=[Stroke(kind="circle", cx=80, cy=40, r=12)])


def test_grid_overlay_keeps_the_board_size(board_blank):
    out = ct.grid_overlay(board_blank)
    assert out.shape == board_blank.shape
    assert not np.array_equal(out, board_blank)


def test_prompt_carries_coordinates_budget_and_exchange(board_blank):
    content = ct.build_user_content(board_blank, ctx())
    assert content[0]["type"] == "image" and content[0]["source"]["media_type"] == "image/jpeg"
    base64.b64decode(content[0]["source"]["data"])
    text = content[1]["text"]
    assert "(40.0, 60.0)" in text and "(120.0, 60.0)" in text
    assert "Exchange 2 of 5" in text and "400 mm" in text and "green" in text
    assert "last exchange" not in text
    assert "last exchange" in ct.build_user_content(board_blank, ctx(exchange=5))[1]["text"]


def test_history_is_summarized_into_the_prompt(board_blank):
    text = ct.build_user_content(board_blank, ctx(history=[{"sees": "A fish.", "adds": "Bubbles.", "strokes": 3}]))[1]["text"]
    assert 'Turn 1: you saw "A fish." and added "Bubbles."' in text


def test_propose_returns_the_parsed_proposal_and_the_request_shape(board_blank):
    client = FakeClient(Reply(GOOD))
    result = asyncio.run(ct.ClaudeTurn(client).propose(board_blank, ctx()))
    assert result.source == "claude" and result.proposal.sees == "A horizon line."
    kw = client.kwargs
    assert kw["model"] == cfg.CLAUDE_MODEL and kw["output_format"] is Proposal
    assert kw["thinking"] == {"type": "adaptive"} and kw["output_config"] == {"effort": cfg.CLAUDE_EFFORT}
    assert kw["fallbacks"] == "default" and "server-side-fallback-2026-07-01" in kw["betas"]
    assert kw["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert kw["timeout"] == cfg.CLAUDE_TIMEOUT_S
    assert result.usage["input_tokens"] == 1200


def test_timeout_and_api_errors_fall_back(board_blank):
    req = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    slow = asyncio.run(ct.ClaudeTurn(FakeClient(error=anthropic.APITimeoutError(request=req))).propose(board_blank, ctx()))
    assert slow.source == "fallback" and slow.proposal is None and "timeout" in slow.error.lower()
    err = anthropic.APIConnectionError(request=req)
    down = asyncio.run(ct.ClaudeTurn(FakeClient(error=err)).propose(board_blank, ctx()))
    assert down.source == "fallback" and "APIConnectionError" in down.error


def test_refusal_and_empty_proposals_fall_back(board_blank):
    refused = asyncio.run(ct.ClaudeTurn(FakeClient(Reply(None, stop_reason="refusal"))).propose(board_blank, ctx()))
    assert refused.source == "fallback" and "refusal" in refused.error
    empty = Proposal(sees="x", adds="y", color="green", strokes=[])
    result = asyncio.run(ct.ClaudeTurn(FakeClient(Reply(empty))).propose(board_blank, ctx()))
    assert result.source == "fallback" and result.proposal is not None


def test_disallowed_color_is_replaced_by_the_first_offered(board_blank):
    odd = GOOD.model_copy(update={"color": "purple"})
    result = asyncio.run(ct.ClaudeTurn(FakeClient(Reply(odd))).propose(board_blank, ctx(colors=["green", "red"])))
    assert result.proposal.color == "green"


def test_api_key_comes_from_env_or_dotenv(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    assert ct.api_key() == "sk-test"
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    monkeypatch.setattr(ct.viam_conn, "load_env", lambda: {"ANTHROPIC_API_KEY": "sk-dotenv"})
    assert ct.api_key() == "sk-dotenv"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_claude_turn.py -q`
Expected: `ModuleNotFoundError: No module named 'duet.claude_turn'`

- [ ] **Step 3: Write `claude_turn.py`**

`code/hackathon/duet/claude_turn.py`:

```python
"""One Claude request per turn: the gridded board photo, the traced human strokes, and the turn
history go in; a validated Proposal comes out, or a fallback marker when the call fails or is slow.

    python -m duet.claude_turn      one request on tests/fixtures/board_blank.jpg, printed; needs ANTHROPIC_API_KEY in .env
"""
from __future__ import annotations

import asyncio
import base64
import os
from dataclasses import dataclass, field
from time import monotonic

import anthropic
import cv2
import numpy as np
from pydantic import ValidationError

import viam_conn
from duet import config as cfg
from duet import vision
from duet.proposal import Proposal
from duet.strokes import Polyline, resample

SYSTEM_PROMPT = f"""You are the robot half of Duet, a drawing game on a small dry-erase board. A visitor draws a mark with a marker; you look at a photo of the board and add to the drawing so that, over a few exchanges, the two of you make one picture together.

Coordinates are board millimeters with the origin at the top-left of the photo, x to the right and y down. The photo carries a labeled 20 mm grid along its edges. The board is {cfg.BOARD_W_MM:.0f} x {cfg.BOARD_H_MM:.0f} mm and only the area inside a {cfg.INSET_MM:.0f} mm margin is drawable.

How to draw:
- Respond to what is there. Read the visitor's mark generously (a wobbly oval may be a fish, a face, a stone) and build on that reading. Keep later turns consistent with what you said before.
- Draw simply: a few bold, legible shapes a marker can make, not many tiny ones. Use polylines, circles and arcs only, with coordinates you can read off the grid.
- Stay inside the drawable area. Keep new strokes at least 3 mm from existing ink unless a stroke is meant to touch it; mark such strokes attached.
- Keep the total path length within the budget you are given. Put the most important stroke first.
- sees: one short, specific sentence on what the drawing is now. adds: one short sentence on what you are adding and why. Both are shown to the visitor.
- color must be one of the colors offered."""

ARTIST_NOTES = {
    "haring": "Keith Haring: your strokes will be redrawn as one bold continuous outline with short "
              "radiating motion ticks, so give clean single lines and closed figures.",
}


def grid_overlay(board: np.ndarray, step_mm: int = 20) -> np.ndarray:
    """Faint grid lines every `step_mm` with millimeter labels along the top and left edges."""
    out = board.copy()
    h, w = out.shape[:2]
    px = vision.PX_PER_MM
    for x in range(0, int(cfg.BOARD_W_MM) + 1, step_mm):
        cv2.line(out, (x * px, 0), (x * px, h - 1), (205, 205, 205), 1)
        cv2.putText(out, str(x), (x * px + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 190), 1, cv2.LINE_AA)
    for y in range(0, int(cfg.BOARD_H_MM) + 1, step_mm):
        cv2.line(out, (0, y * px), (w - 1, y * px), (205, 205, 205), 1)
        cv2.putText(out, str(y), (2, y * px + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 190), 1, cv2.LINE_AA)
    return out


def photo_block(board: np.ndarray, quality: int = 85) -> dict:
    ok, jpg = cv2.imencode(".jpg", grid_overlay(board), [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("could not encode the board photo")
    return {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                        "data": base64.standard_b64encode(jpg.tobytes()).decode("ascii")}}


def fmt_polylines(polylines: list[Polyline], max_points: int = 24) -> str:
    lines = []
    for i, pl in enumerate(polylines, 1):
        pts = pl if len(pl) <= max_points else resample(pl, max(1.0, sum(
            ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5 for a, b in zip(pl, pl[1:])) / max_points))
        lines.append(f"  stroke {i}: " + " ".join(f"({x:.1f}, {y:.1f})" for x, y in pts[:max_points * 2]))
    return "\n".join(lines) if lines else "  (none traced)"


@dataclass(frozen=True)
class TurnContext:
    human: list[Polyline]                 # the visitor's new strokes this turn, board mm
    history: list[dict]                   # [{"sees": ..., "adds": ..., "strokes": n}, ...] for earlier turns
    artist: str
    colors: list[str]
    length: str
    budget_mm: float
    exchange: int
    total: int


@dataclass(frozen=True)
class TurnResult:
    proposal: Proposal | None
    source: str                           # "claude" | "fallback"
    latency_s: float
    error: str | None = None
    usage: dict = field(default_factory=dict)


def build_user_content(board: np.ndarray, ctx: TurnContext) -> list[dict]:
    history = "\n".join(f'  Turn {i}: you saw "{h["sees"]}" and added "{h["adds"]}".'
                        for i, h in enumerate(ctx.history, 1)) or "  (this is the first turn)"
    closing = " This is the last exchange: finish the piece." if ctx.exchange >= ctx.total else ""
    text = (f"Artist mode: {ARTIST_NOTES.get(ctx.artist, ctx.artist)}\n"
            f"Exchange {ctx.exchange} of {ctx.total}.{closing}\n"
            f"Length: {ctx.length}, budget {ctx.budget_mm:.0f} mm of path.\n"
            f"Colors available this turn: {', '.join(ctx.colors)}.\n"
            f"The visitor's new strokes this turn, in board mm:\n{fmt_polylines(ctx.human)}\n"
            f"History:\n{history}\n"
            f"Look at the photo, then answer with the JSON.")
    return [photo_block(board), {"type": "text", "text": text}]


def api_key() -> str | None:
    return os.environ.get("ANTHROPIC_API_KEY") or viam_conn.load_env().get("ANTHROPIC_API_KEY")


def make_client() -> anthropic.AsyncAnthropic:
    key = api_key()
    if not key:
        raise SystemExit("ANTHROPIC_API_KEY is missing: add it to code/hackathon/.env (never to a tracked file)")
    return anthropic.AsyncAnthropic(api_key=key, timeout=cfg.CLAUDE_TIMEOUT_S, max_retries=0)


class ClaudeTurn:
    def __init__(self, client, model: str = cfg.CLAUDE_MODEL):
        self.client = client
        self.model = model

    async def propose(self, board: np.ndarray, ctx: TurnContext) -> TurnResult:
        t0 = monotonic()
        try:
            reply = await self.client.beta.messages.parse(
                model=self.model,
                max_tokens=cfg.CLAUDE_MAX_TOKENS,
                system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": build_user_content(board, ctx)}],
                output_format=Proposal,
                thinking={"type": "adaptive"},
                output_config={"effort": cfg.CLAUDE_EFFORT},
                fallbacks="default",
                betas=["server-side-fallback-2026-07-01"],
                timeout=cfg.CLAUDE_TIMEOUT_S,
            )
        except anthropic.APITimeoutError:
            return TurnResult(None, "fallback", monotonic() - t0, f"timeout after {cfg.CLAUDE_TIMEOUT_S:.0f} s")
        except (anthropic.APIError, ValidationError) as exc:
            return TurnResult(None, "fallback", monotonic() - t0, f"{type(exc).__name__}: {exc}")
        dt = monotonic() - t0
        usage = {k: getattr(reply.usage, k, None) for k in
                 ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")}
        if reply.stop_reason == "refusal":
            return TurnResult(None, "fallback", dt, "refusal", usage)
        proposal = reply.parsed_output
        if proposal is None:
            return TurnResult(None, "fallback", dt, "no parsed output", usage)
        if proposal.color not in ctx.colors:
            proposal = proposal.model_copy(update={"color": ctx.colors[0]})
        if not proposal.strokes:
            return TurnResult(proposal, "fallback", dt, "empty proposal", usage)
        return TurnResult(proposal, "claude", dt, None, usage)


async def _main() -> None:
    board = cv2.imread(str(cfg.FIXTURES_DIR / "board_blank.jpg"))
    ctx = TurnContext(human=[[(60.0, 120.0), (120.0, 120.0)]], history=[], artist=cfg.ARTIST,
                      colors=list(cfg.DOCK_SLOTS), length="short", budget_mm=cfg.BUDGET_MM["short"], exchange=1, total=3)
    result = await ClaudeTurn(make_client()).propose(board, ctx)
    print(f"{result.source} in {result.latency_s:.1f} s; error={result.error}; usage={result.usage}")
    if result.proposal:
        print(result.proposal.model_dump_json(indent=1))


if __name__ == "__main__":
    asyncio.run(_main())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_claude_turn.py -q`
Expected: `9 passed`

- [ ] **Step 5: Write the bench**

`code/hackathon/duet/claude_bench.py`:

```python
"""Stage 5 exit test without the robot: run saved boards through Claude, validate and style the
proposals, write SVG previews, and report latency against the 8 s budget.

    python -m duet.claude_bench --make-boards    draw ten human marks on the blank board fixture -> tests/fixtures/boards/
    python -m duet.claude_bench                  run every board through Claude; previews in captures/bench/; stats
    python -m duet.claude_bench --offline        no Claude call: preview the fallback grammar for every board
    python -m duet.claude_bench --length medium  use another budget (short by default)
"""
from __future__ import annotations

import asyncio
import json
import math
import statistics
import sys
from pathlib import Path

import cv2
import numpy as np

from duet import config as cfg
from duet import planner, svg, vision
from duet.claude_turn import ClaudeTurn, TurnContext, api_key, make_client
from duet.styles import haring

BOARDS = cfg.FIXTURES_DIR / "boards"
OUT = Path(__file__).resolve().parent.parent / "captures" / "bench"
INK = (40, 90, 40)   # dark green marker, BGR


def _circle(cx, cy, r, n=40):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]


def _star(cx, cy, r1, r2):
    pts = []
    for k in range(11):
        r = r1 if k % 2 == 0 else r2
        a = -math.pi / 2 + k * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


SHAPES: dict[str, list[list[tuple[float, float]]]] = {
    "fish": [[(50, 120), (70, 100), (110, 100), (130, 120), (110, 140), (70, 140), (50, 120)],
             [(130, 120), (150, 105), (150, 135), (130, 120)]],
    "house": [[(60, 150), (60, 100), (90, 75), (120, 100), (120, 150), (60, 150)]],
    "spiral": [[(90 + 1.6 * t * math.cos(t), 120 + 1.6 * t * math.sin(t)) for t in np.linspace(0, 6 * math.pi, 90)]],
    "sun": [_circle(90, 110, 25)],
    "wave": [[(30 + x, 150 + 10 * math.sin(x / 8)) for x in range(0, 121, 4)]],
    "arrow": [[(40, 120), (130, 120)], [(110, 105), (130, 120), (110, 135)]],
    "star": [_star(90, 115, 35, 15)],
    "tree": [[(90, 180), (90, 130)], [(60, 130), (90, 80), (120, 130), (60, 130)]],
    "face": [_circle(90, 110, 30), _circle(78, 100, 3), _circle(102, 100, 3),
             [(75 + 15 * math.cos(a), 118 + 10 * math.sin(a)) for a in np.linspace(0.3, math.pi - 0.3, 12)]],
    "boat": [[(50, 140), (130, 140), (115, 160), (65, 160), (50, 140)], [(90, 140), (90, 90), (125, 130), (90, 130)]],
}


def make_board(blank: np.ndarray, polylines: list[list[tuple[float, float]]]) -> np.ndarray:
    board = blank.copy()
    for pl in polylines:
        pts = np.array([[x * vision.PX_PER_MM, y * vision.PX_PER_MM] for x, y in pl], dtype=np.int32)
        cv2.polylines(board, [pts], False, INK, 3, cv2.LINE_AA)
    return board


def make_boards() -> None:
    BOARDS.mkdir(parents=True, exist_ok=True)
    blank = cv2.imread(str(cfg.FIXTURES_DIR / "board_blank.jpg"))
    for i, (name, pls) in enumerate(SHAPES.items(), 1):
        cv2.imwrite(str(BOARDS / f"{i:02d}-{name}.jpg"), make_board(blank, pls), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"{len(SHAPES)} boards written to {BOARDS}")


async def run(offline: bool, length: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    blank = cv2.imread(str(cfg.FIXTURES_DIR / "board_blank.jpg"))
    turn = None if offline else ClaudeTurn(make_client())
    budget = cfg.BUDGET_MM[length]
    rows = []
    for path in sorted(BOARDS.glob("*.jpg")):
        board = cv2.imread(str(path))
        mask, _ = vision.new_ink(board, blank)
        human = vision.trace(mask)
        ctx = TurnContext(human=human, history=[], artist=cfg.ARTIST, colors=list(cfg.DOCK_SLOTS),
                          length=length, budget_mm=budget, exchange=1, total=3)
        if turn is None:
            styled, source, latency, error, sees, adds = haring.fallback(human, budget), "offline", 0.0, None, "", ""
        else:
            result = await turn.propose(board, ctx)
            source, latency, error = result.source, result.latency_s, result.error
            if result.proposal and result.source == "claude":
                styled = haring.style(planner.validate(result.proposal.strokes, human, budget), budget)
                sees, adds = result.proposal.sees, result.proposal.adds
            else:
                styled, sees, adds = haring.fallback(human, budget), "", ""
        drawn = sum(sum(math.dist(a, b) for a, b in zip(pl, pl[1:])) for pl in styled)
        (OUT / f"{path.stem}.svg").write_text(svg.render([
            {"id": "human", "color": "#222222", "width": 1.2, "polylines": human},
            {"id": "plan", "color": cfg.COLOR_HEX["green"], "width": 1.0, "polylines": styled}]))
        rows.append({"board": path.stem, "source": source, "latency_s": round(latency, 2), "error": error,
                     "strokes": len(styled), "mm": round(drawn), "sees": sees, "adds": adds})
        print(f"{path.stem:12s} {source:8s} {latency:5.1f} s  {len(styled):3d} strokes {drawn:5.0f} mm  {sees} {adds}")
    (OUT / "results.json").write_text(json.dumps(rows, indent=2))
    lat = [r["latency_s"] for r in rows if r["source"] == "claude"]
    if lat:
        p95 = sorted(lat)[int(0.95 * (len(lat) - 1))]
        print(f"\nClaude answered {len(lat)}/{len(rows)}: median {statistics.median(lat):.1f} s, p95 {p95:.1f} s "
              f"({'within' if p95 <= cfg.CLAUDE_TIMEOUT_S else 'OVER'} the {cfg.CLAUDE_TIMEOUT_S:.0f} s budget)")
    print(f"previews in {OUT}")


def main(argv: list[str]) -> None:
    if "--make-boards" in argv:
        make_boards()
        return
    length = argv[argv.index("--length") + 1] if "--length" in argv else "short"
    offline = "--offline" in argv
    if not offline and not api_key():
        raise SystemExit("no ANTHROPIC_API_KEY in .env; run with --offline or add the key")
    asyncio.run(run(offline, length))


if __name__ == "__main__":
    main(sys.argv[1:])
```

- [ ] **Step 6: Make the boards and run the bench offline, then live**

Run: `python -m duet.claude_bench --make-boards && python -m duet.claude_bench --offline`
Expected: ten boards in `tests/fixtures/boards/`, ten SVGs in `captures/bench/`, every row `offline` with a non-zero stroke count. Open two of the SVGs (the Read tool renders them) and check the outline hugs the mark.

Run: `python -m duet.claude_bench`
Expected: ten rows with `claude` as the source and a latency line. Record the median and p95 in the commit message and in `notes/hackathon/04-plan.md` under a new "Stage 5 results" bullet. If p95 exceeds 8 s, run once more with `CLAUDE_MODEL = "claude-sonnet-5"` (edit the constant, rerun) and keep whichever meets the budget; if neither does, keep Opus and raise `CLAUDE_TIMEOUT_S` to the measured p95 rounded up, noting it. Look at three previews: are the strokes near the human mark, inside the inset, and does `sees` describe the shape? If the proposals are wildly off-board, the grid labels are unreadable at 4 px/mm: bump the font scale in `grid_overlay` to 0.5 and rerun.

- [ ] **Step 7: Commit**

```bash
git add duet/claude_turn.py duet/claude_bench.py tests/test_claude_turn.py tests/fixtures/boards/ notes/hackathon/04-plan.md
git commit -m "feat: Claude turn with structured output, fallback, and a saved-board latency bench"
```

---

### Task 7: Plan 2 wrap-up

- [ ] **Step 1: Full suite and a stale-warning check**

Run: `python -m pytest -q`
Expected: everything green (46 from plan 1 plus roughly 40 new).

- [ ] **Step 2: Update the hackathon README table**

Append rows to the table in `code/hackathon/README.md`:

```markdown
| `duet/` | The Duet drawing robot. `python -m duet.<module>`; see each module's docstring. Pure core under test: `strokes`, `calib`, `vision`, `trigger`, `planner`, `styles/haring`, `svg`; hardware scripts `teach`, `stroke_bench`, `dock_test`, `calibrate`; `claude_bench` runs saved boards through Claude with no robot |
| `tests/fixtures/` | Real look-pose captures from 2026-09-18 (`look_before.jpg`, `look_after.jpg`, `look_depth.npz`), the warped blank board, and ten synthetic boards for the Claude bench |
```

- [ ] **Step 3: Commit**

```bash
git add code/hackathon/README.md
git commit -m "docs: duet modules and fixtures in the hackathon README"
```

---

## Morning hardware steps (not part of this plan's execution)

These finish stages 4 to 6 on the machine and take about 30 minutes with the arm connected:

1. `python -m duet.calibrate --check` at the look pose: marks re-found, drift under 1 mm. If the board moved overnight, `--tl` again.
2. Put the green marker in its cap and, from the look pose, record its end-plug dot: run `python -m duet.calibrate` to save a fresh `captures/calib_frame.jpg`, open it, read the dot's pixel position, and add to `calibration.json`: `"dots": {"green": {"xy": [x, y], "hsv_lo": [40, 60, 60], "hsv_hi": [85, 255, 255]}}`. Check with a one-liner: `python -c "import cv2,json,numpy as np;from duet import vision;cal=json.load(open('duet/data/calibration.json'));f=cv2.imread('captures/calib_frame.jpg');q=vision.board_quad(np.array(cal['marks_image'],np.float32),cal['board_tl_index']);print(vision.dock_dots(f,cal['dots'],vision.board_homography(q)))"` should print `home`.
3. Re-measure the dock rectangle with the marker in the tub and update it with `python -m duet.calibrate --dock x0 y0 x1 y1`.
4. Hold a hand over the board at the look pose and confirm `hand_present` is True on a live frame (plan 3's `run.py` prints the hand reading in its log).
5. Stage 6 exit: with `run.py` in Held mode, draw a mark, take the hand away, and watch the terminal fire the turn after 2 s; a hand over the board must block it.
