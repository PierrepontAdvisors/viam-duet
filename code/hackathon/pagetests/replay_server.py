"""Replay harness for the Duet page. Serves the page, the static files, the session files, and a
WebSocket that speaks the agreed protocol by replaying tonight's real session: its photos, plan SVGs,
and Claude's sentences, with storybook thoughts and quips added, and the calibration frame as the
camera. Dev only; the real server is duet/web.py.

    DUET_SPEED=3 python pagetests/replay_server.py     # faster turns
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import os
import re
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                                   # code/hackathon in this worktree
MAIN = Path(os.environ.get("DUET_MAIN", "/Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/code/hackathon"))
STATIC = ROOT / "duet" / "static"
SESSIONS = Path(os.environ.get("DUET_SESSIONS", str(MAIN / "sessions")))
SESSION_ID = os.environ.get("DUET_SESSION", "20260918-190258")
FRAME = Path(os.environ.get("DUET_FRAME", str(MAIN / "captures" / "calib_frame.jpg")))
CALIB = json.loads((ROOT / "duet" / "data" / "calibration.json").read_text())
SPEED = float(os.environ.get("DUET_SPEED", "1"))
PORT = int(os.environ.get("DUET_PORT", "8765"))
HUMAN_TURN_S = float(os.environ.get("DUET_HUMAN_S", "8"))

THOUGHTS = ["Is that a creature waking up?", "Ooh, it is growing loops!", "Petals on top, a tail below…",
            "So many little cells!", "Hmm... my words got lost.", "A whole colony! What now?"]
QUIPS = ["I'll give it a tiny heartbeat!", "Let's make that head glow!", "One more eye, just for you!",
         "Wake up, little cell!", "Lost my words. Drawing anyway!", "Time to dance! Wonderful work!"]
PATH_RE = re.compile(r'<path d="([^"]+)"[^>]*stroke="([^"]+)"')
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def polylines_from_svg(text: str) -> tuple[list, list]:
    """Black paths are the traced human ink, green paths the robot's plan, both in board mm."""
    ink, robot = [], []
    for d, stroke in PATH_RE.findall(text):
        nums = [float(v) for v in NUM_RE.findall(d)]
        pl = [[nums[i], nums[i + 1]] for i in range(0, len(nums) - 1, 2)]
        (robot if stroke == "green" else ink).append(pl)
    return ink, robot


def load_session() -> tuple[list[dict], dict[int, tuple[list, list]]]:
    folder = SESSIONS / SESSION_ID
    history = json.loads((folder / "session.json").read_text()).get("history", [])
    plans = {int(p.stem.split("-")[1]): polylines_from_svg(p.read_text()) for p in sorted(folder.glob("plan-*.svg"))}
    return history, plans


class Bus:
    SNAPSHOT = ("calib", "state", "dock", "human", "interpretation", "plan", "progress", "shot", "video", "error")

    def __init__(self) -> None:
        self.last: dict[str, dict] = {}
        self.queues: set[asyncio.Queue] = set()

    def emit(self, kind: str, **fields) -> dict:
        msg = {"type": kind, **fields}
        self.last[kind] = msg
        for q in list(self.queues):
            q.put_nowait(msg)
        return msg

    def snapshot(self) -> list[dict]:
        return [self.last[k] for k in self.SNAPSHOT if k in self.last]


