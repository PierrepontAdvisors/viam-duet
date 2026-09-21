"""Start Duet: the camera poller, the controller, Claude, the session loop, and the page.

    python -m duet.run                      the real machine; page at http://localhost:8000
    python -m duet.run --fake               no machine: a fake camera replays the boards of the recorded session that
                                            ships in site/demo/sessions (a fake visitor "draws" each human turn,
                                            a fake arm "draws" each robot turn), canned proposals, the page live
    python -m duet.run --fake --claude      the same replay, but the real Claude call on the real boards
    python -m duet.run --fake --replay 20260918-185927 --exchanges 1     a session under sessions/ (gitignored recordings)
    python -m duet.run --length medium --exchanges 3 --handoff dock --port 8080

Stop with Ctrl-C. Every event is also printed to the terminal, so the loop can be watched without the page. New session
on the page starts a fresh piece without a restart.
"""
from __future__ import annotations

import argparse
import os
import asyncio
import contextlib
import json
import logging
import re
from pathlib import Path

import cv2
import numpy as np
import uvicorn

from duet import claude_turn
from duet import config as cfg
from duet import vision
from duet.recorder import Recorder
from duet.session import ARTISTS, EventBus, HandGuard, Session, Settings
from duet.tasks import watch
from duet.web import make_app


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="run Duet")
    p.add_argument("--fake", action="store_true", help="no machine: replay real boards through a fake camera and arm")
    p.add_argument("--claude", action="store_true", help="with --fake: call the real Claude anyway")
    p.add_argument("--replay", default=str(cfg.SHIPPED_SESSION), help="with --fake: a path to a folder of turn photos, or a session name under sessions/; default: the showcase session that ships in site/demo/sessions")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--host", default="127.0.0.1", help="the page accepts arm commands from any client, so stay on loopback unless a second screen needs it")
    p.add_argument("--artist", choices=ARTISTS, default=cfg.ARTIST)
    p.add_argument("--length", choices=tuple(cfg.BUDGET_MM), default="short")
    p.add_argument("--exchanges", type=int, default=5)
    p.add_argument("--handoff", choices=("held", "dock"), default="held" if cfg.HELD_MODE else "dock")
    p.add_argument("--no-guard", action="store_true",
                   help="no camera hand check before the arm moves: for a venue where the Viam link drops frames, "
                        "so that 'no frame' would read as a hand and block every turn; the operator, Pause, "
                        "Reset arm, and the E-stop are the guard")
    return p


def replay_paths(folder: Path) -> tuple[Path, list[Path], list[Path]]:
    """The start photo and the human and robot photos of a recorded session, in turn order."""
    def turn(p: Path) -> int:
        return int(re.match(r"turn-(\d+)-", p.name).group(1))
    start = folder / "turn-00-start.jpg"
    if not start.exists():
        raise SystemExit(f"no recorded session at {folder}: record one against the machine, or pass --replay a folder of turn photos, "
                         "for example the showcase session at site/demo/sessions/20260919-151119 (from code/hackathon: "
                         "--replay ../../site/demo/sessions/20260919-151119)")
    humans = sorted(folder.glob("turn-*-human.jpg"), key=turn)
    robots = sorted(folder.glob("turn-*-robot.jpg"), key=turn)
    return start, humans, robots


def replay_folder(value: str) -> Path:
    """`--replay` is a session name under sessions/ (gitignored recordings) or a path to any folder of turn photos."""
    return Path(value) if ("/" in value or os.sep in value) else cfg.SESSIONS_DIR / value


VISITOR_WAITS = (2.0, 0.6, 1.0)   # the fake visitor: settle, hand over the board, look at the mark, then Go


class ClaudeBrain:
    """The real Claude turn, off the event loop so the page and camera keep moving while it thinks."""

    def __init__(self):
        self.client = claude_turn.make_client()

    async def propose(self, board, human_cam, history, length, exchange, total, artist="haring"):
        return await asyncio.to_thread(claude_turn.propose, self.client, board, human_cam, history, length,
                                       exchange, total, artist)


class QuietShutdownCancels(logging.Filter):
    """On Ctrl-C the graceful timeout cancels the never-ending MJPEG response and uvicorn logs that
    CancelledError as a forty-line traceback. It is the timeout doing its job, and an operator who
    just stopped the arm should not have to read it to see that nothing went wrong. Real request
    failures are other exception types and still print."""

    def filter(self, record: logging.LogRecord) -> bool:
        exc = record.exc_info[1] if record.exc_info else None
        return not isinstance(exc, asyncio.CancelledError)


async def log_events(bus: EventBus) -> None:
    q = bus.subscribe()
    try:
        while True:
            m = await q.get()
            t = m["type"]
            if t == "state":
                done = m["state"] in ("finish", "finished")
                print(f"[state] {m['state']}  exchange {m['turn'] if done else m['turn'] + 1} of {m['exchanges']}  "
                      f"{m['length']}/{m['handoff']}  hand check {m['hand_guard']}"
                      + (f"  ERROR {m['error']}" if m.get("error") else ""), flush=True)
            elif t == "interpretation":
                print(f"[claude] {m['source']} {m['latency_s']} s: {m['sees']} {m['adds']} {m.get('error') or ''}", flush=True)
            elif t == "plan":
                print(f"[plan] {len(m['polylines'])} strokes, budget {m['budget_mm']} mm", flush=True)
            elif t == "shot":
                print(f"[shot] {m['url']}  turn {m['turn']}  {m['who']}", flush=True)
            elif t in ("error", "dock", "video", "human", "feed"):
                print(f"[{t}] " + json.dumps({k: v for k, v in m.items() if k not in ("type", "polylines", "new")}), flush=True)
    finally:
        bus.unsubscribe(q)


