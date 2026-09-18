# Duet plan 1 of 3: Foundation (stages 1 to 3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Get the xArm drawing a square on the board and picking and returning markers from the dock reliably, through Viam, with taught poses and a tested geometry core.

**Architecture:** A `duet` package under `code/hackathon/` with pure geometry modules (`strokes`, `calib`) covered by pytest, one `Controller` that owns the arm, gripper, and motion service, and three operator scripts (`teach`, `stroke_bench`, `dock_test`). Every arm motion is a planned `motion.move` of the `gripper` frame so the machine's configured obstacles apply. Spec: `docs/superpowers/specs/2026-09-18-duet-design.md`, sections 3 to 5 and stages 1 to 3.

**Tech Stack:** Python 3.12 venv at `code/hackathon/.venv` (viam-sdk 0.80.0), numpy, pytest. Credentials from `code/hackathon/.env`. Machine `armfarm22` with resources `arm`, `gripper`, `cam`, motion service `builtin`.

**Working conventions for every task:**
- Run all commands from `code/hackathon` with the venv active: `cd "/Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/code/hackathon" && source .venv/bin/activate`.
- Scripts run as modules: `python -m duet.teach ...`. This puts `code/hackathon` on `sys.path`, so `import viam_conn` (the existing connection helper) works from inside the package.
- Git: the repo refuses commits on `main`. Stay on the branch `feat/duet-design`, which is already checked out. Commit messages use `<type>: <description>`.
- Hardware steps say **HARDWARE**. Before any of them: the E-stop is within reach, nobody's hands are near the arm, and `python explore.py` has printed the machine's resources in the last hour.

---

### Task 1: Package skeleton, dependencies, constants

**Files:**
- Create: `code/hackathon/duet/__init__.py`
- Create: `code/hackathon/duet/config.py`
- Create: `code/hackathon/duet/data/.gitkeep`
- Create: `code/hackathon/tests/__init__.py`
- Create: `code/hackathon/pytest.ini`
- Modify: `.gitignore` (repo root)

- [ ] **Step 1: Install test and math dependencies into the venv**

Run: `pip install -q pytest numpy && python -c "import numpy, pytest; print(numpy.__version__, pytest.__version__)"`
Expected: two version numbers, no errors.

- [ ] **Step 2: Create the package and constants**

`code/hackathon/duet/__init__.py`: empty file.

`code/hackathon/duet/data/.gitkeep`: empty file.

`code/hackathon/tests/__init__.py`: empty file.

`code/hackathon/duet/config.py`:

```python
"""Constants for Duet. Geometry is in board millimeters. Speeds are xArm joint speeds in degrees per second."""
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_DIR / "data"                 # poses.json and calibration.json, committed
SESSIONS_DIR = PACKAGE_DIR.parent / "sessions"  # per-session photos and video, gitignored

POSES_PATH = DATA_DIR / "poses.json"
CALIBRATION_PATH = DATA_DIR / "calibration.json"

# Writing surface inside the raised frame. Landscape as the camera sees it; confirm in stage 4.
BOARD_W_MM = 279.0
BOARD_H_MM = 216.0
INSET_MM = 15.0        # drawable area starts this far inside the corners
LIFT_MM = 20.0         # pen-up travel height above the board
WAYPOINT_MM = 8.0      # spacing of planned moves along a stroke; set from the stage 2 measurement

SPEED_TRAVEL = 30.0    # deg/s, matches the machine's configured speed
SPEED_DRAW = 15.0
SPEED_DOCK = 10.0

GRIPPER_OPEN_FOR_PICK = 500   # 0 closed .. 850 open; set to barrel width + 15 mm in stage 3
UNCAP_LIFT_MM = 40.0          # straight-up pull that uncaps the marker
DOCK_HOVER_MM = 60.0          # safe height above a slot
PRESS_MM = 3.0                # extra push when reseating the tip in its cap

BUDGET_MM = {"short": 400.0, "medium": 1200.0, "long": 3000.0}
BUDGET_S = {"short": 15.0, "medium": 40.0, "long": 90.0}

MOVE_TIMEOUT_S = 30.0
LINE_TOLERANCE_MM = 1.0
```

`code/hackathon/pytest.ini`:

```ini
[pytest]
testpaths = tests
```

- [ ] **Step 3: Ignore session output at the repo root**

Append to `.gitignore` at the repo root:

```
code/hackathon/sessions/
```

- [ ] **Step 4: Verify the package imports and pytest runs empty**

Run: `python -c "from duet import config; print(config.POSES_PATH)" && python -m pytest -q`
Expected: the poses path printed, then `no tests ran`.

- [ ] **Step 5: Commit**

```bash
git add duet/__init__.py duet/config.py duet/data/.gitkeep tests/__init__.py pytest.ini ../../.gitignore
git commit -m "feat: duet package skeleton and constants"
```

---

### Task 2: Pure stroke geometry

**Files:**
- Create: `code/hackathon/duet/strokes.py`
- Test: `code/hackathon/tests/test_strokes.py`

- [ ] **Step 1: Write the failing tests**

`code/hackathon/tests/test_strokes.py`:

