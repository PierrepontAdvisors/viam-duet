# 07 — Place the arm and gripper

Source: page 7 of the course print view (exercise, ~3 min)
Date:

## What this page is about
Confirm the arm's frame at the world origin and re-parent the gripper onto the arm with a tool offset. Use the JSON toggle in the Frame section to see the whole frame at once.

## Values I need
- `arm-1` frame: parent `world`, translation 0/0/0, orientation ov_degrees with z=1, th=0. Already correct from the defaults, no change.
- `gripper-1` frame: parent `arm-1`, translation x=0 y=0 **z=196**, same orientation.
- Why 196 mm: distance from the arm's flange to the face of the vacuum cups, the point that touches a box. On real hardware this is the tool center point from the datasheet or a measurement.

## Checkpoint
Gripper renders on the arm's wrist in the 3D scene; World panel lists both.

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
