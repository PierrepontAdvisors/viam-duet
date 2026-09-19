"""The page's server: the static page, one WebSocket carrying every session event and the page's
commands, an MJPEG stream of the camera with the planned strokes overlaid at the look pose, and the
session files. Local screen only; the public tunnel is P1."""
from __future__ import annotations

import asyncio
import contextlib
import time
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from duet import config as cfg
from duet import vision

STATIC = cfg.PACKAGE_DIR / "static"
ALLOWED_SETTINGS = ("artist", "length", "exchanges", "mode", "handoff", "energy", "direction")
STREAM_PERIOD_S = 0.2
NO_FRAME_AFTER_S = 2.0         # after this long without a frame the stream says so instead of freezing
PLACEHOLDER_SIZE = (360, 640)  # height, width of the "no camera frame" card
IMAGE_SIZE = (1280, 720)       # the RealSense color stream the calibration was made on


def hex_to_bgr(color: str) -> tuple[int, int, int]:
    c = color.lstrip("#")
    return int(c[4:6], 16), int(c[2:4], 16), int(c[0:2], 16)


def mjpeg_part(bgr: np.ndarray, quality: int = 70) -> bytes:
    ok, jpg = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("could not encode a stream frame")
    data = jpg.tobytes()
    return (b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(len(data)).encode()
            + b"\r\n\r\n" + data + b"\r\n")


def no_frame_part() -> bytes:
    """A card for the stream while the camera has given nothing, so the panel reads as stalled."""
    img = np.full((*PLACEHOLDER_SIZE, 3), 40, np.uint8)
    cv2.putText(img, "no camera frame", (110, 195), cv2.FONT_HERSHEY_SIMPLEX, 1.1,
                (200, 200, 200), 2, cv2.LINE_AA)
    return mjpeg_part(img)


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


def make_app(session, frames, bus, sessions_dir: Path = cfg.SESSIONS_DIR, calibration: dict | None = None) -> FastAPI:
    app = FastAPI(title="Duet")
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
        elif kind == "clear_error":
            await session.clear_error()
        elif kind == "restart":
            session.restart()
        elif kind == "reset_arm":
            await session.reset_arm()
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

    def shown(f, with_overlay: bool) -> np.ndarray:
        if not with_overlay or not session.at_look or not session.plan:
            return f.color
        color = hex_to_bgr(cfg.COLOR_HEX.get(getattr(session, "color", "green"), "#222222"))
        return overlay(f.color, session.plan, h_inv, color, cam_to_robot)

    async def mjpeg(with_overlay: bool):
        seen = time.monotonic()
        while True:
            f = frames.latest()
            if f is not None:
                seen = time.monotonic()
                yield mjpeg_part(shown(f, with_overlay))
            elif time.monotonic() - seen > NO_FRAME_AFTER_S:
                yield no_frame_part()
            await asyncio.sleep(STREAM_PERIOD_S)

    @app.get("/stream.mjpg")
    async def stream(overlay_on: int = Query(1, alias="overlay")):
        """`?overlay=0` skips the server-side stroke overlay, for a page that draws its own layers."""
        return StreamingResponse(mjpeg(bool(overlay_on)), media_type="multipart/x-mixed-replace; boundary=frame")

    return app
