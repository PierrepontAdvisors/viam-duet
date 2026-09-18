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
            await asyncio.sleep(cfg.GRIPPER_SETTLE_S)
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
