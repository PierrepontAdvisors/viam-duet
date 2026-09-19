"""Start Duet: the camera poller, the controller, Claude, the session loop, and the page.

    python -m duet.run                      the real machine; page at http://localhost:8000
    python -m duet.run --fake               no machine: a fake camera replays the real day-1 boards from
                                            sessions/20260918-190258 (a fake visitor "draws" each human turn,
                                            a fake arm "draws" each robot turn), canned proposals, the page live
    python -m duet.run --fake --claude      the same replay, but the real Claude call on the real boards
    python -m duet.run --fake --replay 20260918-185927
    python -m duet.run --length medium --exchanges 3 --handoff dock --port 8080

Stop with Ctrl-C. Every event is also printed to the terminal, so the trigger can be watched without the page.
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
import re
from pathlib import Path

import cv2
import uvicorn

from duet import claude_turn
from duet import config as cfg
from duet.recorder import Recorder
from duet.session import EventBus, HandGuard, Session, Settings
from duet.web import make_app


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="run Duet")
    p.add_argument("--fake", action="store_true", help="no machine: replay real boards through a fake camera and arm")
    p.add_argument("--claude", action="store_true", help="with --fake: call the real Claude anyway")
    p.add_argument("--replay", default="20260918-190258", help="with --fake: the session folder whose boards are replayed")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--host", default="127.0.0.1", help="the page accepts arm commands from any client, so stay on loopback unless a second screen needs it")
    p.add_argument("--length", choices=tuple(cfg.BUDGET_MM), default="short")
    p.add_argument("--exchanges", type=int, default=5)
    p.add_argument("--handoff", choices=("held", "dock"), default="held" if cfg.HELD_MODE else "dock")
    return p


def replay_paths(folder: Path) -> tuple[Path, list[Path], list[Path]]:
    """The start photo and the human and robot photos of a recorded session, in turn order."""
    def turn(p: Path) -> int:
        return int(re.match(r"turn-(\d+)-", p.name).group(1))
    humans = sorted(folder.glob("turn-*-human.jpg"), key=turn)
    robots = sorted(folder.glob("turn-*-robot.jpg"), key=turn)
    return folder / "turn-00-start.jpg", humans, robots


class ClaudeBrain:
    """The real Claude turn, off the event loop so the page and camera keep moving while it thinks."""

    def __init__(self):
        self.client = claude_turn.make_client()

    async def propose(self, board, human_cam, history, length, exchange, total):
        return await asyncio.to_thread(claude_turn.propose, self.client, board, human_cam, history, length, exchange, total)


async def log_events(bus: EventBus) -> None:
    q = bus.subscribe()
    while True:
        m = await q.get()
        t = m["type"]
        if t == "state":
            print(f"[state] {m['state']}  turn {m['turn']} of {m['exchanges']}  {m['length']}/{m['handoff']}  "
                  f"hand check {m['hand_guard']}" + (f"  ERROR {m['error']}" if m.get("error") else ""), flush=True)
        elif t == "interpretation":
            print(f"[claude] {m['source']} {m['latency_s']} s: {m['sees']} {m['adds']} {m.get('error') or ''}", flush=True)
        elif t == "plan":
            print(f"[plan] {len(m['polylines'])} strokes, budget {m['budget_mm']} mm", flush=True)
        elif t in ("error", "dock", "video", "human"):
            print(f"[{t}] " + json.dumps({k: v for k, v in m.items() if k not in ("type", "polylines", "new")}), flush=True)


async def fake_visitor(bus: EventBus, frames, humans: list[Path]) -> None:
    """Each human turn: wait a moment, move a hand over the board for a second, then show the next
    real human-turn board and hold still, so the held trigger fires by itself."""
    q = bus.subscribe()
    boards = list(humans)
    while True:
        m = await q.get()
        if m["type"] == "state" and m["state"] == "human_turn":
            await asyncio.sleep(2.0)
            if not boards:
                print("[visitor] out of recorded turns; the board is yours", flush=True)
                return
            frames.jitter(1.2)
            await asyncio.sleep(0.6)
            frames.show_board(cv2.imread(str(boards.pop(0))))
            print("[visitor] drew a mark", flush=True)


async def main(args: argparse.Namespace) -> None:
    cal = json.loads(cfg.CALIBRATION_PATH.read_text())
    settings = Settings(length=args.length, exchanges=args.exchanges, handoff=args.handoff)
    bus = EventBus()
    rec = Recorder(settings=settings.record())
    machine = frames = ctl = None
    tasks: list[asyncio.Task] = []
    if args.fake:
        from duet.fakes import FakeBrain, FakeController, FakeFrames
        start, humans, robots = replay_paths(cfg.SESSIONS_DIR / args.replay)
        frames = FakeFrames(cv2.imread(str(cfg.FIXTURES_DIR / "look_frame.jpg")), cal)
        frames.show_board(cv2.imread(str(start)))
        frames.robot_boards = [cv2.imread(str(p)) for p in robots]
        ctl = FakeController(frames, stroke_s=0.3)
        brain = ClaudeBrain() if args.claude else FakeBrain(latency_s=1.0)
        tasks.append(asyncio.create_task(fake_visitor(bus, frames, humans)))
    else:
        from viam.components.camera import Camera
        import viam_conn
        from duet.calib import BoardToRobot, load_poses
        from duet.camera import FrameSource
        from duet.controller import Controller
        machine = await viam_conn.connect()
        frames = FrameSource(Camera.from_robot(machine, viam_conn.CAMERA))
        await frames.start()
        poses = load_poses()
        ctl = Controller(machine, poses, BoardToRobot.from_poses(poses))
        ctl.held_mode = args.handoff == "held"
        brain = ClaudeBrain()
    guard = HandGuard(frames, cal)
    session = Session(settings, frames, ctl, brain, rec, bus, cal, guard=guard)
    app = make_app(session, frames, bus, calibration=cal)
    server = uvicorn.Server(uvicorn.Config(app, host=args.host, port=args.port, log_level="warning"))
    print(f"Duet on http://localhost:{args.port}  source={'fake replay of ' + args.replay if args.fake else 'armfarm22'} "
          f"brain={type(brain).__name__} hand_check={guard.mode} session={rec.dir}", flush=True)
    # the logger first: it subscribes before the loop's first emit, so `start` is printed too
    tasks += [asyncio.create_task(log_events(bus)), asyncio.create_task(session.run())]
    try:
        await server.serve()
    finally:
        with contextlib.suppress(Exception):
            await ctl.stop()                   # the arm halts before the loop is torn down
        for t in tasks:
            t.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await t
        if machine is not None:
            await frames.stop()
            await machine.close()


if __name__ == "__main__":
    asyncio.run(main(build_parser().parse_args()))
