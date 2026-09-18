# 06 — The frame system and geometry

Source: page 6 of the course print view (lesson, ~4 min)
Date:

## What this page is about
Why the arm and gripper are stacked at the origin, and the two ideas that fix it: frames say where something is, geometries say how much space it takes.

## Key concepts
- **Frame** — a coordinate system: an origin plus three right-handed axes. `world` is the fixed root; here it sits at the arm's base.
- **Parent** — every other frame is defined relative to a parent by a translation and an orientation, both measured in the parent's axes. Viam composes them into a tree rooted at `world`.
- **Offsets ride their parents** — attach the gripper to the arm's flange with an offset and it follows every wrist motion automatically.
- **Geometry** — a box, sphere, or capsule that gives a frame a volume. The motion planner routes around geometries.
- **Scene = planner data** — the 3D scene draws from the same frame data the planner uses, so what looks right is what gets planned against.

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
