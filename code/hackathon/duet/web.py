"""The page's server: the static page, one WebSocket carrying every session event and the page's
commands, an MJPEG stream of the camera that holds the last capture still while the arm is away from
the look pose, and the session files. Local screen only; the public tunnel is P1."""
from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path
from time import monotonic

import cv2
import numpy as np
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from duet import config as cfg
from duet import vision
from duet.tasks import watch

STATIC = cfg.PACKAGE_DIR / "static"
ALLOWED_SETTINGS = ("artist", "length", "exchanges", "mode", "handoff", "energy", "direction")
STREAM_FPS = 4                 # new frames only; the camera itself delivers one to three a second
STREAM_PERIOD_S = 1 / STREAM_FPS
STREAM_WIDTH = 960             # the page registers on the 16:9 aspect, not the pixel size
STREAM_QUALITY = 65
STREAM_KEEPALIVE_S = 10.0   # a proxy cuts an idle response; the current picture is resent this often while nothing changes
IMAGE_SIZE = (1280, 720)       # the RealSense color stream the calibration was made on


def hex_to_bgr(color: str) -> tuple[int, int, int]:
    c = color.lstrip("#")
    return int(c[4:6], 16), int(c[2:4], 16), int(c[0:2], 16)


def mjpeg_part(bgr: np.ndarray, quality: int = STREAM_QUALITY) -> bytes:
    ok, jpg = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("could not encode a stream frame")
    data = jpg.tobytes()
    return (b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(len(data)).encode()
            + b"\r\n\r\n" + data + b"\r\n")


def stream_size(bgr: np.ndarray) -> np.ndarray:
    """Scale a frame down to STREAM_WIDTH, keeping the aspect; smaller frames pass through."""
    h, w = bgr.shape[:2]
    if w <= STREAM_WIDTH:
        return bgr
    return cv2.resize(bgr, (STREAM_WIDTH, round(h * STREAM_WIDTH / w)), interpolation=cv2.INTER_AREA)


def feed_pick(session, frames) -> tuple[str, np.ndarray | None, object]:
    """What the stream shows now. "held": the session's last capture while the arm is away from the
    look pose (the wrist camera is swinging over the board and the page's overlay would slide off it);
    "live": the latest fresh camera frame; "stale": nothing to send, so the browser keeps its last
    image instead of a gray card. The key changes when the picture should be resent."""
    still = session.held_frame
    if not session.at_look and still is not None:
        return "held", still, ("held", session.held_id)          # the id is unique for the process, unlike id(still)
    f = frames.latest()
    if f is not None:
        return "live", f.color, ("live", f.t)
    return "stale", None, None


def overlay(img: np.ndarray, plan, h_inv: np.ndarray | None, color_bgr: tuple[int, int, int],
            cam_to_robot: dict | None = None) -> np.ndarray:
    """Draw a plan onto a camera frame, leaving `img` untouched.

    `plan` is in robot-board millimeters but the homography maps camera-board pixels, so the
    calibrated per-axis fit (robot = a * cam + b) is inverted first; without one the two frames are
    taken to be the same."""
    if h_inv is None or not plan:
        return img
    ax, bx, ay, by = 1.0, 0.0, 1.0, 0.0
    if cam_to_robot and cam_to_robot.get("ax") and cam_to_robot.get("ay"):
        ax, bx = float(cam_to_robot["ax"]), float(cam_to_robot["bx"])
        ay, by = float(cam_to_robot["ay"]), float(cam_to_robot["by"])
    out = img.copy()
    for pl in plan:
        if len(pl) < 2:
            continue
        pts = np.array([[[(x - bx) / ax * vision.PX_PER_MM, (y - by) / ay * vision.PX_PER_MM]
                         for x, y in pl]], np.float32)
        cv2.polylines(out, [cv2.perspectiveTransform(pts, h_inv)[0].astype(np.int32)], False,
                      color_bgr, 2, cv2.LINE_AA)
    return out


def render_plan(session, img: np.ndarray, source: str, h_inv, cam_to_robot) -> np.ndarray:
    """The server-side plan overlay for `?overlay=1` clients: on any look-pose picture, live or held."""
    if not session.plan or not (session.at_look or source == "held"):
        return img
    color = hex_to_bgr(cfg.COLOR_HEX.get(getattr(session, "color", "green"), "#222222"))
    return overlay(img, session.plan, h_inv, color, cam_to_robot)


async def mjpeg(session, frames, render, period_s: float = STREAM_PERIOD_S, keepalive_s: float = STREAM_KEEPALIVE_S):
    """Multipart JPEG chunks, one per new picture, plus a keepalive resend of the current picture so a
    proxy does not cut an idle response; nothing while the picture is stale. `render(session, img, source)`
    may draw on the picture before it is scaled and encoded."""
    key = None
    sent_at = 0.0
    while True:
        source, img, k = feed_pick(session, frames)
        now = monotonic()
        if k is not None and (k != key or now - sent_at >= keepalive_s):
            key = k
            sent_at = now
            yield mjpeg_part(stream_size(render(session, img, source)))
        await asyncio.sleep(period_s)


