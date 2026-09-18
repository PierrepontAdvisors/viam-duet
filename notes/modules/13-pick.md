# 13 — Pick

Source: page 13 of the course print view (exercise, ~12 min)
Date:

## What this page is about
Ask the pick-station where the box is, hover above it, descend, grab, lift.

## Key concepts
- **DoCommand** — a component can expose commands beyond its standard API. The course helpers `grasp_pose` and `pick_home_pose` use it to ask the pick-station where to grab and where to hover. Those values come from the station's own attributes and frame in CONFIGURE, nothing hidden.
- **Gripper API** — `grab()` engages suction.
- **Box visuals are cosmetic** — the simulated gripper holds nothing, so `show_box` and `attach_box` tell the pack-sequencer service where to draw the box. It affects what you see, not motion.

## Values I need
- Box dimensions: W 200, L 150, H 100 (mm). Grasp depth: 10 mm pressed onto the box top so the cups seat.
- `__init__` grows a `Gripper` handle, a `placed` list, and a cached pallet top.

## The pick sequence
Home pose above the box, draw the box at the station, descend to grasp minus grasp depth, grab, attach the box to the gripper, return to home.

## Checkpoint
`pick` shows a box, the gripper takes it and lifts, box rides the gripper.

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
