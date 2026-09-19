# Morning checklist (Sat 2026-09-19)

Everything below needs the machine. Order matters; each line is a few minutes. E-stop within reach before the first arm move.

- [x] feat/duet-page is merged into feat/duet-design (commit 1487ab7, 08:55): the designed page is what `python -m duet.run` serves. Run everything from the main checkout on feat/duet-design; the `.worktrees/duet-page` worktree is no longer needed. Page tests: `node --test 'pagetests/*.test.mjs'` from `code/hackathon` (32 pass).

## Before the arm moves (10 min)
- [ ] `cd code/hackathon && source .venv/bin/activate` — every command below assumes it.
- [ ] `python explore.py`: connected, resources listed, E-stop not latched. This also saves `captures/depth.dep`; take it at the look pose (see below) for the hand check.
- [ ] `git log --oneline -15` to see what landed overnight; `python -m pytest -q` green.
- [ ] `python -m duet.teach show`, then `python -m duet.teach verify`: every taught pose still reached (ends at the dock slot, not the look pose).
- [ ] `python -m duet.teach load`: puts the pen in the gripper; this also parks the arm at the look pose for the next steps.
- [ ] Wipe the board. `python -m duet.calibrate --check` at the look pose: marks re-found, drift small. If the board moved: `python -m duet.calibrate --tl D`, draw the two squares with `stroke_bench 20 --at 15 15` and `--at 120 180`, then `calibrate --check` and `--fit 15,15,20 120,180,20`.
- [ ] The run command binds `127.0.0.1` by default; use `--host 0.0.0.0` only if a second screen must reach the page, since any client can command the arm.
- [ ] Once the arm has left the look pose it draws through a hand — the wrist camera cannot see the board from there. Pause on the page is the only guard while it draws; the E-stop is the real one.

## Hand check and camera cadence (10 min)
- [ ] With the arm at the look pose, run `python explore.py` (it saves the depth frame as `captures/depth.dep`), then `python -m duet.calibrate --dock x0 y0 x1 y1` with the tub's rectangle read off `captures/calib_frame.jpg`, then `python -m duet.calibrate --plane captures/depth.dep`. Read its two warnings: the plane height should be near 450 mm and the empty-board check must not see a hand. The page's header then says `hand check: depth at the look pose`. Without this step the color backup runs, which is fine for the demo.
- [ ] Measure the real frame cadence once (the trigger's stillness window assumes at least two frames per 1.5 s): `python -c "import asyncio,viam_conn;from viam.components.camera import Camera;from duet.camera import FrameSource
async def m():
    async with await viam_conn.connect() as r:
        s=FrameSource(Camera.from_robot(r,viam_conn.CAMERA));await s.start();await asyncio.sleep(10);f=list(s.frames);await s.stop()
        print(len(f),'frames in',round(f[-1].t-f[0].t,1),'s; gap',round((f[-1].t-f[0].t)/max(1,len(f)-1),2),'s; errors',s.errors)
asyncio.run(m())"`. If the gap is over 0.7 s, raise `STILL_WINDOW_S` in `config.py` to three gaps.
- [ ] `python -m duet.run --handoff held`, open http://localhost:8000. Hold a hand over the board: the terminal must not fire a turn while it is there. Draw a mark, take the hand away: the turn fires after 2 s. That is the stage 6 exit.

## One full exchange from the page (20 min)
- [ ] Held mode first. `python -m duet.run --exchanges 3 --length short`. Draw, step back, watch: capture, Claude's sentence, the plan preview, the arm drawing, the look pose, "human turn" again. The stage 8 exit is one exchange without touching the terminal.
- [ ] If a move is refused or the arm faults: the page shows paused; fix the cause, Clear arm error, Resume.
- [ ] If a turn does not end within about 10 s of the person stepping back, that is the stillness or hand reading, not the trigger: press Pass, then check the cadence line above and whether the header says the hand check is on depth or color.
- [ ] A Claude timeout (12 s on Short; overnight the real call took 8.9 to 9.9 s, so it is close) does not pause anything: the page shows "Fallback grammar" and the robot draws the Haring outline instead; nothing to click. If it happens twice in a row, raise `TIMEOUT_S["short"]` in `duet/claude_turn.py` to 15.
- [ ] If the page pauses with "corner mark near (...) not found", the marks are not being re-found under the room light: re-run `python -m duet.calibrate --check` and, if it fails too, `--tl D` then the two-square `--fit`.
- [ ] Dock mode only if there is time: record the green dot with `"dots": {"green": {"xy": [x, y], "hsv_lo": [40, 60, 60], "hsv_hi": [85, 255, 255]}}` in `calibration.json` (pixel position from `captures/calib_frame.jpg` with the marker capped in the tub), then `--handoff dock`.

## Rest of the morning
- [ ] Let a session finish: the video appears on the page and in `sessions/<id>/session.mp4`.
- [ ] Three sessions in a row on Short. Tune `PEN_DOWN_OFFSET_MM`, the Claude timeouts in `claude_turn.TIMEOUT_S`, and the prompt from what the boards look like.
- [ ] Freeze code by 14:30. Demo script: Short, 3 exchanges, one clear shape, let Claude's sentence carry the room.
- [ ] If time allows: ask Viam staff for a webcam on a stand over the table and give `HandGuard` a second frame source, so the hand check works while the arm draws; collision sensitivity 5 on the arm.