```python
import math

from duet.strokes import cut_to_budget, length, resample


def test_length_of_closed_square():
    square = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
    assert length(square) == 40


def test_length_of_single_point_is_zero():
    assert length([(3, 3)]) == 0


def test_resample_keeps_endpoints_and_respects_spacing():
    pts = resample([(0, 0), (30, 0)], 8)
    assert pts[0] == (0, 0)
    assert pts[-1] == (30, 0)
    assert len(pts) == 5  # 0, 7.5, 15, 22.5, 30
    assert all(math.dist(a, b) <= 8 + 1e-9 for a, b in zip(pts, pts[1:]))


def test_resample_keeps_every_original_vertex():
    pts = resample([(0, 0), (10, 0), (10, 10)], 4)
    assert (10, 0) in pts
    assert (10, 10) in pts


def test_cut_to_budget_keeps_whole_strokes_then_cuts_one():
    strokes = [[(0, 0), (10, 0)], [(0, 0), (0, 10)], [(0, 0), (50, 0)]]
    out = cut_to_budget(strokes, 25)
    assert out[:2] == strokes[:2]
    assert out[2] == [(0, 0), (5.0, 0.0)]
    assert len(out) == 3


def test_cut_to_budget_with_nothing_left():
    assert cut_to_budget([[(0, 0), (1, 0)]], 0) == []


def test_cut_to_budget_exact_at_interior_vertex():
    out = cut_to_budget([[(0, 0), (10, 0), (10, 10)]], 10)
    assert out == [[(0, 0), (10, 0)]]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_strokes.py -q`
Expected: `ModuleNotFoundError: No module named 'duet.strokes'`

- [ ] **Step 3: Write the implementation**

`code/hackathon/duet/strokes.py`:

```python
"""Pure geometry for polylines in board millimeters. No I/O, no robot."""
from __future__ import annotations

import math

Point = tuple[float, float]
Polyline = list[Point]


def length(points: Polyline) -> float:
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def resample(points: Polyline, spacing: float) -> Polyline:
    """Points along the same path no more than `spacing` apart. Every original vertex is kept."""
    if len(points) < 2:
        return list(points)
    out: Polyline = [points[0]]
    for a, b in zip(points, points[1:]):
        n = max(1, math.ceil(math.dist(a, b) / spacing))
        for k in range(1, n + 1):
            t = k / n
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def cut_to_budget(polylines: list[Polyline], budget_mm: float) -> list[Polyline]:
    """Keep whole polylines, in order, while they fit; cut the first one that does not; drop the rest."""
    kept: list[Polyline] = []
    remaining = budget_mm
    for pl in polylines:
        if remaining <= 0:
            break
        if length(pl) <= remaining:
            kept.append(list(pl))
            remaining -= length(pl)
            continue
        partial: Polyline = [pl[0]]
        for a, b in zip(pl, pl[1:]):
            if remaining <= 0:
                break
            d = math.dist(a, b)
            if d <= remaining:
                partial.append(b)
                remaining -= d
            else:
                t = remaining / d
                partial.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
                remaining = 0
                break
        if len(partial) > 1:
            kept.append(partial)
        break
    return kept
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_strokes.py -q`
Expected: `7 passed`

- [ ] **Step 5: Commit**

```bash
git add duet/strokes.py tests/test_strokes.py
git commit -m "feat: stroke geometry helpers with tests"
```

---

### Task 3: Board-to-robot calibration and pose storage

**Files:**
- Create: `code/hackathon/duet/calib.py`
- Test: `code/hackathon/tests/test_calib.py`

- [ ] **Step 1: Write the failing tests**

`code/hackathon/tests/test_calib.py`:

```python
import pytest
from viam.proto.common import Pose

from duet.calib import BoardToRobot, dict_to_pose, load_poses, pose_to_dict, save_pose


def down(x, y, z):
    return Pose(x=x, y=y, z=z, o_x=0, o_y=0, o_z=-1, theta=0)


def flat_board():
    # top-left, top-right, bottom-left of a 279 x 216 board; board x runs along world y here
    return BoardToRobot.from_corners(down(300, -100, 5), down(300, 179, 5), down(84, -100, 5), 279, 216)


def test_corners_map_to_themselves():
    b = flat_board()
    tl, tr, bl = b.to_world(0, 0), b.to_world(279, 0), b.to_world(0, 216)
    assert (tl.x, tl.y, tl.z) == (300, -100, 5)
    assert (round(tr.x, 6), round(tr.y, 6)) == (300, 179)
    assert (round(bl.x, 6), round(bl.y, 6)) == (84, -100)


def test_center_lift_and_orientation():
    c = flat_board().to_world(139.5, 108, lift=20)
    assert (round(c.x, 6), round(c.y, 6), c.z) == (192, 39.5, 25)
    assert (c.o_x, c.o_y, c.o_z, c.theta) == (0, 0, -1, 0)


def test_tilted_plane_interpolates_z():
    b = BoardToRobot.from_corners(down(300, -100, 0), down(300, 179, 10), down(84, -100, 0), 279, 216)
    assert round(b.to_world(139.5, 0).z, 6) == 5


def test_pose_dict_roundtrip():
    p = down(1.5, 2.5, 3.5)
    assert dict_to_pose(pose_to_dict(p)) == p


def test_save_and_load_nested_names(tmp_path):
    path = tmp_path / "poses.json"
    save_pose("corner.tl", down(1, 2, 3), path)
    poses = save_pose("look", down(4, 5, 6), path)
    assert poses["corner"]["tl"]["z"] == 3
    assert load_poses(path)["look"]["x"] == 4


def test_from_poses_uses_corner_entries(tmp_path):
    path = tmp_path / "poses.json"
    save_pose("corner.tl", down(300, -100, 5), path)
    save_pose("corner.tr", down(300, 179, 5), path)
    save_pose("corner.bl", down(84, -100, 5), path)
    b = BoardToRobot.from_poses(load_poses(path))
    assert round(b.to_world(279, 216).x, 6) == 84


def test_far_corner_is_parallelogram_closure():
    far = flat_board().to_world(279, 216)
    assert (round(far.x, 6), round(far.y, 6), far.z) == (84, 179, 5)


def test_file_roundtrip_preserves_all_fields(tmp_path):
    path = tmp_path / "poses.json"
    original = Pose(x=1.5, y=-2.5, z=3.25, o_x=0.1, o_y=0.2, o_z=-0.97, theta=12.5)
    save_pose("corner.tl", original, path)
    assert dict_to_pose(load_poses(path)["corner"]["tl"]) == original


def test_from_poses_reports_missing_corners():
    with pytest.raises(ValueError, match="missing corner touch-offs: tr, bl"):
        BoardToRobot.from_poses({"corner": {"tl": pose_to_dict(down(0, 0, 0))}})
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_calib.py -q`
Expected: `ModuleNotFoundError: No module named 'duet.calib'`

