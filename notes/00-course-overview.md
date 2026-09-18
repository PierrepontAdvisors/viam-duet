# Course overview

Source: https://viam-101-w28-9jnk.learn.viam.com/workshop/content/print.html (login required)
Outline captured: 2026-09-17. **Course completed: 2026-09-17.**

## What the course is
- Build a palletizing robot entirely in simulation, no hardware: a simulated UR5e arm with a vacuum gripper picks boxes from a pick-station and stacks them on a pallet, two layers of four.
- Two halves: configure the work cell in the Viam app, then write one Python program (`palletizer.py`) that drives it one verb at a time.
- Total hands-on time the course estimates: about 2 hours 20 minutes across 19 pages.
- Help channel: `#viam-101` on the Viam Discord.

## Outline
Type: **E** = exercise (you do something), **L** = lesson (read/watch, no code). Time is the course's estimate.

| # | Page | Type | Time | Note file | Done |
|---|------|------|------|-----------|------|
| 1 | Overview | L | 3m | [01](modules/01-overview.md) | [x] |
| 2 | Create your machine | E | 3m | [02](modules/02-create-machine.md) | [x] machine `palletizer-101` exists |
| 3 | Run viam-server | E | 3m | [03](modules/03-run-viam-server.md) | [x] done on the Mac via Homebrew, not in the course IDE |
| 4 | The machine you're going to build | L | 5m | [04](modules/04-machine-you-build.md) | [x] |
| 5 | Add the arm and gripper | E | 5m | [05](modules/05-add-arm-gripper.md) | [x] |
| 6 | The frame system and geometry | L | 4m | [06](modules/06-frames-and-geometry.md) | [x] |
| 7 | Place the arm and gripper | E | 3m | [07](modules/07-place-arm-gripper.md) | [x] |
| 8 | Connect from code | E | 4m | [08](modules/08-connect-from-code.md) | [x] |
| 9 | Scaffold the program | E | 6m | [09](modules/09-scaffold-program.md) | [x] |
| 10 | Add the work cell | E | 10m | [10](modules/10-add-work-cell.md) | [x] |
| 11 | Poses | L | 4m | [11](modules/11-poses.md) | [x] |
| 12 | Move | E | 15m | [12](modules/12-move.md) | [x] |
| 13 | Pick | E | 12m | [13](modules/13-pick.md) | [x] |
| 14 | Place | E | 10m | [14](modules/14-place.md) | [x] |
| 15 | Run | E | 12m | [15](modules/15-run.md) | [x] |
| 16 | Obstacles and WorldState | L | 9m | [16](modules/16-obstacles-worldstate.md) | [x] |
| 17 | Avoid placed boxes | E | 14m | [17](modules/17-avoid-placed-boxes.md) | [x] |
| 18 | Model the held box | E | 14m | [18](modules/18-model-held-box.md) | [x] |
| 19 | Recap | L | 5m | [19](modules/19-recap.md) | [x] |

## The arc, in one paragraph
Pages 1–3 get a machine online. Pages 4–7 put an arm and gripper on it and teach the frame system (where things are). Pages 8–9 connect Python and build a tiny command-dispatch program. Page 10 finishes the cell (floor by hand, pallet and pick-station via a fragment). Pages 11–15 drive the arm with the motion service: move, pick, place, then loop it into a full pack. Pages 16–18 make it collision-safe by telling the planner about placed boxes and the box in the gripper. Page 19 points at the next course: wrapping the program as a Viam module.

## Goals for taking this course
-

## Progress
| Date | Page | Notes |
|------|------|-------|
| 2026-09-17 | 2, 3 | Created machine in app; installed and started viam-server locally on the Mac |
| 2026-09-17 | 4–19 | Built the cell and wrote palletizer.py through the held-box fix. Full eight-box pack ran clean. Proof: [proof/2026-09-17-viam101-pallet-complete.png](proof/2026-09-17-viam101-pallet-complete.png) |
