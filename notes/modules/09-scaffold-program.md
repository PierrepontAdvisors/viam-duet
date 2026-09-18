# 09 — Scaffold the program

Source: page 9 of the course print view (exercise, ~6 min)
Date:

## What this page is about
Create `palletizer.py`: a `Palletizer` class holding the connection, plus a dictionary that maps a word on the command line to one method. Every later page adds one method and one entry.

## Key concepts
- **RobotClient** — the connection object from `helpers.connect()`; the class wraps it.
- **Verb dispatch** — `STEPS = {"resources": ..., "wave": ..., "zero": ...}`. `python palletizer.py wave` runs one step. The course points out this is the same shape a Viam module uses to expose commands through DoCommand.
- **Joint control is the wrong abstraction** — `wave` sets six joint angles directly (degrees, base to wrist: 0, -45, -30, 0, 60, 0) and `zero` returns them to zero. It works, but you'd have to compute angles and avoid obstacles yourself. The motion service does that for you from page 12 on.

## Three starting methods
- `resources` — a safe first call: print the sorted names the machine exposes.
- `wave` — `Arm.from_robot(robot, "arm-1")` then move to the joint positions above.
- `zero` — same, all zeros.

## Checkpoint
`wave` moves the arm in the 3D scene; `zero` returns it.

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