- [ ] **Step 3: Write the implementation**

`code/hackathon/duet/calib.py`:

```python
"""Board-to-robot calibration and pose storage.

Three touch-off corners, recorded as gripper poses in `world` while the marker tip rests on the
writing surface, define the board plane. Commanding the gripper to a pose from `to_world` puts the
tip on the board, so the marker length never needs measuring.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from viam.proto.common import Pose

from duet import config as cfg


def pose_to_dict(p: Pose) -> dict:
    return {"x": p.x, "y": p.y, "z": p.z, "o_x": p.o_x, "o_y": p.o_y, "o_z": p.o_z, "theta": p.theta}


def dict_to_pose(d: dict) -> Pose:
    return Pose(x=d["x"], y=d["y"], z=d["z"], o_x=d["o_x"], o_y=d["o_y"], o_z=d["o_z"], theta=d["theta"])


def load_poses(path: Path = cfg.POSES_PATH) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_pose(name: str, pose: Pose, path: Path = cfg.POSES_PATH) -> dict:
    """Store `pose` under a dotted name such as 'slot.red'; rewrite the file atomically; return the new dict."""
    poses = load_poses(path)
    node = poses
    *parents, leaf = name.split(".")
    for key in parents:
        node = node.setdefault(key, {})
    node[leaf] = pose_to_dict(pose)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(poses, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)   # atomic on POSIX: a crash mid-write cannot truncate the taught poses
    return poses


@dataclass(frozen=True)
class BoardToRobot:
    origin: tuple[float, float, float]        # top-left corner in world mm
    ex: tuple[float, float, float]            # vector top-left -> top-right
    ey: tuple[float, float, float]            # vector top-left -> bottom-left
    width_mm: float
    height_mm: float
    orientation: tuple[float, float, float, float]  # o_x, o_y, o_z, theta of the touch-off

    @classmethod
    def from_corners(cls, tl: Pose, tr: Pose, bl: Pose, width_mm: float, height_mm: float) -> "BoardToRobot":
        o = np.array([tl.x, tl.y, tl.z])
        ex = np.array([tr.x, tr.y, tr.z]) - o
        ey = np.array([bl.x, bl.y, bl.z]) - o
        return cls(tuple(map(float, o)), tuple(map(float, ex)), tuple(map(float, ey)),
                   width_mm, height_mm, (tl.o_x, tl.o_y, tl.o_z, tl.theta))

    @classmethod
    def from_poses(cls, poses: dict) -> "BoardToRobot":
        corners = poses.get("corner", {})
        missing = [name for name in ("tl", "tr", "bl") if name not in corners]
        if missing:
            raise ValueError(f"missing corner touch-offs: {', '.join(missing)}; "
                             "run `python -m duet.teach corner <name>` for each")
        return cls.from_corners(dict_to_pose(corners["tl"]), dict_to_pose(corners["tr"]),
                                dict_to_pose(corners["bl"]), cfg.BOARD_W_MM, cfg.BOARD_H_MM)

    def to_world(self, u: float, v: float, lift: float = 0.0) -> Pose:
        """Gripper pose that puts the marker tip at board point (u, v), raised by `lift` mm.
        `lift` is along world z, not the board normal; the board is assumed to be close to level."""
        o, ex, ey = (np.array(t) for t in (self.origin, self.ex, self.ey))
        p = o + ex * (u / self.width_mm) + ey * (v / self.height_mm)
        ox, oy, oz, th = self.orientation
        return Pose(x=float(p[0]), y=float(p[1]), z=float(p[2] + lift), o_x=ox, o_y=oy, o_z=oz, theta=th)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_calib.py -q`
Expected: `9 passed`

- [ ] **Step 5: Commit**

```bash
git add duet/calib.py tests/test_calib.py
git commit -m "feat: board-to-robot calibration and pose storage with tests"
```

---

### Task 4: The controller

**Files:**
- Create: `code/hackathon/duet/controller.py`
- Test: `code/hackathon/tests/test_controller_offline.py` (stubbed clients; covers abort, halt, busy, hand refusal, recovery)

The hardware paths are exercised by Tasks 5 to 7. The offline test file is committed in the repo at `code/hackathon/tests/test_controller_offline.py`; copy it as-is when re-executing this plan elsewhere.

- [ ] **Step 1: Write the controller**

`code/hackathon/duet/controller.py`:

