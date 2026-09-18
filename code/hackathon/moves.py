"""Small, explicit test moves. Every arm move here goes through the motion service, so the
table and wall obstacles configured on the machine are honored. Keep a hand near the E-stop anyway.

    python moves.py where            print the gripper tip pose in the world frame
    python moves.py open             open the gripper
    python moves.py grab             close the gripper
    python moves.py up 50            lift the tip 50 mm straight up, orientation unchanged
    python moves.py down 50          lower the tip 50 mm
    python moves.py goto X Y Z       move the tip to (X, Y, Z) mm in world, tool pointing down
    python moves.py stop             stop the arm now
"""
import asyncio
import sys

from viam.components.arm import Arm
from viam.components.gripper import Gripper
from viam.proto.common import Pose, PoseInFrame
from viam.services.motion import MotionClient

import viam_conn as cfg

MAX_STEP_MM = 150.0  # refuse a single relative move larger than this
PLAN_TIMEOUT_S = 60.0


def down_pose(x: float, y: float, z: float) -> Pose:
    """Tool pointing straight down at (x, y, z) in the world frame."""
    return Pose(x=x, y=y, z=z, o_x=0, o_y=0, o_z=-1, theta=0)


def shifted(p: Pose, dz: float) -> Pose:
    return Pose(x=p.x, y=p.y, z=p.z + dz, o_x=p.o_x, o_y=p.o_y, o_z=p.o_z, theta=p.theta)


async def tip_pose(motion: MotionClient) -> Pose:
    result = await motion.get_pose(component_name=cfg.GRIPPER, destination_frame="world")
    p = result.pose
    print(f"tip: x={p.x:.1f} y={p.y:.1f} z={p.z:.1f} o=({p.o_x:.2f}, {p.o_y:.2f}, {p.o_z:.2f}) th={p.theta:.1f}")
    return p


async def move_tip(motion: MotionClient, pose: Pose, frame: str = "world") -> bool:
    ok = await motion.move(
        component_name=cfg.GRIPPER,
        destination=PoseInFrame(reference_frame=frame, pose=pose),
        timeout=PLAN_TIMEOUT_S,
    )
    print("moved" if ok else "planner refused the move")
    return ok


async def main(argv: list[str]) -> None:
    verb = argv[0] if argv else "where"
    args = argv[1:]
    async with await cfg.connect() as machine:
        arm = Arm.from_robot(machine, cfg.ARM)
        gripper = Gripper.from_robot(machine, cfg.GRIPPER)
        motion = MotionClient.from_robot(machine, cfg.MOTION)

        if verb == "where":
            await tip_pose(motion)
        elif verb == "open":
            await gripper.open()
            print("open")
        elif verb == "grab":
            print("grabbed" if await gripper.grab() else "grab returned False")
        elif verb == "stop":
            await arm.stop()
            print("stopped")
        elif verb in ("up", "down"):
            mm = float(args[0]) if args else 50.0
            if not 0 < mm <= MAX_STEP_MM:
                raise SystemExit(f"step must be between 0 and {MAX_STEP_MM:.0f} mm")
            current = await tip_pose(motion)
            await move_tip(motion, shifted(current, mm if verb == "up" else -mm))
            await tip_pose(motion)
        elif verb == "goto":
            if len(args) < 3:
                raise SystemExit("usage: python moves.py goto X Y Z")
            x, y, z = (float(a) for a in args[:3])
            await move_tip(motion, down_pose(x, y, z))
            await tip_pose(motion)
        else:
            raise SystemExit(__doc__)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
