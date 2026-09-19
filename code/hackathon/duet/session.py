"""The turn loop: one asyncio task, one method per state, the only module that calls the others in
sequence. The human turn ends when the Go button on the page sends `pass`, and every dependency comes
in through the constructor so tests and `run.py --fake` can swap the camera, the arm, and Claude."""
from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass, replace
from time import monotonic

import numpy as np

from duet import config as cfg
from duet import planner, svg, vision
from duet.camera import Frame
from duet.claude_turn import TurnResult
from duet.controller import Blocked
from duet.strokes import Polyline, length
from duet.styles import abstract, haring, mondrian, vangogh
from duet.turn import all_ink, map_strokes

ARTISTS = ("abstract", "haring", "mondrian", "vangogh")
STYLERS = {"abstract": abstract, "haring": haring, "mondrian": mondrian, "vangogh": vangogh}
# Where Resume picks up after a fault. `interpret` and `plan` retry themselves: the visitor's strokes
# are already consumed, so sending them back to `human_turn` would ask for the mark to be drawn again.
RETRY_AFTER_FAULT = {"start": "start", "look": "look", "human_turn": "human_turn", "capture": "human_turn",
                     "interpret": "interpret", "plan": "plan", "robot_draw": "look", "finish": "finish"}
HAND_WAIT_S = 30
HAND_WAIT_MESSAGE_S = 5        # how often the "still waiting" line is repeated while the arm is held back
SETTLE_AFTER_LOOK_S = 0.8      # the camera image settles after the arm stops, as in duet.turn
FALLBACK_QUIP = "Lost my words. Drawing anyway!"   # the speech bubble when Claude did not answer
FALLBACK_THOUGHT = "Hmm... my words got lost."       # the thought cloud when Claude did not answer


