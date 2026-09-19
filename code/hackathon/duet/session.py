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
                      artists=list(ARTISTS), **asdict(self.settings))

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
        if self.settings.handoff == "dock" and not self.cal.get("dots"):
            self.bus.emit("error", message="dock handoff has no calibrated marker dots, so the turn cannot end by itself: "
                                           "use Pass, or switch the marker setting to Held")
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
        # The trigger's debounce can fire one poll after a hand was last seen; never photograph a
        # hand (it would be traced as ink and become the hand check's reference).
        if self.guard is not None and await self.guard():
            self.bus.emit("error", message="a hand is still over the board; still your turn")
            return "human_turn"
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
                      thought=(getattr(p, "thought", "") or FALLBACK_THOUGHT) if p else FALLBACK_THOUGHT,
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
                                              energy=self.settings.energy, direction_deg=self.settings.direction)
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
        if video is not None:
            self.bus.emit("video", url=f"/sessions/{self.rec.id}/session.mp4", path=str(video))
        else:
            self.bus.emit("error", message="the video could not be stitched; the turn photos are in the session folder")
        return "finished"