```python
"""The only module that talks to the arm. Every motion is a planned move of the gripper frame,
so the obstacles configured on the machine (table, walls, ceiling) always apply.

Run `python -m duet.controller` to print the arm's status without moving anything.
"""
from __future__ import annotations

import asyncio
import math
from contextlib import asynccontextmanager
from dataclasses import dataclass
from time import monotonic
from typing import AsyncIterator, Awaitable, Callable

from viam.components.arm import Arm
from viam.components.gripper import Gripper
from viam.proto.common import Pose, PoseInFrame
from viam.proto.service.motion import Constraints, LinearConstraint
from viam.robot.client import RobotClient
from viam.services.motion import MotionClient

import viam_conn
from duet import config as cfg
from duet.calib import BoardToRobot, dict_to_pose
from duet.strokes import Polyline, resample


class MoveRefused(RuntimeError):
    """The motion service found no collision-free path to the target."""


class Blocked(RuntimeError):
    """A hand was over the board or dock, so the controller refused to start."""


class Busy(RuntimeError):
    """Another sequence is running. Commands are rejected, never queued, so nothing fires late."""


class Aborted(RuntimeError):
    """stop() was called while a sequence was running."""


@dataclass(frozen=True)
class DrawResult:
    strokes_done: int
    drawn_mm: float
    seconds: float
    blocked: bool = False   # a hand appeared between strokes; the pen is up and the arm is idle


def shifted(p: Pose, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> Pose:
    """A new pose offset in world axes, orientation unchanged."""
    return Pose(x=p.x + dx, y=p.y + dy, z=p.z + dz, o_x=p.o_x, o_y=p.o_y, o_z=p.o_z, theta=p.theta)


LINEAR = Constraints(linear_constraint=[LinearConstraint(line_tolerance_mm=cfg.LINE_TOLERANCE_MM)])


class Controller:
    """Sequences run one at a time. `stop()` halts the arm and aborts the running sequence at its
    next move; `recover()` clears the arm's error state and lifts the tool if it was left low."""

    def __init__(self, machine: RobotClient, poses: dict, board: BoardToRobot | None = None):
        self.arm = Arm.from_robot(machine, viam_conn.ARM)
        self.gripper = Gripper.from_robot(machine, viam_conn.GRIPPER)
        self.motion = MotionClient.from_robot(machine, viam_conn.MOTION)
        self.poses = poses
        self.board = board
        self.held_mode = False                       # True: marker stays in the gripper, dock steps skipped
        # Set by the session in plan 3. Must answer within HAND_CHECK_TIMEOUT_S and must not call
        # back into this controller (it runs while the sequence lock is held).
        self.hand_check: Callable[[], Awaitable[bool]] | None = None
        self.events: asyncio.Queue = asyncio.Queue()
        self.move_times: list[float] = []            # seconds per planned move, for stroke_bench
        self.needs_lift = False                      # tool is at or near a surface; recover() lifts first
        self._lift_mm = cfg.LIFT_MM                  # how far recover() must lift to clear that surface
        self.last_error: str | None = None
        self._abort = asyncio.Event()
        self._lock = asyncio.Lock()

    # ---- primitives --------------------------------------------------------------------------
    async def _move(self, pose: Pose, linear: bool = False) -> None:
        if self._abort.is_set():
            raise Aborted("stop() was called")
        t0 = monotonic()
        ok = await self.motion.move(
            component_name=viam_conn.GRIPPER,
            destination=PoseInFrame(reference_frame="world", pose=pose),
            constraints=LINEAR if linear else None,
            timeout=cfg.MOVE_TIMEOUT_S,
        )
        self.move_times.append(monotonic() - t0)
        if not ok:
            raise MoveRefused(f"no path to x={pose.x:.0f} y={pose.y:.0f} z={pose.z:.0f}")

    async def set_speed(self, deg_per_s: float) -> None:
        await self.arm.do_command({"set_speed": float(deg_per_s)})

    async def gripper_set(self, position: int) -> None:
        """Gripper opening on the xArm scale: 0 closed, 850 fully open."""
        await self.gripper.do_command({"set": float(position)})

    async def tip_pose(self) -> Pose:
        result = await self.motion.get_pose(component_name=viam_conn.GRIPPER, destination_frame="world")
        return result.pose

    async def _hand_present(self) -> bool:
        """Fail safe: a slow or faulting hand check counts as a hand present."""
        if self.hand_check is None:
            return False
        try:
            async with asyncio.timeout(cfg.HAND_CHECK_TIMEOUT_S):
                return await self.hand_check()
        except Exception as exc:
            self.last_error = f"hand check failed ({type(exc).__name__}: {exc}); treated as a hand present"
            return True

    async def _halt(self) -> None:
        try:
            await self.arm.stop()
        except Exception as exc:
            self.last_error = f"{self.last_error or 'halt'}; arm.stop failed: {exc}"

    def _mark_low(self, lift_mm: float) -> None:
        self.needs_lift, self._lift_mm = True, lift_mm

    def _mark_clear(self) -> None:
        self.needs_lift = False

    @asynccontextmanager
    async def _sequence(self, check_hand: bool = True, wait_s: float | None = None) -> AsyncIterator[None]:
        """One sequence at a time. Rejects with Busy if another is running (or waits up to `wait_s`
        for it to unwind), refuses with Blocked if a hand is present, and on any failure records
        `last_error`, halts the arm, and re-raises."""
        if wait_s is None:
            if self._lock.locked():
                raise Busy("a sequence is already running; wait for it or call stop()")
            await self._lock.acquire()
        else:
            try:
                async with asyncio.timeout(wait_s):
                    await self._lock.acquire()
            except TimeoutError:
                raise Busy(f"a sequence is still running after {wait_s:.0f} s") from None
        try:
            self._abort.clear()
            if check_hand and await self._hand_present():
                raise Blocked("hand over the board or dock")
            try:
                yield
            except Exception as exc:
                self.last_error = f"{type(exc).__name__}: {exc}"
                await self._halt()
                raise
        finally:
            self._lock.release()

    def _pose(self, *keys: str) -> Pose:
        node = self.poses
        for key in keys:
            node = node[key]
        return dict_to_pose(node)

    def _apply_board_displacement(self, pose: Pose, d: tuple[float, float]) -> Pose:
        """Shift a world pose by a board-millimeter displacement, using only the board map's linear part."""
        if self.board is None:
            raise ValueError("a dot displacement needs the board calibration; run teach.py corner first")
        b = self.board
        ex = [c / b.width_mm for c in b.ex]
        ey = [c / b.height_mm for c in b.ey]
        return shifted(pose,
                       dx=ex[0] * d[0] + ey[0] * d[1],
                       dy=ex[1] * d[0] + ey[1] * d[1],
                       dz=ex[2] * d[0] + ey[2] * d[1])

    # ---- sequences ---------------------------------------------------------------------------
    async def move_to(self, pose: Pose, linear: bool = False, low: bool = False) -> None:
        """Public single move, used by teach.verify. `low=True` marks the target as at or near a
        surface, so recover() lifts first if this move is interrupted."""
        async with self._sequence():
            if low:
                self._mark_low(cfg.UNCAP_LIFT_MM)
            await self._move(pose, linear)
            if not low:
                self._mark_clear()

    async def go_look(self) -> None:
        async with self._sequence():
            await self.set_speed(cfg.SPEED_TRAVEL)
            await self._move(self._pose("look"))
            self._mark_clear()

    async def pick_marker(self, slot: str, displacement_mm: tuple[float, float] = (0.0, 0.0)) -> None:
        """Hover, descend, grab, pull straight up to uncap, rise. `displacement_mm` is where the camera
        saw the marker's dot relative to its calibrated spot (plan 2); (0, 0) trusts the taught pose."""
        if self.held_mode:
            return
        async with self._sequence():
            grip = self._pose("slot", slot)
            if displacement_mm != (0.0, 0.0):
                grip = self._apply_board_displacement(grip, displacement_mm)
            await self.gripper_set(cfg.GRIPPER_OPEN_FOR_PICK)
            await self.set_speed(cfg.SPEED_TRAVEL)
            await self._move(shifted(grip, dz=cfg.DOCK_HOVER_MM))
            await self.set_speed(cfg.SPEED_DOCK)
            self._mark_low(cfg.UNCAP_LIFT_MM)
            await self._move(grip, linear=True)
            grabbed = await self.gripper.grab()
            await asyncio.sleep(cfg.GRIPPER_SETTLE_S)
            if cfg.REQUIRE_GRAB_DETECT and not grabbed:
                raise RuntimeError(f"gripper closed on nothing at slot {slot}")
            await self._move(shifted(grip, dz=cfg.UNCAP_LIFT_MM), linear=True)
            await self._move(shifted(grip, dz=cfg.DOCK_HOVER_MM), linear=True)
            self._mark_clear()
            await self.set_speed(cfg.SPEED_TRAVEL)

    async def return_marker(self, slot: str) -> None:
        """Hover, descend slowly, seat the tip in the cap, press, release, rise."""
        if self.held_mode:
            return
        async with self._sequence():
            seat = self._pose("seat", slot)
            await self.set_speed(cfg.SPEED_TRAVEL)
            await self._move(shifted(seat, dz=cfg.DOCK_HOVER_MM))
            await self.set_speed(cfg.SPEED_DOCK)
            self._mark_low(cfg.UNCAP_LIFT_MM)
            await self._move(shifted(seat, dz=cfg.UNCAP_LIFT_MM), linear=True)
            await self._move(seat, linear=True)
            await self._move(shifted(seat, dz=-cfg.PRESS_MM), linear=True)
            await self.gripper_set(cfg.GRIPPER_OPEN_FOR_PICK)
            await asyncio.sleep(cfg.GRIPPER_SETTLE_S)
            await self._move(shifted(seat, dz=cfg.DOCK_HOVER_MM), linear=True)
            self._mark_clear()
            await self.set_speed(cfg.SPEED_TRAVEL)

    async def draw(self, polylines: list[Polyline], budget_mm: float, budget_s: float,
                   z_offset_mm: float = 0.0) -> DrawResult:
        """Draw polylines (board mm) in order until either budget runs out. The stroke in progress
        always finishes and the pen lifts. A hand seen between strokes ends the turn with
        `blocked=True` and no emergency stop. `z_offset_mm` raises every pen-down pose (dry runs)."""
        if self.board is None:
            raise RuntimeError("no board calibration: run `python -m duet.teach corner tl|tr|bl` first")
        async with self._sequence():
            start = monotonic()
            drawn = 0.0
            done = 0
            blocked = False
            for index, pl in enumerate(polylines):
                if drawn >= budget_mm or monotonic() - start >= budget_s:
                    break
                if index > 0 and await self._hand_present():
                    blocked = True
                    break
                pts = resample(pl, cfg.WAYPOINT_MM)
                if not pts:
                    continue
                drawn += await self._stroke(pts, z_offset_mm)
                done += 1
                await self.events.put({"type": "progress", "stroke": index, "drawn_mm": drawn})
            return DrawResult(done, drawn, monotonic() - start, blocked)

    async def _stroke(self, pts: Polyline, z_offset_mm: float) -> float:
        """Travel to the first point, draw through every point, lift. Returns millimeters drawn."""
        lifted = cfg.LIFT_MM + z_offset_mm
        await self.set_speed(cfg.SPEED_TRAVEL)
        await self._move(self.board.to_world(*pts[0], lift=lifted))
        await self.set_speed(cfg.SPEED_DRAW)
        self._mark_low(cfg.LIFT_MM)
        await self._move(self.board.to_world(*pts[0], lift=z_offset_mm), linear=True)
        drawn = 0.0
        prev = pts[0]
        for p in pts[1:]:
            await self._move(self.board.to_world(*p, lift=z_offset_mm), linear=True)
            drawn += math.dist(prev, p)
            prev = p
        await self._move(self.board.to_world(*prev, lift=lifted), linear=True)
        self._mark_clear()
        await self.set_speed(cfg.SPEED_TRAVEL)
        return drawn

    # ---- emergency and recovery --------------------------------------------------------------
    async def stop(self) -> None:
        """Emergency path, no lock: halt the arm now and abort the running sequence at its next move."""
        self._abort.set()
        await self._halt()

    async def clear_error(self) -> None:
        await self.arm.do_command({"clear_error": True})

    async def recover(self) -> None:
        """After a stop or a fault: wait for the aborted sequence to unwind, clear the arm's error
        state, and if the tool was left low lift it straight up before anything else moves. Runs
        without the hand gate, since the lift is a retreat from the surface and from any hand."""
        async with self._sequence(check_hand=False, wait_s=cfg.MOVE_TIMEOUT_S + 1):
            await self.clear_error()
            if self.needs_lift:
                await self.set_speed(cfg.SPEED_DOCK)
                await self._move(shifted(await self.tip_pose(), dz=self._lift_mm), linear=True)
                self._mark_clear()
            await self.set_speed(cfg.SPEED_TRAVEL)
        self.last_error = None

    async def status(self) -> dict:
        joints = await self.arm.get_joint_positions()
        holding = await self.gripper.is_holding_something()
        return {
            "joints_deg": [round(v, 1) for v in joints.values],
            "holding": holding.is_holding_something,
            "needs_lift": self.needs_lift,
            "last_error": self.last_error,
            "planned_moves": len(self.move_times),
        }


async def _main() -> None:
    from duet.calib import load_poses
    async with await viam_conn.connect() as machine:
        print(await Controller(machine, load_poses()).status())


if __name__ == "__main__":
    asyncio.run(_main())
```

