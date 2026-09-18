# Duet on Viam: design

Date: 2026-09-18. Status: approved in brainstorming, ready for an implementation plan.
Source PRD: `docs/duet/PRD-duet.md` (copied from Downloads the same day).

## 1. Summary and decisions

Duet is the PRD's tabletop drawing robot: a person draws a mark on an 8.5 x 11 in dry erase board, Claude looks at a photo and says what it sees and what it will add, and a UFactory xArm draws the addition in an artist's stroke grammar. This document adapts the PRD to the hardware actually in hand at Viam's Fine Motor Skills hackathon and to a solo builder.

Decisions made during brainstorming:

- **Scope is the PRD's full P0**, including the physical marker-dock handoff. The builder chose this over a marker-in-gripper simplification.
- **A Marker toggle in the UI selects the handoff.** `Dock` is the PRD behavior. `Held` keeps one marker in the gripper and passes the turn on "hand gone and new ink". Same controller, two steps skipped. Dock is built first; Held is the demo-day fallback.
- **Viam replaces the xArm Python SDK.** The arm belongs to a Viam machine (`armfarm22`) whose viam-server owns the control-box connection. Arm, gripper, camera, and motion planning all go through the Viam Python SDK.
- **Claude is called with structured output**, model `claude-opus-5` with adaptive thinking and low effort, measured against the PRD's 8-second budget; `claude-sonnet-5` is the alternative if Opus misses it.
- **Work is staged, not scheduled.** Ten stages, each with an exit test. No clock times.
- **Haring is the only artist in P0.** Mondrian and Van Gogh are P1 functions with the same signature.



## 2. Constraints and environment

- One builder. Everything runs on the builder's Mac from `code/hackathon/duet/`, using the existing Python 3.12 venv at `code/hackathon/.venv` (viam-sdk 0.80.0) plus `anthropic`, `fastapi`, `uvicorn`, `opencv-python`, `numpy`, `shapely`, `scikit-image`, `pydantic`, `pytest`. ffmpeg is installed at `/opt/homebrew/bin/ffmpeg`.
- The machine `armfarm22` exposes `arm` (viam:ufactory:xArm6), `gripper` (viam:ufactory:gripper), `cam` (viam:camera:realsense, aligned color and depth), the built-in motion service, and obstacle components `table`, `wall-front`, `wall-side`, `ceiling`. Credentials live in `code/hackathon/.env`, which git ignores.
- Nothing is installed on the station's Linux box. Two config changes are requested from Viam staff in the app: arm `collision_sensitivity` 5 (default 3) and confirmation that `speed_degs_per_sec` stays at 30.
- The physical kit from the PRD is on hand: framed board, three fine-tip markers with caps, putty-filled dock container, tape for corner marks.
- Safety rules from the PRD stand: E-stop within the operator's reach; the robot never moves while a hand is over the board or dock; speed stays low near the board.



## 3. Architecture

One asyncio process. Modules, each with one job:


| Module              | Job                                                                                                                                                                                        | Depends on                           |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| `config.py`         | Paths, constants (board size, inset, budgets, thresholds), env loading                                                                                                                     | nothing                              |
| `camera.py`         | Polls `cam.get_images()` at about 5 fps into a latest-frame slot (color, depth); provides `capture_median(n=5)`                                                                            | Viam camera                          |
| `calib.py`          | The two transforms: pixels to board mm (homography from corner marks) and board mm to gripper pose in `world` (affine from touch-off); loads and saves `calibration.json` and `poses.json` | numpy, OpenCV                        |
| `vision.py`         | Pure functions on frames: find corners, warp, diff, trace, coverage, dock dots, hand-from-depth, stillness                                                                                 | numpy, OpenCV, scikit-image, shapely |
| `trigger.py`        | The human-turn-over state machine, fed by `vision` readings; Dock and Held rules                                                                                                           | `vision`                             |
| `claude_turn.py`    | Builds the prompt with the gridded photo, calls Claude with a schema, returns a proposal or a timeout                                                                                      | anthropic SDK                        |
| `planner.py`        | Validates a proposal: clip, clearance, budget; pure                                                                                                                                        | shapely                              |
| `styles/haring.py`  | Styles validated strokes into polylines and one color; pure                                                                                                                                | shapely                              |
| `controller.py`     | Owns the arm, gripper, and motion clients; look pose, dock pick and return, drawing, stop                                                                                                  | Viam SDK, `calib`                    |
| `session.py`        | The turn loop state machine; the only module that calls the others in sequence                                                                                                             | all above                            |
| `recorder.py`       | Session folder, turn photos, `session.json`, ffmpeg stitch                                                                                                                                 | ffmpeg                               |
| `web.py`            | FastAPI: static page, `/ws`, `/stream.mjpg`, session files                                                                                                                                 | fastapi, `camera`                    |
| `static/index.html` | The single page                                                                                                                                                                            | nothing                              |


