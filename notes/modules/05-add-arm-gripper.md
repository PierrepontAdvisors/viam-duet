# 05 — Add the arm and gripper

Source: page 5 of the course print view (exercise, ~5 min)
Date:

## What this page is about
Add two components from the registry, give each a default frame so it shows up in the 3D scene, and see both sitting at the origin. Placement comes on page 7.

## Key concepts
- **Component** — a piece of hardware. You declare it; Viam fetches and runs the module.
- **Model** — one implementation of a component type, e.g. `arm/simulated` or `robotiq-epick/simulated-epick-vacuum-gripper`. Every model of a type exposes the same API.
- **No frame, no scene** — a component without a frame does not render in the 3D scene, so every component gets one.

## Values I need
- Arm: search "simulated", pick `arm/simulated` (not `arm/fake`). Name `arm-1`. Attributes: arm-model `ur5e`, simulate-time `true`, speed `1.5` (joint speed, rad/s). Frame: Set defaults.
- Gripper: search "simulated epick", pick `robotiq-epick/simulated-epick-vacuum-gripper`. Name `gripper-1`. Attributes: grab_delay_ms `250`. Frame: Set defaults. A supporting module installs automatically.
- 3D scene settings worth changing now: raise the framerate; optionally hide colliders until page 10.

## Checkpoint
Both READY in CONFIGURE, both at the world origin in the 3D scene, gripper not yet on the arm.

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
