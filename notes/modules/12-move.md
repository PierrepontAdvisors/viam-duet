# 12 — Move

Source: page 12 of the course print view (exercise, ~15 min)
Date:

## What this page is about
First direct call to the motion service. Instead of joint angles, name a frame to move and a destination; the planner works out a collision-free path.

## Key concepts
- **component_name is the frame that reaches the pose** — name the gripper and the cup face arrives at the pose; name the arm and the flange arrives, so the cups end 196 mm lower. The page has you try both.
- **Destination is a PoseInFrame** — the pose paired with the frame it's measured in (`world`).
- **Obstacles parameter** — left empty for now; becomes a WorldState on page 17.

## What I add to palletizer.py
- Imports: `helpers`, `MotionClient`, `Pose`, `PoseInFrame`.
- `down_pose(x, y, z)` — builds a Pose at that point with the tool pointing straight down (orientation z = -1).
- `move_gripper(pose, obstacles=None)` — gets the motion client, wraps the pose in a `PoseInFrame` on `world`, calls `motion.move` with component_name = the gripper constant, the destination, the obstacles as world_state, and timeouts. Wrapped in the course's retry helper.
- `move` step — sends the gripper to (400, -300, 400). Add to STEPS.

## Checkpoint
`move` drives the gripper to the pose; naming the arm instead shows the cups 196 mm below it.

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
