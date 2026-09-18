"""Camera calibration from the look pose: find the four corner marks, record where they are and
which one is the board's top-left, and save a warped board image to check.

    python -m duet.calibrate                 detect the marks and save captures/calib_marks.jpg with labels A-D
    python -m duet.calibrate --tl C          record the calibration with image corner C as the board's top-left
    python -m duet.calibrate --check         re-detect within the calibrated regions and save the warped board

The arm must be at the look pose. Board top-left is the corner you touched off as `corner tl`.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from viam.components.camera import Camera

import viam_conn
from duet import config as cfg
from duet import vision
from duet.camera import median_capture

CAPTURES = Path(__file__).resolve().parent.parent / "captures"
LABELS = "ABCD"   # image order: top-left, top-right, bottom-right, bottom-left


def load_calibration() -> dict:
    return json.loads(cfg.CALIBRATION_PATH.read_text()) if cfg.CALIBRATION_PATH.exists() else {}


def save_calibration(data: dict) -> None:
    cfg.CALIBRATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = cfg.CALIBRATION_PATH.with_name(cfg.CALIBRATION_PATH.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    tmp.replace(cfg.CALIBRATION_PATH)


def annotate(frame: np.ndarray, quad: np.ndarray) -> np.ndarray:
    out = frame.copy()
    for name, (x, y) in zip(LABELS, quad):
        cv2.circle(out, (int(x), int(y)), 14, (0, 0, 255), 2)
        cv2.putText(out, name, (int(x) + 16, int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    return out


async def capture() -> np.ndarray:
    async with await viam_conn.connect() as machine:
        return await median_capture(Camera.from_robot(machine, viam_conn.CAMERA))


def main(argv: list[str]) -> None:
    CAPTURES.mkdir(exist_ok=True)
    frame = asyncio.run(capture())
    cv2.imwrite(str(CAPTURES / "calib_frame.jpg"), frame)
    if "--check" in argv:
        cal = load_calibration()
        quad = vision.find_corner_marks(frame, expected=cal["marks_image"])
        drift = max(float(np.hypot(*(np.array(q) - np.array(e)))) for q, e in zip(quad, cal["marks_image"]))
        board = vision.warp_to_board(frame, vision.board_quad(quad, cal["board_tl_index"]))
        cv2.imwrite(str(CAPTURES / "calib_board.jpg"), board)
        print(f"marks re-found; max drift {drift:.1f} px ({drift / vision.PX_PER_MM:.2f} mm). "
              f"Warped board saved to captures/calib_board.jpg")
        return
    quad = vision.find_corner_marks(frame)
    cv2.imwrite(str(CAPTURES / "calib_marks.jpg"), annotate(frame, quad))
    print("marks (image order A=top-left, B=top-right, C=bottom-right, D=bottom-left):",
          [(n, round(float(x)), round(float(y))) for n, (x, y) in zip(LABELS, quad)])
    if "--tl" not in argv:
        print("saved captures/calib_marks.jpg. Re-run with --tl <letter> to record which mark is the board's top-left.")
        return
    letter = argv[argv.index("--tl") + 1].upper()
    if letter not in LABELS:
        raise SystemExit("--tl needs A, B, C, or D")
    k = LABELS.index(letter)
    save_calibration({
        "marks_image": [[float(x), float(y)] for x, y in quad],
        "board_tl_index": k,
        "px_per_mm": vision.PX_PER_MM,
        "board_mm": [cfg.BOARD_W_MM, cfg.BOARD_H_MM],
    })
    board = vision.warp_to_board(frame, vision.board_quad(quad, k))
    cv2.imwrite(str(CAPTURES / "calib_board.jpg"), board)
    print(f"calibration saved to {cfg.CALIBRATION_PATH}; warped board in captures/calib_board.jpg")


if __name__ == "__main__":
    main(sys.argv[1:])