class Replay:
    """One scripted session that loops forever: idle, look, then human and robot turns from the files."""

    def __init__(self, bus: Bus) -> None:
        self.bus = bus
        self.history, self.plans = load_session()
        self.settings = {"artist": "haring", "length": "long", "exchanges": 5, "mode": "duet", "handoff": "held",
                         "energy": 0.5, "direction": 0.0}
        self.state, self.turn, self.error = "idle", 0, None
        self.paused = asyncio.Event()
        self.passed = asyncio.Event()

    def emit_state(self) -> None:
        self.bus.emit("state", state=self.state, turn=self.turn, coverage=round(0.05 * self.turn, 3), error=self.error,
                      at_look=self.state in ("look", "human_turn", "capture", "interpret", "plan"),
                      hand_guard="color at the look pose", session=SESSION_ID, artists=["haring"], **self.settings)

    def go(self, state: str) -> None:
        self.state = state
        self.emit_state()

    async def wait(self, seconds: float) -> None:
        await asyncio.sleep(seconds / SPEED)
        while self.paused.is_set():
            await asyncio.sleep(0.05)

    def shot(self, turn: int, who: str) -> None:
        folder = SESSIONS / SESSION_ID
        frame = folder / f"turn-{turn:02d}-{who}-frame.jpg"
        self.bus.emit("shot", url=f"/sessions/{SESSION_ID}/turn-{turn:02d}-{who}.jpg", turn=turn, who=who,
                      frame_url=f"/sessions/{SESSION_ID}/{frame.name}" if frame.exists() else None)

    async def run(self) -> None:
        while True:
            self.turn, self.error = 0, None
            self.go("idle"); await self.wait(1.0)
            self.go("look"); self.shot(0, "start"); await self.wait(1.0)
            all_ink: list = []
            for t in sorted(self.plans):
                ink, robot = self.plans[t]
                self.go("human_turn")
                self.passed.clear()
                with contextlib.suppress(asyncio.TimeoutError):
                    await asyncio.wait_for(self.passed.wait(), HUMAN_TURN_S / SPEED)
                self.turn = t
                self.go("capture"); self.shot(t, "human")
                all_ink = all_ink + ink
                self.bus.emit("human", polylines=all_ink, new=ink, found=True); await self.wait(1.0)
                self.go("interpret"); await self.wait(3.0)
                h = self.history[t - 1] if t - 1 < len(self.history) else {"sees": "", "adds": "", "source": "claude"}
                fallback = h.get("source") == "fallback"
                self.bus.emit("interpretation", sees=h.get("sees", ""), adds=h.get("adds", ""), source=h.get("source", "claude"),
                              latency_s=None if fallback else 7.5, error="timeout" if fallback else None,
                              thought="Hmm... my words got lost." if fallback else THOUGHTS[(t - 1) % len(THOUGHTS)],
                              quip="Lost my words. Drawing anyway!" if fallback else QUIPS[(t - 1) % len(QUIPS)])
                self.go("plan"); self.bus.emit("plan", polylines=robot, color="#1b8f3a", budget_mm=4000); await self.wait(2.0)
                self.go("robot_draw")
                drawn = 0.0
                for i, pl in enumerate(robot):
                    await self.wait(0.4)
                    drawn += sum(((pl[k][0] - pl[k - 1][0]) ** 2 + (pl[k][1] - pl[k - 1][1]) ** 2) ** 0.5 for k in range(1, len(pl)))
                    self.bus.emit("progress", stroke=i, drawn_mm=round(drawn))
                self.shot(t, "robot"); self.go("look"); await self.wait(1.0)
            self.go("finish"); await self.wait(1.5)
            self.go("finished")
            if (SESSIONS / SESSION_ID / "session.mp4").exists():
                self.bus.emit("video", url=f"/sessions/{SESSION_ID}/session.mp4")
            await self.wait(15.0)

    def handle(self, cmd: dict) -> dict | None:
        kind = cmd.get("type")
        if kind == "set":
            try:
                self.apply(cmd)
            except ValueError as exc:
                return {"type": "error", "message": f"setting refused: {exc}"}
            self.emit_state()
        elif kind == "pause":
            self.paused.set(); self.go("paused")
        elif kind == "resume":
            self.paused.clear(); self.go("human_turn" if self.turn == 0 else "look")
        elif kind == "pass":
            self.passed.set()
        elif kind == "clear_error":
            self.error = None; self.emit_state()
        else:
            return {"type": "error", "message": f"unknown command {kind!r}"}
        return None

    def apply(self, cmd: dict) -> None:
        s = dict(self.settings)
        if "length" in cmd:
            if cmd["length"] not in ("short", "medium", "long"):
                raise ValueError("length must be short, medium or long")
            s["length"] = cmd["length"]
        if "exchanges" in cmd:
            n = int(cmd["exchanges"])
            if not 1 <= n <= 10:
                raise ValueError("exchanges must be 1 to 10")
            s["exchanges"] = n
        if "handoff" in cmd:
            if cmd["handoff"] not in ("held", "dock"):
                raise ValueError("handoff must be held or dock")
            s["handoff"] = cmd["handoff"]
        if "artist" in cmd:
            if cmd["artist"] != "haring":
                raise ValueError("artist must be one of ('haring',)")
            s["artist"] = cmd["artist"]
        for key, lo, hi in (("energy", 0.0, 1.0), ("direction", 0.0, 359.0)):
            if key in cmd:
                try:
                    v = float(cmd[key])
                except (TypeError, ValueError):
                    raise ValueError(f"{key} must be a number") from None
                if not lo <= v <= hi:
                    raise ValueError(f"{key} must be from {lo:g} to {hi:g}")
                s[key] = v
        self.settings = s


def mjpeg_part(data: bytes) -> bytes:
    return b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(len(data)).encode() + b"\r\n\r\n" + data + b"\r\n"


def make_app() -> FastAPI:
    bus = Bus()
    replay = Replay(bus)

    @contextlib.asynccontextmanager
    async def lifespan(_app: FastAPI):
        task = asyncio.create_task(replay.run())
        yield
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

    app = FastAPI(title="Duet replay", lifespan=lifespan)
    calib = {"type": "calib", "marks_image": CALIB["marks_image"], "board_tl_index": CALIB["board_tl_index"],
             "board_mm": CALIB["board_mm"], "image_size": [1280, 720], "cam_to_robot": CALIB["cam_to_robot"]}
    bus.emit("calib", **{k: v for k, v in calib.items() if k != "type"})
    app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
    app.mount("/sessions", StaticFiles(directory=str(SESSIONS)), name="sessions")
    frame_bytes = FRAME.read_bytes()

    @app.get("/")
    async def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/health")
    async def health():
        return {"state": replay.state, "turn": replay.turn}

    @app.get("/calibration.json")
    async def calibration():
        return JSONResponse(calib)

    @app.get("/stream.mjpg")
    async def stream():
        async def gen():
            while True:
                yield mjpeg_part(frame_bytes)
                await asyncio.sleep(0.2)
        return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")

    @app.websocket("/ws")
    async def ws(sock: WebSocket):
        await sock.accept()
        q: asyncio.Queue = asyncio.Queue()
        bus.queues.add(q)
        try:
            for msg in bus.snapshot():
                await sock.send_json(msg)

            async def pump():
                while True:
                    await sock.send_json(await q.get())
            task = asyncio.create_task(pump())
            try:
                while True:
                    reply = replay.handle(await sock.receive_json())
                    if reply is not None:
                        await sock.send_json(reply)
            finally:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task
        except WebSocketDisconnect:
            pass
        finally:
            bus.queues.discard(q)

    return app


if __name__ == "__main__":
    uvicorn.run(make_app(), host="127.0.0.1", port=PORT, log_level="warning")
