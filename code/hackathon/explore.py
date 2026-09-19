"""Read-only tour of the machine. Proves the connection and prints what the arm, gripper,
and camera report. Moves nothing. Saves the camera frames to captures/.

    python explore.py
"""
import asyncio
from collections import defaultdict
from pathlib import Path

from viam.components.arm import Arm
from viam.components.camera import Camera
from viam.components.gripper import Gripper
from viam.services.motion import MotionClient

import viam_conn as cfg

CAPTURES = Path(__file__).with_name("captures")


def fmt_pose(p) -> str:
    return (
        f"x={p.x:.1f} y={p.y:.1f} z={p.z:.1f} mm, "
        f"orientation o=({p.o_x:.2f}, {p.o_y:.2f}, {p.o_z:.2f}) theta={p.theta:.1f} deg"
    )


def extension_for(mime_type) -> str:
    m = str(getattr(mime_type, "value", mime_type)).lower()  # CameraMimeType enum or plain str
    if "png" in m:
        return "png"
    if "jpeg" in m or "jpg" in m:
        return "jpg"
    if "dep" in m:
        return "dep"  # Viam's raw depth format
    return "bin"


async def main() -> None:
    async with await cfg.connect() as machine:
        print(f"connected to {cfg.MACHINE_ADDRESS}\n")

        by_api: dict[str, list[str]] = defaultdict(list)
        for rn in machine.resource_names:
            by_api[f"{rn.type}:{rn.subtype}"].append(rn.name)
        print("resources:")
        for api in sorted(by_api):
            print(f"  {api}: {', '.join(sorted(by_api[api]))}")
        print("  (obstacles built with erh:vmodutils:obstacle show up as grippers)\n")

        await section("arm", show_arm, machine)
        await section("gripper", show_gripper, machine)
        await section("motion service", show_tip, machine)
        await section("camera", show_camera, machine)


async def section(label: str, fn, machine) -> None:
    """Run one part of the tour; report a failure and keep going instead of dying."""
    try:
        await fn(machine)
    except Exception as exc:  # one dead component should not hide the others
        print(f"{label}: FAILED: {exc}")
    print()


async def show_arm(machine) -> None:
    arm = Arm.from_robot(machine, cfg.ARM)
    print(f"arm '{cfg.ARM}'")
    print("  flange position:", fmt_pose(await arm.get_end_position()))
    joints = await arm.get_joint_positions()
    print("  joints (deg):", [round(v, 1) for v in joints.values])
    print("  moving:", await arm.is_moving())


async def show_gripper(machine) -> None:
    gripper = Gripper.from_robot(machine, cfg.GRIPPER)
    holding = await gripper.is_holding_something()
    print(f"gripper '{cfg.GRIPPER}'")
    print("  holding something:", holding.is_holding_something)


async def show_tip(machine) -> None:
    motion = MotionClient.from_robot(machine, cfg.MOTION)
    tip = await motion.get_pose(component_name=cfg.GRIPPER, destination_frame="world")
    print("gripper tip in world (motion service):", fmt_pose(tip.pose))


async def show_camera(machine) -> None:
    cam = Camera.from_robot(machine, cfg.CAMERA)
    images, _ = await cam.get_images()
    CAPTURES.mkdir(exist_ok=True)
    print(f"camera '{cfg.CAMERA}' returned {len(images)} image(s)")
    for img in images:  # NamedImage: .name, .data, .mime_type
        out = CAPTURES / f"{img.name}.{extension_for(img.mime_type)}"
        out.write_bytes(img.data)
        print(f"  {img.name}: {img.mime_type}, {len(img.data)} bytes -> {out}")
    cloud, mime = await cam.get_point_cloud()
    print(f"  point cloud: {mime}, {len(cloud)} bytes")


if __name__ == "__main__":
    asyncio.run(main())
