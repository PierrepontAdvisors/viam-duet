"""Pure functions on frames: corner marks, the board warp, new ink, tracing. No I/O, no robot."""
from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations

import cv2
import numpy as np

from duet import config as cfg

PX_PER_MM = 4
BOARD_PX = (int(round(cfg.BOARD_W_MM * PX_PER_MM)), int(round(cfg.BOARD_H_MM * PX_PER_MM)))  # (w, h)

Point = tuple[float, float]


def dark_blobs(bgr: np.ndarray, thresh: int = 30, min_area: int = 150, max_area: int = 6000) -> list[tuple[float, float, int]]:
    """Centroids and areas of compact dark blobs. The corner marks read 14 to 35 on the gray scale,
    ink about 45, the frame's shadow line about 100 and the board 120 to 130, so 40 isolates the marks.
    At a 450 mm camera height a mark is about 2000 px."""
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


# ---- new ink and tracing, on warped board images ------------------------------------------------

def drawable_mask() -> np.ndarray:
    """1 inside the drawable area (the board minus the inset), 0 elsewhere."""
    w, h = BOARD_PX
    m = np.zeros((h, w), dtype=np.uint8)
    i = int(cfg.INSET_MM * PX_PER_MM)
    m[i:h - i, i:w - i] = 1
    return m


