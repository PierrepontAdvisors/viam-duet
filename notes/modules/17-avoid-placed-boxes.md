# 17 — Avoid placed boxes

Source: page 17 of the course print view (exercise, ~14 min)
Date:

## What this page is about
Build a WorldState from the boxes already on the pallet and hand it to the motion service on every move.

## Key concepts
- **Static vs dynamic obstacles** — the floor is in the machine config, so the planner always sees it. Placed boxes appear one at a time, so they're passed per move.
- **WorldState** — a set of obstacles; each is a geometry expressed in a reference frame. A placed box is expressed in `world` at its center.
- **Refusal beats collision** — if a move can only be done through a box, the planner now refuses instead of clipping.

## What I add
- Imports from `viam.proto.common`: `WorldState`, `GeometriesInFrame`, `Geometry`, `RectangularPrism`, `Vector3`.
- `obstacles()` — a local `cuboid(label, frame, x, y, z)` builder wraps a box-sized `RectangularPrism` in a `Geometry` inside a `GeometriesInFrame`; one per placed box, labelled `placed-i`; returns a `WorldState` or `None` when the pallet is empty.
- Pass `self.obstacles()` (call it, with parentheses) on both home moves in `pick` and the placing move in `place`.

## Checkpoint
The arm arcs around the stack; the carried box still clips neighbors.

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