async def watch_feed(session, frames, bus, period_s: float = STREAM_PERIOD_S) -> None:
    """One task per app: tells the page which picture the stream is showing, on change only."""
    source = None
    while True:
        now = feed_pick(session, frames)[0]
        if now != source:
            source = now
            bus.emit("feed", source=source)
        await asyncio.sleep(period_s)


RELAUNCHABLE = ("idle", "human_turn", "finished", "paused")   # the arm is at the look pose or stopped: the run may exit


def make_app(session, frames, bus, sessions_dir: Path = cfg.SESSIONS_DIR, calibration: dict | None = None,
             relaunch=None) -> FastAPI:
    """`relaunch()` asks the run to exit cleanly (the arm is stopped on the way out); under demo.sh the
    run comes back five seconds later with whatever code is on disk. Without one the command is refused."""
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        task = watch(asyncio.create_task(watch_feed(session, frames, bus), name="feed"))
        try:
            yield
        finally:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await task

    app = FastAPI(title="Duet", lifespan=lifespan)
    sessions_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/sessions", StaticFiles(directory=str(sessions_dir)), name="sessions")
    app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")   # the page's css and js, once it splits them out
    h_inv = None
    cam_to_robot: dict | None = None
    calib: dict = {}
    if calibration and "marks_image" in calibration:
        quad = vision.board_quad(np.array(calibration["marks_image"], np.float32), calibration["board_tl_index"])
        h_inv = np.linalg.inv(vision.board_homography(quad))
        cam_to_robot = calibration.get("cam_to_robot")
        # The page registers its own layers onto the camera image with this; see the mockup session's protocol.
        calib = {"marks_image": calibration["marks_image"], "board_tl_index": calibration["board_tl_index"],
                 "board_mm": [cfg.BOARD_W_MM, cfg.BOARD_H_MM], "image_size": list(IMAGE_SIZE),
                 "cam_to_robot": cam_to_robot}
        bus.emit("calib", **calib)

    @app.get("/")
    async def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/health")
    async def health():
        return {"state": session.state, "turn": session.turn}

    @app.get("/calibration.json")
    async def calibration_json():
        return calib

    async def handle(cmd: dict) -> dict | None:
        kind = cmd.get("type")
        if kind == "set":
            changes = {k: v for k, v in cmd.items() if k in ALLOWED_SETTINGS}
            try:
                if "exchanges" in changes:
                    changes["exchanges"] = int(changes["exchanges"])
                for key in ("energy", "direction"):
                    if key in changes:
                        changes[key] = float(changes[key])
                session.update_settings(**changes)
            except (ValueError, TypeError) as exc:
                return {"type": "error", "message": f"setting refused: {exc}"}
            return None
        if kind == "pause":
            await session.pause()
        elif kind == "resume":
            session.resume()
        elif kind == "pass":
            session.pass_turn()
        elif kind == "end":
            session.end()
        elif kind == "clear_error":
            await session.clear_error()
        elif kind == "restart":
            session.restart()
        elif kind == "reset_arm":
            await session.reset_arm()
        elif kind == "relaunch":
            if relaunch is None:
                return {"type": "error", "message": "relaunch refused: this run has no relauncher (start it with demo.sh)"}
            if session.state not in RELAUNCHABLE:
                return {"type": "error", "message": "relaunch refused: the robot is moving; wait for the look pose or pause first"}
            bus.emit("error", message="relaunching the run; the page comes back on its own in about 15 seconds")
            relaunch()
        else:
            return {"type": "error", "message": f"unknown command {kind!r}"}
        return None

    @app.websocket("/ws")
    async def ws(sock: WebSocket):
        await sock.accept()
        q = bus.subscribe()
        pump: asyncio.Task | None = None
        try:
            for msg in bus.snapshot():
                await sock.send_json(msg)

            async def forward():
                try:
                    while True:
                        await sock.send_json(await q.get())
                except Exception:
                    # A payload that will not serialize would otherwise leave the page holding a live
                    # socket that never updates again; close it so its reconnect loop takes over.
                    with contextlib.suppress(Exception):
                        await sock.close(code=1011)
                    raise
            pump = asyncio.create_task(forward())
            while True:
                cmd = await sock.receive_json()
                try:
                    reply = (await handle(cmd) if isinstance(cmd, dict)
                             else {"type": "error", "message": "command must be an object"})
                except Exception as exc:   # a command that fails (the arm is offline, say) must not close the page
                    reply = {"type": "error", "message": f"command failed: {exc}"}
                if reply is not None:
                    await sock.send_json(reply)
        except (WebSocketDisconnect, ValueError):  # ValueError: a frame that is not JSON
            pass
        finally:
            if pump is not None:
                pump.cancel()
                with contextlib.suppress(asyncio.CancelledError, Exception):
                    await pump
            bus.unsubscribe(q)

    @app.get("/stream.mjpg")
    async def stream(overlay_on: int = Query(1, alias="overlay")):
        """`?overlay=0` skips the server-side stroke overlay, for a page that draws its own layers."""
        parts = mjpeg(session, frames,
                      lambda s, img, source: render_plan(s, img, source, h_inv, cam_to_robot) if overlay_on else img)
        return StreamingResponse(parts, media_type="multipart/x-mixed-replace; boundary=frame")

    return app
