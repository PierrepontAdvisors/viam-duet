# Plan

## Team
- Members:
- Machine name: `armfarm22` (address in `code/hackathon/.env`)
- Arm model (xArm6 / 850 / UR):
- Camera (RealSense D435 / Orbbec Astra 2):

## Challenge
Pick one. Score each on: can we demo a partial version by end of Day 1? Does it need force feedback we don't have?

| Challenge | What it really needs | Risk |
|-----------|----------------------|------|
| Recycling sort | Detector for 2–4 object classes, per-class drop pose, robust grasp on odd shapes | Perception in clutter; grasp failures |
| Bin picking / packing | Same loop as the 101 palletizer plus real vision; packing pattern | Grasp reliability |
| Charger plugging | Sub-cm accuracy, compliant approach, plug hidden at contact | Very hard without force sensing |
| Pouring | Continuous wrist rotation while holding; cup detection | Spills; needs a steady grasp |
| Block stacking / Jenga | Precise place, slow approach, force sense for the pull | Jenga pull is hard; stacking is doable |
| Egg transfer | Gentle grip force control | Gripper force may not be tunable |
| Bring your own | | |

Decision:
Why:

## Skeleton of any of these
1. Save poses: home (camera sees the workspace), travel, per-target drop poses. Use the arm position saver.
2. Vision: shape-finder + detections-to-segments gives 3D centers in the camera frame. YOLOv8 for named classes.
3. Pick: detect at home → motion.move to approach in the camera frame → descend in the gripper frame → grab → travel pose.
4. Place: saved pose or a computed pose in world → open.
5. Loop until nothing is detected. Log every failure.

Reference: `code/hackathon/reference/pick-and-place/scripts/reference-solution.py` does 1–5 on this hardware.

## Timeboxes
| When | Goal |
|------|------|
| Day 1, 11:00 | `explore.py` connects; gripper and camera verified; E-stop located; joint-5 limit set |
| Day 1, 12:30 | Saved poses; one manual pick-and-place from the Control tab |
| Day 1, 15:00 | Static sequence from Python (milestone one) |
| Day 1, 18:00 | Vision detects the target; one perception-guided pick |
| Day 1, 21:00 | Loop runs end to end at least once. Commit |
| Day 2, 12:00 | Reliability: three clean runs in a row. Then polish |
| Day 2, 14:30 | Demo script rehearsed. Freeze code |
| Day 2, 15:30 | Demos |

## Open questions for Viam staff
- 

## Stage results (2026-09-18, armfarm22, single green marker)
- **Decision:** one marker (green) in the dock; the visitor draws with the same marker and recaps it to pass the turn. Red and blue removed.
- **Stage 1:** 7 poses taught (3 corners, approach, look, seat, slot). `verify` reached all of them. Board writing surface measured from the corners: 172 × 237 mm, corners 2.7° off square. Manual mode drops out on its own sometimes; the teach prompts have an `m` key to re-enter it. The gripper's holding sensor reports True when empty, so grab detection stays off.
- **Dock:** one clean cycle: pick, uncap, return with the marker dropping into its cap from 5 mm.
- **Stage 2 dry run:** 60 mm square, 240 mm in 8.9 s, 52 planned moves, mean 0.47 s, p95 1.47 s, 27 mm/s. Short budget of 400 mm fits in ~15 s at `WAYPOINT_MM = 8`, so it stays at 8.
- **Held mode decided (18:20):** the dock pick worked but cost time; the robot keeps one green marker permanently (`HELD_MODE = True`). The visitor draws with a separate marker. Dock pick/return stays available with `--dock`.
- **Pen height:** corners must be touched off with the marker in the runtime grip (`teach load`, then `corner tl/tr/bl`), because a hand-held touch-off put the tip 27 mm off. `teach touch 1` confirmed a 1 mm offset just kisses the surface (`PEN_DOWN_OFFSET_MM = 1`). Board writing surface: 176 × 240 mm.
- **Look pose:** taught straight down (x=338 y=-192 z=367). Camera sees the whole board landscape, marks about 25 px; threshold 30 isolates them. Image corner D is board top-left. Camera-to-robot fit from two drawn squares: x = 0.963·cam + 4.4, y = 0.982·cam + 6.4 (about 2 mm residual). Marks drifted 5 mm between captures; per-turn re-detection absorbs it.
- **Stage 5 (Claude):** `claude-opus-5`, low effort, structured output via `messages.parse`; 7.4 to 7.6 s per turn on the real board, timeout raised to 12 s. Fallback grammar untested live.
- **First full exchange 19:02:** `turn start` / `turn next` worked: 13 human strokes traced, 8 robot strokes drawn in 13 s. Session files in `code/hackathon/sessions/20260918-185927/`.
- **Tomorrow:** web page (stream, interpretation, plan, counter, controls), the hand-and-ink trigger instead of the Enter prompts, recorder plus ffmpeg stitch, then hardening. Wipe the board and re-run `calibrate --check` first thing; if the board moved, `calibrate --tl D` and the two-square `--fit`.
- **Stage 7, page (night of day 1):** `duet/static/` built to the page spec on branch `feat/duet-page`; verified against `pagetests/replay_server.py`, which replays session 20260918-190258 over the agreed protocol. Swap-in needs the backend's `/static` mount in `web.py`.