Scripts beside the package: `teach.py`, `calibrate.py`, `stroke_bench.py`, `dock_test.py`, `run.py`.

Data flow per turn: `camera` frames feed `trigger`. On trigger, `session` asks `camera` for a median capture, `vision` warps it into the turn photo, `recorder` saves it, `vision` diffs and traces the new ink, `claude_turn` proposes strokes, `planner` validates, `haring` styles, `web` previews, `controller` picks the marker and draws, returns the marker, goes to the look pose, and `session` captures the robot's turn photo.

## 4. Coordinate systems and calibration

All geometry is in board millimeters, origin at the board's top-left, x to the right, y down, as in the PRD. Drawable area is the board minus a 15 mm inset for the raised frame.

**Pixels to board.** Four dark tape squares sit at the board corners. At the fixed look pose each corner lives inside a known rectangular region of the frame, recorded by `calibrate.py`. `vision.find_corners` thresholds for dark blobs inside each region and returns four centroids. OpenCV computes the homography to a flat board image at 4 px/mm (about 860 x 1120 px). Every capture re-detects the corners; if any centroid moves more than 4 px (1 mm) from calibration, `session` emits a board-shifted warning.

**Board to robot.** `teach.py corner tl|tr|bl` puts the arm in manual mode, waits for the operator to rest the marker tip on the board at that corner, reads `motion.get_pose("gripper", "world")`, and exits manual mode. Three gripper poses define an affine map from (x_mm, y_mm) to a gripper position, and the fitted plane defines pen-down z. Because the poses are of the gripper frame while the tip touches the surface, the marker length never needs measuring. Orientation for all board moves is the recorded touch-off orientation (tool pointing down). Travel height is pen-down plus 20 mm.

**Look pose.** Taught the same way, 350 to 400 mm above the board and tilted 15 to 20 degrees off vertical so the strip light's reflection falls out of frame. The homography absorbs the tilt. It doubles as the park pose.

**Dock slots.** `teach.py slot <color>` records the gripper pose at grip height for each marker, and `seat <color>` the pose with the tip seated in the cap. `calibrate.py` also records each marker's end-plug dot position in board coordinates and the board plane's depth for the hand detector.

Files: `poses.json` (taught poses) and `calibration.json` (corner regions, dot positions, thresholds). Both are committed; they contain no secrets.

## 5. Controller

`Controller` holds the arm, gripper, and motion clients and an asyncio lock. Every public call acquires the lock, so two sequences can never interleave.

Public surface:

- `go_look()`: planned `motion.move` of the `gripper` frame to the look pose.
- `pick_marker(slot, dot_xy_mm)`: open part way with `gripper.do_command({"set": N})` where N is barrel width plus 15 mm in the gripper's 0 to 850 scale (measured once in stage 3); planned move to the hover pose 60 mm above the slot; `arm.do_command({"set_speed": 10})`; linear-constrained descent to grip height, with the target shifted by the dot's displacement from its calibrated position (only the displacement is used, mapped through the linear part of the board-to-robot map, so the dots' height above the board plane adds no parallax error); `gripper.grab()`; linear-constrained pull of 40 mm straight up; rise to travel height; `set_speed` 30.
- `return_marker(slot)`: hover; slow linear descent to seat height; press to the taught press depth; open part way; rise.
- `draw(polylines, color)`: for each polyline in order: travel at lift height to the first point (plain planned move), linear descent to pen-down, each waypoint as a linear-constrained move at speed 15, lift. Waypoints are resampled to the spacing chosen in stage 2 (5 to 10 mm). Emits a progress event per stroke. Stops cleanly when the millimeter or second budget is exhausted: the current stroke finishes, the pen lifts.
- `stop()`: halts the arm immediately and raises an abort flag that the running sequence sees at its next move. It never takes the lock.
- `recover()`: waits for the aborted sequence to unwind, clears the arm's error state, and, if the tool was left at or near a surface (`needs_lift`), lifts it straight up by the height that sequence needs (20 mm from the board, 40 mm from a dock slot) before anything else. It skips the hand gate, since the lift is a retreat from the surface and from any hand. The page's Resume control calls it.
- `clear_error()`: `arm.do_command({"clear_error": True})`.
- `status()`: joints, gripper holding, `needs_lift`, last error.

Rules:

- All motion is `motion.move` on the `gripper` frame with the configured obstacles in force. `LinearConstraint(line_tolerance_mm=1.0)` on pen-down and dock vertical segments; no constraint on travel. `move_to_joint_positions` is never used.
- The hand check runs at the start of every sequence and between strokes. At the start, a hand raises `Blocked` without halting. Between strokes, `draw` ends the turn with `blocked=True`, pen up, no halt. A check slower than two seconds, or one that raises, counts as a hand present, and the hook must not call back into the controller.
- Any exception inside a sequence: the arm halts, `last_error` is recorded, and the session enters `Paused`. Resume runs `recover()` first.
- Sequences never queue. A command issued while another runs raises `Busy`, so nothing fires late.
- `pick_marker` checks `grab()`'s result only when `REQUIRE_GRAB_DETECT` is on, which stage 3 decides once the gripper unit's reporting is known.
- In Held mode, `pick_marker` and `return_marker` return immediately.



## 6. Vision and trigger

`vision.py` is pure functions on numpy arrays.

- `median_frame(frames)`: per-pixel median of five color frames.
- `find_corners(frame, regions)`: dark-blob centroids within the four regions.
- `warp(frame, corners)`: the 4 px/mm board image.
- `new_ink(current, previous, inset_mask)`: grayscale, blur, absolute difference, threshold, morphological open, masked. Returns a binary mask and coverage fraction.
- `trace(mask)`: skeletonize, follow skeleton pixels into polylines, split at junctions, simplify with a 0.5 mm tolerance, return polylines in board mm.
- `dock_dots(frame, slots)`: per slot, an HSV threshold for that marker's color inside its region; returns present, missing, out of position (more than 3 mm from the recorded spot), or wrong color. Also returns the centroid's displacement from the recorded spot for the pick correction.
- `hand_present(depth, board_region, plane_depth)`: true if a connected region over the board or dock is more than 25 mm above the plane and larger than 2000 mm². Backup: color motion over the last 1.5 s.
- `still(frames)`: mean absolute frame-to-frame difference below a threshold for 1.5 s.

`trigger.py` is a small state machine over those readings. Dock rule: during the human's turn at least one dot went missing; now all three are present and in position; the scene has been still 1.5 s; no hand. Held rule: no hand for 2 s; still; the diff finds new ink. A dot that is home but out of position or in the wrong slot moves the trigger to `Reseat` and the page asks the visitor to reseat that marker. The operator can also pass the turn from the page.

## 7. The Claude turn

`claude_turn.py` makes one request per turn with the Python Anthropic SDK.

Input assembled by `session`: the warped board photo with a millimeter grid and labels drawn along the edges (JPEG, base64 image block), the traced human polylines as coordinates, the turn history (prior `sees` and `adds` sentences and a summary of prior strokes), the artist, the colors the artist allows this turn, the length setting and its millimeter budget, and "exchange n of N".

Request: `client.messages.parse()` with a Pydantic schema so the reply is guaranteed to fit. Model `claude-opus-5`, adaptive thinking left on, `output_config.effort` `low`, the system prompt marked for caching, `max_tokens` sized for the largest Long proposal. The client is constructed with an 8-second timeout and zero retries. Server-side refusal fallback is enabled as the SDK recommends for Opus 5.

Schema: `sees: str` (one sentence), `adds: str` (one sentence), `color: Literal[allowed colors]`, `strokes: list[Stroke]` where a Stroke is one of `Polyline(points)`, `Circle(center, radius)`, `Arc(center, radius, start_deg, end_deg)`, each with `attached: bool`.

`planner.validate(proposal, existing_ink, drawable, budget_mm)`: convert circles and arcs to polylines; clip to the drawable polygon; buffer existing ink by 3 mm and push unattached strokes outside it (drop a stroke that cannot be moved); keep order; cut at the budget. Pure, tested.

`styles.haring.style(strokes, human_ink, length, energy, direction)`: each stroke drawn bold as two passes 1.5 mm apart; ticks 8 to 15 mm long radiating from the stroke every 25 mm, tilted by `direction` and scaled by `energy` (constants until the live-data layer exists). Returns polylines and the color. Pure, tested.

Fallback: on timeout, error, or an empty proposal, `styles.haring.fallback(human_ink)` produces an outline offset around the new mark plus ticks in the artist's outline color, and the `interpretation` message carries `source: "fallback"` so the page says so.

Model measurement (stage 5): run ten saved boards through Opus 5 at low effort and record the latency distribution. If the 95th percentile exceeds 8 s, switch the constant to `claude-sonnet-5` and re-measure. This settles the PRD's open question by data.

## 8. Session loop and recording

`session.py` runs one asyncio task with one function per state: `HumanTurn`, `Capture`, `Interpret`, `Plan`, `RobotDraw`, `Look`, `Finish`, plus `Paused` (reachable from any state on error or the Pause control) and `Reseat` (from `HumanTurn` when the trigger reports a misplaced marker). Each transition emits a `state` message. `Capture` and `Look` both save a turn photo. `Capture` returns to `HumanTurn` if no new ink is found.

Settings: artist, length, exchange count (3 to 10), mode (Duet; Solo is P1), handoff (Dock or Held). Exchange count is editable mid-session; length is applied at the next turn.

Finish: exchange count reached or coverage at or above one third. The robot draws a small fixed signature polyline in the corner in the current color, returns the marker, goes to the look pose, and `recorder` stitches the video.

`recorder.py`: `sessions/<id>/turn-NN-human.jpg`, `turn-NN-robot.jpg`, `plan-NN.svg`, `session.json` (settings, sentences, source, timings), then ffmpeg at 1 s per frame with a 2 s hold on the last frame into `session.mp4`. Captions are P1.

## 9. Web page and protocol

`web.py` serves `static/index.html`, `/ws`, `/stream.mjpg`, and `/sessions/`. Local screen only; the public tunnel and read-only token are P1.

Panels (all P0): live camera (MJPEG in an image tag, planned strokes overlaid while at the look pose), interpretation (`sees`, `adds`, and the source), exchange counter with the last turn's photo, vector plan (inline SVG: human ink traced, drawn strokes solid in the marker color, queued strokes dashed), controls, session video.

Controls: artist picker, Short/Medium/Long, exchange count, Marker toggle (Dock/Held), Pause, "clear arm error", and in Held mode "pass turn". No Done button in Dock mode; recapping passes the turn.

WebSocket messages, JSON with a `type` field: `state`, `dock` (per-slot status), `human` (traced polylines), `interpretation`, `plan`, `progress`, `video`, `shot`, `mode`, `error`, and from the page `set` (a settings change), `pause`, `resume`, `pass`, `clear_error`. `data` (energy, direction) is P1.

The page follows the builder's preview convention: meaningful elements carry `data-el` names and the D key toggles a developer mode that copies an element's name on click.

## 10. Configuration and secrets

`code/hackathon/.env` holds the Viam address and API key already, and gains `ANTHROPIC_API_KEY`. `.env` is gitignored. `poses.json` and `calibration.json` are committed. `sessions/` is gitignored except for a `.gitkeep`.

Constants in `config.py`: board 279 x 216 mm (11 x 8.5 in, landscape as the camera sees it; confirm orientation in stage 4), inset 15 mm, lift 20 mm, budgets 400/1200/3000 mm and 15/40/90 s, waypoint spacing (set in stage 2), clearance 3 mm, dot tolerance 3 mm, stillness 1.5 s, hand height 25 mm, coverage end 0.33.

## 11. Testing

pytest covers the pure core, because those tests are cheap and they catch geometry errors before the arm moves:

- `calib`: homography round trip on synthetic corners; affine round trip on synthetic touch-off poses.
- `vision`: `new_ink` and `trace` on synthetic boards with drawn strokes; `dock_dots` on synthetic dots; `hand_present` on synthetic depth.
- `planner`: clipping at the inset, clearance push, budget cut, order preserved.
- `haring`: output within budget, tick count scales with energy, two passes per stroke.
- `trigger`: the Dock and Held rules driven by scripted readings, including the Reseat path.

Hardware is verified by scripts with logged results: `stroke_bench.py` (square plus per-move timing), `dock_test.py` (20 cycles, pass count), `claude_turn.py` on saved photos (latency and an SVG preview), and `teach.py verify` (replays taught poses).

## 12. Stages

Each stage ends with an exit test and leaves a working demo of increasing scope.

1. **Foundation.** Kit staged: corner tape, weighted dock, markers planted by the arm in manual mode. `teach.py` records look, slots, seats, corners. Exit: `verify` replays every taught pose at low speed without incident.
2. **First ink.** `stroke_bench.py` draws a hard-coded square with a held marker and logs time per planned move. Exit: a square on the board; waypoint spacing chosen.
3. **Dock.** Pick, uncap, recap, return for one slot, then all three. Exit: `dock_test.py` passes at least 19 of 20 cycles.
4. **Eyes.** Look-pose capture, corners, warp, turn photo saved; diff and trace on real ink. Exit: traced polylines overlay the human's mark in an SVG.
5. **Brain.** Claude call, validation, Haring styling, SVG preview from saved photos. Exit: sensible, in-budget strokes from ten saved boards; latency measured.
6. **Trigger.** Dots, stillness, hand, state machine. Exit: recapping at the real dock passes the turn on the terminal reliably; a hand blocks it.
7. **Page.** HTML page, WebSocket, MJPEG, controls. Exit: every panel updates from replayed events with no robot.
8. **Loop.** Everything wired; Held toggle. Exit: one full exchange end to end.
9. **Memory.** Session folder, photos, `session.json`, ffmpeg. Exit: a playable MP4.
10. **Harden.** Repeated runs, prompt and budget tuning, rehearsal.

Ordering rule: if stage 3 will not pass, continue with the Marker toggle on Held and return to the dock after stage 9.

## 13. Risks specific to this design


| Risk                                                                                   | Handling                                                                                                                                                               |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Planned moves are slow, so dense strokes take too long                                 | Stage 2 measures latency; waypoint spacing and the second-based budget absorb it; strokes stay coarse rather than the loop breaking                                    |
| The planner's path between two waypoints is not straight enough for legible strokes    | Linear constraint with 1 mm tolerance on every pen-down segment; verified visually in stage 2                                                                          |
| Gripper partial-open scale (0 to 850) does not map cleanly to millimeters              | Measured once in stage 3 with calipers at three settings; stored in `config.py`                                                                                        |
| The gripper generation (G1 or G2) changes how `grab` and `is_holding_something` behave | `dock_test.py` logs `is_holding_something` after each grab; if it is unreliable on this unit, the pull-up is confirmed by the dot disappearing from the camera instead |
| Corner tape confused with ink                                                          | Corners searched only inside fixed regions; ink diff masked by the inset                                                                                               |
| Claude latency exceeds 8 s                                                             | Fallback grammar answers; stage 5 chooses the model by measurement                                                                                                     |
| The wrist camera's pose is not exactly the look pose                                   | Every capture is taken after `go_look()` completes and re-detects corners; mid-motion frames are for streaming only                                                    |
| A collision stop leaves the arm in an error state                                      | `clear_error` from the page; the session stays Paused until the operator resumes                                                                                       |




## 14. Items to confirm on the hardware

- Plan latency per move and the resulting waypoint spacing (stage 2).
- Gripper unit generation and the open-scale to millimeter mapping (stage 3).
- Board orientation in the camera frame, landscape or portrait, which sets the board constant (stage 4).
- Whether the RealSense depth is clean enough over the white board for the hand detector, or whether the color-motion backup must be primary (stage 6).
- Which model meets the 8-second budget (stage 5).

