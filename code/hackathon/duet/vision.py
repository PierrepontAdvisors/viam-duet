"""Pure functions on frames: corner marks, the board warp, new ink, tracing. No I/O, no robot."""
from __future__ import annotations

from itertools import combinations

import cv2
import numpy as np

from duet import config as cfg

PX_PER_MM = 4
BOARD_PX = (int(round(cfg.BOARD_W_MM * PX_PER_MM)), int(round(cfg.BOARD_H_MM * PX_PER_MM)))  # (w, h)

Point = tuple[float, float]


def dark_blobs(bgr: np.ndarray, thresh: int = 60, min_area: int = 200, max_area: int = 2500) -> list[tuple[float, float, int]]:
    """Centroids and areas of compact dark blobs. The corner marks read about 35 on the gray scale and
    the board about 130; above 75 the marks fuse with the shadow line along the frame, so stay low."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY_INV)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, _, stats, cents = cv2.connectedComponentsWithStats(mask)
    out = []
    for i in range(1, n):
        area = int(stats[i, cv2.CC_STAT_AREA])
        w, h = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
        if min_area <= area <= max_area and 0.5 <= w / max(h, 1) <= 2.0:
            out.append((float(cents[i][0]), float(cents[i][1]), area))
    return out


def order_quad(pts) -> np.ndarray:
    """Four points ordered top-left, top-right, bottom-right, bottom-left in image axes."""
    p = np.array(pts, dtype=np.float32)
    s, d = p.sum(axis=1), p[:, 0] - p[:, 1]
    return np.array([p[np.argmin(s)], p[np.argmax(d)], p[np.argmax(s)], p[np.argmin(d)]], dtype=np.float32)


def _rectangle_score(q: np.ndarray) -> float | None:
    tl, tr, br, bl = q
    top, bottom = np.linalg.norm(tr - tl), np.linalg.norm(br - bl)
    left, right = np.linalg.norm(bl - tl), np.linalg.norm(br - tr)
    if min(top, bottom, left, right) < 40:
        return None
    if abs(top - bottom) / max(top, bottom) > 0.15 or abs(left - right) / max(left, right) > 0.15:
        return None
    v1, v2 = tr - tl, bl - tl
    if abs(float(np.dot(v1, v2)) / (np.linalg.norm(v1) * np.linalg.norm(v2))) > 0.2:
        return None
    return float(top * left)


def find_corner_marks(bgr: np.ndarray, expected: list[Point] | None = None, roi: int = 70) -> np.ndarray:
    """The four corner marks as an ordered quad (image tl, tr, br, bl). With `expected` centroids from
    calibration, each is searched within `roi` px of its last position; without, the four dark blobs
    forming the largest well-formed rectangle are taken."""
    if expected is not None:
        found = []
        for ex, ey in expected:
            x0, y0 = max(int(ex - roi), 0), max(int(ey - roi), 0)
            sub = bgr[y0:int(ey + roi), x0:int(ex + roi)]
            blobs = dark_blobs(sub)
            if not blobs:
                raise ValueError(f"corner mark near ({ex:.0f}, {ey:.0f}) not found")
            bx, by, _ = min(blobs, key=lambda b: (b[0] + x0 - ex) ** 2 + (b[1] + y0 - ey) ** 2)
            found.append((bx + x0, by + y0))
        return order_quad(found)
    blobs = dark_blobs(bgr)
    if len(blobs) < 4:
        raise ValueError(f"only {len(blobs)} dark blobs found; need 4 corner marks")
    best = None
    for combo in combinations(blobs[:16], 4):
        q = order_quad([(b[0], b[1]) for b in combo])
        score = _rectangle_score(q)
        if score is not None and (best is None or score > best[0]):
            best = (score, q)
    if best is None:
        raise ValueError("no rectangular set of four marks found")
    return best[1]


def board_quad(marks_image: np.ndarray, board_tl_index: int) -> np.ndarray:
    """Reorder an image-ordered quad into board order (tl, tr, br, bl). `board_tl_index` says which
    image corner is the board's top-left; board x (the short edge) runs to the neighbor along the
    shorter side, board y to the neighbor along the longer side."""
    q = marks_image
    k = board_tl_index
    nxt, prv = q[(k + 1) % 4], q[(k - 1) % 4]
    tl = q[k]
    if np.linalg.norm(nxt - tl) <= np.linalg.norm(prv - tl):
        tr, bl = nxt, prv
    else:
        tr, bl = prv, nxt
    br = q[(k + 2) % 4]
    return np.array([tl, tr, br, bl], dtype=np.float32)


def warp_to_board(bgr: np.ndarray, quad_board_order: np.ndarray) -> np.ndarray:
    """Flat top-down board image at PX_PER_MM, origin at the board's top-left."""
    w, h = BOARD_PX
    dst = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
    m = cv2.getPerspectiveTransform(quad_board_order, dst)
    return cv2.warpPerspective(bgr, m, (w, h))


def px_to_mm(x_px: float, y_px: float) -> Point:
    return x_px / PX_PER_MM, y_px / PX_PER_MM
