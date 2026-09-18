# 14 — Place

Source: page 14 of the course print view (exercise, ~10 min)
Date:

## What this page is about
Complete one cycle: pick, carry over the pallet, lower, release, remember where the box ended up.

## Key concepts
- **Pallet knows itself** — `helpers.pallet_top(robot)` returns the center of the pallet's top face; cache it once.
- **Isolate the placement rule** — `_place_pose(i, cx, cy, top)` decides where box i goes and returns x, y, and the gripper-tip z. For now every box goes to the pallet center, one box-height up. Page 15 swaps in the real pattern without touching the cycle.
- **Gripper `open()`** releases the box; then draw it resting and append its center to `placed`.

## Checkpoint
`place` moves one box from the pick-station to the pallet center.

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