- [ ] **Step 2: Verify it compiles and the status command works**

Run: `python -m py_compile duet/controller.py && python -m duet.controller`
Expected: a dict with six joint angles, `holding`, `needs_lift: False`, `last_error: None`, and `planned_moves: 0`. If the E-stop is still latched, `holding` fails with "Emergency Stop Button Pushed In"; release the E-stop and rerun.

- [ ] **Step 3: Commit**

```bash
git add duet/controller.py
git commit -m "feat: duet controller with planned moves, dock sequences, and drawing"
```

---

### Task 5: Teach poses (stage 1)

**Files:**
- Create: `code/hackathon/duet/teach.py`
- Creates at runtime: `code/hackathon/duet/data/poses.json`

- [ ] **Step 1: Write the teach script**

`code/hackathon/duet/teach.py`:

```python
"""Record poses by moving the arm by hand (xArm manual mode).

    python -m duet.teach look            park and look pose above the board
    python -m duet.teach slot red        fingers around the red marker's barrel at grip height (also green, blue)
    python -m duet.teach seat red        holding the red marker, tip seated in its cap
    python -m duet.teach corner tl       holding a marker, tip touching the top-left inner corner (also tr, bl)
    python -m duet.teach show            print every stored pose
    python -m duet.teach verify          replay every stored pose, 30 mm high, one at a time
"""
from __future__ import annotations

import asyncio
import sys

from viam.components.arm import Arm

import viam_conn
from duet import config as cfg
from duet.calib import dict_to_pose, load_poses, save_pose
from duet.controller import Controller, shifted

SLOTS = ("red", "green", "blue")
CORNERS = ("tl", "tr", "bl")
VERIFY_LIFT_MM = 30.0


def flatten(poses: dict, prefix: str = "") -> list[tuple[str, dict]]:
    """[('corner.tl', {...}), ('look', {...}), ...] in sorted order."""
    out: list[tuple[str, dict]] = []
    for key, value in sorted(poses.items()):
        name = f"{prefix}{key}"
        if "o_z" in value:
            out.append((name, value))
        else:
            out.extend(flatten(value, name + "."))
    return out


async def ask(prompt: str) -> str:
    return await asyncio.to_thread(input, prompt)   # keeps the Viam session alive while you work


async def teach(name: str, prompt: str, with_marker: bool, release_after: bool = False) -> None:
    async with await viam_conn.connect() as machine:
        arm = Arm.from_robot(machine, viam_conn.ARM)
        c = Controller(machine, load_poses())
        await c.gripper_set(cfg.GRIPPER_OPEN_FOR_PICK)
        if with_marker:
            await ask("Put a marker between the fingers, tip down. Enter to grab... ")
            await c.gripper.grab()
        await arm.do_command({"enter_manual_mode": True})
        try:
            await ask(f"MANUAL MODE. {prompt}\nThen press Enter here... ")
            pose = await c.tip_pose()
        finally:
            await arm.do_command({"exit_manual_mode": True})
        save_pose(name, pose)
        print(f"saved {name}: x={pose.x:.1f} y={pose.y:.1f} z={pose.z:.1f}")
        if release_after:
            await c.gripper_set(cfg.GRIPPER_OPEN_FOR_PICK)   # leave the marker standing in its cap
            await asyncio.sleep(0.3)
            await c.set_speed(cfg.SPEED_DOCK)
            await c.move_to(shifted(pose, dz=cfg.DOCK_HOVER_MM))
            await c.set_speed(cfg.SPEED_TRAVEL)


async def verify() -> None:
    poses = load_poses()
    async with await viam_conn.connect() as machine:
        c = Controller(machine, poses)
        await c.set_speed(cfg.SPEED_DOCK)
        for name, d in flatten(poses):
            pose = dict_to_pose(d)
            target = pose if name == "look" else shifted(pose, dz=VERIFY_LIFT_MM)
            where = "exact" if name == "look" else f"{VERIFY_LIFT_MM:.0f} mm above"
            await ask(f"next: {name} ({where}). Enter to move, Ctrl-C to abort... ")
            await c.move_to(target)
            print(f"  at {name}")
        await c.set_speed(cfg.SPEED_TRAVEL)


def main(argv: list[str]) -> None:
    if not argv:
        raise SystemExit(__doc__)
    verb, args = argv[0], argv[1:]
    if verb == "look":
        asyncio.run(teach("look", "Move the arm to the look pose: 350 to 400 mm above the board, "
                          "tilted 15 to 20 degrees so the light's reflection is out of the camera frame.", False))
    elif verb == "slot" and args and args[0] in SLOTS:
        asyncio.run(teach(f"slot.{args[0]}", f"Put the open fingers around the {args[0]} marker's barrel at "
                          "grip height while it stands in its cap, gripper pointing straight down.", False))
    elif verb == "seat" and args and args[0] in SLOTS:
        asyncio.run(teach(f"seat.{args[0]}", f"Push the {args[0]} marker's cap into the putty in its row "
                          "position and seat the tip in it, gripper pointing straight down.", True, release_after=True))
    elif verb == "corner" and args and args[0] in CORNERS:
        asyncio.run(teach(f"corner.{args[0]}", f"Rest the marker tip on the writing surface at the {args[0]} "
                          "inner corner, gripper pointing straight down.", True))
    elif verb == "show":
        for name, d in flatten(load_poses()):
            print(f"{name:12s} x={d['x']:7.1f} y={d['y']:7.1f} z={d['z']:7.1f}")
    elif verb == "verify":
        asyncio.run(verify())
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
```

