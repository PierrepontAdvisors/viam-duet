"""Stage 2: pick the marker from the dock, draw a hard-coded square, return it, timing every planned move.

    python -m duet.stroke_bench            60 mm square at the board center
    python -m duet.stroke_bench 40         40 mm square
    python -m duet.stroke_bench 60 --dry   same, traced 20 mm above the surface without touching it
    python -m duet.stroke_bench 60 --held  the marker is already in the gripper; skip the dock pick and return
    python -m duet.stroke_bench 60 --dock  pick from the dock and return even when config.HELD_MODE is on
    python -m duet.stroke_bench 60 --pen 3 draw 3 mm above the touched-off plane for this run (tunes PEN_DOWN_OFFSET_MM)

At any prompt, type q and press Enter to quit. Ctrl-C does not interrupt a prompt.
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
    answer = (await asyncio.to_thread(input, prompt)).strip().lower()
    if answer == "q":
        raise SystemExit("quit; the arm stays where it is")
    return answer


async def main(side_mm: float, dry: bool, held: bool) -> None:
    poses = load_poses()
    board = BoardToRobot.from_poses(poses)
    cx, cy, h = cfg.BOARD_W_MM / 2, cfg.BOARD_H_MM / 2, side_mm / 2
    square = [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h), (cx - h, cy - h)]
    async with await viam_conn.connect() as machine:
        c = Controller(machine, poses, board)
        c.held_mode = held
        what = "draw" if held else f"pick the {cfg.MARKER} marker from the dock and draw"
        await ask(f"Stand clear of the arm, board, and dock. Enter to {what}, q to quit... ")
        await c.go_look()
        await c.pick_marker(cfg.MARKER)      # no-op with --held
        result = await c.draw([square], budget_mm=10_000, budget_s=600, z_offset_mm=cfg.LIFT_MM if dry else 0.0)
        await c.return_marker(cfg.MARKER)    # no-op with --held
        await c.go_look()
    t = c.move_times
    print(f"strokes {result.strokes_done}, {result.drawn_mm:.0f} mm in {result.seconds:.1f} s")
    print(f"planned moves {len(t)}: mean {statistics.mean(t):.2f} s, "
          f"p95 {sorted(t)[int(0.95 * (len(t) - 1))]:.2f} s, max {max(t):.2f} s")
    print(f"drawing rate {result.drawn_mm / result.seconds:.0f} mm/s at WAYPOINT_MM={cfg.WAYPOINT_MM}")


if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--pen" in argv:
        i = argv.index("--pen")
        cfg.PEN_DOWN_OFFSET_MM = float(argv[i + 1])
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    print(f"pen-down offset {cfg.PEN_DOWN_OFFSET_MM:.1f} mm above the touched-off plane")
    held = ("--held" in argv or cfg.HELD_MODE) and "--dock" not in argv
    asyncio.run(main(float(args[0]) if args else 60.0, dry="--dry" in argv, held=held))