def new_ink(current: np.ndarray, previous: np.ndarray, thresh: int = 40) -> tuple[np.ndarray, float]:
    """Mask (0/255) of pixels that got darker since the previous turn photo, inside the drawable area,
    and the fraction of the drawable area that is inked in `current` (for the end-of-session rule)."""
    cur = cv2.GaussianBlur(cv2.cvtColor(current, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    prev = cv2.GaussianBlur(cv2.cvtColor(previous, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    darker = np.clip(prev.astype(np.int16) - cur.astype(np.int16), 0, 255).astype(np.uint8)
    _, mask = cv2.threshold(darker, thresh, 255, cv2.THRESH_BINARY)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    area = drawable_mask()
    mask = mask * area
    ink_now = (cur < 90).astype(np.uint8) * area
    coverage = float(ink_now.sum()) / float(area.sum())
    return mask, coverage


def trace(mask: np.ndarray, simplify_mm: float = 0.5, min_len_mm: float = 3.0) -> list[list[Point]]:
    """Skeletonize an ink mask and return its paths as simplified polylines in board millimeters."""
    from skan import Skeleton
    from skimage.morphology import skeletonize

    sk = skeletonize(mask > 0)
    if int(sk.sum()) < 2:
        return []
    skel = Skeleton(sk)
    out: list[list[Point]] = []
    for i in range(skel.n_paths):
        coords = skel.path_coordinates(i)                       # (n, 2) rows, cols
        pts = np.array([[c, r] for r, c in coords], dtype=np.float32).reshape(-1, 1, 2)
        approx = cv2.approxPolyDP(pts, simplify_mm * PX_PER_MM, closed=False).reshape(-1, 2)
        pl = [(float(x) / PX_PER_MM, float(y) / PX_PER_MM) for x, y in approx]
        if len(pl) >= 2 and sum(np.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pl, pl[1:])) >= min_len_mm:
            out.append(pl)
    return out


# ---- camera-to-robot alignment ------------------------------------------------------------------

def find_square(board: np.ndarray, near_mm: Point, search_mm: float = 30.0, ink_thresh: int = 90) -> tuple[float, float, float, float] | None:
    """Bounding box (x0, y0, x1, y1) in board mm of the ink square drawn around `near_mm`, ignoring
    the corner marks (blobs touching the image border). None if nothing is there."""
    gray = cv2.GaussianBlur(cv2.cvtColor(board, cv2.COLOR_BGR2GRAY), (3, 3), 0)
    h, w = gray.shape
    blank = int(12 * PX_PER_MM)                               # the corner marks reach ~10 mm in; blank them
    for cx, cy in ((0, 0), (w, 0), (w, h), (0, h)):
        cv2.rectangle(gray, (cx - blank, cy - blank), (cx + blank, cy + blank), 255, -1)
    x0 = max(int((near_mm[0] - search_mm) * PX_PER_MM), 0)
    y0 = max(int((near_mm[1] - search_mm) * PX_PER_MM), 0)
    x1 = min(int((near_mm[0] + search_mm) * PX_PER_MM), w)
    y1 = min(int((near_mm[1] + search_mm) * PX_PER_MM), h)
    region = gray[y0:y1, x0:x1]
    _, mask = cv2.threshold(region, ink_thresh, 255, cv2.THRESH_BINARY_INV)
    n, _, stats, _ = cv2.connectedComponentsWithStats(mask)
    best = None
    for i in range(1, n):
        x, y, bw, bh, area = (int(v) for v in stats[i])
        touches_border = (x + x0 == 0 or y + y0 == 0 or x + x0 + bw >= w or y + y0 + bh >= h)
        if touches_border or area < 100:
            continue
        if best is None or area > best[0]:
            best = (area, x + x0, y + y0, bw, bh)
    if best is None:
        return None
    _, x, y, bw, bh = best
    return x / PX_PER_MM, y / PX_PER_MM, (x + bw) / PX_PER_MM, (y + bh) / PX_PER_MM


def fit_axis(cam_pairs: list[tuple[float, float]]) -> tuple[float, float]:
    """Least-squares robot = a * cam + b from (cam, robot) pairs."""
    cam = np.array([c for c, _ in cam_pairs]); rob = np.array([r for _, r in cam_pairs])
    a, b = np.polyfit(cam, rob, 1)
    return float(a), float(b)


def cam_to_robot(polylines: list[list[Point]], cal: dict) -> list[list[Point]]:
    """Apply the calibrated per-axis map so camera-board millimeters become robot-board millimeters."""
    m = cal.get("cam_to_robot")
    if not m:
        return polylines
    ax, bx, ay, by = m["ax"], m["bx"], m["ay"], m["by"]
    return [[(ax * x + bx, ay * y + by) for x, y in pl] for pl in polylines]


# ---- trigger readings: homography helpers, hand from depth or color, dock dots, stillness --------

def board_homography(quad_board_order: np.ndarray) -> np.ndarray:
    """3x3 map from image pixels to warped-board pixels (PX_PER_MM, origin at the board's top-left)."""
    w, h = BOARD_PX
    dst = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
    return cv2.getPerspectiveTransform(np.asarray(quad_board_order, dtype=np.float32), dst)


def to_board_mm(homography: np.ndarray, pts_px: list[Point]) -> list[Point]:
    """Image pixels to camera-board millimeters through the corner-mark homography."""
    out = cv2.perspectiveTransform(np.array([pts_px], dtype=np.float32), homography)[0]
    return [(float(x) / PX_PER_MM, float(y) / PX_PER_MM) for x, y in out]


def mm_per_px(quad_image: np.ndarray) -> float:
    """Average scale at the look pose: the board's area over the corner quad's pixel area."""
    area_px = abs(cv2.contourArea(np.asarray(quad_image, dtype=np.float32)))
    return math.sqrt(cfg.BOARD_W_MM * cfg.BOARD_H_MM / area_px)


def polygon_mask(shape_hw: tuple[int, int], polygons: list) -> np.ndarray:
    """1 inside any of the polygons (lists of (x, y) image points), 0 elsewhere."""
    m = np.zeros(shape_hw[:2], dtype=np.uint8)
    for poly in polygons:
        cv2.fillPoly(m, [np.asarray(poly, dtype=np.int32)], 1)
    return m


def fit_plane(depth: np.ndarray, mask: np.ndarray) -> tuple[float, float, float]:
    """Least-squares plane z = a*x + b*y + c through the valid readings inside `mask`. Readings far
    from the median (glare on the board reflects the ceiling and reads as meters) are dropped, and
    the fit is repeated without outliers."""
    ys, xs = np.nonzero((mask > 0) & (depth > 0))
    z = depth[ys, xs].astype(np.float64)
    if z.size < 100:
        raise ValueError("not enough valid depth readings inside the region")
    keep = np.abs(z - np.median(z)) < 80
    if keep.sum() < 100:
        raise ValueError("not enough valid depth readings inside the region")
    a = np.column_stack([xs, ys, np.ones_like(xs)]).astype(np.float64)
    coef, *_ = np.linalg.lstsq(a[keep], z[keep], rcond=None)
    keep = np.abs(a @ coef - z) < 15
    if keep.sum() >= 100:
        coef, *_ = np.linalg.lstsq(a[keep], z[keep], rcond=None)
    return float(coef[0]), float(coef[1]), float(coef[2])


def plane_depth(shape_hw: tuple[int, int], plane: tuple[float, float, float]) -> np.ndarray:
    a, b, c = plane
    ys, xs = np.mgrid[0:shape_hw[0], 0:shape_hw[1]]
    return (a * xs + b * ys + c).astype(np.float32)


def reference_depth(shape_hw: tuple[int, int], plane: tuple[float, float, float],
                    offsets: list[tuple[list, float]]) -> np.ndarray:
    """The surface a hand is measured against: the board plane, raised by `offset_mm` inside each
    polygon (the dock's putty stands above the board plane, so its own top is the reference there)."""
    ref = plane_depth(shape_hw, plane)
    for polygon, offset_mm in offsets:
        ref[polygon_mask(shape_hw, [polygon]) > 0] -= float(offset_mm)
    return ref


def _big_blob(mask: np.ndarray, mm2_per_px: float, area_mm2: float) -> bool:
    n, _, stats, _ = cv2.connectedComponentsWithStats(mask)
    return any(stats[i, cv2.CC_STAT_AREA] * mm2_per_px >= area_mm2 for i in range(1, n))


def hand_present_depth(depth: np.ndarray, region_mask: np.ndarray, expected_depth: np.ndarray,
                       mm2_per_px: float, height_mm: float = cfg.HAND_HEIGHT_MM,
                       area_mm2: float = cfg.HAND_AREA_MM2) -> bool:
    """True if a connected blob inside the region sits more than `height_mm` above the expected
    surface and covers at least `area_mm2`. Zero depth (no reading) never counts."""
    above = ((depth > 0) & (depth.astype(np.float32) < expected_depth - height_mm) & (region_mask > 0)).astype(np.uint8)
    above = cv2.morphologyEx(above, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    return _big_blob(above, mm2_per_px, area_mm2)


def hand_present_color(current: np.ndarray, reference: np.ndarray, region_mask: np.ndarray, mm2_per_px: float,
                       thresh: int = cfg.HAND_DIFF_THRESH, open_px: int = cfg.HAND_OPEN_PX,
                       area_mm2: float = cfg.HAND_COLOR_AREA_MM2) -> bool:
    """The backup when no depth plane is calibrated: compare the frame with the reference frame
    taken at the look pose after the robot's last turn. The difference is the largest of the three
    color channels, because on this camera's exposure the board reads mid-gray (about 127) and a
    medium skin tone has nearly the same gray level while its blue channel is far lower. New marker
    lines are thin and vanish under the opening; a hand is a big changed blob."""
    cur = cv2.GaussianBlur(current, (5, 5), 0)
    ref = cv2.GaussianBlur(reference, (5, 5), 0)
    diff = cv2.absdiff(cur, ref).max(axis=2)
    changed = ((diff > thresh) & (region_mask > 0)).astype(np.uint8)
    changed = cv2.morphologyEx(changed, cv2.MORPH_OPEN, np.ones((open_px, open_px), np.uint8))
    return _big_blob(changed, mm2_per_px, area_mm2)


@dataclass(frozen=True)
class DotReading:
    status: str                              # "home" | "moved" | "missing"
    displacement_mm: tuple[float, float]     # where the dot is relative to its recorded spot, camera-board axes


def dock_dots(frame_bgr: np.ndarray, slots: dict, homography: np.ndarray,
              tol_mm: float = cfg.DOT_TOLERANCE_MM, roi_px: int = 45) -> dict[str, DotReading]:
    """Per docked marker: is its colored end plug at the recorded image spot? `slots` comes from
    calibration.json: {"green": {"xy": [x, y], "hsv_lo": [...], "hsv_hi": [...]}}. The displacement
    is measured through the board homography so it is in board axes, ready for the pick correction."""
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    h, w = hsv.shape[:2]
    out: dict[str, DotReading] = {}
    for name, slot in slots.items():
        ex, ey = slot["xy"]
        x0, y0 = max(int(ex - roi_px), 0), max(int(ey - roi_px), 0)
        x1, y1 = max(min(int(ex + roi_px), w), 0), max(min(int(ey + roi_px), h), 0)
        if x1 <= x0 or y1 <= y0:
            out[name] = DotReading("missing", (0.0, 0.0))
            continue
        sub = hsv[y0:y1, x0:x1]
        mask = cv2.inRange(sub, np.array(slot["hsv_lo"], np.uint8), np.array(slot["hsv_hi"], np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, _, stats, cents = cv2.connectedComponentsWithStats(mask)
        best = max(range(1, n), key=lambda i: stats[i, cv2.CC_STAT_AREA], default=None)
        if best is None or stats[best, cv2.CC_STAT_AREA] < cfg.DOT_MIN_AREA_PX:
            out[name] = DotReading("missing", (0.0, 0.0))
            continue
        fx, fy = float(cents[best][0]) + x0, float(cents[best][1]) + y0
        (bx, by), (rx, ry) = to_board_mm(homography, [(fx, fy), (float(ex), float(ey))])
        d = (bx - rx, by - ry)
        out[name] = DotReading("home" if math.hypot(*d) <= tol_mm else "moved", d)
    return out


def still(frames: list[np.ndarray], thresh: float = cfg.STILL_THRESH) -> bool:
    """True when every consecutive pair of frames differs by less than `thresh` on average (gray,
    downsampled). Fewer than two frames is not still: there is nothing to compare."""
    if len(frames) < 2:
        return False
    small = [cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (160, 90), interpolation=cv2.INTER_AREA) for f in frames]
    return all(float(np.mean(cv2.absdiff(a, b))) < thresh for a, b in zip(small, small[1:]))
