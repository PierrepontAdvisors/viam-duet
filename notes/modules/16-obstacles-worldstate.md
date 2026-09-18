# 16 — Obstacles and WorldState

Source: page 16 of the course print view (lesson, ~9 min)
Date:

## What this page is about
No code. Run the pack, raise the scene framerate, and watch the top layer for two collisions: the wrist passing through placed boxes, and the carried box sliding through its neighbors.

## Key concepts
- **Two separate worlds** — the scene's store draws the boxes you tell it about; the planner only knows the obstacles you pass on each Move call. So far the moves have passed none, so the planner can't see the stack.
- Fix one: placed boxes (page 17). Fix two: the box in the gripper (page 18).

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
