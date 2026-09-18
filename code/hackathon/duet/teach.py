"""Record poses by moving the arm by hand (xArm manual mode).

    python -m duet.teach look            park and look pose above the board
    python -m duet.teach approach        dock approach pose: every pick and return enters and leaves the dock through it
    python -m duet.teach slot red        fingers around the red marker's barrel at grip height (also green, blue)
    python -m duet.teach seat red        holding the red marker, tip seated in its cap
    python -m duet.teach corner tl       holding a marker, tip touching the top-left inner corner (also tr, bl)
    python -m duet.teach show            print every stored pose
    python -m duet.teach verify          replay every stored pose, 30 mm high, one at a time
    python -m duet.teach recover         clear the arm's error state after a fault
    python -m duet.teach pick            pick the marker from the dock with the runtime grip and hold it,
                                         so corners can be re-taught with the exact grip the robot uses

At any prompt, type q and press Enter to abort: manual mode is exited and nothing is saved.
Ctrl-C does not interrupt a prompt, so use q.
"""
from __future__ import annotations

import asyncio
import sys

import viam_conn
from duet import config as cfg
from duet.calib import dict_to_pose, load_poses, save_pose
from duet.controller import Controller, shifted

SLOTS = ("red", "green", "blue")
CORNERS = ("tl", "tr", "bl")
VERIFY_LIFT_MM = 30.0


class Abort(Exception):
    """The operator typed q at a prompt."""


def flatten(poses: dict, prefix: str = "") -> list[tuple[str, dict]]:
    """[('corner.tl', {...}), ('look', {...}), ...] in sorted order. A leaf is a pose dict, which
    has the pose keys; anything else is a group. Group names are never pose field names."""
    out: list[tuple[str, dict]] = []
    for key, value in sorted(poses.items()):
        name = f"{prefix}{key}"
        if "o_z" in value:
            out.append((name, value))
        else:
            out.extend(flatten(value, name + "."))
    return out


async def ask(prompt: str) -> str:
    """Terminal prompt on a worker thread so the Viam session stays alive. `q` aborts."""
    answer = (await asyncio.to_thread(input, prompt)).strip().lower()
    if answer == "q":
        raise Abort()
    return answer


async def ask_in_manual(c: Controller, prompt: str) -> None:
    """Prompt while the arm should be limp. The driver sometimes drops out of manual mode on its
    own, so `m` re-enters it; any other answer (except q) continues."""
    while True:
        answer = await ask(prompt + "\n  Enter to continue, m if the arm is not limp, q to abort... ")
        if answer != "m":
            return
        await c.manual_mode(False)
        await c.manual_mode(True)
        print("re-entered manual mode; try moving the arm")


async def prepare_gripper(c: Controller) -> bool:
    """The operator says what the gripper holds, because this unit's holding sensor is unreliable:
    k = keep what it holds, o = open the fingers, q = abort. Returns True when kept."""
    answer = await ask("Is a marker already in the gripper? k = keep it, o = open the fingers "
                       "(anything held will drop), q = abort: ")
    if answer == "k":
        return True
    if answer != "o":
        raise Abort()
    await c.gripper_set(cfg.GRIPPER_OPEN_FOR_PICK)
    return False


async def teach(name: str, prompt: str, with_marker: bool, release_after: bool = False) -> None:
    async with await viam_conn.connect() as machine:
        c = Controller(machine, load_poses())
        try:
            kept = await prepare_gripper(c)
            await c.manual_mode(True)
            try:
                if with_marker and not kept:
                    await ask_in_manual(c, "MANUAL MODE, the arm should be limp. Lower the open fingers around "
                                           "the marker's barrel, standing in its cap or held there by hand, then "
                                           "Enter to grab.")
                    await c.gripper.grab()
                    await asyncio.sleep(cfg.GRIPPER_SETTLE_S)
                await ask_in_manual(c, f"MANUAL MODE, the arm should be limp. {prompt}")
                pose = await c.tip_pose()
            finally:
                await c.manual_mode(False)
            save_pose(name, pose)
            print(f"saved {name}: x={pose.x:.1f} y={pose.y:.1f} z={pose.z:.1f}")
        except Abort:
            print("aborted: nothing saved")
            return
        if not release_after:
            return
        try:
            await ask("Hands clear of the arm? Enter to release the marker and lift, q to keep holding it... ")
        except Abort:
            print("marker still held; the arm has not moved")
            return
        try:
            await c.gripper_set(cfg.GRIPPER_OPEN_FOR_PICK)   # leave the marker standing in its cap
            await asyncio.sleep(cfg.GRIPPER_SETTLE_S)
            await c.set_speed(cfg.SPEED_DOCK)
            await c.move_to(shifted(pose, dz=cfg.DOCK_HOVER_MM))
            await c.set_speed(cfg.SPEED_TRAVEL)
        except Exception as exc:
            print(f"lift failed after saving {name}: {exc}\n"
                  "The gripper is open and the arm is near the dock. Check that it is clear, then run "
                  "`python -m duet.teach recover` before the next command.")


