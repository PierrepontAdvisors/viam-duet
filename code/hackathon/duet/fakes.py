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
from duet.controller import Aborted, DrawResult
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

    def show_hand(self, present: bool) -> None:
        """A hand-sized patch of medium skin over the board center, on the camera image only."""
        self.hand = present

    def _frame(self) -> Frame:
        img = self.image
        if getattr(self, "hand", False):
            img = self.image.copy()
            cx, cy = int(self.mask.nonzero()[1].mean()), int(self.mask.nonzero()[0].mean())
            cv2.ellipse(img, (cx, cy), (100, 75), 20, 0, 360, (90, 120, 170), -1)
        if monotonic() < self.jitter_until:
            self.n += 1
            img = cv2.add(img, np.full_like(img, 12 if self.n % 2 else 0))
        return Frame(img, self.depth, monotonic())

    def latest(self) -> Frame:
        return self._frame()

    def recent(self, seconds: float) -> list[Frame]:
        return [self._frame(), self._frame()]

    async def capture_median(self, n: int = 5, delay_s: float = 0.0) -> np.ndarray:
        return self._frame().color.copy()


class FakeController:
    def __init__(self, frames: FakeFrames | None = None, stroke_s: float = 0.02, fail_go_look_once: bool = False):
        self.frames = frames
        self.stroke_s = stroke_s
        self.fail_go_look_once = fail_go_look_once     # a latched arm error on the first move
        self._abort = asyncio.Event()                  # set by stop(), cleared by recover()
        self.calls: list[tuple] = []
        self.drawn: list[list[Polyline]] = []
        self.events: asyncio.Queue = asyncio.Queue()
        self.hand_check = None
        self.held_mode = cfg.HELD_MODE
        self.last_error: str | None = None
        self.needs_lift = False

    async def go_look(self) -> None:
        self.calls.append(("go_look",))
        if self.fail_go_look_once:
            self.fail_go_look_once = False
            raise RuntimeError("xArm: Emergency Stop Button Pushed In")

    async def pick_marker(self, slot: str, displacement_mm=(0.0, 0.0)) -> None:
        self.calls.append(("pick", slot, displacement_mm))

    async def return_marker(self, slot: str) -> None:
        self.calls.append(("return", slot))

    async def draw(self, polylines: list[Polyline], budget_mm: float, budget_s: float, z_offset_mm: float = 0.0) -> DrawResult:
        self.calls.append(("draw", len(polylines)))
        t0, drawn, done = monotonic(), 0.0, 0
        for i, pl in enumerate(polylines):
            if self._abort.is_set():
                raise Aborted("stop() was called")
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
        self._abort.set()

    async def recover(self) -> None:
        self.calls.append(("recover",))
        self._abort.clear()

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
                         thought="Is that a creature waking up?", quip="What a creature! Here comes the sun.", color="green",
                         strokes=[_stroke(kind="circle", cx=min(max(cx, lo + 14), hi_x - 14), cy=max(lo + 14, top - 32), r=12.0)])
        else:
            y = min(hi_y, bottom + 25)
            p = Proposal(sees="The scene has a sun now.", adds="A ground line under the creature.",
                         thought="Where does the creature stand?", quip="Let's give it ground to stand on.", color="green",
                         strokes=[_stroke(kind="polyline", points=[Pt(x=lo, y=y), Pt(x=hi_x, y=y)])])
        return TurnResult(p, "fake", self.latency_s, None)
