"""Stage 3: pick, uncap, recap, and return one marker N times; count clean cycles.

    python -m duet.dock_test green 20
    python -m duet.dock_test cycles 20        same, using the configured marker (config.MARKER)
    python -m duet.dock_test gripper 300      open the gripper to a position on the 0..850 scale and stop

At any prompt, type q and press Enter to stop. Ctrl-C does not interrupt a prompt.
"""
from __future__ import annotations

import asyncio
import sys

import viam_conn
from duet import config as cfg
from duet.calib import load_poses
from duet.controller import Controller

SLOTS = ("red", "green", "blue")


async def ask(prompt: str) -> str:
    return (await asyncio.to_thread(input, prompt)).strip().lower()


async def set_gripper(position: int) -> None:
    async with await viam_conn.connect() as machine:
        await Controller(machine, load_poses()).gripper_set(position)
        print(f"gripper at {position}; measure the finger gap with calipers")


async def cycles(slot: str, count: int) -> None:
    poses = load_poses()
    async with await viam_conn.connect() as machine:
        c = Controller(machine, poses)
        if await ask(f"Stand clear of the arm and the dock. Enter to run {count} cycles on {slot}, q to quit: ") == "q":
            return
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
                if await ask("Fix it, stand clear, then Enter to continue or q to stop: ") == "q":
                    break
                await c.recover()   # clears the arm's error and lifts if the tool was left low
        await c.go_look()
    print(f"{ok}/{count} cycles succeeded")


def main(argv: list[str]) -> None:
    if not argv:
        raise SystemExit(__doc__)
    if argv[0] == "gripper":
        if len(argv) < 2 or not argv[1].isdigit() or not 0 <= int(argv[1]) <= 850:
            raise SystemExit("usage: python -m duet.dock_test gripper <0..850>")
        asyncio.run(set_gripper(int(argv[1])))
        return
    slot = argv[0] if argv[0] not in ("cycles",) else cfg.MARKER
    if slot not in SLOTS:
        raise SystemExit(f"unknown marker '{slot}'; choose one of {', '.join(SLOTS)}")
    count = int(argv[1]) if len(argv) > 1 else 20
    asyncio.run(cycles(slot, count))


if __name__ == "__main__":
    main(sys.argv[1:])
