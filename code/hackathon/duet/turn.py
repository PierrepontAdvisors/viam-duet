"""One duet exchange per command, driven from the terminal (the web page comes later).

    python -m duet.turn start [--length short|medium|long] [--exchanges 5]   photograph the blank board
    python -m duet.turn next                                                 you drew; the robot answers
    python -m duet.turn status

Session files land in code/hackathon/sessions/<id>/: turn-NN-human.jpg, turn-NN-robot.jpg,
plan-NN.svg, session.json. At any prompt, q and Enter skips the drawing.
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from viam.components.camera import Camera

import viam_conn
from duet import config as cfg
from duet import planner, svg, vision
from duet.calib import BoardToRobot, load_poses
from duet.calibrate import load_calibration
from duet.camera import median_capture
from duet.claude_turn import TurnResult, make_client, propose
from duet.controller import Controller
from duet.strokes import length
from duet.styles import haring

STATE = cfg.SESSIONS_DIR / "current.json"


async def ask(prompt: str) -> str:
    return (await asyncio.to_thread(input, prompt)).strip().lower()


def load_state() -> dict:
    if not STATE.exists():
        raise SystemExit("no session; run `python -m duet.turn start` first")
    return json.loads(STATE.read_text())


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2))
    (cfg.SESSIONS_DIR / state["id"] / "session.json").write_text(json.dumps(state, indent=2))


def warp(frame: np.ndarray, cal: dict) -> np.ndarray:
    quad = vision.find_corner_marks(frame, expected=cal["marks_image"])
    return vision.warp_to_board(frame, vision.board_quad(quad, cal["board_tl_index"]))


async def look_and_capture(c: Controller, cam: Camera, cal: dict) -> np.ndarray:
    await c.go_look()
    await asyncio.sleep(0.8)
    return warp(await median_capture(cam), cal)


def map_strokes(strokes: list[dict], cal: dict) -> list[dict]:
    """Claude reads positions off the camera's gridded photo, so its strokes are camera-board mm.
    Map them to robot-board mm with the calibrated per-axis fit."""
    m = cal.get("cam_to_robot")
    if not m:
        return strokes
    ax, bx, ay, by = m["ax"], m["bx"], m["ay"], m["by"]
    out = []
    for s in strokes:
        t = dict(s)
        t["points"] = [{"x": ax * p["x"] + bx, "y": ay * p["y"] + by} for p in s.get("points", [])]
        t["cx"], t["cy"], t["r"] = ax * s.get("cx", 0) + bx, ay * s.get("cy", 0) + by, s.get("r", 0) * (ax + ay) / 2
        out.append(t)
    return out


def all_ink(board: np.ndarray, cal: dict) -> list:
    white = np.full_like(board, 235)
    return vision.cam_to_robot(vision.trace(vision.new_ink(board, white)[0]), cal)


async def start(length_setting: str, exchanges: int) -> None:
    poses, cal = load_poses(), load_calibration()
    sid = time.strftime("%Y%m%d-%H%M%S")
    folder = cfg.SESSIONS_DIR / sid
    folder.mkdir(parents=True, exist_ok=True)
    async with await viam_conn.connect() as machine:
        c = Controller(machine, poses, BoardToRobot.from_poses(poses))
        cam = Camera.from_robot(machine, viam_conn.CAMERA)
        await ask("Stand clear. Enter to move to the look pose and photograph the board, q to abort... ")
        board = await look_and_capture(c, cam, cal)
    cv2.imwrite(str(folder / "turn-00-start.jpg"), board)
    save_state({"id": sid, "length": length_setting, "exchanges": exchanges, "turn": 0,
                "history": [], "last_photo": "turn-00-start.jpg", "started": sid})
    print(f"session {sid} started ({length_setting}, {exchanges} exchanges). Draw something, then run "
          "`python -m duet.turn next`.")


async def next_turn() -> None:
    state = load_state()
    poses, cal = load_poses(), load_calibration()
    folder = cfg.SESSIONS_DIR / state["id"]
    n = state["turn"] + 1
    length_setting = state["length"]
    client = make_client()
    async with await viam_conn.connect() as machine:
        c = Controller(machine, poses, BoardToRobot.from_poses(poses))
        cam = Camera.from_robot(machine, viam_conn.CAMERA)
        await ask(f"Exchange {n} of {state['exchanges']}. Hands off the board. Enter to look, q to abort... ")
        current = await look_and_capture(c, cam, cal)
        previous = cv2.imread(str(folder / state["last_photo"]))
        mask, coverage = vision.new_ink(current, previous)
        human_cam = vision.trace(mask)
        if not human_cam:
            print("no new ink found since the last photo; draw something first")
            return
        cv2.imwrite(str(folder / f"turn-{n:02d}-human.jpg"), current)
        human = vision.cam_to_robot(human_cam, cal)
        ink = all_ink(current, cal)
        print(f"found {len(human_cam)} new stroke(s), {sum(length(p) for p in human):.0f} mm; board coverage {coverage:.1%}")

        result: TurnResult = propose(client, current, human_cam, state["history"], length_setting, n, state["exchanges"])
        if result.proposal:
            print(f"\nClaude ({result.latency_s:.1f} s):\n  sees: {result.proposal.sees}\n  adds: {result.proposal.adds}\n")
            strokes = map_strokes([s.model_dump() for s in result.proposal.strokes], cal)
            safe = planner.validate(strokes, ink, cfg.BUDGET_MM[length_setting])
            planned, color = haring.style(safe)
            sees, adds = result.proposal.sees, result.proposal.adds
        else:
            print(f"\nClaude unavailable ({result.error}); the Haring fallback answers.\n")
            planned, color = haring.fallback(human)
            sees, adds = "(fallback)", "outline and ticks around your mark"
        svg.write(folder / f"plan-{n:02d}.svg", ink, [], planned, color)
        total = sum(length(p) for p in planned)
        print(f"plan: {len(planned)} strokes, {total:.0f} mm (budget {cfg.BUDGET_MM[length_setting]:.0f}); "
              f"preview {folder / f'plan-{n:02d}.svg'}")
        if await ask("Hands clear of the board? Enter to draw, q to skip drawing... ") == "q":
            print("skipped")
            return
        res = await c.draw(planned, cfg.BUDGET_MM[length_setting], cfg.BUDGET_S[length_setting])
        print(f"drew {res.strokes_done} strokes, {res.drawn_mm:.0f} mm in {res.seconds:.0f} s" + (" (stopped: hand seen)" if res.blocked else ""))
        robot_photo = await look_and_capture(c, cam, cal)
    cv2.imwrite(str(folder / f"turn-{n:02d}-robot.jpg"), robot_photo)
    state["history"].append({"sees": sees, "adds": adds, "source": result.source})
    state["turn"], state["last_photo"] = n, f"turn-{n:02d}-robot.jpg"
    save_state(state)
    done = n >= state["exchanges"] or coverage >= cfg.COVERAGE_END
    print(f"exchange {n} of {state['exchanges']} complete." + (" The piece is finished." if done else " Your turn."))


def main(argv: list[str]) -> None:
    if not argv:
        raise SystemExit(__doc__)
    verb = argv[0]
    if verb == "start":
        length_setting = argv[argv.index("--length") + 1] if "--length" in argv else "short"
        exchanges = int(argv[argv.index("--exchanges") + 1]) if "--exchanges" in argv else 5
        asyncio.run(start(length_setting, exchanges))
    elif verb == "next":
        asyncio.run(next_turn())
    elif verb == "status":
        s = load_state()
        print(json.dumps({k: s[k] for k in ("id", "length", "exchanges", "turn", "last_photo")}, indent=2))
        for i, h in enumerate(s["history"], 1):
            print(f"  {i}: [{h['source']}] sees: {h['sees']} | adds: {h['adds']}")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
