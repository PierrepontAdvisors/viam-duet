# Plan

## Team
- Members:
- Machine name:
- Arm model (xArm6 / 850 / UR):
- Camera (RealSense D435 / Orbbec Astra 2):

## Challenge
Pick one. Score each on: can we demo a partial version by end of Day 1? Does it need force feedback we don't have?

| Challenge | What it really needs | Risk |
|-----------|----------------------|------|
| Recycling sort | Detector for 2–4 object classes, per-class drop pose, robust grasp on odd shapes | Perception in clutter; grasp failures |
| Bin picking / packing | Same loop as the 101 palletizer plus real vision; packing pattern | Grasp reliability |
| Charger plugging | Sub-cm accuracy, compliant approach, plug hidden at contact | Very hard without force sensing |
| Pouring | Continuous wrist rotation while holding; cup detection | Spills; needs a steady grasp |
| Block stacking / Jenga | Precise place, slow approach, force sense for the pull | Jenga pull is hard; stacking is doable |
| Egg transfer | Gentle grip force control | Gripper force may not be tunable |
| Bring your own | | |

Decision:
Why:

## Skeleton of any of these
1. Save poses: home (camera sees the workspace), travel, per-target drop poses. Use the arm position saver.
2. Vision: shape-finder + detections-to-segments gives 3D centers in the camera frame. YOLOv8 for named classes.
3. Pick: detect at home → motion.move to approach in the camera frame → descend in the gripper frame → grab → travel pose.
4. Place: saved pose or a computed pose in world → open.
5. Loop until nothing is detected. Log every failure.

Reference: `code/hackathon/reference/pick-and-place/scripts/reference-solution.py` does 1–5 on this hardware.

## Timeboxes
| When | Goal |
|------|------|
| Day 1, 11:00 | `explore.py` connects; gripper and camera verified; E-stop located; joint-5 limit set |
| Day 1, 12:30 | Saved poses; one manual pick-and-place from the Control tab |
| Day 1, 15:00 | Static sequence from Python (milestone one) |
| Day 1, 18:00 | Vision detects the target; one perception-guided pick |
| Day 1, 21:00 | Loop runs end to end at least once. Commit |
| Day 2, 12:00 | Reliability: three clean runs in a row. Then polish |
| Day 2, 14:30 | Demo script rehearsed. Freeze code |
| Day 2, 15:30 | Demos |

## Open questions for Viam staff
- 