- [ ] **Step 2: Verify it compiles and prints usage**

Run: `python -m py_compile duet/teach.py && python -m duet.teach; echo "exit=$?"`
Expected: the usage text, `exit=1`.

- [ ] **Step 3: Commit the script**

```bash
git add duet/teach.py
git commit -m "feat: teach script for look, slot, seat, and corner poses"
```

- [ ] **Step 4: HARDWARE. Stage the kit**

Tape a dark square at each of the four inner corners of the writing surface. Weight the dock container and tape its rim to the desk. Put the board on mounting putty. Wrap the blue marker's barrel in tape like the other two.

- [ ] **Step 5: HARDWARE. Plant the markers with the arm**

For each color: run `python -m duet.teach seat red` (then green, blue). When prompted, put the capped marker between the fingers, tip down. In manual mode, push its cap into the putty in its row position with the gripper pointing straight down, then press Enter. The script records the seat pose with the marker vertical, opens the gripper so the marker stays standing, and lifts the arm clear.
Expected: three `saved seat.<color>` lines; `python -m duet.teach show` lists them with similar z values.

- [ ] **Step 6: HARDWARE. Teach grip heights, corners, and the look pose**

Run, in order, answering each prompt:
```bash
python -m duet.teach slot red && python -m duet.teach slot green && python -m duet.teach slot blue
python -m duet.teach corner tl && python -m duet.teach corner tr && python -m duet.teach corner bl
python -m duet.teach look
```
For the corners, keep the same marker in the gripper for all three and touch the tip to the surface inside the frame at each corner mark.
Expected: `python -m duet.teach show` lists 10 poses: `corner.bl/tl/tr`, `look`, `seat.*`, `slot.*`.

