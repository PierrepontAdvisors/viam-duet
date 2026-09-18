# Move an arm

Command an arm to a target pose, along a constrained path, or directly in joint space. Build pick-and-place flows from those primitives.
> Source: https://docs.viam.com/motion-planning/move-an-arm/overview/


Viam exposes three ways to command an arm. Three questions sort them:

1. **What do you know about the destination?** A Cartesian target (a pose
   in space) calls for the motion service. A specific joint configuration
   calls for direct joint commands.
2. **Does the path matter, or only the endpoint?** If you
   need a straight line, a fixed orientation, or any other rule about
   the path itself, you need constraints.
3. **Do you want obstacle avoidance and IK picked for you, or fine
   manual control?** The motion service picks the IK solution and plans
   around obstacles for you; direct joint commands execute exactly the
   angles you send.

| Pattern                                                                          | Input                    | Obstacle avoidance | Path-shape control | When to pick                                                                                                                                     |
| -------------------------------------------------------------------------------- | ------------------------ | ------------------ | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| [Move to a pose](/motion-planning/move-an-arm/move-to-pose/)                     | Cartesian target         | Yes                | No                 | You know where the end effector needs to go and want the planner to choose the path.                                                             |
| [Move with constraints](/motion-planning/move-an-arm/move-with-constraints/)     | Cartesian target + rules | Yes                | Yes                | The shape of the motion matters (straight-line tool path, level end effector).                                                                   |
| [Move by joint positions](/motion-planning/move-an-arm/move-by-joint-positions/) | Joint angles             | No                 | Direct             | You know the joint angles, need predictable motion between known configurations, or want to avoid the planner picking an unexpected IK solution. |

For the four constraint types the planner enforces, see
[Configure motion constraints](/motion-planning/move-an-arm/constraints/).

## Pick and place

Pick-and-place is the point where motion planning, vision, and gripper
control meet. Each service works on its own, but the failure modes that
matter most (the gripper closing on air, a depth estimate that crashes
the arm into the table) only appear when all three run together.

The workflow splits into two stages so each can be developed and debugged
independently:

- **Pick** covers detection, approach, and grasp. The arm moves to a
  pre-grasp pose above the object, descends, closes the gripper on the
  object, and lifts.
- **Place** covers transport and release. The arm moves the grasped
  object to a target location, descends, opens the gripper, and retreats.

Both stages reuse the obstacle definitions and geometry-attachment patterns
from [Obstacles](/motion-planning/obstacles/) and the arm-motion patterns
from the table above.

## How-tos

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/motion-planning/move-an-arm/move-to-pose/"><div ><div>Move an arm to a pose</div><p>Use the motion service to move a robot arm to a target pose (position and orientation) in 3D space.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/move-an-arm/move-with-constraints/"><div ><div>Move with constraints</div><p>Move an arm along a straight line or with a fixed orientation using motion constraints.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/move-an-arm/constraints/"><div ><div>Configure constraints</div><p>Restrict how the arm moves between poses using linear, orientation, and collision constraints.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/move-an-arm/move-by-joint-positions/"><div ><div>Move by joint positions</div><p>Command an arm directly in joint space using MoveToJointPositions and MoveThroughJointPositions, bypassing the motion planner.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/move-an-arm/multiple-waypoints/"><div ><div>Move through waypoints</div><p>Plan a single continuous trajectory through an ordered list of intermediate goals using armplanning.PlanMotion.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/move-an-arm/pose-clouds/"><div ><div>Pose clouds</div><p>Give the planner a region of acceptable destinations instead of a single exact pose, so it can find a solution faster.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/move-an-arm/pick-an-object/"><div ><div>Pick an object</div><p>Detect, localize, and grasp an object with a robot arm and gripper.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/move-an-arm/place-an-object/"><div ><div>Place an object</div><p>Move a grasped object to a target location and release it.</p></div>
    </a></div>

</div>
</div>

