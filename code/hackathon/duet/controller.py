"""The only module that talks to the arm. Every motion is a planned move of the gripper frame,
so the obstacles configured on the machine (table, walls, ceiling) always apply.

Run `python -m duet.controller` to print the arm's status without moving anything.
"""
from __future__ import annotations

import asyncio
import math
from dataclasses import dataclass
from time import monotonic
from typing import Awaitable, Callable

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
    """A hand was over the board or dock, so the controller refused to move."""


@dataclass(frozen=True)
class DrawResult:
    strokes_done: int
    drawn_mm: float
    seconds: float


def shifted(p: Pose, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> Pose:
    """A new pose offset in world axes, orientation unchanged."""
    return Pose(x=p.x + dx, y=p.y + dy, z=p.z + dz, o_x=p.o_x, o_y=p.o_y, o_z=p.o_z, theta=p.theta)


LINEAR = Constraints(linear_constraint=[LinearConstraint(line_tolerance_mm=cfg.LINE_TOLERANCE_MM)])


class Controller:
    def __init__(self, machine: RobotClient, poses: dict, board: BoardToRobot | None = None):
        self.arm = Arm.from_robot(machine, viam_conn.ARM)
        self.gripper = Gripper.from_robot(machine, viam_conn.GRIPPER)
        self.motion = MotionClient.from_robot(machine, viam_conn.MOTION)
        self.poses = poses
        self.board = board
        self.held_mode = False                       # True: marker stays in the gripper, dock steps skipped
        self.hand_check: Callable[[], Awaitable[bool]] | None = None   # set by the session in plan 3
        self.events: asyncio.Queue = asyncio.Queue()
        self.move_times: list[float] = []            # seconds per planned move, for stroke_bench
        self._lock = asyncio.Lock()

    # ---- primitives --------------------------------------------------------------------------
    async def _move(self, pose: Pose, linear: bool = False) -> None:
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

    async def move_to(self, pose: Pose, linear: bool = False) -> None:
        """Public single move, used by teach.verify."""
        async with self._lock:
            await self._assert_clear()
            await self._move(pose, linear)

    async def set_speed(self, deg_per_s: float) -> None:
        await self.arm.do_command({"set_speed": float(deg_per_s)})

    async def gripper_set(self, position: int) -> None:
        """Gripper opening on the xArm scale: 0 closed, 850 fully open."""
        await self.gripper.do_command({"set": float(position)})

    async def tip_pose(self) -> Pose:
        result = await self.motion.get_pose(component_name=viam_conn.GRIPPER, destination_frame="world")
        return result.pose

    async def _assert_clear(self) -> None:
        if self.hand_check is not None and await self.hand_check():
            raise Blocked("hand over the board or dock")

    def _pose(self, *keys: str) -> Pose:
        node = self.poses
        for key in keys:
            node = node[key]
        return dict_to_pose(node)

    def _apply_board_displacement(self, pose: Pose, d: tuple[float, float]) -> Pose:
        """Shift a world pose by a board-millimeter displacement, using only the board map's linear part."""
        b = self.board
        ex = [c / b.width_mm for c in b.ex]
        ey = [c / b.height_mm for c in b.ey]
        return shifted(pose,
                       dx=ex[0] * d[0] + ey[0] * d[1],
                       dy=ex[1] * d[0] + ey[1] * d[1],
                       dz=ex[2] * d[0] + ey[2] * d[1])

    # ---- sequences ---------------------------------------------------------------------------
    async def go_look(self) -> None:
        async with self._lock:
            await self._assert_clear()
            await self.set_speed(cfg.SPEED_TRAVEL)
            await self._move(self._pose("look"))

    async def pick_marker(self, slot: str, displacement_mm: tuple[float, float] = (0.0, 0.0)) -> None:
        """Hover, descend, grab, pull straight up to uncap, rise. `displacement_mm` is where the camera
        saw the marker's dot relative to its calibrated spot (plan 2); (0, 0) trusts the taught pose."""
        if self.held_mode:
            return
        async with self._lock:
            await self._assert_clear()
            grip = self._pose("slot", slot)
            if displacement_mm != (0.0, 0.0) and self.board is not None:
                grip = self._apply_board_displacement(grip, displacement_mm)
            await self.gripper_set(cfg.GRIPPER_OPEN_FOR_PICK)
            await self.set_speed(cfg.SPEED_TRAVEL)
            await self._move(shifted(grip, dz=cfg.DOCK_HOVER_MM))
            await self.set_speed(cfg.SPEED_DOCK)
            await self._move(grip, linear=True)
            await self.gripper.grab()
            await asyncio.sleep(0.3)
            await self._move(shifted(grip, dz=cfg.UNCAP_LIFT_MM), linear=True)
            await self._move(shifted(grip, dz=cfg.DOCK_HOVER_MM), linear=True)
            await self.set_speed(cfg.SPEED_TRAVEL)

    async def return_marker(self, slot: str) -> None:
        """Hover, descend slowly, seat the tip in the cap, press, release, rise."""
        if self.held_mode:
            return
        async with self._lock:
            await self._assert_clear()
            seat = self._pose("seat", slot)
            await self.set_speed(cfg.SPEED_TRAVEL)
            await self._move(shifted(seat, dz=cfg.DOCK_HOVER_MM))
            await self.set_speed(cfg.SPEED_DOCK)
            await self._move(shifted(seat, dz=cfg.UNCAP_LIFT_MM), linear=True)
            await self._move(seat, linear=True)
            await self._move(shifted(seat, dz=-cfg.PRESS_MM), linear=True)
            await self.gripper_set(cfg.GRIPPER_OPEN_FOR_PICK)
            await asyncio.sleep(0.3)
            await self._move(shifted(seat, dz=cfg.DOCK_HOVER_MM), linear=True)
            await self.set_speed(cfg.SPEED_TRAVEL)

    async def draw(self, polylines: list[Polyline], budget_mm: float, budget_s: float,
                   z_offset_mm: float = 0.0) -> DrawResult:
        """Draw polylines (board mm) in order until either budget runs out. Pen up between strokes.
        `z_offset_mm` raises every pen-down pose; stroke_bench uses it for a dry run above the surface."""
        if self.board is None:
            raise RuntimeError("no board calibration: run `python -m duet.teach corner tl|tr|bl` first")
        async with self._lock:
            start = monotonic()
            drawn = 0.0
            done = 0
            try:
                await self.set_speed(cfg.SPEED_TRAVEL)
                for index, pl in enumerate(polylines):
                    if drawn >= budget_mm or monotonic() - start >= budget_s:
                        break
                    await self._assert_clear()
                    pts = resample(pl, cfg.WAYPOINT_MM)
                    await self._move(self.board.to_world(*pts[0], lift=cfg.LIFT_MM + z_offset_mm))
                    await self.set_speed(cfg.SPEED_DRAW)
                    await self._move(self.board.to_world(*pts[0], lift=z_offset_mm), linear=True)
                    prev = pts[0]
                    for p in pts[1:]:
                        await self._move(self.board.to_world(*p, lift=z_offset_mm), linear=True)
                        drawn += math.dist(prev, p)
                        prev = p
                    await self._move(self.board.to_world(*prev, lift=cfg.LIFT_MM + z_offset_mm), linear=True)
                    await self.set_speed(cfg.SPEED_TRAVEL)
                    done += 1
                    await self.events.put({"type": "progress", "stroke": index, "drawn_mm": drawn})
            except Exception:
                await self.stop()
                raise
            return DrawResult(done, drawn, monotonic() - start)

    async def stop(self) -> None:
        """Emergency path: no lock, so it works while another sequence holds it."""
        await self.arm.stop()

    async def clear_error(self) -> None:
        await self.arm.do_command({"clear_error": True})

    async def status(self) -> dict:
        joints = await self.arm.get_joint_positions()
        holding = await self.gripper.is_holding_something()
        return {
            "joints_deg": [round(v, 1) for v in joints.values],
            "holding": holding.is_holding_something,
            "planned_moves": len(self.move_times),
        }


async def _main() -> None:
    from duet.calib import load_poses
    async with await viam_conn.connect() as machine:
        print(await Controller(machine, load_poses()).status())


if __name__ == "__main__":
    asyncio.run(_main())
