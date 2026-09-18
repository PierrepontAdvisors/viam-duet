# 19 — Recap

Source: page 19 of the course print view (lesson, ~5 min)
Date: 2026-09-17 — completed. Proof screenshot: `../proof/2026-09-17-viam101-pallet-complete.png`

## What this page is about
What was configured (arm, gripper at the right offset, floor, pallet, pick-station, two scene services), what was written (one program, one verb at a time), and the ideas that carry to any Viam app.

## Ideas to keep
- Components and services; the registry; the frame system; the motion service ("say where, not how"); DoCommand; the two world states (scene store vs planner WorldState); the edit-run-watch loop.

## What comes next
`palletizer.py` is already shaped like a Viam module: the class is the logic, the STEPS map is how a module exposes commands via DoCommand. The follow-on tutorial wraps it as a module deployed from a GitHub repo so any machine in a fleet can run it.

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
