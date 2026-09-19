"""Open strokes: every plan large, single-lined, and free of overlap, whatever the artist drew.
Pure functions on polylines in robot-board millimeters; the planner calls them around the artist's
styling. Dots (polylines shorter than DOT_EXEMPT_MM) pass through enlarge, uncross, thin, and cap."""
from __future__ import annotations

import math
import random

from shapely.geometry import LineString, Point, Polygon

from duet import config as cfg
from duet.strokes import Polyline, length, resample

SAMPLE_MM = 2.0
LOOP_MIN_MM = 20.0


def span(pl: Polyline) -> float:
    xs, ys = [p[0] for p in pl], [p[1] for p in pl]
    return max(max(xs) - min(xs), max(ys) - min(ys))


def _is_dot(pl: Polyline) -> bool:
    return len(pl) < 2 or length(pl) < cfg.DOT_EXEMPT_MM


def enlarge(polylines: list[Polyline], min_mm: float = cfg.MIN_SHAPE_MM, target_mm: float = cfg.TARGET_SHAPE_MM) -> list[Polyline]:
    """Shapes smaller than `min_mm` across are scaled about their centroid to `target_mm`."""
    out: list[Polyline] = []
    for pl in polylines:
        s = span(pl) if not _is_dot(pl) else 0.0
        if 0.0 < s < min_mm:
            k = target_mm / s
            cx, cy = sum(p[0] for p in pl) / len(pl), sum(p[1] for p in pl) / len(pl)
            pl = [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in pl]
        out.append(pl)
    return out


def uncross(pl: Polyline, gap: float = cfg.SELF_GAP_MM) -> Polyline:
    """Cut a stroke where it comes back within `gap` of an earlier part of itself. A stroke that
    returns to its own start after at least LOOP_MIN_MM is a loop and is closed instead of cut."""
    if _is_dot(pl):
        return list(pl)
    pts = resample(pl, SAMPLE_MM)
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    behind = 2 * gap                      # ignore the stroke's own recent past: tight curves are not crossings
    kept = [pts[0]]
    for i in range(1, len(pts)):
        p, hit = pts[i], None
        j = 0
        while j < i and cum[i] - cum[j] > behind:
            if math.dist(p, pts[j]) < gap:
                hit = j
                break
            j += 1
        if hit is None:
            kept.append(p)
            continue
        if cum[hit] <= behind and cum[i] >= LOOP_MIN_MM:
            kept.append(pts[0])           # closing back onto the start: a loop, closed exactly
        break
    return kept


def thin(polylines: list[Polyline], gap: float = cfg.PARALLEL_GAP_MM) -> list[Polyline]:
    """Drop a stroke that runs alongside an earlier kept stroke: more than half its samples within `gap`."""
    kept: list[Polyline] = []
    lines: list[LineString] = []
    for pl in polylines:
        if _is_dot(pl):
            kept.append(pl)
            continue
        samples = resample(pl, SAMPLE_MM)
        parallel = any(sum(1 for p in samples if line.distance(Point(p)) < gap) > len(samples) / 2 for line in lines)
        if parallel:
            continue
        kept.append(pl)
        lines.append(LineString(pl))
    return kept


def cap(polylines: list[Polyline], length_setting: str, caps: dict[str, int] = cfg.STROKE_CAP) -> list[Polyline]:
    """Keep the first `caps[length]` strokes; dots are never counted and pass through in place."""
    limit, count, out = caps[length_setting], 0, []
    for pl in polylines:
        if _is_dot(pl):
            out.append(pl)
        elif count < limit:
            out.append(pl)
            count += 1
    return out


def stipple(polygon: list[tuple[float, float]], spacing: float = cfg.DOT_SPACING_MM, jitter: float = cfg.DOT_JITTER_MM,
            dot_mm: float = cfg.DOT_MM, max_dots: int = cfg.DOTS_MAX, seed: int = 0) -> list[Polyline]:
    """Fill a polygon with sparse dots on a jittered grid, each a short tick; the grid widens until
    at most `max_dots` fit. The seed makes a replay draw the same dots."""
    poly = Polygon(polygon)
    if not poly.is_valid:
        poly = poly.buffer(0)
    if poly.is_empty:
        return []
    minx, miny, maxx, maxy = poly.bounds
    step = spacing
    while True:
        xs = [minx + step / 2 + i * step for i in range(int((maxx - minx) / step) + 1)]
        ys = [miny + step / 2 + i * step for i in range(int((maxy - miny) / step) + 1)]
        grid = [(x, y) for x in xs for y in ys if poly.contains(Point(x, y))]
        if len(grid) <= max_dots or step > max(maxx - minx, maxy - miny):
            break
        step *= 1.25
    rng = random.Random(seed)
    out: list[Polyline] = []
    for x, y in grid:
        jx, jy = rng.uniform(-jitter, jitter), rng.uniform(-jitter, jitter)
        out.append([(x + jx, y + jy), (x + jx + dot_mm, y + jy)])
    return out