- [ ] **Step 7: HARDWARE. Stage 1 exit test**

Run: `python -m duet.teach verify`
Expected: the arm visits every pose in turn at low speed, 30 mm above each taught point (exactly at `look`), with no collision stop and no `MoveRefused`. If a pose is refused, re-teach it slightly higher or further from the walls.

- [ ] **Step 8: Commit the taught poses**

```bash
git add duet/data/poses.json
git commit -m "chore: taught poses for armfarm22"
```

---

### Task 6: Stroke bench (stage 2)

**Files:**
- Create: `code/hackathon/duet/stroke_bench.py`
- Modify: `code/hackathon/duet/config.py` (WAYPOINT_MM, after measuring)

- [ ] **Step 1: Write the bench**

`code/hackathon/duet/stroke_bench.py`:

```python
"""Stage 2: draw a hard-coded square with a marker held in the gripper, timing every planned move.

    python -m duet.stroke_bench          60 mm square at the board center
    python -m duet.stroke_bench 40       40 mm square
    python -m duet.stroke_bench 60 --dry same, traced 20 mm above the surface without touching it
"""
from __future__ import annotations

import asyncio
import statistics
import sys

import viam_conn
from duet import config as cfg
from duet.calib import BoardToRobot, load_poses
from duet.controller import Controller


async def ask(prompt: str) -> str:
    return await asyncio.to_thread(input, prompt)


async def main(side_mm: float, dry: bool) -> None:
    poses = load_poses()
    board = BoardToRobot.from_poses(poses)
    cx, cy, h = cfg.BOARD_W_MM / 2, cfg.BOARD_H_MM / 2, side_mm / 2
    square = [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h), (cx - h, cy - h)]
    async with await viam_conn.connect() as machine:
        c = Controller(machine, poses, board)
        c.held_mode = True
        await c.gripper_set(cfg.GRIPPER_OPEN_FOR_PICK)
        await ask("Put a marker between the fingers, tip down. Enter to grab... ")
        await c.gripper.grab()
        await c.go_look()
        await ask("Hands clear of the board? Enter to draw... ")
        result = await c.draw([square], budget_mm=10_000, budget_s=600, z_offset_mm=cfg.LIFT_MM if dry else 0.0)
        await c.go_look()
    t = c.move_times
    print(f"strokes {result.strokes_done}, {result.drawn_mm:.0f} mm in {result.seconds:.1f} s")
    print(f"planned moves {len(t)}: mean {statistics.mean(t):.2f} s, "
          f"p95 {sorted(t)[int(0.95 * (len(t) - 1))]:.2f} s, max {max(t):.2f} s")
    print(f"drawing rate {result.drawn_mm / result.seconds:.0f} mm/s at WAYPOINT_MM={cfg.WAYPOINT_MM}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry"]
    asyncio.run(main(float(args[0]) if args else 60.0, dry="--dry" in sys.argv))
```

- [ ] **Step 2: Verify it compiles**

Run: `python -m py_compile duet/stroke_bench.py && echo ok`
Expected: `ok`