@dataclass(frozen=True)
class Settings:
    artist: str = cfg.ARTIST
    length: str = "short"
    exchanges: int = 5
    mode: str = "duet"
    handoff: str = "held" if cfg.HELD_MODE else "dock"
    energy: float = 0.5          # tick count and length in the styler, 0 to 1 (the page's light chooser sets it)
    direction: float = 0.0       # tick tilt in degrees, 0 to 359

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
        if not isinstance(self.energy, (int, float)) or not 0.0 <= self.energy <= 1.0:
            raise ValueError("energy must be a number from 0 to 1")
        if not isinstance(self.direction, (int, float)) or not 0.0 <= self.direction < 360.0:
            raise ValueError("direction must be degrees from 0 to 359")
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
        self._signed = False                # the signature is drawn once, even if `finish` retries
        self._running = asyncio.Event()
        self._running.set()
        self._pass = asyncio.Event()
        self._resume_to = "human_turn"
        self._homography: np.ndarray | None = None

    # ---- controls, called from the page ------------------------------------------------------
    def update_settings(self, **changes) -> Settings:
        if self.state in ("robot_draw", "finish") and changes.get("handoff", self.settings.handoff) != self.settings.handoff:
            # the arm is holding the pen: switching now would send it through the other mode's return sequence
            raise ValueError("the marker handoff cannot change while the arm is drawing")
        self.settings = replace(self.settings, **changes).check()
        self.ctl.held_mode = self.settings.handoff == "held"    # the arm must not reach for a dock it is not using
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
        self.bus.last.pop("error", None)
        self.emit_state()

    # ---- events --------------------------------------------------------------------------------
    def emit_state(self) -> None:
        guard = "off" if self.guard is None else f"{self.guard.mode} at the look pose"
        self.bus.emit("state", state=self.state, turn=self.turn, coverage=round(self.coverage, 3),
                      error=self.last_error, at_look=self.at_look, hand_guard=guard, session=self.rec.id,
                      artists=list(ARTISTS), camera_errors=getattr(self.frames, "errors", 0),
                      camera_error=getattr(self.frames, "last_error", None), **asdict(self.settings))

    def _set(self, state: str) -> None:
        self.state = state
        self.states_seen.append(state)
        self.emit_state()

    def _emit_shot(self, who: str, turn: int) -> None:
        """`who` is "start", "human", "robot" or "final", so the page can label thumbnails without parsing
        the URL, and `turn` is the photo's own turn number, the one in its filename. `frame_url` is the
        raw landscape camera frame of the same capture, when one was saved."""
        p = self.rec.latest_photo
        if p is not None:
            f = self.rec.latest_frame
            self.bus.emit("shot", url=f"/sessions/{self.rec.id}/{p.name}", turn=turn, who=who,
                          frame_url=f"/sessions/{self.rec.id}/{f.name}" if f is not None else None)

    def _set_look(self, value: bool) -> None:
        self.at_look = value
        if self.guard is not None:
            self.guard.at_look = value

    # ---- the loop ------------------------------------------------------------------------------
    async def run(self) -> None:
        try:
            self._set("start")
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
                    if not self._running.is_set():
                        continue          # the operator paused: stop() aborted the state, it did not fault
                    self.last_error = f"{type(exc).__name__}: {exc}"
                    self.bus.emit("error", message=self.last_error)
                    self._running.clear()
                    continue
                self._set(nxt)
        finally:
            self.rec.write()

    async def _state_start(self) -> str:
        await self.ctl.go_look()
        self._set_look(True)
        self.previous_photo, frame = await self._capture_board()
        self.rec.save_photo(0, "start", self.previous_photo, frame)
        self._emit_shot("start", 0)
        return "human_turn"

    def _board_homography(self) -> np.ndarray:
        if self._homography is None:
            quad = vision.board_quad(np.array(self.cal["marks_image"], np.float32), self.cal["board_tl_index"])
            self._homography = vision.board_homography(quad)
        return self._homography

    async def _state_human_turn(self) -> str:
        """The visitor draws, then presses Go on the page (the `pass` command). Nothing ends the turn
        by itself: the stillness, hand, and marker-dot trigger was removed on day 2."""
        self._pass.clear()
        while True:
            if not self._running.is_set():
                return "human_turn"
            if self._pass.is_set():
                self._pass.clear()
                return "capture"
            await asyncio.sleep(self.poll_s)

    async def _capture_board(self) -> tuple[np.ndarray, np.ndarray]:
        """A median capture at the look pose: the warped board and the raw frame it came from. Also
        refreshes the hand guard's reference frame, since the arm is at the look pose and nobody is drawing."""
        await asyncio.sleep(SETTLE_AFTER_LOOK_S if self.poll_s >= 0.1 else 0.0)
        frame = await self.frames.capture_median()
        quad = vision.find_corner_marks(frame, expected=self.cal["marks_image"])
        drift = max(float(np.hypot(*(np.asarray(q) - np.asarray(e)))) for q, e in zip(quad, self.cal["marks_image"]))
        if drift > 70:
            self.bus.emit("error", message=f"board shifted {drift * self._mm_per_px():.0f} mm since calibration; re-run calibrate")
        if self.guard is not None:
            if self.guard.reading(Frame(frame, None, monotonic())) is True:
                self.bus.emit("error", message="a hand was in the capture; keeping the previous reference frame")
            else:
                self.guard.reference = frame
        return vision.warp_to_board(frame, vision.board_quad(quad, self.cal["board_tl_index"])), frame

    def _mm_per_px(self) -> float:
        return float(self.cal.get("mm_per_px") or vision.mm_per_px(np.array(self.cal["marks_image"], np.float32)))

    async def _state_capture(self) -> str:
        # Go can be pressed while a hand is still over the board; never photograph a hand (it would
        # be traced as ink and become the hand check's reference).
        if self.guard is not None and await self.guard():
            self.bus.emit("error", message="a hand is still over the board; still your turn")
            return "human_turn"
        photo, frame = await self._capture_board()
        mask, coverage = vision.new_ink(photo, self.previous_photo)
        new_cam = vision.trace(mask)
        if not new_cam:
            self.bus.emit("human", polylines=self.human_ink, new=[], found=False, turn=self.turn + 1)
            return "human_turn"
        self.human_new_cam = new_cam
        self.human_new = vision.cam_to_robot(new_cam, self.cal)
        self.human_ink = self.human_ink + self.human_new
        self.coverage = coverage
        self.previous_photo = photo
        self.rec.save_photo(self.turn + 1, "human", photo, frame)
        self._emit_shot("human", self.turn + 1)
        self.bus.emit("human", polylines=self.human_ink, new=self.human_new, found=True, turn=self.turn + 1)
        return "interpret"

    async def _state_interpret(self) -> str:
        self.result = await self.brain.propose(self.previous_photo, self.human_new_cam, self.history,
                                               self.settings.length, self.turn + 1, self.settings.exchanges,
                                               artist=self.settings.artist)
        p = self.result.proposal
        self.bus.emit("interpretation", sees=p.sees if p else "", adds=p.adds if p else "",
                      thought=(getattr(p, "thought", "") or FALLBACK_THOUGHT) if p else FALLBACK_THOUGHT,
                      quip=(getattr(p, "quip", "") or FALLBACK_QUIP) if p else FALLBACK_QUIP,
                      source=self.result.source, latency_s=round(self.result.latency_s, 2), error=self.result.error,
                      turn=self.turn + 1)
        return "plan"

    async def _state_plan(self) -> str:
        budget = cfg.BUDGET_MM[self.settings.length]
        ink = all_ink(self.previous_photo, self.cal)
        r = self.result
        if r is not None and r.proposal is not None:
            strokes = map_strokes([s.model_dump() for s in r.proposal.strokes], self.cal)
            styled, self.color = STYLERS[self.settings.artist].style(
                planner.validate(strokes, ink, budget),
                energy=self.settings.energy, direction_deg=self.settings.direction)
            sees, adds, source = r.proposal.sees, r.proposal.adds, r.source
        else:
            styled, self.color = STYLERS[self.settings.artist].fallback(self.human_new)
            sees, adds, source = "(fallback)", "outline and ticks around your mark", "fallback"
        self.plan = planner.finalize(styled, ink, budget)
        if not self.plan and r is not None and r.proposal is not None:
            # every stroke Claude proposed sat inside the 5 mm clearance: answer the visitor's mark instead
            styled, self.color = STYLERS[self.settings.artist].fallback(self.human_new)
            self.plan = planner.finalize(styled, ink, budget)
            source = "fallback"
        if not self.plan:
            self.bus.emit("error", message="every proposed stroke was within 5 mm of existing ink; "
                                           "nothing to draw this turn")
        self.history = self.history + [{"sees": sees, "adds": adds, "source": source}]
        turn = self.turn + 1
        self.rec.save_svg(turn, svg.render(ink, self.robot_ink, self.plan, self.color))
        self.rec.record_turn(turn, sees=sees, adds=adds, source=source, latency_s=round(r.latency_s, 2) if r else None,
                             error=r.error if r else None, color=self.color,
                             planned_mm=round(sum(length(pl) for pl in self.plan)))
        self.bus.emit("plan", polylines=self.plan, color=cfg.COLOR_HEX.get(self.color, "#222222"), budget_mm=budget,
                      turn=self.turn + 1)
        return "robot_draw"

    async def _wait_hands_clear(self) -> None:
        """Right before the arm leaves the look pose: wait for the hand to go, then mark the guard
        blind until the next go_look (the wrist camera no longer sees the board it was checked against)."""
        if self.guard is not None:
            cause = "hand over the board or dock"
            for second in range(HAND_WAIT_S):
                blind = self.frames.latest() is None       # no frame at all reads as a hand; say which it is
                if not blind and not await self.guard():
                    break
                cause = "no camera frame for the hand check" if blind else "hand over the board or dock"
                if second % HAND_WAIT_MESSAGE_S == 0:      # the same line every second is noise on the page
                    self.bus.emit("error", message=f"{cause}; waiting" if blind else
                                  f"{cause}: waiting before the arm moves")
                await asyncio.sleep(1.0)
            else:
                raise Blocked(f"{cause} for {HAND_WAIT_S} s")
        self._set_look(False)

    async def _forward_progress(self, task: asyncio.Task, turn: int) -> None:
        while not task.done():
            try:
                ev = await asyncio.wait_for(self.ctl.events.get(), 0.1)
            except asyncio.TimeoutError:
                continue
            self.bus.emit("progress", stroke=ev["stroke"], drawn_mm=round(ev["drawn_mm"]), turn=turn)
        while not self.ctl.events.empty():
            ev = self.ctl.events.get_nowait()
            self.bus.emit("progress", stroke=ev["stroke"], drawn_mm=round(ev["drawn_mm"]), turn=turn)

    async def _draw(self, polylines: list[Polyline], budget_mm: float, budget_s: float, turn: int):
        """`turn` is the exchange the strokes belong to: the one in progress for a plan, the one just
        finished for the signature."""
        await self._wait_hands_clear()
        await self.ctl.pick_marker(self.color, self.dot_displacement.get(self.color, (0.0, 0.0)))
        task = asyncio.create_task(self.ctl.draw(polylines, budget_mm, budget_s))
        try:
            await self._forward_progress(task, turn)
            result = await task
        except BaseException:
            # the loop is being cancelled or the draw failed; the arm must stop before anything else
            await self.ctl.stop()
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
            raise
        await self.ctl.return_marker(self.color)
        return result

    async def _state_robot_draw(self) -> str:
        if not self.plan:
            return "look"
        result = await self._draw(self.plan, cfg.BUDGET_MM[self.settings.length], cfg.BUDGET_S[self.settings.length],
                                  self.turn + 1)
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
        self._emit_shot("robot", self.turn)
        self.rec.record_turn(self.turn, coverage=round(self.coverage, 3))
        self.rec.set_turn(self.turn)
        self.rec.write()
        if self.turn >= self.settings.exchanges or self.coverage >= cfg.COVERAGE_END:
            return "finish"
        return "human_turn"

    async def _state_finish(self) -> str:
        ox, oy = cfg.BOARD_W_MM - cfg.INSET_MM - 12, cfg.BOARD_H_MM - cfg.INSET_MM - 12
        signature = [[(ox + x, oy + y) for x, y in pl] for pl in cfg.SIGNATURE_MM]
        if not self._signed:
            self.bus.emit("plan", polylines=signature, color=cfg.COLOR_HEX.get(self.color, "#222222"), budget_mm=100,
                          turn=self.turn)
            await self._draw(signature, 100.0, 20.0, self.turn)
            self.robot_ink = self.robot_ink + signature
            self._signed = True
        await self.ctl.go_look()
        self._set_look(True)
        photo, frame = await self._capture_board()
        self.previous_photo = photo
        self.rec.save_photo(self.turn, "final", photo, frame)
        self._emit_shot("final", self.turn)
        self.rec.write()
        video = await asyncio.to_thread(self.rec.stitch)
        if video is not None:
            self.bus.emit("video", url=f"/sessions/{self.rec.id}/session.mp4", path=str(video))
        else:
            self.bus.emit("error", message="the video could not be stitched; the turn photos are in the session folder")
        return "finished"