async def verify() -> None:
    poses = load_poses()
    async with await viam_conn.connect() as machine:
        c = Controller(machine, poses)
        await c.set_speed(cfg.SPEED_DOCK)
        try:
            for name, d in flatten(poses):
                pose = dict_to_pose(d)
                target = pose if name == "look" else shifted(pose, dz=VERIFY_LIFT_MM)
                where = "exact" if name == "look" else f"{VERIFY_LIFT_MM:.0f} mm above"
                await ask(f"next: {name} ({where}). Stand clear. Enter to move, q to stop... ")
                await c.move_to(target)
                print(f"  at {name}")
        except Abort:
            print("stopped; the arm stays where it is")
        finally:
            await c.set_speed(cfg.SPEED_TRAVEL)


async def recover() -> None:
    async with await viam_conn.connect() as machine:
        await Controller(machine, load_poses()).recover()
        print("arm error cleared")


async def pick() -> None:
    async with await viam_conn.connect() as machine:
        c = Controller(machine, load_poses())
        try:
            await ask(f"Stand clear of the arm and dock. Enter to pick the {cfg.MARKER} marker with the runtime "
                      "grip and hold it, q to abort... ")
        except Abort:
            return
        await c.go_look()
        await c.pick_marker(cfg.MARKER)
        print("holding the marker above the dock. Now run `teach corner tl|tr|bl` and answer k, "
              "then `teach seat green` with k to put it back.")


def main(argv: list[str]) -> None:
    if not argv:
        raise SystemExit(__doc__)
    verb, args = argv[0], argv[1:]
    choice = args[0] if args else ""
    if verb == "look":
        asyncio.run(teach("look", "Move the arm to the look pose: 350 to 400 mm above the board, "
                          "tilted 15 to 20 degrees so the light's reflection is out of the camera frame.", False))
    elif verb == "approach":
        asyncio.run(teach("dock.approach", "Move the arm to the dock approach pose: gripper pointing straight "
                          "down about 80 mm above the marker caps, on the side of the row away from the camera "
                          "cable, fingers aligned to close across the row. Picks enter and leave through here.",
                          False))
    elif verb in ("slot", "seat"):
        if choice not in SLOTS:
            raise SystemExit(f"unknown marker '{choice}'; choose one of {', '.join(SLOTS)}")
        if verb == "slot":
            asyncio.run(teach(f"slot.{choice}", f"Put the open fingers around the {choice} marker's barrel at "
                              "grip height while it stands in its cap, gripper pointing straight down.", False))
        else:
            asyncio.run(teach(f"seat.{choice}", f"Make sure the {choice} marker's cap is pushed into the putty "
                              "at its row position with the tip seated in it and the gripper pointing straight down. "
                              "If it already is, just press Enter.", True, release_after=True))
    elif verb == "corner":
        if choice not in CORNERS:
            raise SystemExit(f"unknown corner '{choice}'; choose one of {', '.join(CORNERS)}")
        asyncio.run(teach(f"corner.{choice}", f"Rest the marker tip on the writing surface at the {choice} "
                          "inner corner, gripper pointing straight down.", True))
    elif verb == "show":
        for name, d in flatten(load_poses()):
            print(f"{name:12s} x={d['x']:7.1f} y={d['y']:7.1f} z={d['z']:7.1f}")
    elif verb == "verify":
        asyncio.run(verify())
    elif verb == "recover":
        asyncio.run(recover())
    elif verb == "pick":
        asyncio.run(pick())
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