- [ ] **Step 3: Commit the script**

```bash
git add duet/stroke_bench.py
git commit -m "feat: stroke bench that draws a square and times planned moves"
```

- [ ] **Step 4: HARDWARE. Dry run above the surface**

Run: `python -m duet.stroke_bench 60 --dry`
Expected: the arm travels to the board center and traces a square 20 mm above the surface without touching it, then returns to the look pose. The timing lines print. If any move is refused, the board corners may be too close to a configured wall; re-teach the corners further inside the frame.

- [ ] **Step 5: HARDWARE. Stage 2 exit test**

Uncap the marker, wipe the board, run: `python -m duet.stroke_bench 60`
Expected: a closed square on the board with four straight sides. Record the mean seconds per planned move.

- [ ] **Step 6: Set the waypoint spacing from the measurement**

With mean move time `m` seconds and a Short turn budget of 15 s for 400 mm, the spacing that fits is about `400 * m / 15` mm, rounded to the nearest 2 mm, but never below 5 or above 15. Edit `WAYPOINT_MM` in `code/hackathon/duet/config.py` to that value and rerun the bench once to confirm the square is still straight.

- [ ] **Step 7: Commit**

```bash
git add duet/config.py
git commit -m "chore: waypoint spacing from the stroke bench measurement"
```

---

### Task 7: Dock test (stage 3)

**Files:**
- Create: `code/hackathon/duet/dock_test.py`
- Modify: `code/hackathon/duet/config.py` (GRIPPER_OPEN_FOR_PICK, after measuring)

- [ ] **Step 1: Write the dock test**

`code/hackathon/duet/dock_test.py`:

```python
"""Stage 3: pick, uncap, recap, and return one marker N times; count clean cycles.

    python -m duet.dock_test red 20
    python -m duet.dock_test gripper 300     open the gripper to a position on the 0..850 scale and stop
"""
from __future__ import annotations

import asyncio
import sys

import viam_conn
from duet.calib import load_poses
from duet.controller import Controller


async def ask(prompt: str) -> str:
    return await asyncio.to_thread(input, prompt)


async def set_gripper(position: int) -> None:
    async with await viam_conn.connect() as machine:
        await Controller(machine, load_poses()).gripper_set(position)
        print(f"gripper at {position}; measure the finger gap with calipers")


async def cycles(slot: str, count: int) -> None:
    poses = load_poses()
    async with await viam_conn.connect() as machine:
        c = Controller(machine, poses)
        await c.go_look()
        ok = 0
        for i in range(1, count + 1):
            try:
                await c.pick_marker(slot)
                holding = (await c.gripper.is_holding_something()).is_holding_something
                await c.return_marker(slot)
                ok += 1
                print(f"cycle {i}: ok (holding reported {holding})")
            except Exception as exc:
                print(f"cycle {i}: FAILED: {exc}")
                await c.stop()
                if (await ask("Fix it and press Enter to continue, or q to stop: ")).strip() == "q":
                    break
                await c.recover()   # clears the arm's error and lifts if the tool was left low
        await c.go_look()
    print(f"{ok}/{count} cycles succeeded")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "gripper":
        asyncio.run(set_gripper(int(sys.argv[2])))
    else:
        asyncio.run(cycles(sys.argv[1] if len(sys.argv) > 1 else "red",
                           int(sys.argv[2]) if len(sys.argv) > 2 else 20))
```

- [ ] **Step 2: Verify it compiles**

Run: `python -m py_compile duet/dock_test.py && echo ok`
Expected: `ok`

- [ ] **Step 3: Commit the script**

```bash
git add duet/dock_test.py
git commit -m "feat: dock cycle test"
```

- [ ] **Step 4: HARDWARE. Measure the gripper opening scale**

Run `python -m duet.dock_test gripper 300`, measure the gap between the fingertips with calipers, then repeat at 500 and 700. Note the millimeters at each. Measure a marker barrel's diameter. Choose the position whose gap is the barrel plus about 15 mm and set `GRIPPER_OPEN_FOR_PICK` in `code/hackathon/duet/config.py` to it.

- [ ] **Step 5: HARDWARE. Single cycle on each slot**

Run: `python -m duet.dock_test red 1`, then `green 1`, then `blue 1`.
Expected: for each, the arm hovers, descends, closes on the barrel, pulls the marker straight up out of its cap, rises, then reverses and seats the tip back in the cap. Watch for: a cap lifting with the marker (weight the dock more), the marker slipping in the fingers (build the tape collar up), the tip missing the cap on return (re-teach `seat.<color>`).

- [ ] **Step 6: HARDWARE. Stage 3 exit test**

Run: `python -m duet.dock_test red 20` and then `python -m duet.dock_test blue 20`.
Expected: at least 19 of 20 on each. If `holding reported False` appears while the marker was clearly held, note it in `notes/stuck-log.md`: this gripper unit does not report holding reliably and plan 2 must confirm picks by the dot vanishing from the camera instead.

- [ ] **Step 7: Commit**

```bash
git add duet/config.py
git commit -m "chore: gripper pick opening from the dock measurement"
```

- [ ] **Step 8: Log the stage results**

Append to `notes/hackathon/04-plan.md` under a new heading `## Stage results`: the stroke bench's mean move time and chosen `WAYPOINT_MM`, the gripper scale measurements, and the dock cycle counts. Commit with `docs: stage 1-3 results`.

---

## What plan 2 picks up

Plan 2 (`2026-09-18-duet-2-perception.md`) adds `camera.py`, `vision.py`, `calib.PixelsToBoard`, `calibrate.py`, `claude_turn.py`, `planner.py`, `styles/haring.py`, and `trigger.py`, and wires the camera's dot displacement into `Controller.pick_marker`. It depends on `poses.json` and the constants measured here.
