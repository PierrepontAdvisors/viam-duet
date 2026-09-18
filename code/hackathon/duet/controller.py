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
        self._waiting = 0                            # recover() calls waiting for the lock; nothing may slip in front

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
        if not self._abort.is_set():   # a stop() during the lift may have truncated it: keep the flag
            self.needs_lift = False

    @asynccontextmanager
    async def _sequence(self, check_hand: bool = True, wait_s: float | None = None) -> AsyncIterator[None]:
        """One sequence at a time. Rejects with Busy if another is running (or waits up to `wait_s`
        for it to unwind), refuses with Blocked if a hand is present, and on any failure records
        `last_error`, halts the arm, and re-raises."""
        if wait_s is None:
            if self._lock.locked() or self._waiting:
                raise Busy("a sequence is already running; wait for it or call stop()")
            await self._lock.acquire()
        else:
            self._waiting += 1
            try:
                async with asyncio.timeout(wait_s):
                    await self._lock.acquire()
            except TimeoutError:
                raise Busy(f"a sequence is still running after {wait_s:.0f} s") from None
            finally:
                self._waiting -= 1
        try:
            self._abort.clear()
            if check_hand and await self._hand_present():
                raise Blocked("hand over the board or dock")
            try:
                yield
            except BaseException as exc:   # includes task cancellation: the arm must still halt
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

    async def manual_mode(self, on: bool) -> None:
        """xArm teaching mode: the arm goes limp so the operator can move it by hand. Not a
        sequence: no lock and no hand gate, because hands on the arm are the point."""
        await self.arm.do_command({"enter_manual_mode": True} if on else {"exit_manual_mode": True})

    async def recover(self) -> None:
        """After a stop or a fault: wait for the aborted sequence to unwind, clear the arm's error
        state, and if the tool was left low lift it straight up before anything else moves. Runs
        without the hand gate, since the lift is a retreat from the surface and from any hand."""
        async with self._sequence(check_hand=False, wait_s=2 * cfg.MOVE_TIMEOUT_S):
            await self.clear_error()
            if self.needs_lift:
                await self.set_speed(cfg.SPEED_DOCK)
                await self._move(shifted(await self.tip_pose(), dz=self._lift_mm), linear=True)
                self._mark_clear()
            await self.set_speed(cfg.SPEED_TRAVEL)
        if not self._abort.is_set():   # a stop() during the recovery lift leaves the error in place
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
