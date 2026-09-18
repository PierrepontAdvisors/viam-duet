"""Compute a straight-down look pose over the board center and center the camera on the board.

    python -m duet.aim            move, capture, correct, repeat (up to 4 times), then save as `look`
    python -m duet.aim --height 400

Starts with the gripper over the board center at the given height (default 450 mm above the
touched-off plane; the pen hangs ~200 mm below the camera, so this puts the camera near 450 mm),
pointing straight down with the touch-off orientation. Steps the height down if the pose is unreachable. Each round captures a
frame, finds the corner marks, measures the board center's offset from the image center, converts
that to board millimeters with the marks' scale, and shifts the gripper by the opposite amount.
"""
from __future__ import annotations

import asyncio
import sys
import time

import cv2
import numpy as np
from viam.components.camera import Camera

import viam_conn
from duet import config as cfg
from duet import vision
from duet.calib import BoardToRobot, load_poses, save_pose
from duet.camera import median_capture
from duet.controller import Controller, MoveRefused, shifted

IMAGE_CENTER = (640.0, 360.0)
TOLERANCE_MM = 3.0
ROUNDS = 4


async def try_move(c: Controller, pose) -> bool:
    """Planned move; False if the planner or the arm's IK rejects the pose as unreachable."""
    try:
        await c.move_to(pose)
        return True
    except Exception as exc:
        text = str(exc)
        if "unreachable" in text or "IK" in text or isinstance(exc, MoveRefused):
            print(f"  unreachable: {text[:90]}", flush=True)
            await c.clear_error()
            return False
        raise


async def main(height_mm: float) -> None:
    poses = load_poses()
    board = BoardToRobot.from_poses(poses)
    cx, cy = cfg.BOARD_W_MM / 2, cfg.BOARD_H_MM / 2
    async with await viam_conn.connect() as machine:
        c = Controller(machine, poses, board)
        cam = Camera.from_robot(machine, viam_conn.CAMERA)
        for s in range(10, 0, -1):
            print(f"arm moves in {s}...", flush=True)
            time.sleep(1)
        await c.set_speed(cfg.SPEED_TRAVEL)
        pose = None
        for h in (height_mm, height_mm - 20, height_mm - 40, height_mm - 60, height_mm - 80):
            print(f"trying gripper {h:.0f} mm above the plane over the board center", flush=True)
            candidate = board.to_world(cx, cy, lift=h)
            if await try_move(c, candidate):
                pose, height_mm = candidate, h
                break
        if pose is None:
            raise SystemExit("no reachable straight-down pose over the board; lower --height further")
        for round_no in range(1, ROUNDS + 1):
            if round_no > 1 and not await try_move(c, pose):
                raise SystemExit("the corrected pose is unreachable; try a lower --height")
            await asyncio.sleep(1.0)
            frame = await median_capture(cam)
            quad = vision.find_corner_marks(frame)
            center_px = quad.mean(axis=0)
            dx_px, dy_px = center_px[0] - IMAGE_CENTER[0], center_px[1] - IMAGE_CENTER[1]
            px_per_mm_x = float(np.linalg.norm(quad[1] - quad[0])) / cfg.BOARD_W_MM
            px_per_mm_y = float(np.linalg.norm(quad[3] - quad[0])) / cfg.BOARD_H_MM
            dx_mm, dy_mm = dx_px / px_per_mm_x, dy_px / px_per_mm_y
            top, left = quad[1] - quad[0], quad[3] - quad[0]
            skew = abs(float(np.dot(top, left)) / (np.linalg.norm(top) * np.linalg.norm(left)))
            print(f"round {round_no}: board center is {dx_mm:+.1f} mm x, {dy_mm:+.1f} mm y from the image center; "
                  f"{px_per_mm_x:.2f} px/mm; edge skew cos {skew:.3f}", flush=True)
            cv2.imwrite(f"captures/aim_{round_no}.jpg", frame)
            if abs(dx_mm) <= TOLERANCE_MM and abs(dy_mm) <= TOLERANCE_MM:
                break
            # the camera must move by (+dx, +dy) in board axes to bring the board center to the image center
            b = board
            ex = np.array(b.ex) / b.width_mm
            ey = np.array(b.ey) / b.height_mm
            shift = ex * dx_mm + ey * dy_mm
            pose = shifted(pose, dx=float(shift[0]), dy=float(shift[1]), dz=float(shift[2]))
        save_pose("look", pose)
        print(f"saved look: x={pose.x:.1f} y={pose.y:.1f} z={pose.z:.1f}")


if __name__ == "__main__":
    h = float(sys.argv[sys.argv.index("--height") + 1]) if "--height" in sys.argv else 220.0
    asyncio.run(main(h))
