# 10 — Add the work cell

Source: page 10 of the course print view (exercise, ~10 min)
Date:

## What this page is about
Finish the cell: build the floor by hand so the planner won't drive the arm through the ground, then pull in the pallet, pick-station, and two scene services in one step with a fragment.

## Values I need
- Floor: search "fake generic", pick the **component** `generic/fake` (there's also a service with the same name; the dialog title "Add component" confirms). Name `floor`. No attributes. Frame JSON: parent `world`, translation z=**-5**, geometry box **2000 × 2000 × 10**.
- Fragment: search `viam101-workcell`, the result tagged FRAGMENT. Add, save. Nothing to name or configure.

## What the fragment delivers
- `pallet` and `pick-station` components, placed on either side of the arm with dimensions and box presentation already set.
- `workcell-scene` service: draws pallet and pick-station in the 3D scene.
- `pack-sequencer` service: tracks each box and draws it wherever the code says (at the station, on the gripper, on the pallet).
- Pinned module versions for all four.

## Key concepts
- **Frame vs geometry** — the frame is where; the geometry is the volume the planner avoids. The arm didn't need a geometry because its kinematic model brings one.
- **Fragment** — a reusable bundle of config blocks. Ten identical machines get one fragment, not ten copy-pastes.

## Checkpoint
Floor, pallet, pick-station READY; cell renders in the 3D scene; `python palletizer.py resources` lists everything including the builtin motion service.

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
