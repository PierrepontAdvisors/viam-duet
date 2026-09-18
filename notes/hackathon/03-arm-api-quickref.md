# Python SDK quick reference for the arm rig

Verified 2026-09-18 against viam-sdk 0.80.0 (installed in `code/hackathon/.venv`) and the local docs mirror. Units: millimeters and degrees at the API surface; motion-service joint limits are radians.

## Connect
```python
from viam.robot.client import RobotClient
opts = RobotClient.Options.with_api_key(api_key=KEY, api_key_id=KEY_ID)
machine = await RobotClient.at_address(ADDRESS, opts)   # or: async with await ... as machine
machine.resource_names                                   # list of ResourceName (namespace, type, subtype, name)
```

## Arm (`viam.components.arm.Arm`) — direct control, NO obstacle checking
| Call | Notes |
|------|-------|
| `await arm.get_end_position()` | Pose of the flange in the arm's base frame |
| `await arm.get_joint_positions()` | `.values` is a list of degrees, base to wrist |
| `await arm.move_to_position(pose=Pose(...))` | Straight to a flange pose. Ignores table and wall |
| `await arm.move_to_joint_positions(positions=JointPositions(values=[...]))` | Degrees. Ignores obstacles |
| `await arm.stop()` / `await arm.is_moving()` | |

## Gripper (`viam.components.gripper.Gripper`)
| Call | Notes |
|------|-------|
| `await gripper.open()` | |
| `await gripper.grab()` | Returns True if it closed on something |
| `(await gripper.is_holding_something()).is_holding_something` | Returns a HoldingStatus object, not a bool |

## Camera (`viam.components.camera.Camera`)
| Call | Notes |
|------|-------|
| `images, meta = await cam.get_images()` | List of NamedImage; each has `.name`, `.data` (bytes), `.mime_type`. Color and depth come back as separate entries |
| `data, mime = await cam.get_point_cloud()` | Bytes of a PCD |
| There is no `get_image()` in 0.80 | Use `get_images()` |

## Motion service (`viam.services.motion.MotionClient`, name `"builtin"`) — plans around obstacles
```python
from viam.proto.common import Pose, PoseInFrame
motion = MotionClient.from_robot(machine, "builtin")

# where is the gripper tip, in world?
pif = await motion.get_pose(component_name="gripper", destination_frame="world")

# move the gripper tip to a pose, tool pointing straight down
ok = await motion.move(
    component_name="gripper",                       # plain string name of the frame to move
    destination=PoseInFrame(reference_frame="world", pose=Pose(x=300, y=0, z=150, o_x=0, o_y=0, o_z=-1, theta=0)),
    world_state=None,                               # extra obstacles; the configured table/wall are already known
    timeout=60,
)
```
- `component_name` is the frame that arrives at the pose. Name the gripper and the fingertips arrive; name the arm and the flange arrives.
- `reference_frame` can be any configured frame. Two patterns from the pick-and-place tutorial:
  - Detect in the camera frame, then move to `PoseInFrame(reference_frame="cam", pose=approach)` while the arm is still at the pose where the detection was made. The camera is on the wrist, so its frame moves with the arm.
  - Descend straight down in the gripper's own frame: `PoseInFrame(reference_frame="gripper", pose=Pose(x=0, y=0, z=+distance, o_x=0, o_y=0, o_z=1, theta=0))`.
- Returns False when the planner refuses (unreachable, or only reachable through an obstacle).
- `await motion.stop_plan(component_name="gripper")` cancels an in-flight plan.

## Vision service (`viam.services.vision.VisionClient`)
| Call | Returns |
|------|---------|
| `await vision.get_detections_from_camera("cam")` | List of Detection with bounding box and `.class_name`, `.confidence` |
| `await vision.get_object_point_clouds("cam")` | List of PointCloudObject; `obj.geometries.geometries[0].center` is a Pose in the camera frame, `.label` the class |
| `await vision.capture_all_from_camera("cam", return_image=True, return_detections=True)` | One call for image + detections |

## Saved poses (`erh:vmodutils:arm-position-saver`, presents as a Switch)
```python
from viam.components.switch import Switch
home = Switch.from_robot(machine, "home-pose")
await home.set_position(2)      # position 2 = "go to the saved pose" in the tutorial's convention
```
Save the pose from the app first (manual mode, move by hand, then save).

## Pose conventions
- `Pose(x, y, z, o_x, o_y, o_z, theta)`: position plus an orientation vector (the tool's z-axis direction) and a twist about it in degrees.
- Tool straight down: `o_z=-1`. Same direction as the flange's z-axis: `o_z=1`.
- The 101 course's `down_pose()` helper is reused in `code/hackathon/moves.py`.
