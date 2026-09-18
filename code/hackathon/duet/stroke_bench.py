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
