# 18 — Model the held box

Source: page 18 of the course print view (exercise, ~14 min)
Date:

## What this page is about
Add the box in the gripper to the obstacle set, expressed in the gripper's frame so it moves with the arm, and split placement into a lateral approach then a vertical descent.

## Key concepts
- **Frame choice makes an obstacle fixed or moving** — same mechanism as page 17; putting the geometry in `gripper-1` instead of `world` makes it ride along.
- **Why split the placement** — at the moment of placement the held box touches its neighbors, which the planner reads as a collision and refuses. So: move over the slot at a clearance height with the held box modeled, then lower straight down without it.

## What I add
- `obstacles(held=False)` — when held, append one more cuboid labelled `held` in the gripper frame at 0, 0, half a box height.
- `_clear_tip(z_tip)` — a transit height that clears the tallest placed box by one box height plus 10 mm.
- In `pick`, the retract after grabbing passes `held=True`.
- In `place`, two moves: to (x, y, clear height) with `held=True`, then to (x, y, z_tip) with placed-only obstacles; then open, draw, record.

## Checkpoint
Full pack with no clipping. Done building.

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
