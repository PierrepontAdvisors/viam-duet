# Stuck log

Every problem, in order. Newest at the bottom. Fill in the fix even if it was trivial.

---

## YYYY-MM-DD — short description
**Module:**
**Symptom:** exact error text or behavior
**What I tried:**
1.
**Fix:**
**Why it worked:**
**Time lost:**

## 2026-09-17 — palletizer.py fails to start after adding obstacles()
**Module:** 17 — Avoid placed boxes
**Symptom:** `SyntaxError: 'return' outside function` pointing at the `return WorldState(...)` line. Every verb fails, even `resources`, because the file won't compile.
**What I tried:**
1. Pasted the file to Claude.
**Fix:** The `obs = [...]` comprehension and the `return` were indented at class level (4 spaces) instead of inside `obstacles` (8 spaces). Indented them to match `def cuboid`.
**Why it worked:** Python decides what belongs to a method purely by indentation. Dedenting past the method body put `return` directly in the class, which is illegal, and `self` is not defined there either.
**Also caught:** the final retract in `pick` still called `move_gripper(home)` without `self.obstacles()`; page 17 says to change both home moves.
**Time lost:**

## 2026-09-17 — page 18 edits: SyntaxError, then TypeError on obstacles(held=True)
**Module:** 18 — Model the held box
**Symptom:** First `SyntaxError: 'return' outside function` at the end of `_clear_tip`. After fixing that, `TypeError: obstacles() got an unexpected keyword argument 'held'`.
**What I tried:**
1. Pasted the file to Claude.
**Fix:**
1. `_clear_tip`: the `max_top = ...` and `return max(...)` lines were at class level; indented them into the method.
2. `obstacles`: the body used `held` and callers passed `held=True`, but the signature was still `def obstacles(self)`. Changed to `def obstacles(self, held=False)`.
3. `pick`: the two home moves were swapped. The first move (gripper empty) should pass `self.obstacles()`; the retract after `grab()` (box in gripper) should pass `self.obstacles(held=True)`. The retract had no obstacles at all.
**Why it worked:** Same indentation rule as the last entry. For the TypeError: Python only accepts keyword arguments the `def` line declares, so adding a parameter to the body without adding it to the signature breaks every caller.
**Time lost:**

## 2026-09-17 — full pack stopped after 6 boxes, then completed on rerun
**Module:** 18 — Model the held box
**Symptom:** `python palletizer.py` placed six boxes and stopped.
**What I tried:**
1. Checked the viam-server log: no ERROR lines at all. The planner logged a goal pose for every move up to box 5's descent, then nothing. Planning errors are returned to the Python client, not logged by the server, so the traceback in the Python terminal is the thing to read next time.
2. Reran the pack. It completed all eight boxes cleanly (see `proof/2026-09-17-viam101-pallet-complete.png`).
**Fix:** None applied. Root cause not established.
**Why it worked:** Unknown. The motion planner is sampling-based, so a hard move near the arm's reach limit can time out on one run and succeed on the next. If it recurs, capture the Python traceback and raise the planner timeout in `move_gripper` (the `extra={"timeout": 15.0}` value) before changing anything else.
**Time lost:**

## 2026-09-18 — gripper call fails with "xArm: Emergency Stop Button Pushed In"
**Module:** hackathon, first connection to `armfarm22`
**Symptom:** `explore.py` connected, listed resources, and read the arm, then `gripper.is_holding_something()` raised `GRPCError(UNKNOWN, 'xArm: Emergency Stop Button Pushed In;')`.
**What I tried:**
1. Nothing in code. The message comes straight from the xArm controller.
**Fix:** Physical. The red E-stop on the control box is engaged. Release it (twist to pop it out) once the area around the arm is clear, then rerun. The gripper talks to the same controller as the arm, so it refuses everything while the stop is in.
**Why it worked:** The controller blocks all commands, including gripper state, while the E-stop is latched. Reads of the arm's position still work.
**Time lost:**

## 2026-09-18 — xArm drops out of manual (teach) mode on its own
**Module:** hackathon teach.py
**Symptom:** After `enter_manual_mode` the arm was rigid, or went rigid a few seconds later. The module logged "Manual mode enabled" every time.
**Fix:** The driver forgets it is in manual mode when its Modbus link blips (`started` resets to -1) and the next ready-check re-enables servo mode. Added an `m` key at every teach prompt that re-enters manual mode. Works reliably enough with one or two retries.

## 2026-09-18 — gripper holding sensor reports True when empty
**Symptom:** `is_holding_something()` returned True with the fingers open and nothing in them.
**Fix:** Stopped trusting it. The teach and bench scripts ask the operator (`k`/`o`/`q`); `REQUIRE_GRAB_DETECT` stays False.

## 2026-09-18 — pen crushed the felt on the first square
**Symptom:** Drawing pressed the tip hard enough to flatten it, at offsets of 0, 1, and 3 mm.
**Fix:** The corners had been touched off with the marker held by hand; the robot's grip held it 27 mm differently. Re-teaching the corners with the marker in the runtime grip fixed it; a 1 mm offset then just kisses the surface.

## 2026-09-18 — straight-down look pose over the board center was unreachable
**Symptom:** `zero IK solutions produced` at 450 mm above the plane.
**Fix:** The pen and gripper hang about 200 mm below the camera and the xArm6 reaches about 700 mm; a straight-down pose with the gripper 240 mm above the plane puts the camera near 450 mm and is reachable. Taught by hand.
