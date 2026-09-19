"""The page's server: the static page, one WebSocket carrying every session event and the page's
commands, an MJPEG stream of the camera with the planned strokes overlaid at the look pose, and the
session files. Local screen only; the public tunnel is P1."""
from __future__ import annotations

import asyncio
import contextlib
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


def make_app(session, frames, bus, sessions_dir: Path = cfg.SESSIONS_DIR, calibration: dict | None = None) -> FastAPI:
    app = FastAPI(title="Duet")
    sessions_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/sessions", StaticFiles(directory=str(sessions_dir)), name="sessions")
    app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")   # the page's css and js, once it splits them out
    h_inv = None
    calib: dict = {}
    if calibration and "marks_image" in calibration:
        quad = vision.board_quad(np.array(calibration["marks_image"], np.float32), calibration["board_tl_index"])
        h_inv = np.linalg.inv(vision.board_homography(quad))
        # The page registers its own layers onto the camera image with this; see the mockup session's protocol.
        calib = {"marks_image": calibration["marks_image"], "board_tl_index": calibration["board_tl_index"],
                 "board_mm": [cfg.BOARD_W_MM, cfg.BOARD_H_MM], "image_size": list(IMAGE_SIZE),
                 "cam_to_robot": calibration.get("cam_to_robot")}
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
                while True:
                    await sock.send_json(await q.get())
            pump = asyncio.create_task(forward())
            while True:
                reply = await handle(await sock.receive_json())
                if reply is not None:
                    await sock.send_json(reply)
        except WebSocketDisconnect:
            pass
        finally:
            if pump is not None:
                pump.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await pump
            bus.unsubscribe(q)

    def overlay(img: np.ndarray) -> np.ndarray:
        if h_inv is None or not session.plan or not session.at_look:
            return img
        out = img.copy()
        color = hex_to_bgr(cfg.COLOR_HEX.get(getattr(session, "color", "green"), "#222222"))
        for pl in session.plan:
            if len(pl) < 2:
                continue
            pts = np.array([[[x * vision.PX_PER_MM, y * vision.PX_PER_MM] for x, y in pl]], np.float32)
            cv2.polylines(out, [cv2.perspectiveTransform(pts, h_inv)[0].astype(np.int32)], False, color, 2, cv2.LINE_AA)
        return out

    async def mjpeg(with_overlay: bool):
        while True:
            f = frames.latest()
            if f is not None:
                yield mjpeg_part(overlay(f.color) if with_overlay else f.color)
            await asyncio.sleep(STREAM_PERIOD_S)

    @app.get("/stream.mjpg")
    async def stream(overlay_on: int = Query(1, alias="overlay")):
        """`?overlay=0` skips the server-side stroke overlay, for a page that draws its own layers."""
        return StreamingResponse(mjpeg(bool(overlay_on)), media_type="multipart/x-mixed-replace; boundary=frame")

    return app
