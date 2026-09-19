"""Camera calibration from the look pose: find the four corner marks, record where they are and
which one is the board's top-left, and save a warped board image to check.

    python -m duet.calibrate                 detect the marks and save captures/calib_marks.jpg with labels A-D
    python -m duet.calibrate --tl C          record the calibration with image corner C as the board's top-left
    python -m duet.calibrate --check         re-detect within the calibrated regions and save the warped board
    python -m duet.calibrate --fit 15,15,20 120,180,20
                                             fit camera-to-robot scale and offset from squares the robot drew
                                             (top-left x, y and side, in robot mm); reads captures/calib_board.jpg
    python -m duet.calibrate --plane FILE    OFFLINE: fit the board plane for the depth hand check from a saved
                                             depth map (captures/depth.dep from explore.py, taken at the look pose)
    python -m duet.calibrate --dock x0 y0 x1 y1
                                             OFFLINE: record the dock tub's image rectangle for the hand check

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


def fit(squares: list[tuple[float, float, float]], line_mm: float = 1.0) -> None:
    """Measure each robot-drawn square in captures/calib_board.jpg and fit robot = a * cam + b per axis."""
    board = cv2.imread(str(CAPTURES / "calib_board.jpg"))
    xs, ys = [], []
    for x, y, side in squares:
        box = vision.find_square(board, (x + side / 2, y + side / 2))
        if box is None:
            raise SystemExit(f"no square found near ({x}, {y})")
        cx0, cy0, cx1, cy1 = box
        print(f"square at robot ({x}, {y}) side {side}: camera sees x {cx0:.1f}..{cx1:.1f}, y {cy0:.1f}..{cy1:.1f}")
        xs += [(cx0, x - line_mm / 2), (cx1, x + side + line_mm / 2)]
        ys += [(cy0, y - line_mm / 2), (cy1, y + side + line_mm / 2)]
    ax, bx = vision.fit_axis(xs)
    ay, by = vision.fit_axis(ys)
    cal = load_calibration()
    cal["cam_to_robot"] = {"ax": ax, "bx": bx, "ay": ay, "by": by}
    save_calibration(cal)
    print(f"fit: robot_x = {ax:.4f} * cam_x {bx:+.2f};  robot_y = {ay:.4f} * cam_y {by:+.2f}  (saved)")


def offline(argv: list[str]) -> bool:
    """The verbs that need no camera. Returns True when one ran."""
    cal = load_calibration()
    if "--dock" in argv:
        i = argv.index("--dock")
        x0, y0, x1, y1 = (int(v) for v in argv[i + 1:i + 5])
        cal["dock_region_image"] = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
        save_calibration(cal)
        print(f"dock region saved: x {x0}..{x1}, y {y0}..{y1}")
        return True
    if "--plane" in argv:
        from duet.camera import decode_depth
        path = Path(argv[argv.index("--plane") + 1])
        depth = np.load(path)["depth"] if path.suffix == ".npz" else decode_depth(path.read_bytes())
        quad = np.array(cal["marks_image"], dtype=np.float32)
        center = quad.mean(axis=0)
        padded = [[float(x + 25 * np.sign(x - center[0])), float(y + 25 * np.sign(y - center[1]))] for x, y in quad]
        plane = vision.fit_plane(depth, vision.polygon_mask(depth.shape, [padded]))
        cal.update({"plane": list(plane), "board_region_image": padded, "mm_per_px": vision.mm_per_px(quad)})
        expected = vision.plane_depth(depth.shape, plane)
        inside = (vision.polygon_mask(depth.shape, [padded]) > 0) & (depth > 0)
        resid = np.abs(depth[inside].astype(np.float32) - expected[inside])
        print(f"plane z = {plane[0]:.4f} x + {plane[1]:.4f} y + {plane[2]:.1f}; "
              f"median residual {np.median(resid):.1f} mm, {np.mean(resid < 15) * 100:.0f}% of readings within 15 mm")
        if "dock_region_image" in cal:
            dock = (vision.polygon_mask(depth.shape, [cal["dock_region_image"]]) > 0) & (depth > 0)
            cal["dock_offset_mm"] = float(np.median(expected[dock] - depth[dock].astype(np.float32)))
            print(f"dock surface sits {cal['dock_offset_mm']:.0f} mm above the board plane (hand check reference)")
        save_calibration(cal)
        return True
    return False


def main(argv: list[str]) -> None:
    CAPTURES.mkdir(exist_ok=True)
    if offline(argv):
        return
    if "--fit" in argv:
        specs = [tuple(float(v) for v in a.split(",")) for a in argv[argv.index("--fit") + 1:] if "," in a]
        fit(specs)
        return
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