async def fake_visitor(bus: EventBus, frames, start: Path, humans: list[Path], robots: list[Path], session) -> None:
    """Each human turn: wait a moment, move a hand over the board for a second, show the next real
    human-turn board, then press Go (the pass command), as a visitor would. A new session id (New
    session on the page) puts the recorded piece back: the blank board and every turn again."""
    q = bus.subscribe()
    boards: list[Path] = []
    session_id = None
    settle, hand, look = VISITOR_WAITS
    try:
        while True:
            m = await q.get()
            if m["type"] != "state":
                continue
            if m.get("session") != session_id:
                session_id = m.get("session")
                boards = list(humans)
                frames.show_board(cv2.imread(str(start)))
                frames.robot_boards = [cv2.imread(str(p)) for p in robots]
            if m["state"] == "human_turn":
                await asyncio.sleep(settle)
                if not boards:
                    print("[visitor] out of recorded turns; the board is yours", flush=True)
                    continue
                frames.jitter(1.2)
                await asyncio.sleep(hand)
                frames.show_board(cv2.imread(str(boards.pop(0))))
                print("[visitor] drew a mark", flush=True)
                await asyncio.sleep(look)
                session.pass_turn()
                print("[visitor] pressed Go", flush=True)
    finally:
        bus.unsubscribe(q)


async def main(args: argparse.Namespace) -> None:
    cal = json.loads(cfg.CALIBRATION_PATH.read_text())
    settings = Settings(artist=args.artist, length=args.length, exchanges=args.exchanges, handoff=args.handoff)
    bus = EventBus()
    rec = Recorder(settings=settings.record())
    machine = frames = ctl = None
    tasks: list[asyncio.Task] = []
    if args.fake:
        from duet.fakes import FakeBrain, FakeController, FakeFrames
        start, humans, robots = replay_paths(replay_folder(args.replay))
        frames = FakeFrames(cv2.imread(str(cfg.FIXTURES_DIR / "look_frame.jpg")), cal)
        frames.show_board(cv2.imread(str(start)))
        frames.robot_boards = [cv2.imread(str(p)) for p in robots]
        ctl = FakeController(frames, stroke_s=0.3)
        brain = ClaudeBrain() if args.claude else FakeBrain(latency_s=1.0)
    else:
        from viam.components.camera import Camera
        import viam_conn
        from duet.calib import BoardToRobot, load_poses
        from duet.camera import FrameSource
        from duet.controller import Controller
        poses = load_poses()                  # a missing corner touch-off or Anthropic key should fail
        board = BoardToRobot.from_poses(poses)  # before anything reaches for the machine
        brain = ClaudeBrain()
        machine = await viam_conn.connect()
        frames = FrameSource(Camera.from_robot(machine, viam_conn.CAMERA))
        await frames.start()
        ctl = Controller(machine, poses, board)
        ctl.held_mode = args.handoff == "held"
    warm = np.zeros((8, 8), np.uint8)          # skan's first import costs 1.5 s; pay it before the first exchange
    warm[3, 1:7] = 255                         # a line, so Skeleton is built too and not just imported
    vision.trace(warm)
    guard = None if args.no_guard else HandGuard(frames, cal)
    session = Session(settings, frames, ctl, brain, rec, bus, cal, guard=guard)
    if args.fake:
        tasks.append(watch(asyncio.create_task(fake_visitor(bus, frames, start, humans, robots, session), name="visitor")))
    def relaunch() -> None:
        """The page's Relaunch run: uvicorn stops serving, the finally below stops the arm, the process
        exits, and demo.sh starts it again with the code now on disk."""
        server.should_exit = True
    app = make_app(session, frames, bus, calibration=cal, relaunch=relaunch)
    # the MJPEG stream never ends by itself, so an open page would hold a graceful shutdown forever
    server = uvicorn.Server(uvicorn.Config(app, host=args.host, port=args.port, log_level="warning",
                                           timeout_graceful_shutdown=1))
    logging.getLogger("uvicorn.error").addFilter(QuietShutdownCancels())
    print(f"Duet on http://localhost:{args.port}  source={'fake replay of ' + args.replay if args.fake else 'armfarm22'} "
          f"brain={type(brain).__name__} hand_check={'off' if guard is None else guard.mode} session={rec.dir}", flush=True)
    # the logger first: it subscribes before the loop's first emit, so `start` is printed too
    tasks += [watch(asyncio.create_task(log_events(bus), name="log")),
              watch(asyncio.create_task(session.run_forever(), name="session"))]
    try:
        await server.serve()
    finally:
        with contextlib.suppress(Exception):
            await ctl.stop()                   # the arm halts before the loop is torn down
        for t in tasks:
            t.cancel()
            with contextlib.suppress(Exception, asyncio.CancelledError):
                await t                        # one task that already died must not abort the rest
        if machine is not None:
            with contextlib.suppress(Exception):
                await frames.stop()
            with contextlib.suppress(Exception):
                await machine.close()


if __name__ == "__main__":
    asyncio.run(main(build_parser().parse_args()))
